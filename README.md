# Faculty Project Matching System - Team 3

A web application that facilitates seamless matching between students and professors for third year and final year academic projects. The system supports project listing, applications, scheduling meetings, resume uploads, and has seperate role-based dashboards.

## Features

* Browse and apply for faculty-posted projects
* Upload resume individually for each role/application and describe statement of interest
* Faculty view of applicants with student profiles
* Calendar-based meeting slot booking
* Seperate dashboards for faculty and students

## Tech Stack

* **Backend:** Django and Python
* **Frontend:** HTML, CSS, Bootstrap, JavaScript, FullCalendar.js library
* **Database:** SQLite (to make it portable)

This simple tech stack allowed us to learn while implementing the features ourselves with minimal help from AI :)

## Setup Instructions

1. **Clone the repository**

   ```bash
   git clone https://github.com/sidran1310/facultyprojectsys.git
   cd facultyprojectsys
   ```

3. **Start the server**

   ```bash
   python manage.py runserver
   ```



## Contributions per student

* **Spoorthi and Vivek** – Worked on the user interface using HTML and CSS  
* **Sidhanth and Adya** – Handled backend logic using Django and SQLite 
* **Kruthi** – Managed project application forms, and meeting scheduling


## Credentials

This project includes user accounts which we used for development, testing and demo purposes. Users are categorized as **Superuser (Django admin)**, **Professors**, and **Students**. Use the credentials below to log in depending on the role:

### Superuser

| Role      | Email                | Password          |
|-----------|----------------------|-------------------|
| Admin     | `hello@hello.hello`  | `passwordpassword` |

Use this account to access the Django Admin Dashboard at:  
https://127.0.0.1:8000/admin

---

### Professors

| Name     | Email                             | Password     |
|----------|-----------------------------------|--------------|
| Sidhanth | `sidhanth@mahindrauniversity.edu.in` | `ihatemu456` |
| Adya     | `adya@mahindrauniversity.edu.in`     | `ilovemu123` |
| Avinash  | `avinash@mahindrauniversity.edu.in`  | `test123456` |

---

### Students

| Name     | Email                               | Password     |
|----------|-------------------------------------|--------------|
| Adya     | `se22uari205@mahindrauniversity.edu.in` | `ilovemu456` |
| Sidhanth | `se22uari161@mahindrauniversity.edu.in` | `ihatemu123` |

---

## Custom User Model & Role Auto-Detection

This project uses a **custom `User` model** that supports multiple roles (Student or Professor) via the `usertype` field and has automatic determination of role of user.

### How it works:

- On user creation via signup:
  - Emails following the pattern `rollno@mahindrauniversity.edu.in` are **automatically classified as Students**.
  - Emails like `name@mahindrauniversity.edu.in` are **automatically classified as Professors**.
- The `usertype` is stored and enforced across the platform.
- This classification logic helps direct users to the correct dashboards and access permissions.
- Only a **Django Admin** can change a user's type later through the admin interface.
- To prevent misuse i.e. anyone signing up as a professor there will be email verification when deployed on actual production server. Although we haven't incliuded an email system yet, due to Django's built-in support it will take very less time to set it up via SMTP which will be routed through a dedicated email address on our college domain

### Additional Note
- The instructions for a strong password is added automatically by Django, and attempts to supress those were breaking the entire login site, therefore we let it be, also it causes the user to not be able to use a password which involves their name or username/roll number, as well as passwords including common words like "qwerty" or "password".


