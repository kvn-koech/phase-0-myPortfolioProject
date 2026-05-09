from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
from flask_sqlalchemy import SQLAlchemy
from flask_mail import Mail, Message
from datetime import datetime
import os
import re
import threading
from dotenv import load_dotenv

load_dotenv()

# Base directories
BASE_DIR = os.path.abspath(os.path.dirname(__file__))
FRONTEND_DIR = os.path.join(BASE_DIR, '..', 'frontend')

app = Flask(__name__, static_folder=FRONTEND_DIR, static_url_path='')
CORS(app)

# Database Configuration
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + os.path.join(BASE_DIR, 'portfolio.db')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)

# Email Configuration
app.config['MAIL_SERVER'] = 'smtp.gmail.com'
app.config['MAIL_PORT'] = 465
app.config['MAIL_USE_SSL'] = True
app.config['MAIL_USERNAME'] = os.environ.get('MAIL_USERNAME')
app.config['MAIL_PASSWORD'] = os.environ.get('MAIL_PASSWORD')
app.config['MAIL_DEFAULT_SENDER'] = os.environ.get('MAIL_USERNAME')

mail = Mail(app)

def send_async_email(app, msg):
    with app.app_context():
        try:
            mail.send(msg)
            print("Email notification sent successfully.")
        except Exception as e:
            print(f"Failed to send email: {e}")

def is_valid_email(email):
    regex = r'^\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,7}\b$'
    return re.match(regex, email)

# --- Database Models ---
class ContactMessage(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(120), nullable=False)
    message = db.Column(db.Text, nullable=False)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)

    def __repr__(self):
        return f'<ContactMessage {self.email}>'

# Create tables
with app.app_context():
    db.create_all()

# --- Routes ---
@app.route('/')
def serve_index():
    """Serve the main frontend HTML file."""
    return send_from_directory(app.static_folder, 'index.html')

@app.route('/api/contact', methods=['POST'])
def handle_contact():
    """Endpoint to handle contact form submissions."""
    # Data can come as JSON or Form Data depending on how fetch is called
    if request.is_json:
        data = request.get_json()
    else:
        data = request.form

    name = data.get('name')
    email = data.get('email')
    message = data.get('message')

    if not name or not email or not message:
        return jsonify({"success": False, "error": "Missing required fields"}), 400

    if not is_valid_email(email):
        return jsonify({"success": False, "error": "Invalid email address"}), 400

    try:
        # Save to database
        new_msg = ContactMessage(name=name, email=email, message=message)
        db.session.add(new_msg)
        db.session.commit()
        
        print(f"New contact saved: {name} - {email}")
        
        # Send email notification
        if app.config['MAIL_USERNAME'] and app.config['MAIL_PASSWORD']:
            msg = Message(
                subject=f"New Portfolio Contact from {name}",
                recipients=[os.environ.get('RECEIVER_EMAIL', app.config['MAIL_USERNAME'])],
                body=f"Name: {name}\nEmail: {email}\n\nMessage:\n{message}"
            )
            # Run in background thread
            thread = threading.Thread(target=send_async_email, args=(app, msg))
            thread.start()
        else:
            print("Warning: Email credentials not set in .env. Email not sent.")
        
        return jsonify({"success": True, "message": "Message saved successfully!"}), 201

    except Exception as e:
        print(f"Error saving message: {e}")
        return jsonify({"success": False, "error": "Internal Server Error"}), 500

if __name__ == '__main__':
    app.run(debug=True, port=5000)
