from flask import Flask, request, jsonify, session, render_template
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash
from flask_cors import CORS

# Initialize the Flask application
app = Flask(__name__)
app.secret_key = '960610Moon'  # A secret key for session management
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///users.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Correct CORS setup: allow credentials from localhost:3000
CORS(app, supports_credentials=True, resources={r"/*": {"origins": "http://localhost:3000"}})

# Initialize the database
db = SQLAlchemy(app)

# User model
class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(128), nullable=False)

# Create the database tables if they don't exist
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

# Check login status
@app.route('/check-session')
def check_session():
    return jsonify({'logged_in': 'user_id' in session})

# Route for the homepage or signup page
@app.route('/')
def home():
    return render_template('signup.html')  # Ensure 'signup.html' is in the 'templates' folder

# Run the application
if __name__ == '__main__':
    app.run(debug=True, port=5000)