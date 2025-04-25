from flask import Flask, request, jsonify, session, redirect, url_for
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash
from flask_cors import CORS

# This is a simple Flask application that provides user registration, login, and logout functionality.
app = Flask(__name__)
app.secret_key = '960610Moon'  #A secret key i randomly entered in the terminal
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///users.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['CORS_HEADERS'] = 'Content-Type'
app.config['CORS_RESOURCES'] = {r"/*": {"origins": "*"}}  # Allow all origins
app.config['CORS_SUPPORTS_CREDENTIALS'] = True  # Allow credentials
app.config['CORS_EXPOSE_HEADERS'] = ['Content-Type', 'Authorization']  # Expose specific headers
app.config['CORS_ALLOW_HEADERS'] = ['Content-Type', 'Authorization']  # Allow specific headers
app.config['CORS_ALLOW_METHODS'] = ['GET', 'POST', 'PUT', 'DELETE', 'OPTIONS']  # Allow specific methods
app.config['CORS_MAX_AGE'] = 3600  # Cache preflight response for 1 hour
app.config['CORS_SEND_WILDCARD'] = True  # Send wildcard in CORS response


# Initialize the database
db = SQLAlchemy(app)
CORS(app)


# User model
class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(128), nullable=False)

with app.app_context():
    db.create_all()

# Register endpoint
@app.route('/register', methods=['POST'])
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
@app.route('/login', methods=['POST'])
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
@app.route('/logout', methods=['GET'])
def logout():
    session.pop('user_id', None)
    return jsonify({'message': 'Logged out successfully.'})

# Check login status (optional)
@app.route('/check-session')
def check_session():
    return jsonify({'logged_in': 'user_id' in session})