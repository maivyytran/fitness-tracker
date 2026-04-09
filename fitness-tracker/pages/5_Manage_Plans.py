import streamlit as st
import psycopg2

st.set_page_config(page_title="Manage Plans", page_icon="💳")

def get_connection():
    return psycopg2.connect(st.secrets["DB_URL"])

st.title("💳 Manage Membership Plans")

# ── Add Plan ─────────────────────────────────────────────────
st.subheader("Add New Plan")

with st.form("add_plan_form"):
    plan_name = st.text_input("Plan Name")
    col1, col2 = st.columns(2)
    price = col1.number_input("Price Per Month ($)", min_value=0.0, step=0.01, format="%.2f")
    classes_per_month = col2.number_input("Classes Per Month", min_value=1, step=1, value=1)
    description = st.text_area("Description (optional)", max_chars=500)
    submitted = st.form_submit_button("Add Plan")

    if submitted:
        if not plan_name:
            st.warning("Plan name is required.")
        elif len(plan_name) > 100:
            st.warning("Plan name must be 100 characters or fewer.")
        elif price < 0:
            st.warning("Price must be a positive number.")
        elif classes_per_month < 1:
            st.warning("Classes per month must be at least 1.")
        else:
            try:
                conn = get_connection()
                cur = conn.cursor()
                cur.execute("""
                    INSERT INTO membership_plan (plan_name, price_per_month, classes_per_month, description)
                    VALUES (%s, %s, %s, %s);
                """, (plan_name, price, classes_per_month, description if description else None))
                conn.commit()
                cur.close()
                conn.close()
                st.success(f"✅ Plan '{plan_name}' added successfully!")
            except psycopg2.errors.UniqueViolation:
                st.error("⚠️ A plan with that name already exists.")
            except Exception as e:
                st.error(f"Error: {e}")

st.markdown("---")

# ── Summary Metrics ──────────────────────────────────────────
st.subheader("📊 Plan Summary")

try:
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("""
        SELECT p.plan_name,
               COUNT(m.memberID) AS total_members,
               p.price_per_month,
               p.classes_per_month
        FROM membership_plan p
        LEFT JOIN member m ON p.planID = m.planID
        GROUP BY p.planID, p.plan_name, p.price_per_month, p.classes_per_month
        ORDER BY p.plan_name;
    """)
    summary = cur.fetchall()
    cur.close()
    conn.close()

    if summary:
        st.table([{
            "Plan": row[0],
            "Members Enrolled": row[1],
            "Price/Month": f"${row[2]:,.2f}",
            "Classes/Month": row[3]
        } for row in summary])
    else:
        st.info("No plans yet.")
except Exception as e:
    st.error(f"Error: {e}")

st.markdown("---")

# ── Edit / Delete ────────────────────────────────────────────
st.subheader("Current Plans")

try:
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("""
        SELECT planID, plan_name, price_per_month, classes_per_month, description
        FROM membership_plan ORDER BY plan_name;
    """)
    plans = cur.fetchall()
    cur.close()
    conn.close()
except Exception as e:
    st.error(f"Error: {e}")
    plans = []

if not plans:
    st.info("No plans yet.")
else:
    for plan in plans:
        pid, pname, price, classes, desc = plan
        with st.expander(f"{pname} — ${price:,.2f}/month — {classes} classes/month"):

            # ── Edit form ────────────────────────────────────
            with st.form(f"edit_plan_{pid}"):
                new_name = st.text_input("Plan Name", value=pname)
                col1, col2 = st.columns(2)
                new_price = col1.number_input("Price Per Month ($)", min_value=0.0,
                                               step=0.01, format="%.2f", value=float(price))
                new_classes = col2.number_input("Classes Per Month", min_value=1,
                                                 step=1, value=classes)
                new_desc = st.text_area("Description", value=desc or "", max_chars=500)
                save = st.form_submit_button("💾 Save Changes")

            if save:
                if not new_name:
                    st.warning("Plan name is required.")
                elif len(new_name) > 100:
                    st.warning("Plan name must be 100 characters or fewer.")
                elif new_price < 0:
                    st.warning("Price must be a positive number.")
                elif new_classes < 1:
                    st.warning("Classes per month must be at least 1.")
                else:
                    try:
                        conn = get_connection()
                        cur = conn.cursor()
                        cur.execute("""
                            UPDATE membership_plan
                            SET plan_name=%s, price_per_month=%s,
                                classes_per_month=%s, description=%s
                            WHERE planID=%s;
                        """, (new_name, new_price, new_classes,
                              new_desc if new_desc else None, pid))
                        conn.commit()
                        cur.close()
                        conn.close()
                        st.success("✅ Plan updated successfully!")
                        st.rerun()
                    except psycopg2.errors.UniqueViolation:
                        st.error("⚠️ A plan with that name already exists.")
                    except Exception as e:
                        st.error(f"Error: {e}")

            # ── Delete (outside form) ─────────────────────────
            st.markdown("**Delete Plan**")
            try:
                conn = get_connection()
                cur = conn.cursor()
                cur.execute("""
                    SELECT COUNT(*) FROM member
                    WHERE planID=%s AND active = true;
                """, (pid,))
                active_count = cur.fetchone()[0]
                cur.close()
                conn.close()
            except Exception as e:
                st.error(f"Error: {e}")
                active_count = 1

            if active_count > 0:
                st.error(f"⚠️ Cannot delete — {active_count} active member(s) are on this plan. Reassign them first.")
            else:
                confirm = st.checkbox(
                    f"⚠️ Check to confirm deletion of '{pname}'.",
                    key=f"confirm_del_plan_{pid}"
                )
                if confirm:
                    if st.button("🗑️ Delete Plan", key=f"del_btn_plan_{pid}"):
                        try:
                            conn = get_connection()
                            cur = conn.cursor()
                            cur.execute("DELETE FROM membership_plan WHERE planID=%s;", (pid,))
                            conn.commit()
                            cur.close()
                            conn.close()
                            st.success("🗑️ Plan deleted.")
                            st.rerun()
                        except Exception as e:
                            st.error(f"Error: {e}")
