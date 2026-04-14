from flask import render_template, request, redirect, flash, url_for, current_app
from . import main_bp
from database import assignments_collection, approved
from extensions import mail
from flask_mail import Message
import config
from werkzeug.utils import secure_filename
from bson.objectid import ObjectId
import os

@main_bp.route('/assignments')
def assignments_view():
    faculty_email = "faculty@college.edu"
    faculty_name = "Prof. John Doe"
    
    all_assignments = list(assignments_collection.find({"faculty_email": faculty_email}))
    
    assigned_data = [
        {"course_name": "Data Structures", "batch": "BCA- A1"},
        {"course_name": "Algorithms", "batch": "BCA- B2"},
        {"course_name": "Operating Systems", "batch": "MCA"}
    ]
    
    return render_template("assignments.html", faculty_name=faculty_name, assignments=all_assignments, assigned_data=assigned_data)

@main_bp.route('/create_assignment', methods=['POST'])
def create_assignment():
    course_name = request.form.get('course_name')
    batch = request.form.get('batch')
    title = request.form.get('title')
    description = request.form.get('description')
    deadline = request.form.get('deadline')
    faculty_email = "faculty@college.edu"
    
    file = request.files.get('assignment_file')
    file_url = None
    if file and file.filename != '':
        filename = secure_filename(file.filename)
        file_path = os.path.join(current_app.config['UPLOAD_FOLDER'], filename)
        file.save(file_path)
        file_url = url_for('static', filename='uploads/' + filename)
    
    assignment_data = {
        "faculty_email": faculty_email,
        "course_name": course_name,
        "batch": batch,
        "title": title,
        "description": description,
        "deadline": deadline,
        "file_url": file_url,
        "submissions": []
    }
    assignments_collection.insert_one(assignment_data)
    
    students = list(approved.find({"role": "student"}))
    if len(students) == 0:
        students = [{"email": "imagnus506@gmail.com"}]
        
    recipient_emails = [st['email'] for st in students if '@' in st.get('email', '')]
    if recipient_emails:
        msg = Message(f"New Assignment Posted: {title}",
                      sender=config.MAIL_USERNAME,
                      bcc=recipient_emails)
        msg.body = f"Hello Students,\n\nA new assignment has been posted for {course_name}.\n\nTitle: {title}\nDeadline: {deadline.replace('T', ' ')}\n\nPlease check your student portal for instructions and to upload your submission.\n\nRegards,\n{faculty_email}"
        try:
            mail.send(msg)
            flash(f"Assignment '{title}' posted and emailed to students successfully! 📝", "success")
        except Exception as e:
            flash(f"Assignment '{title}' posted, but email failed: {str(e)}", "error")
    else:
        flash(f"Assignment '{title}' posted, but no student emails found. 📝", "success")
    
    return redirect(url_for('main.assignments_view'))

@main_bp.route('/delete_assignment/<assignment_id>', methods=['POST'])
def delete_assignment(assignment_id):
    try:
        assignments_collection.delete_one({"_id": ObjectId(assignment_id)})
        flash("Assignment deleted successfully! 🗑️", "success")
    except Exception as e:
        flash("Error deleting assignment.", "error")
    return redirect(url_for('main.assignments_view'))
