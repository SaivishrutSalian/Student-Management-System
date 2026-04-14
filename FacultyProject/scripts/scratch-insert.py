import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from database import faculty_collection, timetable_collection

# 1. Add Prof. Alan Turing if not exists
turing = faculty_collection.find_one({"email": "alan@college.edu"})
if not turing:
    turing_id = faculty_collection.insert_one({
        "name": "Prof. Alan Turing",
        "email": "alan@college.edu",
        "password": "password123",
        "role": "faculty",
        "phone": "555-0100",
        "department": "Computer Science"
    }).inserted_id
    print("Added Prof. Alan Turing.")

# 2. Clear old timetable if any just in case
timetable_collection.delete_many({"faculty_email": "alan@college.edu"})

# 3. Add 4 dummy classes manually
classes = [
    {
        "faculty_email": "alan@college.edu",
        "faculty_name_assigned": "Prof. Alan Turing",
        "day": "Monday",
        "time": "09:00 AM - 10:00 AM",
        "course": "Cryptography",
        "batch": "MCA",
        "room": "Enigma Lab"
    },
    {
        "faculty_email": "alan@college.edu",
        "faculty_name_assigned": "Prof. Alan Turing",
        "day": "Tuesday",
        "time": "11:00 AM - 12:00 PM",
        "course": "Automata Theory",
        "batch": "BCA- A1",
        "room": "Room 201"
    },
    {
        "faculty_email": "alan@college.edu",
        "faculty_name_assigned": "Prof. Alan Turing",
        "day": "Wednesday",
        "time": "09:00 AM - 10:00 AM",
        "course": "Cryptography",
        "batch": "MCA",
        "room": "Enigma Lab"
    },
    {
        "faculty_email": "alan@college.edu",
        "faculty_name_assigned": "Prof. Alan Turing",
        "day": "Friday",
        "time": "02:00 PM - 03:00 PM",
        "course": "AI Ethics",
        "batch": "BCA- C2",
        "room": "Seminar Hall 1"
    }
]

timetable_collection.insert_many(classes)
print("Added dummy classes for Prof. Alan Turing.")
