from flask import render_template, request, redirect, flash, url_for
from . import main_bp
from database import announcements_collection, approved
from extensions import mail
from flask_mail import Message
import config
import datetime

@main_bp.route('/announcements')
def announcements_view():
    faculty_email = "faculty@college.edu"
    faculty_name = "Prof. John Doe"
    
    past_announcements = list(announcements_collection.find({"faculty_email": faculty_email}))
    
    assigned_data = [
        {"course_name": "Data Structures", "batch": "BCA- A1"},
        {"course_name": "Algorithms", "batch": "BCA- B2"},
        {"course_name": "Operating Systems", "batch": "MCA"}
    ]
    
    return render_template("announcements.html", faculty_name=faculty_name, announcements=past_announcements, assigned_data=assigned_data)

@main_bp.route('/post_announcement', methods=['POST'])
def post_announcement():
    title = request.form.get('title')
    message_content = request.form.get('message')
    course_name = request.form.get('course_name')
    batch = request.form.get('batch')
    faculty_email = "faculty@college.edu"
    
    announcements_collection.insert_one({
        "faculty_email": faculty_email,
        "title": title,
        "message": message_content,
        "course_name": course_name,
        "batch": batch,
        "date_posted": datetime.datetime.now().strftime("%Y-%m-%d %I:%M %p")
    })
    
    students = list(approved.find({"role": "student"}))
    if len(students) == 0:
        students = [{"email": "imagnus506@gmail.com"}]
        
    recipient_emails = [st['email'] for st in students if '@' in st.get('email', '')]
    
    if recipient_emails:
        msg = Message(f"Important Announcement: {title}",
                      sender=config.MAIL_USERNAME,
                      bcc=recipient_emails)
        msg.body = f"Hello Students,\n\nA new announcement has been posted by your faculty:\n\n{message_content}\n\nRegards,\n{faculty_email}"
        try:
            mail.send(msg)
            flash("Notice posted and emailed to all students successfully! 📢", "success")
        except Exception as e:
            flash(f"Notice posted to board, but email failed: {str(e)}", "error")
    else:
        flash("Notice posted to board, but no student emails found.", "success")
        
    return redirect(url_for('main.announcements_view'))
