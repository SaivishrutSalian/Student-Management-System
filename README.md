# Student Management System - Faculty Module

A comprehensive, Flask-based robust Faculty Management Module designed to streamline daily academic operations for college faculty and Heads of Department (HODs). This application is a part of a larger Student Management System, providing a centralized hub for managing classes, students, assignments, and course materials.

## ✨ Key Features

- **Role-Based Access Control (RBAC):** Secure login subsystem differentiating privileges between typical Faculty members and Heads of Department (HODs).
- **Personalized Timetables:** Individualized faculty scheduling for managing classes effectively.
- **Student & Attendance Management:** Direct tracking and management of subjective student profiles, grades, and daily attendance parameters.
- **Course Material Hub:** A centralized, organized repository for securely uploading, storing, and filtering course documents (PDFs, DOCs, PPTs) tailored to specific student batches.
- **Virtual Classrooms & Assignments:** Supports assignment distribution, submission tracking, and virtual classroom interactions.
- **Automated Email Notifications:** Integrates with Gmail's SMTP service to send out automated alerts for new assignments, updates, and organizational notices.

## 🛠️ Technology Stack

- **Backend Architecture:** Python, Flask, Flask Blueprint (Modular structure)
- **Database:** MongoDB (via PyMongo)
- **Frontend / UI:** HTML, Vanilla CSS (Dark/Light mode themes), JavaScript
- **Mailing:** Flask-Mail (SMTP Integration)
- **Environment Management:** `python-dotenv` for secure environment variable handling

## 📁 Project Structure

```text
FacultyProject/
├── app.py                 # Main entry point for the Flask application
├── config.py              # Application configuration and environment loader
├── database.py            # MongoDB connection and collection initializations
├── extensions.py          # Flask extensions (like Flask-Mail) setup
├── routes/                # Modular Flask Blueprints for various app functionalities
│   ├── announcements.py
│   ├── assignments.py
│   ├── attendance.py
│   ├── classrooms.py
│   ├── dashboard.py
│   ├── materials.py
│   └── students.py
├── scripts/               # Local utility scripts for DB migration, dummy data, etc.
├── static/                # Static assets (CSS, JS, Uploaded Course Materials)
├── templates/             # Jinja2 HTML templates for rendering UI
├── .env                   # Local Environment Variables (Git ignored)
└── .gitignore             # Ignored files for version control
```

## 🚀 Getting Started

Follow these steps to set up the project locally.

### 1. Prerequisites
Ensure you have the following installed on your machine:
- **Python 3.8+**
- **MongoDB** (Local instance or a MongoDB Atlas URI)

### 2. Installation
Clone the repository and install the dependencies (assuming you are inside the `FacultyProject` directory):

```bash
# Optional: It is recommended to create a virtual environment first
python -m venv venv
venv\Scripts\activate  # On Windows

# Install required packages (Make sure your requirements.txt is updated or adjust as needed)
pip install flask pymongo python-dotenv flask-mail
```

### 3. Environment Configuration
The application relies on a `.env` file for sensitive credentials. Ensure your `.env` contains the following variables at the root of `FacultyProject`:

```env
MONGO_URI="your_mongodb_connection_string"
MAIL_USERNAME="your_gmail_address"
MAIL_PASSWORD="your_gmail_app_password"
```

### 4. Running the Application
Launch the Flask server with the following command:

```bash
python app.py
```
The application will launch on `http://localhost:5001`.

## 🧑‍💻 Usage & Scripts
For testing purposes and initial setup, the `scripts/` folder provides utility tools:
- **`python scripts/get_faculty_users.py`** - Quickly fetches and prints registered faculty members from the database.
- **`scratch-*.py` scripts** - Use these files to seamlessly insert or manipulate dummy database records for testing edge cases.
