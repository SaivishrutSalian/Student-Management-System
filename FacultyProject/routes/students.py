from flask import render_template, request, redirect, flash, url_for
from . import main_bp
from database import db, approved, attendance_collection, assignments_collection

@main_bp.route('/students')
def students_view():
    faculty_email = "faculty@college.edu"
    faculty_name = "Prof. John Doe"
    
    approved_students = list(approved.find({"role": "student"}))
    if len(approved_students) == 0:
        approved_students = [
            {"name": "Alice Smith", "email": "imagnus506@gmail.com", "role": "student"},
            {"name": "Bob Johnson", "email": "bob@student.college.edu", "role": "student"}
        ]
        approved.insert_many(approved_students)
        
    display_students = []
    for idx, st in enumerate(approved_students, start=10):
        course_name = "Data Structures"
        display_students.append({
            "name": st.get('name', st['email'].split('@')[0].capitalize()),
            "email": st['email'],
            "course_name": course_name,
            "reg_no": f"03SU25BC8{idx}"
        })
        
    return render_template("students.html", faculty_name=faculty_name, students=display_students)

@main_bp.route('/student/<path:student_email>/<course_name>')
def student_profile(student_email, course_name):
    faculty_email = "faculty@college.edu"
    faculty_name = "Prof. John Doe"
    
    st = approved.find_one({"email": student_email, "role": "student"})
    if not st:
        st = {"name": student_email.split('@')[0].capitalize(), "email": student_email}
    
    student_name = st.get('name', student_email.split('@')[0].capitalize())
    roll_no = f"CS26{student_email[:3].upper()}01"
    
    parent_name = st.get('parent_name', 'Not Provided')
    parent_phone = st.get('parent_phone', 'Not Provided')
    
    attended_records = list(attendance_collection.find({"student_email": student_email, "course_name": course_name}))
    # Sort attended records by date descending if possible
    attended_records.sort(key=lambda x: x.get('date', ''), reverse=True)
    
    total_student_sessions = len(attended_records)
    present_sessions = sum(1 for r in attended_records if r.get('status') == 'Present')
    
    if total_student_sessions > 0:
        attendance_percentage = round((present_sessions / total_student_sessions) * 100)
    else:
        attendance_percentage = 0
        
    assignments = list(assignments_collection.find({"course_name": course_name}))
    total_assignments = len(assignments)
    submitted_assignments = 0
    assignment_details = []
    
    for assign in assignments:
        submissions = assign.get('submissions', [])
        submitted = any(student_email in str(sub) for sub in submissions)
        if submitted:
            submitted_assignments += 1
        assignment_details.append({
            "title": assign.get("title", "Untitled"),
            "due_date": assign.get("due_date", "N/A"),
            "submitted": submitted
        })
            
    grade_record = db.grades.find_one({
        "student_email": student_email,
        "course_name": course_name
    }) or {}
    
    return render_template("student_profile.html", 
                           faculty_name=faculty_name,
                           student_email=student_email,
                           student_name=student_name,
                           course_name=course_name,
                           roll_no=roll_no,
                           attendance_percentage=attendance_percentage,
                           present_sessions=present_sessions,
                           total_sessions=total_student_sessions,
                           total_assignments=total_assignments,
                           submitted_assignments=submitted_assignments,
                           assignment_details=assignment_details,
                           attended_records=attended_records,
                           parent_name=parent_name,
                           parent_phone=parent_phone,
                           grade=grade_record)

@main_bp.route('/save_grade', methods=['POST'])
def save_grade():
    student_email = request.form.get('student_email')
    course_name = request.form.get('course_name')
    internal_1 = request.form.get('internal_1')
    internal_2 = request.form.get('internal_2')
    lab_marks = request.form.get('lab_marks')
    external_marks = request.form.get('external_marks')
    faculty_email = "faculty@college.edu"
    remarks = request.form.get('remarks', '')
    parent_name = request.form.get('parent_name', '')
    parent_phone = request.form.get('parent_phone', '')
    
    if parent_name or parent_phone:
        approved.update_one(
            {"email": student_email, "role": "student"},
            {"$set": {"parent_name": parent_name, "parent_phone": parent_phone}}
        )
    
    db.grades.update_one(
        {"student_email": student_email, "course_name": course_name},
        {"$set": {
            "faculty_email": faculty_email, 
            "internal_1": internal_1,
            "internal_2": internal_2,
            "lab": lab_marks,
            "external": external_marks,
            "remarks": remarks
        }},
        upsert=True
    )
    
    flash(f"Grades for {student_email.split('@')[0]} saved successfully! ✅", "success")
    return redirect(url_for('main.student_profile', student_email=student_email, course_name=course_name))
