from flask import Flask, render_template, request, jsonify
from flask_cors import CORS
import json
import os
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from datetime import datetime
import re

app = Flask(__name__)
CORS(app)

# Configuration
ENQUIRIES_FILE = 'enquiries.json'
SMTP_SERVER = 'smtp.gmail.com'
SMTP_PORT = 587
SENDER_EMAIL = 'your-email@gmail.com'  # Replace with your email
SENDER_PASSWORD = 'your-app-password'  # Replace with your app password
ADMIN_EMAIL = 'admin@nipscollege.com'  # Replace with admin email

# Initialize enquiries file
def init_enquiries_file():
    if not os.path.exists(ENQUIRIES_FILE):
        with open(ENQUIRIES_FILE, 'w') as f:
            json.dump([], f)

init_enquiries_file()

# Email validation
def is_valid_email(email):
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return re.match(pattern, email) is not None

# Phone validation
def is_valid_phone(phone):
    pattern = r'^[0-9\-\+\(\)\s]{10,}$'
    return re.match(pattern, phone) is not None

# Send email notification
def send_email_notification(enquiry_data):
    try:
        # Create email content
        subject = f"New Course Enquiry - {enquiry_data['course']}"
        
        body = f"""
        <html>
            <body style="font-family: Arial, sans-serif; line-height: 1.6; color: #333;">
                <div style="max-width: 600px; margin: 0 auto; padding: 20px;">
                    <h2 style="color: #2c3e50; border-bottom: 3px solid #3498db; padding-bottom: 10px;">
                        New Course Enquiry Received
                    </h2>
                    <div style="background-color: #f8f9fa; padding: 20px; border-radius: 8px; margin: 20px 0;">
                        <p><strong>Name:</strong> {enquiry_data['name']}</p>
                        <p><strong>Email:</strong> {enquiry_data['email']}</p>
                        <p><strong>Phone:</strong> {enquiry_data['phone']}</p>
                        <p><strong>Course:</strong> {enquiry_data['course']}</p>
                        <p><strong>Address:</strong> {enquiry_data['address']}</p>
                        <p><strong>Submitted Date:</strong> {enquiry_data['submitted_date']}</p>
                    </div>
                    <p style="color: #7f8c8d; font-size: 12px;">
                        This is an automated message from NIPS College of IT & Management website.
                    </p>
                </div>
            </body>
        </html>
        """
        
        # Create message
        message = MIMEMultipart("alternative")
        message["Subject"] = subject
        message["From"] = SENDER_EMAIL
        message["To"] = ADMIN_EMAIL
        
        # Attach HTML body
        message.attach(MIMEText(body, "html"))
        
        # Send email
        with smtplib.SMTP(SMTP_SERVER, SMTP_PORT) as server:
            server.starttls()
            server.login(SENDER_EMAIL, SENDER_PASSWORD)
            server.sendmail(SENDER_EMAIL, ADMIN_EMAIL, message.as_string())
        
        return True
    except Exception as e:
        print(f"Email sending error: {str(e)}")
        return False

# Save enquiry to file
def save_enquiry(enquiry_data):
    try:
        with open(ENQUIRIES_FILE, 'r') as f:
            enquiries = json.load(f)
        
        enquiries.append(enquiry_data)
        
        with open(ENQUIRIES_FILE, 'w') as f:
            json.dump(enquiries, f, indent=2)
        
        return True
    except Exception as e:
        print(f"Error saving enquiry: {str(e)}")
        return False

# Routes
@app.route('/')
def index():
    return render_template('index.html')

@app.route('/about')
def about():
    return render_template('about.html')

@app.route('/courses')
def courses():
    courses_data = [
        {
            'id': 1,
            'title': 'O Level (DOEACC)',
            'duration': '1 Year',
            'description': 'Foundation level course introducing basic IT concepts, operating systems, and office applications.',
            'details': 'Learn fundamentals of computer systems, DOS, and productivity tools.'
        },
        {
            'id': 2,
            'title': 'COPA (NCVT)',
            'duration': '6 Months',
            'description': 'Computer Operator and Programming Assistant - practical skill-based training.',
            'details': 'Hands-on training in data entry, spreadsheets, and basic programming.'
        },
        {
            'id': 3,
            'title': 'PGDCA',
            'duration': '1 Year',
            'description': 'Post Graduate Diploma in Computer Applications - advanced IT skills for graduates.',
            'details': 'Advanced courses in databases, web development, and software applications.'
        },
        {
            'id': 4,
            'title': 'BCA',
            'duration': '3 Years',
            'description': 'Bachelor of Computer Applications - comprehensive undergraduate degree program.',
            'details': 'Full-fledged undergraduate program covering all aspects of computer science.'
        },
        {
            'id': 5,
            'title': 'MCA',
            'duration': '2 Years',
            'description': 'Master of Computer Applications - postgraduate degree with industry focus.',
            'details': 'Advanced postgraduate program preparing professionals for IT industry.'
        }
    ]
    return render_template('courses.html', courses=courses_data)

@app.route('/contact')
def contact():
    return render_template('contact.html')

# API endpoint for form submission
@app.route('/api/submit-enquiry', methods=['POST'])
def submit_enquiry():
    try:
        data = request.get_json()
        
        # Validation
        if not data.get('name') or len(data.get('name', '').strip()) < 2:
            return jsonify({'success': False, 'message': 'Name is required and must be at least 2 characters'}), 400
        
        if not is_valid_email(data.get('email', '')):
            return jsonify({'success': False, 'message': 'Please enter a valid email address'}), 400
        
        if not is_valid_phone(data.get('phone', '')):
            return jsonify({'success': False, 'message': 'Please enter a valid phone number'}), 400
        
        if not data.get('course'):
            return jsonify({'success': False, 'message': 'Please select a course'}), 400
        
        if not data.get('address') or len(data.get('address', '').strip()) < 5:
            return jsonify({'success': False, 'message': 'Please enter a valid address'}), 400
        
        # Prepare enquiry data
        enquiry_data = {
            'name': data.get('name').strip(),
            'email': data.get('email').strip(),
            'phone': data.get('phone').strip(),
            'course': data.get('course').strip(),
            'address': data.get('address').strip(),
            'submitted_date': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        }
        
        # Save enquiry
        if not save_enquiry(enquiry_data):
            return jsonify({'success': False, 'message': 'Error saving enquiry. Please try again.'}), 500
        
        # Send email
        send_email_notification(enquiry_data)
        
        return jsonify({
            'success': True,
            'message': 'Thank you for your enquiry! We will contact you soon.'
        }), 200
    
    except Exception as e:
        print(f"Error: {str(e)}")
        return jsonify({'success': False, 'message': 'An error occurred. Please try again.'}), 500

# Error handlers
@app.errorhandler(404)
def not_found(error):
    return render_template('index.html'), 404

@app.errorhandler(500)
def server_error(error):
    return jsonify({'error': 'Server error'}), 500

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
