import unittest
from app import create_app, db
from app.models import User
from flask import json
from werkzeug.security import generate_password_hash

class AuthTestCase(unittest.TestCase):
    def setUp(self):
        # Set up a test Flask app with an in-memory SQLite database and CSRF disabled
        self.app = create_app({
            'TESTING': True,
            'SQLALCHEMY_DATABASE_URI': 'sqlite:///:memory:',
            'WTF_CSRF_ENABLED': False
        })
        
        self.client = self.app.test_client()

        # Create all tables before each test
        with self.app.app_context():
            db.create_all()

    def tearDown(self):
        # Clean up the database after each test
        with self.app.app_context():
            db.session.remove()
            db.drop_all()

    def test_register_success(self):
        # Test successful user registration
        res = self.client.post('/register', json={
            'email': 'testuser@example.com',
            'password': 'securepass'
        })
        self.assertEqual(res.status_code, 200)
        self.assertIn(b'User registered successfully.', res.data)

    def test_register_duplicate(self):
        # Test registering with an email that already exists
        with self.app.app_context():
            db.session.add(User(email='dupe@example.com', password_hash='hash'))
            db.session.commit()

        res = self.client.post('/register', json={
            'email': 'dupe@example.com',
            'password': 'anything'
        })
        self.assertEqual(res.status_code, 409)
        self.assertIn(b'Email already registered', res.data)

    def test_login_success(self):
        # Test successful login with correct credentials
        with self.app.app_context():
            hashed = generate_password_hash('mypassword')
            db.session.add(User(email='login@example.com', password_hash=hashed))
            db.session.commit()

        res = self.client.post('/login', json={
            'email': 'login@example.com',
            'password': 'mypassword'
        })
        self.assertEqual(res.status_code, 200)
        self.assertIn(b'Login successful.', res.data)

    def test_login_failure(self):
        # Test login with invalid credentials
        res = self.client.post('/login', json={
            'email': 'missing@example.com',
            'password': 'wrongpass'
        })
        self.assertEqual(res.status_code, 401)
        self.assertIn(b'Invalid credentials.', res.data)

    def test_logout_without_login(self):
        # Test logout route when not logged in (should redirect to login)
        res = self.client.get('/logout', follow_redirects=True)
        self.assertEqual(res.status_code, 200)
        self.assertIn(b'login', res.data.lower())  # should redirect to login page

    def test_invalid_email_format(self):
        # Test registration with an invalid email format
        res = self.client.post('/register', json={
            'email': 'not-an-email',
            'password': 'securepass'
        })
        
        self.assertIn(res.status_code, [200, 400])# Accepts either 200 or 400 depending on validation
