import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from database import timetable_collection

result = timetable_collection.update_many(
    {"faculty_email": "alan@college.edu"},
    {"$set": {"faculty_email": "faculty2@college.edu"}}
)
print(f"Updated {result.modified_count} schedule entries to point to faculty2.")
