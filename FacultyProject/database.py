from pymongo import MongoClient
import config

client = MongoClient(config.MONGO_URI)
db = client.college

approved = db.approved
courses = db.courses
batches = db.batches
assignments_collection = db.assignments
attendance_collection = db.attendance
classrooms_collection = db.classrooms
announcements_collection = db.announcements
timetable_collection = db.timetable
faculty_collection = db.faculty
materials_collection = db.materials
