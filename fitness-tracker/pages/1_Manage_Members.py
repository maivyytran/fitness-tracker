import streamlit as st
import psycopg2
import re

st.set_page_config(page_title="Manage Members", page_icon="👤")

def get_connection():
    return psycopg2.connect(st.secrets["DB_URL"])

def get_plans():
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("SELECT planID, plan_name FROM membership_plan ORDER BY plan_name;")
    plans = cur.fetchall()
    cur.close()
    conn.close()
    return plans

st.title("👤 Manage Members")

# ── Add Member ──────────────────────────────────────────────
st.subheader("Add New Member")
plans = get_plans()
plan_options = {p[1]: p[0] for p in plans}

with st.form("add_member_form"):
    col1, col2 = st.columns(2)
    first_name = col1.text_input("First Name")
    last_name = col2.text_input("Last Name")
    email = st.text_input("Email")
    phone = st.text_input("Phone (optional, digits only)")
    selected_plan = st.selectbox("Membership Plan", options=list(plan_options.keys()))
    active = st.checkbox("Active", value=True)
    submitted = st.form_submit_button("Add Member")

    if submitted:
        email_pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        name_pattern = r'^[a-zA-Z\s]+$'

        if not first_name or not last_name or not email:
            st.warning("First name, last name, and email are required.")
        elif not re.match(name_pattern, first_name):
            st.warning("First name must contain letters only.")
        elif not re.match(name_pattern, last_name):
            st.warning("Last name must contain letters only.")
        elif not re.match(email_pattern, email):
            st.warning("Please enter a valid email address.")
        elif phone and not re.match(r'^\d{10}$', phone):
            st.warning("Phone must be exactly 10 digits.")
        elif not selected_plan:
            st.warning("Please select a membership plan.")
        else:
            try:
                conn = get_connection()
                cur = conn.cursor()
                cur.execute("""
                    INSERT INTO member (planID, first_name, last_name, email, phone, active)
                    VALUES (%s, %s, %s, %s, %s, %s);
                """, (plan_options[selected_plan], first_name, last_name, email,
                      phone if phone else None, active))
                conn.commit()
                cur.close()
                conn.close()
                st.success(f"✅ Member '{first_name} {last_name}' added successfully!")
            except psycopg2.errors.UniqueViolation:
                st.error("⚠️ A member with that email already exists.")
            except Exception as e:
                st.error(f"Error: {e}")

st.markdown("---")

# ── Edit / Delete ────────────────────────────────────────────
st.subheader("Current Members")

try:
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("""
        SELECT m.memberID, m.first_name, m.last_name, m.email, m.phone,
               m.active, p.plan_name
        FROM member m
        JOIN membership_plan p ON m.planID = p.planID
        ORDER BY m.last_name;
    """)
    members = cur.fetchall()
    cur.close()
    conn.close()
except Exception as e:
    st.error(f"Error: {e}")
    members = []

if not members:
    st.info("No members yet.")
else:
    for m in members:
        mid, fname, lname, email, phone, active, plan = m
        with st.expander(f"{lname}, {fname} — {plan} {'✅' if active else '❌'}"):

            # ── Edit form ────────────────────────────────────
            with st.form(f"edit_member_{mid}"):
                col1, col2 = st.columns(2)
                new_first = col1.text_input("First Name", value=fname)
                new_last = col2.text_input("Last Name", value=lname)
                new_email = st.text_input("Email", value=email)
                new_phone = st.text_input("Phone", value=phone or "")
                plans = get_plans()
                plan_options = {p[1]: p[0] for p in plans}
                plan_names = list(plan_options.keys())
                current_plan_index = plan_names.index(plan) if plan in plan_names else 0
                new_plan = st.selectbox("Membership Plan", options=plan_names, index=current_plan_index)
                new_active = st.checkbox("Active", value=active)
                save = st.form_submit_button("💾 Save Changes")

            if save:
                email_pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
                name_pattern = r'^[a-zA-Z\s]+$'
                if not new_first or not new_last or not new_email:
                    st.warning("First name, last name, and email are required.")
                elif not re.match(name_pattern, new_first):
                    st.warning("First name must contain letters only.")
                elif not re.match(name_pattern, new_last):
                    st.warning("Last name must contain letters only.")
                elif not re.match(email_pattern, new_email):
                    st.warning("Please enter a valid email address.")
                elif new_phone and not re.match(r'^\d{10}$', new_phone):
                    st.warning("Phone must be exactly 10 digits.")
                else:
                    try:
                        conn = get_connection()
                        cur = conn.cursor()
                        cur.execute("""
                            UPDATE member
                            SET first_name=%s, last_name=%s, email=%s,
                                phone=%s, planID=%s, active=%s
                            WHERE memberID=%s;
                        """, (new_first, new_last, new_email,
                              new_phone if new_phone else None,
                              plan_options[new_plan], new_active, mid))
                        conn.commit()
                        cur.close()
                        conn.close()
                        st.success("✅ Member updated successfully!")
                        st.rerun()
                    except psycopg2.errors.UniqueViolation:
                        st.error("⚠️ That email is already in use.")
                    except Exception as e:
                        st.error(f"Error: {e}")

            # ── Delete (outside form) ─────────────────────────
            st.markdown("**Delete Member**")
            confirm = st.checkbox(
                f"⚠️ Check to confirm deletion of '{fname} {lname}'. This will also remove all their registrations.",
                key=f"confirm_del_member_{mid}"
            )
            if confirm:
                if st.button("🗑️ Delete Member", key=f"del_btn_member_{mid}"):
                    try:
                        conn = get_connection()
                        cur = conn.cursor()
                        cur.execute("DELETE FROM member WHERE memberID=%s;", (mid,))
                        conn.commit()
                        cur.close()
                        conn.close()
                        st.success("🗑️ Member deleted.")
                        st.rerun()
                    except Exception as e:
                        st.error(f"Error: {e}")
