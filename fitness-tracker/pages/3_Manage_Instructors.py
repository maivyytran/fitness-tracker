import streamlit as st
import psycopg2
import re

st.set_page_config(page_title="Manage Instructors", page_icon="🧑‍🏫")

def get_connection():
    return psycopg2.connect(st.secrets["DB_URL"])

st.title("🧑‍🏫 Manage Instructors")

# ── Add Instructor ───────────────────────────────────────────
st.subheader("Add New Instructor")

with st.form("add_instructor_form"):
    col1, col2 = st.columns(2)
    first_name = col1.text_input("First Name")
    last_name = col2.text_input("Last Name")
    email = st.text_input("Email")
    specialty = st.text_input("Specialty (optional)")
    submitted = st.form_submit_button("Add Instructor")

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
        elif specialty and len(specialty) > 100:
            st.warning("Specialty must be 100 characters or fewer.")
        else:
            try:
                conn = get_connection()
                cur = conn.cursor()
                cur.execute("""
                    INSERT INTO instructor (first_name, last_name, email, specialty)
                    VALUES (%s, %s, %s, %s);
                """, (first_name, last_name, email, specialty if specialty else None))
                conn.commit()
                cur.close()
                conn.close()
                st.success(f"✅ Instructor '{first_name} {last_name}' added successfully!")
            except psycopg2.errors.UniqueViolation:
                st.error("⚠️ An instructor with that email already exists.")
            except Exception as e:
                st.error(f"Error: {e}")

st.markdown("---")

# ── Edit / Delete ────────────────────────────────────────────
st.subheader("Current Instructors")

try:
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("SELECT instructorID, first_name, last_name, email, specialty FROM instructor ORDER BY last_name;")
    instructors = cur.fetchall()
    cur.close()
    conn.close()
except Exception as e:
    st.error(f"Error: {e}")
    instructors = []

if not instructors:
    st.info("No instructors yet.")
else:
    for inst in instructors:
        iid, fname, lname, email, specialty = inst
        with st.expander(f"{lname}, {fname} — {specialty or 'No specialty listed'}"):
            with st.form(f"edit_instructor_{iid}"):
                col1, col2 = st.columns(2)
                new_first = col1.text_input("First Name", value=fname)
                new_last = col2.text_input("Last Name", value=lname)
                new_email = st.text_input("Email", value=email)
                new_specialty = st.text_input("Specialty", value=specialty or "")
                col_save, col_del = st.columns(2)
                save = col_save.form_submit_button("💾 Save Changes")
                delete = col_del.form_submit_button("🗑️ Delete Instructor")

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
                elif new_specialty and len(new_specialty) > 100:
                    st.warning("Specialty must be 100 characters or fewer.")
                else:
                    try:
                        conn = get_connection()
                        cur = conn.cursor()
                        cur.execute("""
                            UPDATE instructor
                            SET first_name=%s, last_name=%s, email=%s, specialty=%s
                            WHERE instructorID=%s;
                        """, (new_first, new_last, new_email,
                              new_specialty if new_specialty else None, iid))
                        conn.commit()
                        cur.close()
                        conn.close()
                        st.success("✅ Instructor updated successfully!")
                        st.rerun()
                    except psycopg2.errors.UniqueViolation:
                        st.error("⚠️ That email is already in use.")
                    except Exception as e:
                        st.error(f"Error: {e}")

            if delete:
                # Block delete if instructor is assigned to any class
                try:
                    conn = get_connection()
                    cur = conn.cursor()
                    cur.execute("SELECT COUNT(*) FROM class WHERE instructorID=%s;", (iid,))
                    class_count = cur.fetchone()[0]
                    cur.close()
                    conn.close()
                except Exception as e:
                    st.error(f"Error: {e}")
                    class_count = 1

                if class_count > 0:
                    st.error(f"⚠️ Cannot delete — this instructor is assigned to {class_count} class(es). Reassign or delete those classes first.")
                else:
                    confirm = st.checkbox(
                        f"⚠️ Confirm delete '{fname} {lname}'?",
                        key=f"confirm_del_instructor_{iid}"
                    )
                    if confirm:
                        try:
                            conn = get_connection()
                            cur = conn.cursor()
                            cur.execute("DELETE FROM instructor WHERE instructorID=%s;", (iid,))
                            conn.commit()
                            cur.close()
                            conn.close()
                            st.success("🗑️ Instructor deleted.")
                            st.rerun()
                        except Exception as e:
                            st.error(f"Error: {e}")