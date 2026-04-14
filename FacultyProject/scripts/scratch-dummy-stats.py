import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from database import attendance_collection, assignments_collection

dummy_email = "imagnus506@gmail.com"
course = "Data Structures"

# 1. Clear old
attendance_collection.delete_many({"student_email": dummy_email})
assignments_collection.delete_many({"course_name": course})

# 2. Add Attendance
attendance_collection.insert_many([
    {"student_email": dummy_email, "course_name": course, "date": "2026-04-10", "time": "10:00 AM", "status": "Present"},
    {"student_email": dummy_email, "course_name": course, "date": "2026-04-11", "time": "10:00 AM", "status": "Present"},
    {"student_email": dummy_email, "course_name": course, "date": "2026-04-12", "time": "10:00 AM", "status": "Absent"}
])

# 3. Add Assignments (One submitted, one pending)
assignments_collection.insert_many([
    {
        "course_name": course,
        "title": "Linked Lists Homework",
        "due_date": "2026-04-15",
        "submissions": [
            f"dummy_{dummy_email}_submission.pdf"
        ]
    },
    {
        "course_name": course,
        "title": "Binary Trees Research",
        "due_date": "2026-04-20",
        "submissions": [] # empty means not submitted
    }
])
print("Dummy data added successfully.")
