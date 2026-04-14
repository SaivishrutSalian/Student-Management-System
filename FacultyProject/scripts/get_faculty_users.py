import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from database import faculty_collection
for f in faculty_collection.find():
    print(f"Role: {f.get('role')}, Email: {f.get('email')}, Pass: {f.get('password')}")
