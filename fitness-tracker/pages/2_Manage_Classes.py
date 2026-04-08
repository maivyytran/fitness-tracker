import streamlit as st
import psycopg2

st.set_page_config(page_title="Manage Classes", page_icon="🏃")

def get_connection():
    return psycopg2.connect(st.secrets["DB_URL"])

def get_instructors():
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("SELECT instructorID, first_name || ' ' || last_name FROM instructor ORDER BY last_name;")
    instructors = cur.fetchall()
    cur.close()
    conn.close()
    return instructors

DAYS = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]

st.title("🏃 Manage Classes")

# ── Add Class ────────────────────────────────────────────────
st.subheader("Add New Class")
instructors = get_instructors()
instructor_options = {i[1]: i[0] for i in instructors}

if not instructors:
    st.warning("No instructors found. Please add an instructor first.")
else:
    with st.form("add_class_form"):
        class_name = st.text_input("Class Name")
        selected_instructor = st.selectbox("Instructor", options=list(instructor_options.keys()))
        day_of_week = st.selectbox("Day of Week", options=DAYS)
        class_time = st.text_input("Class Time (e.g. 9:00 AM)")
        capacity = st.number_input("Capacity", min_value=1, step=1, value=10)
        submitted = st.form_submit_button("Add Class")

        if submitted:
            if not class_name:
                st.warning("Class name is required.")
            elif len(class_name) > 100:
                st.warning("Class name must be 100 characters or fewer.")
            elif not class_time:
                st.warning("Class time is required.")
            elif capacity < 1:
                st.warning("Capacity must be at least 1.")
            else:
                try:
                    conn = get_connection()
                    cur = conn.cursor()
                    cur.execute("""
                        INSERT INTO class (class_name, instructorID, day_of_week, class_time, capacity)
                        VALUES (%s, %s, %s, %s, %s);
                    """, (class_name, instructor_options[selected_instructor],
                          day_of_week, class_time, capacity))
                    conn.commit()
                    cur.close()
                    conn.close()
                    st.success(f"✅ Class '{class_name}' added successfully!")
                except Exception as e:
                    st.error(f"Error: {e}")

st.markdown("---")

# ── Edit / Delete ────────────────────────────────────────────
st.subheader("Current Classes")

try:
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("""
        SELECT c.classID, c.class_name, c.day_of_week, c.class_time,
               c.capacity, i.first_name || ' ' || i.last_name AS instructor
        FROM class c
        JOIN instructor i ON c.instructorID = i.instructorID
        ORDER BY c.day_of_week, c.class_time;
    """)
    classes = cur.fetchall()
    cur.close()
    conn.close()
except Exception as e:
    st.error(f"Error: {e}")
    classes = []

if not classes:
    st.info("No classes yet.")
else:
    for cls in classes:
        cid, cname, day, time, cap, instructor = cls
        with st.expander(f"{cname} — {day} at {time} (Instructor: {instructor})"):
            instructors = get_instructors()
            instructor_options = {i[1]: i[0] for i in instructors}
            instructor_names = list(instructor_options.keys())
            current_instructor_index = instructor_names.index(instructor) if instructor in instructor_names else 0

            with st.form(f"edit_class_{cid}"):
                new_name = st.text_input("Class Name", value=cname)
                new_instructor = st.selectbox("Instructor", options=instructor_names, index=current_instructor_index)
                new_day = st.selectbox("Day of Week", options=DAYS, index=DAYS.index(day) if day in DAYS else 0)
                new_time = st.text_input("Class Time", value=time)
                new_cap = st.number_input("Capacity", min_value=1, step=1, value=cap)
                col_save, col_del = st.columns(2)
                save = col_save.form_submit_button("💾 Save Changes")
                delete = col_del.form_submit_button("🗑️ Delete Class")

            if save:
                if not new_name:
                    st.warning("Class name is required.")
                elif not new_time:
                    st.warning("Class time is required.")
                elif new_cap < 1:
                    st.warning("Capacity must be at least 1.")
                else:
                    try:
                        conn = get_connection()
                        cur = conn.cursor()
                        cur.execute("""
                            UPDATE class
                            SET class_name=%s, instructorID=%s, day_of_week=%s,
                                class_time=%s, capacity=%s
                            WHERE classID=%s;
                        """, (new_name, instructor_options[new_instructor],
                              new_day, new_time, new_cap, cid))
                        conn.commit()
                        cur.close()
                        conn.close()
                        st.success("✅ Class updated successfully!")
                        st.rerun()
                    except Exception as e:
                        st.error(f"Error: {e}")

            if delete:
                confirm = st.checkbox(
                    f"⚠️ Confirm delete '{cname}'? This will also remove all registrations for this class.",
                    key=f"confirm_del_class_{cid}"
                )
                if confirm:
                    try:
                        conn = get_connection()
                        cur = conn.cursor()
                        cur.execute("DELETE FROM class WHERE classID=%s;", (cid,))
                        conn.commit()
                        cur.close()
                        conn.close()
                        st.success("🗑️ Class deleted.")
                        st.rerun()
                    except Exception as e:
                        st.error(f"Error: {e}")