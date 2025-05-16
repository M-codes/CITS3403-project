# CITS3403-project

An infectious disease monitoring system where users can upload datasets of infections, and the application will plot them on a map and you can share areas with high outbreaks to other users.

## Website functionality key points:
- Upload Data
- View data on plot
- Create / Login to save data, and share
- Share Map to social stream, or privately

Mockup design: [Figma Design](https://www.figma.com/design/apbwOMo7xaG9D8hvylg64a/Surface-Laptop%E2%80%A8-Mockup--Community-?node-id=31-3441&p=f&t=012q9qqrHNn1W8v7-0)

## Team Members

| UWA ID | Name | Github Username |
|--------|------|----------------|
| 23237074 | Michael Hii Rong Mee | M-codes |
| 23887375 | Kate Fu | Kateefu |
| 23390948 | Darcy Tyler | dtyler04 |
| 23153032 | Dan Wiese | |

**Note:** Michael: when pushing commit in wsl,  I only config username and not the email so it may look like two users with M-codes but it's still from Michael.

## Getting Started

### To launch the app:

```bash
# 1. Create & Activate the virtual environment
python3 -m venv venv
source venv/bin/activate

# 2. Install required Python packages
pip install -r requirements.txt

# 3. Set up the database
flask db upgrade

# 4. Run the Flask app
flask run
```

### To run unittest tests:

```bash
# 1. Open a terminal in your project directory

# 2. Activate your virtual environment
python3 -m venv venv
source venv/bin/activate

# 3. Install required Python packages
pip install -r requirements.txt

# 4. Testing test_auth.py
python -m unittest tests/test_auth.py

# 5. Testing test_models.py
python -m unittest tests/test_models.py
```

### To run selenium tests:

```bash
# 1. Open a terminal in your project directory

# 2. Activate your virtual environment
python3 -m venv venv
source venv/bin/activate


or on windows: 

python -m venv venv    
.\venv\Scripts\activate

# 3. Install required Python packages
pip install -r requirements.txt

# 4. Set up the database
flask db upgrade

# 5. Run the Flask app
flask run
```

A local development server should start at http://127.0.0.1:5000

```bash
# 6. Open the browser (Signup page) and enter the testing account
Email: test@example.com
Password: Test1234

# 7. Submit the form to create a test account

# 8. Open a new terminal 

# 9. Make sure the virtual environment is still active or activate it again

# 10. Run the selenium test script:
python3 tests/test_selenium.py
```

You should see messages like:
```
✅ Session check passed
✅ Login test passed
```
