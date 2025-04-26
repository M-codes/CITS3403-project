from flask import Blueprint, request, jsonify, session, render_template, flash, redirect, url_for
from werkzeug.security import generate_password_hash, check_password_hash
from . import db  # Import the db object from __init__.py
from flask import current_app

# Create the blueprint
auth_bp = Blueprint('auth', __name__)

# User model
class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(128), nullable=False)

# Create database tables
@auth_bp.before_app_request
def create_tables():
    db.create_all()


# Register endpoint
@auth_bp.route('/register', methods=['POST'])
def register():
    data = request.get_json()
    email = data['email']
    password = data['password']

    if User.query.filter_by(email=email).first():
        return jsonify({'message': 'Email already registered.'}), 409

    hashed_password = generate_password_hash(password)
    new_user = User(email=email, password_hash=hashed_password)
    db.session.add(new_user)
    db.session.commit()

    return jsonify({'message': 'User registered successfully.'})

# Login endpoint
@auth_bp.route('/login', methods=['POST'])
def login():
    data = request.get_json()
    email = data['email']
    password = data['password']

    user = User.query.filter_by(email=email).first()
    if user and check_password_hash(user.password_hash, password):
        session['user_id'] = user.id
        return jsonify({'message': 'Login successful.'})
    return jsonify({'message': 'Invalid credentials.'}), 401

# Logout endpoint
@auth_bp.route('/logout', methods=['GET'])
def logout():
    session.pop('user_id', None)
    return jsonify({'message': 'Logged out successfully.'})

# Check login status
@auth_bp.route('/check-session')
def check_session():
    return jsonify({'logged_in': 'user_id' in session})

# Home route
@auth_bp.route('/')
def home():
    return render_template('signup.html')  # signup.html should be in app/templates/
