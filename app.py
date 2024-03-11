from flask import Flask, render_template, request, jsonify, redirect, url_for, flash,session
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///professors.db'  # Use SQLite database
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.secret_key = 'your_secret_key'  # Add a secret key for flash messages
db = SQLAlchemy(app)

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
    
    
class Student(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(255), nullable=False)
    email = db.Column(db.String(255), nullable=False, unique=True)
    password = db.Column(db.String(255), nullable=False)
    enrollment_no = db.Column(db.String(20), nullable=False, unique=True)
    year = db.Column(db.Integer, nullable=False)
    branch = db.Column(db.String(50), nullable=False)
    subsection = db.Column(db.String(10))
    
    
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
        # Fetch user details from the database using the stored user ID
        user_id = session['user_id']
        student = Student.query.get(user_id)

        # Render the student dashboard with user details
        return render_template('dashboard_student.html', student=student)
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

        # Render the dashboard with user details
        return render_template('dashboard.html', professor=professor)
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