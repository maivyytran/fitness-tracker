import streamlit as st
import psycopg2

st.set_page_config(page_title="Fitness Class Tracker", page_icon="🏋️")

def get_connection():
    return psycopg2.connect(st.secrets["DB_URL"])

st.title("🏋️ Fitness Class Membership Tracker")
st.write("Use the sidebar to manage members, classes, instructors, and registrations.")
st.markdown("---")
st.subheader("📊 Dashboard")

try:
    conn = get_connection()
    cur = conn.cursor()

    cur.execute("SELECT COUNT(*) FROM member WHERE active = true;")
    active_members = cur.fetchone()[0]

    cur.execute("SELECT COUNT(*) FROM class;")
    total_classes = cur.fetchone()[0]

    cur.execute("SELECT COUNT(*) FROM instructor;")
    total_instructors = cur.fetchone()[0]

    cur.execute("""
        SELECT COUNT(*) FROM registration
        WHERE DATE_TRUNC('month', registered_at) = DATE_TRUNC('month', CURRENT_DATE);
    """)
    registrations_this_month = cur.fetchone()[0]

    col1, col2, col3, col4 = st.columns(4)
    col1.metric("Active Members", active_members)
    col2.metric("Classes", total_classes)
    col3.metric("Instructors", total_instructors)
    col4.metric("Registrations This Month", registrations_this_month)

    st.markdown("---")
    st.subheader("📋 Recent Registrations")
    cur.execute("""
        SELECT m.first_name || ' ' || m.last_name AS member,
               c.class_name, c.day_of_week, c.class_time,
               r.registered_at
        FROM registration r
        JOIN member m ON r.memberID = m.memberID
        JOIN class c ON r.classID = c.classID
        ORDER BY r.registered_at DESC
        LIMIT 10;
    """)
    rows = cur.fetchall()
    cur.close()
    conn.close()

    if rows:
        st.table([{
            "Member": row[0],
            "Class": row[1],
            "Day": row[2],
            "Time": row[3],
            "Registered": row[4].strftime("%Y-%m-%d %H:%M")
        } for row in rows])
    else:
        st.info("No registrations yet. Add members and classes to get started!")

except Exception as e:
    st.error(f"Error: {e}")