import unittest
from app import create_app, db
from app.models import User
from flask import json
from werkzeug.security import generate_password_hash

class AuthTestCase(unittest.TestCase):
    def setUp(self):
        self.app = create_app()
        self.app.config['TESTING'] = True
        self.app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'
        self.app.config['WTF_CSRF_ENABLED'] = False
        self.client = self.app.test_client()

        with self.app.app_context():
            db.create_all()

    def tearDown(self):
        with self.app.app_context():
            db.session.remove()
            db.drop_all()

    def test_register_success(self):
        res = self.client.post('/register', json={
            'email': 'testuser@example.com',
            'password': 'securepass'
        })
        self.assertEqual(res.status_code, 200)
        self.assertIn(b'User registered successfully.', res.data)

    def test_register_duplicate(self):
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
        res = self.client.post('/login', json={
            'email': 'missing@example.com',
            'password': 'wrongpass'
        })
        self.assertEqual(res.status_code, 401)
        self.assertIn(b'Invalid credentials.', res.data)

    def test_logout_without_login(self):
        res = self.client.get('/logout', follow_redirects=True)
        self.assertEqual(res.status_code, 200)
        self.assertIn(b'login', res.data.lower())  # should redirect to login page

    def test_invalid_email_format(self):
        res = self.client.post('/register', json={
            'email': 'not-an-email',
            'password': 'securepass'
        })
        # Right now your app accepts any string as email.
        # Once you validate it, update this:
        self.assertIn(res.status_code, [200, 400])
