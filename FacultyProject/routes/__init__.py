from flask import Blueprint

main_bp = Blueprint('main', __name__)

from . import dashboard, students, assignments, attendance, classrooms, announcements, materials
