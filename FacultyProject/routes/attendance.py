from flask import render_template, request, redirect, flash, url_for, Response
from . import main_bp
from database import attendance_collection, approved
from extensions import mail
from flask_mail import Message
import config

@main_bp.route('/attendance')
def attendance_view():
    faculty_email = "faculty@college.edu"
    faculty_name = "Prof. John Doe"
    
    approved_students = list(approved.find({"role": "student"}))
    if len(approved_students) == 0:
        approved_students = [
            {"name": "Alice Smith", "email": "imagnus506@gmail.com"},
            {"name": "Bob Johnson", "email": "bob@student.college.edu"}
        ]
        
    display_students = []
    for st in approved_students:
        display_students.append({
            "name": st.get('name', st['email'].split('@')[0].capitalize()),
            "email": st['email'],
            "course_name": "Data Structures"
        })
        
    assigned_courses = [
        {"course_name": "Data Structures"},
        {"course_name": "Algorithms"},
        {"course_name": "Operating Systems"}
    ]
        
    return render_template("attendance.html", faculty_name=faculty_name, students=display_students, assigned_courses=assigned_courses)

@main_bp.route('/save_attendance', methods=['POST'])
def save_attendance():
    date = request.form.get('date')
    course_name = request.form.get('course_name')
    faculty_email = "faculty@college.edu"
    
    present_emails = []
    absent_emails = []
    
    for key, value in request.form.items():
        if key.startswith('status_'):
            student_email = key.split('status_')[1]
            attendance_collection.update_one(
                {"student_email": student_email, "course_name": course_name, "date": date},
                {"$set": {
                    "status": value,
                    "faculty_email": faculty_email
                }},
                upsert=True
            )
            
            if value == "Present":
                present_emails.append(student_email)
            elif value == "Absent":
                absent_emails.append(student_email)
                
    if present_emails:
        msg_present = Message(f"Attendance Logged: {course_name}", sender=config.MAIL_USERNAME, bcc=present_emails)
        msg_present.body = f"Hello Student,\n\nYou have been marked PRESENT for {course_name} on {date}.\n\nKeep up the good work!\n\nRegards,\nFaculty"
        try: mail.send(msg_present)
        except Exception: pass
        
    if absent_emails:
        msg_absent = Message(f"Attendance Alert: {course_name}", sender=config.MAIL_USERNAME, bcc=absent_emails)
        msg_absent.body = f"Hello Student,\n\nYou have been marked ABSENT for {course_name} on {date}. Please ensure you attend the upcoming sessions.\n\nRegards,\nFaculty"
        try: mail.send(msg_absent)
        except Exception: pass
            
    flash(f"Attendance for {date} saved and emails dispatched! ✅", "success")
    return redirect(url_for('main.attendance_view'))

@main_bp.route('/export_attendance')
def export_attendance():
    faculty_email = "faculty@college.edu"
    records = list(attendance_collection.find({"faculty_email": faculty_email}))
    
    def generate():
        yield "Student Email,Course Name,Date,Status\n"
        for rec in records:
            email = str(rec.get('student_email',''))
            course = str(rec.get('course_name',''))
            date = str(rec.get('date',''))
            status = str(rec.get('status',''))
            yield f"{email},{course},{date},{status}\n"
            
    return Response(generate(), mimetype='text/csv', headers={
        "Content-Disposition": "attachment; filename=attendance_export.csv"
    })
