from flask import Flask
import os
import config
from extensions import mail
from routes import main_bp

app = Flask(__name__)
app.secret_key = "faculty_module_secret_123"
app.config.from_object(config)

app.config['UPLOAD_FOLDER'] = os.path.join('static', 'uploads')
app.config['MATERIALS_FOLDER'] = os.path.join(app.config['UPLOAD_FOLDER'], 'materials')
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
os.makedirs(app.config['MATERIALS_FOLDER'], exist_ok=True)

mail.init_app(app)

app.register_blueprint(main_bp)

if __name__ == "__main__":
    app.run(port=5001, debug=True)
