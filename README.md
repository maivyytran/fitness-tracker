# Fitness Class Membership Tracker

A web application built with Streamlit and PostgreSQL that allows fitness studio staff to manage members, instructors, classes, membership plans, and class registrations. Staff can track membership status, monitor class capacity, and view registration history over time.

## Live App

🔗 https://fitness-tracker-01.streamlit.app/

## ERD 

<img width="500" height="300" alt="project1_ERD" src="https://github.com/user-attachments/assets/44efc244-adbe-4a07-b81b-68caee3d9e83" />

## Table Descriptions

### membership_plan: Stores the types of membership plans available at the studio.

| Column | Type | Description |
|---|---|---|
| planID | SERIAL PK | Unique identifier for each plan |
| plan_name | VARCHAR(100) | Name of the plan (e.g. 4x Month, 6x Month, etc.) |
| price_per_month | NUMERIC(8,2) | Monthly cost of the plan |
| classes_per_month | INTEGER | Number of classes included per month |
| description | TEXT | Optional description of the plan |

### member: Stores gym member profiles and their assigned membership plan.

| Column | Type | Description |
|---|---|---|
| memberID | SERIAL PK | Unique identifier for each member |
| planID | INTEGER FK | References membership_plan(planID) |
| first_name | VARCHAR(100) | Member's first name |
| last_name | VARCHAR(100) | Member's last name |
| email | VARCHAR(100) | Member's unique email address |
| phone | VARCHAR(20) | Optional phone number |
| active | BOOLEAN | Whether the member is currently active |
| joined_at | TIMESTAMP | Date and time the member was added |

### instructor: Stores instructor profiles for staff who lead fitness classes.

| Column | Type | Description |
|---|---|---|
| instructorID | SERIAL PK | Unique identifier for each instructor |
| first_name | VARCHAR(100) | Instructor's first name |
| last_name | VARCHAR(100) | Instructor's last name |
| email | VARCHAR(100) | Instructor's unique email address |
| specialty | VARCHAR(100) | Optional area of specialty (e.g. Yoga, HIIT) |

### class: Stores fitness classes offered by the studio, each linked to an instructor.

| Column | Type | Description |
|---|---|---|
| classID | SERIAL PK | Unique identifier for each class |
| class_name | VARCHAR(100) | Name of the class (e.g. Spin, Pilates) |
| instructorID | INTEGER FK | References instructor(instructorID) |
| day_of_week | VARCHAR(20) | Day the class is held |
| class_time | VARCHAR(20) | Time the class starts (e.g. 9:00 AM) |
| capacity | INTEGER | Maximum number of members allowed |
| duration | INTEGER | Length of the class in minutes |

### registration: Junction table linking members to classes. Tracks which members are registered for which classes.

| Column | Type | Description |
|---|---|---|
| registrationID | SERIAL PK | Unique identifier for each registration |
| memberID | INTEGER FK | References member(memberID) — cascades on delete |
| classID | INTEGER FK | References class(classID) — cascades on delete |
| registered_at | TIMESTAMP | Date and time the registration was created |


## How to Run Locally

### 1. Clone the repository
```bash
git clone https://github.com/[YOUR GITHUB USERNAME]/[YOUR REPO NAME].git
cd [YOUR REPO NAME]
```
### 2. Install dependencies
```bash
pip install -r requirements.txt
```
### 3. Set up your database secrets
Create a file at `.streamlit/secrets.toml` in the project root and add your PostgreSQL connection string:
```toml
DB_URL = "postgresql://your_user:your_password@your_host:5432/your_db"
```
> ⚠️ Never commit this file to GitHub. Make sure `.streamlit/secrets.toml` is in your `.gitignore`.

### 4. Run the app
```bash
streamlit run streamlit_app.py
```
The app will open in your browser at `http://localhost:8501`.


