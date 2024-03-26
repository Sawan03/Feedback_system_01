from flask import Flask, render_template, request, jsonify, redirect, url_for, flash,session
from flask_sqlalchemy import SQLAlchemy
import random
from flask_mail import Mail, Message
from sqlalchemy.schema import UniqueConstraint


app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///professors.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['MAIL_SERVER'] = 'smtp-mail.outlook.com'  # Replace with your SMTP server
app.config['MAIL_PORT'] = 587  # Replace with your SMTP port
app.config['MAIL_USE_TLS'] = True  # Set to False if your server uses SSL
app.config['MAIL_USERNAME'] = 'Sawanrathore815@gmail.com'
app.config['MAIL_PASSWORD'] = 'Ishika@1803'
app.config['MAIL_DEFAULT_SENDER'] = 'Sawanrathore815@gmail.com'  # Replace with your email address
app.secret_key = 'your_secret_key'
db = SQLAlchemy(app)
mail = Mail(app)

class Professor(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(255), nullable=False)
    email = db.Column(db.String(255), nullable=False, unique=True)
    password = db.Column(db.String(255), nullable=False)
    phone = db.Column(db.String(15), nullable=False)
    professor_id = db.Column(db.String(10), nullable=False, unique=True)
    professor_year = db.Column(db.Integer, nullable=False)
    branches = db.Column(db.String(255), nullable=False)
    subjects = db.Column(db.String(255), nullable=False)

class Feedback(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    professor_id = db.Column(db.Integer, db.ForeignKey('professor.id'), nullable=False)
    student_id = db.Column(db.Integer, db.ForeignKey('student.id'), nullable=False)
    feedback_text = db.Column(db.Text, nullable=False)
     # Define relationships
    professor = db.relationship('Professor', backref='feedbacks')
    student = db.relationship('Student', backref='feedbacks')
    __table_args__ = (
        UniqueConstraint('professor_id', 'student_id', name='_professor_student_uc'),
    )
    
class UserData(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    attendance = db.Column(db.Integer)  # Change data type to Integer
    marks = db.Column(db.Integer)  # Change data type to Integer
    behavior = db.Column(db.String(100))



        
class Student(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(255), nullable=False)
    email = db.Column(db.String(255), nullable=False, unique=True)
    password = db.Column(db.String(255), nullable=False)
    enrollment_no = db.Column(db.String(20), nullable=False, unique=True)
    year = db.Column(db.Integer, nullable=False)
    branch = db.Column(db.String(50), nullable=False)
    subsection = db.Column(db.String(10))


otp_store = {}
@app.route('/submit_user_data', methods=['POST'])
def submit_user_data():
    # Retrieve form data
    attendance = request.form.get('attendance')
    marks = request.form.get('marks')
    behavior = request.form.get('behavior')

    # Create a new instance of the UserData model with the form data
    user_data = UserData(attendance=attendance, marks=marks, behavior=behavior)

    try:
        # Add the new instance to the database session
        db.session.add(user_data)

        # Commit the session to save the changes to the database
        db.session.commit()

        # Return a response
        return jsonify({'message': 'Form data submitted successfully'})
    except Exception as e:
        # If an error occurs, rollback the session and return an error response
        db.session.rollback()
        return jsonify({'error': str(e)})
    
@app.route('/submit_feedback', methods=['POST'])
def submit_feedback():
    if request.method == 'POST':
        # Extract data from the request
        professor_id = request.form['professor_id']
        student_id = request.form['student_id']
        feedback_text = request.form['feedback_text']

        # Create a new Feedback object
        new_feedback = Feedback(professor_id=professor_id, student_id=student_id, feedback_text=feedback_text)

        try:
            # Add the new feedback to the database session and commit changes
            db.session.add(new_feedback)
            db.session.commit()
            return jsonify({'status': 'success', 'message': 'Feedback submitted successfully'})
        except Exception as e:
            # If an error occurs, rollback changes and return an error response
            db.session.rollback()
            return jsonify({'status': 'error', 'message': str(e)}), 500
       

@app.route('/send-otp', methods=['POST'])
def send_otp():
    if request.method == 'POST':
        email = request.form.get('email')

        # Basic validation
        if not email or not email.endswith('@indoreinstitute.com'):
            return jsonify({'status': 'error', 'message': 'Invalid email format'}), 400

        # Generate and store OTP
        generated_otp = str(random.randint(1000, 9999))
        otp_store[email] = generated_otp

        # Send OTP to the user's email
        try:
            msg = Message('Verification OTP', recipients=[email])
            msg.body = f'Your OTP for verification is: {generated_otp}'
            mail.send(msg)

            return jsonify({'status': 'success', 'message': f'OTP sent to {email}.'})
        except Exception as e:
            return jsonify({'status': 'error', 'message': f'Error sending OTP: {str(e)}'}), 500

      
@app.route('/verify-email', methods=['POST'])
def verify_email():
    if request.method == 'POST':
        email = request.form.get('email')
        entered_otp = request.form.get('otp')

        # Validate entered OTP
        correct_otp = otp_store.get(email)

        if correct_otp and entered_otp == correct_otp:
            # Mark the email as verified (you may want to store this information in your database)
            session['email_verified'] = True

            response_data = {'status': 'success', 'message': 'Email verification successful!'}
        else:
            response_data = {'status': 'error', 'message': 'Invalid OTP. Please try again.'}

        return jsonify(response_data)
    
@app.route('/')
def index():
    return render_template('home.html')

@app.route('/student_register', methods=['GET', 'POST'])
def register_student():
    if request.method == 'POST':
        try:
            data = request.get_json()

            new_student = Student(
                name=data['name'],
                email=data['email'],
                password=data['password'],
                enrollment_no=data['enrollmentNo'],
                year=data['year'],
                branch=data['branch'],
                subsection=data.get('subsection')  # Optional, depending on your form
            )

            db.session.add(new_student)
            db.session.commit()

            # Store the user's ID in the session for future authentication
            session['user_id'] = new_student.id

            response_data = {'status': 'success'}
            flash('Student registered successfully!', 'success')  # Flash a success message
        except Exception as e:
            db.session.rollback()
            response_data = {'status': 'error', 'message': str(e)}
            flash(f'Error: {str(e)}', 'error')  # Flash an error message
        finally:
            db.session.close()

        return jsonify(response_data)
    else:
        # Handle the GET request (e.g., render the registration form)
        return render_template('student_reg.html')
 
@app.route('/delete_user', methods=['POST'])
def delete_user():
    user_type = request.form['user_type']
    user_id = request.form['user_id']
    
    # Delete the user based on user_type and user_id
    if user_type == 'student':
        student = Student.query.get(user_id)
        if student:
            db.session.delete(student)
            db.session.commit()
            return jsonify({'message': 'Student deleted successfully'})
        else:
            return jsonify({'message': 'Student not found'}), 404
    elif user_type == 'professor':
        professor = Professor.query.get(user_id)
        if professor:
            db.session.delete(professor)
            db.session.commit()
            return jsonify({'message': 'Professor deleted successfully'})
        else:
            return jsonify({'message': 'Professor not found'}), 404
    else:
        return jsonify({'message': 'Invalid user type'}), 400 
@app.route('/admin_dashboard')
def admin_dashboard():
    # Fetch feedback data from the database
    feedback_data = Feedback.query.all()  # Query all feedback records
    
    # Fetch the count of students and professors from the database
    num_students = Student.query.count()
    num_professors = Professor.query.count()
    
    # Fetch all students and professors
    student_data = Student.query.all()
    professor_data = Professor.query.all()

    return render_template('admin_dashboard.html', feedback_data=feedback_data, num_students=num_students, num_professors=num_professors, student_data=student_data, professor_data=professor_data)
@app.route('/register_professor', methods=['GET', 'POST'])
def register_professor():
    if request.method == 'POST':
        try:
            data = request.get_json()

            new_professor = Professor(
                name=data['name'],
                email=data['email'],
                password=data['password'],
                phone=data['phone'],
                professor_id=data['professorId'],
                professor_year=data['professorYear'],
                branches=', '.join(data['branches']),
                subjects=', '.join(data['subjects'])
            )

            db.session.add(new_professor)
            db.session.commit()

            response_data = {'status': 'success'}
            flash('Professor registered successfully!', 'success')  # Flash a success message
        except Exception as e:
            db.session.rollback()
            response_data = {'status': 'error', 'message': str(e)}
            flash(f'Error: {str(e)}', 'error')  # Flash an error message
        finally:
            db.session.close()

        return jsonify(response_data)

    # Handle GET request (if needed)
    # You can render a registration form or redirect to a registration page
    return render_template('pro_registration.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        if request.headers.get('Content-Type') == 'application/json':
            # Handle AJAX request
            data = request.get_json()
            professor_id = data.get('professorId')
            password = data.get('password')

            # Check if the provided credentials match a registered professor
            professor = Professor.query.filter_by(professor_id=professor_id, password=password).first()

            if professor:
                # Store the user's ID in the session for future authentication
                session['user_id'] = professor.id
                return jsonify({'status': 'success'})
            else:
                return jsonify({'status': 'error', 'message': 'Invalid professor ID or password'})

        else:
            # Handle HTML form submission
            email = request.form.get('email')
            password = request.form.get('password')

            # Check if the email and password match a registered professor
            professor = Professor.query.filter_by(email=email, password=password).first()

            if professor:
                # Store the user's ID in the session for future authentication
                session['user_id'] = professor.id
                flash('Login successful!', 'success')
                return redirect(url_for('dashboard'))  # Redirect to the dashboard route
            else:
                flash('Invalid email or password. Please try again.', 'error')

    # Render the login page
    return render_template('pro_login.html')



@app.route('/student_login', methods=['GET', 'POST'])
def student_login():
    if request.method == 'POST':
        if request.headers.get('Content-Type') == 'application/json':
            # Handle AJAX request
            data = request.get_json()
            enrollment_no = data.get('enrollment_no')
            password = data.get('password')

            # Check if the provided credentials match a registered student
            student = Student.query.filter_by(enrollment_no=enrollment_no, password=password).first()

            if student:
                # Store the user's ID in the session for future authentication
                session['user_id'] = student.id
                return jsonify({'status': 'success'})
            else:
                return jsonify({'status': 'error', 'message': 'Invalid student email or password'})

        else:
            # Handle HTML form submission
            enrollment_no = request.form.get('enrollment_no')
            password = request.form.get('password')

            # Check if the email and password match a registered student
            student = Student.query.filter_by(enrollment_no=enrollment_no, password=password).first()

            if student:
                # Store the user's ID in the session for future authentication
                session['user_id'] = student.id
                flash('Login successful!', 'success')
                return redirect(url_for('dashboard_student'))  # Redirect to the student dashboard route
            else:
                flash('Invalid email or password. Please try again.', 'error')

    # Render the student login page
    return render_template('student_login.html')

@app.route('/dashboard_student')
def dashboard_student():
    # Check if the user is authenticated by verifying the presence of their ID in the session
    if 'user_id' in session:
        # Fetch student details from the database using the stored user ID
        student_id = session['user_id']
        student = Student.query.get(student_id)

        if student:
            # Fetch professors based on criteria (student year, professor year, matching branches)
            professors = Professor.query.filter(
                Professor.professor_year == student.year,
                Professor.branches.contains(student.branch)
            ).all()

            # Render the student dashboard with user details and associated professors
            return render_template('dashboard_student.html', student=student, professors=professors)
        else:
            flash('Student not found.', 'error')
            return redirect(url_for('student_login'))
    else:
        flash('You need to log in first.', 'error')
        return redirect(url_for('student_login'))

@app.route('/dashboard')
def dashboard():
    # Check if the user is authenticated by verifying the presence of their ID in the session
    if 'user_id' in session:
        # Fetch user details from the database using the stored user ID
        user_id = session['user_id']
        professor = Professor.query.get(user_id)
        
        # Fetch student data based on the professor's professor_year
        professor_year = professor.professor_year
        
        # Fetch student data from the database based on year
        student_data = Student.query.filter_by(year=professor_year).all()
        
        # Render the dashboard with user details and student data
        return render_template('dashboard.html', professor=professor, student_data=student_data)
    else:
        flash('You need to log in first.', 'error')
        return redirect(url_for('login'))


@app.route('/logout')
def logout():
    # Clear the user ID from the session to log out
    session.pop('user_id', None)
    flash('Logout successful!', 'success')
    return redirect(url_for('login'))
    

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=True)