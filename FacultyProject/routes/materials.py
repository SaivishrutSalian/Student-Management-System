import os
from datetime import datetime
from werkzeug.utils import secure_filename
from flask import render_template, redirect, url_for, session, request, flash, current_app, send_from_directory
from bson.objectid import ObjectId
from database import materials_collection, faculty_collection
from . import main_bp

ALLOWED_EXTENSIONS = {'pdf', 'doc', 'docx', 'ppt', 'pptx'}

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@main_bp.route('/materials')
def materials_view():
    if 'faculty_email' not in session:
        return redirect(url_for('main.login'))
        
    faculty_email = session['faculty_email']
    faculty_name = session['faculty_name']
    
    faculty_filter = request.args.get('faculty_filter', '')
    
    if session.get('role') == 'hod':
        faculties = list(faculty_collection.find({"role": {"$ne": "hod"}}))
        if faculty_filter:
            materials = list(materials_collection.find({"faculty_email": faculty_filter}))
        else:
            materials = list(materials_collection.find())
    else:
        faculties = []
        materials = list(materials_collection.find({"faculty_email": faculty_email}))
        
    return render_template("materials.html", 
                           materials=materials, 
                           faculty_name=faculty_name, 
                           faculties=faculties, 
                           selected_faculty=faculty_filter)

@main_bp.route('/materials/upload', methods=['POST'])
def upload_material():
    if 'faculty_email' not in session:
        return redirect(url_for('main.login'))
        
    if 'file' not in request.files:
        flash('No file part', 'error')
        return redirect(url_for('main.materials_view'))
        
    file = request.files['file']
    if file.filename == '':
        flash('No selected file', 'error')
        return redirect(url_for('main.materials_view'))
        
    if file and allowed_file(file.filename):
        filename = secure_filename(file.filename)
        # Create a unique filename to prevent overwrites
        timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
        unique_filename = f"{timestamp}_{filename}"
        
        file_path = os.path.join(current_app.config['MATERIALS_FOLDER'], unique_filename)
        file.save(file_path)
        
        new_material = {
            "faculty_email": session['faculty_email'],
            "faculty_name": session['faculty_name'],
            "title": request.form.get('title'),
            "course": request.form.get('course'),
            "batch": request.form.get('batch'),
            "filename": filename,
            "filepath": unique_filename,
            "upload_date": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        }
        
        materials_collection.insert_one(new_material)
        flash(f"Successfully uploaded {filename}", "success")
    else:
        flash("Invalid file type. Only PDF, DOC, DOCX, PPT, PPTX are allowed.", "error")
        
    return redirect(url_for('main.materials_view'))

@main_bp.route('/materials/delete/<material_id>', methods=['POST'])
def delete_material(material_id):
    if 'faculty_email' not in session:
        return redirect(url_for('main.login'))
        
    material = materials_collection.find_one({"_id": ObjectId(material_id)})
    if not material:
        flash("Material not found.", "error")
        return redirect(url_for('main.materials_view'))
        
    # Security: only the uploader or HOD can delete
    if session['role'] != 'hod' and material['faculty_email'] != session['faculty_email']:
        flash("Unauthorized to delete this material.", "error")
        return redirect(url_for('main.materials_view'))
        
    # Delete file from disk
    file_path = os.path.join(current_app.config['MATERIALS_FOLDER'], material['filepath'])
    if os.path.exists(file_path):
        os.remove(file_path)
        
    materials_collection.delete_one({"_id": ObjectId(material_id)})
    flash("Material deleted successfully.", "success")
    return redirect(url_for('main.materials_view'))
