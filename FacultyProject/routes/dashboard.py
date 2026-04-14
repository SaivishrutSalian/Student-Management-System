import random
from flask import render_template, redirect, url_for, session, request, flash
from bson.objectid import ObjectId
from database import timetable_collection, faculty_collection
from . import main_bp

@main_bp.route('/')
def index():
    if 'faculty_email' in session:
        return redirect(url_for('main.dashboard'))
    return redirect(url_for('main.login'))

@main_bp.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')
        
        user = faculty_collection.find_one({"email": email})
        
        if user and user.get('password') == password:
            session['faculty_email'] = user['email']
            session['faculty_name'] = user['name']
            session['role'] = user.get('role', 'faculty')
            return redirect(url_for('main.dashboard'))
        else:
            flash("Invalid credentials", "error")
            return redirect(url_for('main.login'))
            
    return render_template("login.html")

@main_bp.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('main.login'))

@main_bp.route('/dashboard')
def dashboard():
    if 'faculty_email' not in session:
        return redirect(url_for('main.login'))
        
    faculty_email = session['faculty_email']
    faculty_name = session['faculty_name']
    
    assigned_data = [
        {"course_name": "Data Structures", "batch": "BCA- A1", "students": 45},
        {"course_name": "Algorithms", "batch": "BCA- B2", "students": 42},
        {"course_name": "Operating Systems", "batch": "MCA", "students": 38}
    ]

    return render_template("dashboard.html", 
                           faculty_name=faculty_name, 
                           email=faculty_email,
                           assigned_data=assigned_data)

@main_bp.route('/timetable')
def timetable_view():
    if 'faculty_email' not in session:
        return redirect(url_for('main.login'))
        
    faculty_email = session['faculty_email']
    faculty_name = session['faculty_name']
    
    faculty_filter = request.args.get('faculty_filter', '')
    
    if session.get('role') == 'hod':
        if faculty_filter:
            timetable_data = list(timetable_collection.find({"faculty_email": faculty_filter}))
        else:
            timetable_data = list(timetable_collection.find())
        faculties = list(faculty_collection.find({"role": {"$ne": "hod"}}))
    else:
        timetable_data = list(timetable_collection.find({"faculty_email": faculty_email}))
        faculties = []
    
    schedule = {
        "Monday": [c for c in timetable_data if c['day'] == "Monday"],
        "Tuesday": [c for c in timetable_data if c['day'] == "Tuesday"],
        "Wednesday": [c for c in timetable_data if c['day'] == "Wednesday"],
        "Thursday": [c for c in timetable_data if c['day'] == "Thursday"],
        "Friday": [c for c in timetable_data if c['day'] == "Friday"]
    }
    
    return render_template("timetable.html", faculty_name=faculty_name, schedule=schedule, faculties=faculties, selected_faculty=faculty_filter)

@main_bp.route('/timetable/add', methods=['POST'])
def add_timetable_class():
    if session.get('role') != 'hod':
        return redirect(url_for('main.timetable_view'))
    
    target_email = request.form.get("faculty_email")
    target_faculty = faculty_collection.find_one({"email": target_email})
    target_name = target_faculty['name'] if target_faculty else target_email
    
    new_class = {
        "faculty_email": target_email,
        "faculty_name_assigned": target_name,
        "day": request.form.get("day"),
        "time": request.form.get("time"),
        "course": request.form.get("course"),
        "batch": request.form.get("batch"),
        "room": request.form.get("room")
    }
    timetable_collection.insert_one(new_class)
    return redirect(url_for('main.timetable_view'))

@main_bp.route('/timetable/delete/<class_id>', methods=['POST'])
def delete_timetable_class(class_id):
    if session.get('role') != 'hod':
        return redirect(url_for('main.timetable_view'))
        
    timetable_collection.delete_one({"_id": ObjectId(class_id)})
    return redirect(url_for('main.timetable_view'))

@main_bp.route('/timetable/auto_generate', methods=['POST'])
def auto_generate_timetable():
    if session.get('role') != 'hod':
        return redirect(url_for('main.timetable_view'))
        
    target_email = request.form.get("faculty_email")
    if not target_email:
        flash("Faculty not specified.", "error")
        return redirect(url_for('main.timetable_view'))

    courses = request.form.getlist("course[]")
    batches = request.form.getlist("batch[]")
    rooms = request.form.getlist("room[]")
    classes_per_weeks = request.form.getlist("classes_per_week[]")
    
    target_faculty = faculty_collection.find_one({"email": target_email})
    target_name = target_faculty['name'] if target_faculty else target_email
    
    days = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday"]
    time_slots = [
        "09:00 AM - 10:00 AM",
        "10:00 AM - 11:00 AM",
        "11:00 AM - 12:00 PM",
        "01:00 PM - 02:00 PM",
        "02:00 PM - 03:00 PM",
        "03:00 PM - 04:00 PM"
    ]
    
    # Fetch ALL classes to model conflicts
    all_classes = list(timetable_collection.find())
    
    available_slots_master = []
    for day in days:
        for t_slot in time_slots:
            available_slots_master.append((day, t_slot))
            
    # Remove ANY slots belonging to the target faculty from the conflict list so we can treat their schedule as empty
    all_classes = [c for c in all_classes if c['faculty_email'] != target_email]
    
    simulated_allocations = []
    
    for i in range(len(courses)):
        course = courses[i]
        batch = batches[i]
        room = rooms[i]
        try:
            cpw = int(classes_per_weeks[i])
        except ValueError:
            cpw = 1
            
        subject_available_slots = list(available_slots_master)
        
        # Filter out slots globally occupied by batches/rooms from OTHER faculties
        for c in all_classes:
            comb = (c['day'], c['time'])
            if (c['batch'] == batch or c.get('room') == room) and comb in subject_available_slots:
                subject_available_slots.remove(comb)
                
        # Filter out slots already allocated in this simulation run for this faculty
        for sa in simulated_allocations:
            comb = (sa['day'], sa['time'])
            if comb in subject_available_slots: # faculty is already booked at this time in simulation
                subject_available_slots.remove(comb)
            elif (sa['batch'] == batch or sa.get('room') == room) and comb in subject_available_slots:
                subject_available_slots.remove(comb) # batch or room is booked in simulation
        
        if len(subject_available_slots) < cpw:
            flash(f"Error: Could not fit '{course}' for '{batch}'. Not enough free, non-overlapping slots.", "error")
            return redirect(url_for('main.timetable_view'))
            
        # Pick random slots
        selected = random.sample(subject_available_slots, cpw)
        for day, t_slot in selected:
            simulated_allocations.append({
                "faculty_email": target_email,
                "faculty_name_assigned": target_name,
                "day": day,
                "time": t_slot,
                "course": course,
                "batch": batch,
                "room": room
            })

    # WIPE clean the faculty's old schedule:
    timetable_collection.delete_many({"faculty_email": target_email})
    
    # Insert new bulk schedule
    if simulated_allocations:
        timetable_collection.insert_many(simulated_allocations)
        
    flash(f"Successfully generated a full weekly schedule ({len(simulated_allocations)} classes) for {target_name}.", "success")
    return redirect(url_for('main.timetable_view', faculty_filter=target_email))
