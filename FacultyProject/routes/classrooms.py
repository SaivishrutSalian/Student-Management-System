from flask import render_template, request, redirect, flash, url_for
from . import main_bp
from database import classrooms_collection, approved
from extensions import mail
from flask_mail import Message
import config
from bson.objectid import ObjectId

@main_bp.route('/virtual_classrooms')
def virtual_classrooms_view():
    faculty_email = "faculty@college.edu"
    faculty_name = "Prof. John Doe"
    
    classes = list(classrooms_collection.find({"faculty_email": faculty_email}))
    
    assigned_data = [
        {"course_name": "Data Structures", "batch": "BCA- A1"},
        {"course_name": "Algorithms", "batch": "BCA- B2"},
        {"course_name": "Operating Systems", "batch": "MCA"}
    ]
    
    return render_template("virtual_classrooms.html", faculty_name=faculty_name, classes=classes, assigned_data=assigned_data)

@main_bp.route('/schedule_class', methods=['POST'])
def schedule_class():
    course_name = request.form.get('course_name')
    batch = request.form.get('batch')
    topic = request.form.get('topic')
    meeting_link = request.form.get('meeting_link')
    meeting_time = request.form.get('meeting_time')
    faculty_email = "faculty@college.edu"
    
    classrooms_collection.insert_one({
        "faculty_email": faculty_email,
        "course_name": course_name,
        "batch": batch,
        "topic": topic,
        "meeting_link": meeting_link,
        "meeting_time": meeting_time
    })
    
    students = list(approved.find({"role": "student"}))
    if len(students) == 0:
        students = [{"email": "imagnus506@gmail.com"}]
        
    recipient_emails = [st['email'] for st in students if '@' in st.get('email', '')]
    
    if recipient_emails:
        msg = Message(f"New Virtual Class Scheduled: {topic}",
                      sender=config.MAIL_USERNAME,
                      bcc=recipient_emails)
                      
        msg.body = f"Hello Students,\n\nA new online class has been scheduled for {course_name}.\n\nTopic: {topic}\nTime: {meeting_time}\nLink: {meeting_link}\n\nPlease be on time.\n\nRegards,\nFaculty"
        try:
            mail.send(msg)
            flash("Class scheduled and emails dispatched successfully! 📧", "success")
        except Exception as e:
            flash(f"Class scheduled, but email failed: {str(e)}", "error")
    else:
        flash("Class scheduled, but no students found in database to email.", "success")
        
    return redirect(url_for('main.virtual_classrooms_view'))

@main_bp.route('/delete_class/<class_id>', methods=['POST'])
def delete_class(class_id):
    try:
        classrooms_collection.delete_one({"_id": ObjectId(class_id)})
        flash("Virtual class cancelled and removed successfully! 🗑️", "success")
    except Exception as e:
        flash("Error deleting class.", "error")
    return redirect(url_for('main.virtual_classrooms_view'))
