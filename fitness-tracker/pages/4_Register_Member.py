import streamlit as st
import psycopg2

st.set_page_config(page_title="Register Member", page_icon="📝")

def get_connection():
    return psycopg2.connect(st.secrets["DB_URL"])

def get_active_members():
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("""
        SELECT memberID, first_name || ' ' || last_name
        FROM member WHERE active = true ORDER BY last_name;
    """)
    members = cur.fetchall()
    cur.close()
    conn.close()
    return members

def get_classes():
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("""
        SELECT c.classID,
               c.class_name || ' — ' || c.day_of_week || ' ' || c.class_time AS label,
               c.capacity
        FROM class c ORDER BY c.class_name;
    """)
    classes = cur.fetchall()
    cur.close()
    conn.close()
    return classes

def get_registration_count(class_id):
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("SELECT COUNT(*) FROM registration WHERE classID=%s;", (class_id,))
    count = cur.fetchone()[0]
    cur.close()
    conn.close()
    return count

st.title("📝 Register Member for a Class")

# ── Register Form ────────────────────────────────────────────
st.subheader("New Registration")

members = get_active_members()
classes = get_classes()

if not members:
    st.warning("No active members found. Please add a member first.")
elif not classes:
    st.warning("No classes found. Please add a class first.")
else:
    member_options = {m[1]: m[0] for m in members}
    class_options = {c[1]: (c[0], c[2]) for c in classes}

    with st.form("register_form"):
        selected_member = st.selectbox("Select Member", options=list(member_options.keys()))
        selected_class = st.selectbox("Select Class", options=list(class_options.keys()))
        submitted = st.form_submit_button("Register")

        if submitted:
            member_id = member_options[selected_member]
            class_id, capacity = class_options[selected_class]
            current_count = get_registration_count(class_id)

            if current_count >= capacity:
                st.error(f"⚠️ '{selected_class}' is full ({current_count}/{capacity} spots taken).")
            else:
                try:
                    conn = get_connection()
                    cur = conn.cursor()
                    cur.execute("""
                        INSERT INTO registration (memberID, classID)
                        VALUES (%s, %s);
                    """, (member_id, class_id))
                    conn.commit()
                    cur.close()
                    conn.close()
                    st.success(f"✅ '{selected_member}' registered for '{selected_class}'!")
                except psycopg2.errors.UniqueViolation:
                    st.error("⚠️ This member is already registered for that class.")
                except Exception as e:
                    st.error(f"Error: {e}")

st.markdown("---")

# ── Search / Filter Registrations ───────────────────────────
st.subheader("🔍 Search Registrations")

search = st.text_input("Search by member name or class name")

try:
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("""
        SELECT m.first_name || ' ' || m.last_name AS member,
               c.class_name, c.day_of_week, c.class_time,
               r.registered_at, r.registrationID
        FROM registration r
        JOIN member m ON r.memberID = m.memberID
        JOIN class c ON r.classID = c.classID
        ORDER BY r.registered_at DESC;
    """)
    all_registrations = cur.fetchall()
    cur.close()
    conn.close()
except Exception as e:
    st.error(f"Error: {e}")
    all_registrations = []

if search:
    filtered = [
        r for r in all_registrations
        if search.lower() in r[0].lower() or search.lower() in r[1].lower()
    ]
else:
    filtered = all_registrations

if not filtered:
    st.info("No registrations found.")
else:
    for r in filtered:
        member, cname, day, time, reg_at, rid = r
        with st.expander(f"{member} → {cname} ({day} {time})"):
            st.write(f"Registered: {reg_at.strftime('%Y-%m-%d %H:%M')}")
            confirm = st.checkbox(
                f"⚠️ Confirm remove this registration?",
                key=f"confirm_del_reg_{rid}"
            )
            if confirm:
                try:
                    conn = get_connection()
                    cur = conn.cursor()
                    cur.execute("DELETE FROM registration WHERE registrationID=%s;", (rid,))
                    conn.commit()
                    cur.close()
                    conn.close()
                    st.success("🗑️ Registration removed.")
                    st.rerun()
                except Exception as e:
                    st.error(f"Error: {e}")