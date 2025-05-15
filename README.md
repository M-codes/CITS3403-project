# CITS3403-project

An infectious disease monitoring system where users can upload datasets of infections, and the application will plot them on a map and you can share areas with high outbreaks to other users.

Website functionality key points:

Updload Data
View data on plot
Create / Login to save data, and share.
Share Map to social stream, or privately
Mockup design https://www.figma.com/design/apbwOMo7xaG9D8hvylg64a/Surface-Laptop%E2%80%A8-Mockup--Community-?node-id=31-3441&p=f&t=012q9qqrHNn1W8v7-0

| UWA ID | name  | Github user name |
|----------|----------|----------|
| 23237074    | Michael Hii Rong Mee     | M-codes     |
| 23887375   | Kate Fu     | Kateefu    |
| 23390948   | Darcy Tyler     | dtyler04     |
| 23153032   | Dan Wiese    |   |

To launch the app:
# 1. Activate the virtual environment
source venv/bin/activate

# 2. Install required Python packages
pip install -r requirements.txt

# 3. Set up the database
flask db upgrade

# 4. Run the Flask app
flask run


To run selenium test:
# 1. Open a terminal in your project directory

# 2. Activate your virtual environment
python3 -m venv venv
source venv/bin/activate

# 3. install required Python packages
pip install -r requirements.txt

# 4. Set up the database
flask db upgrade

# 5. Run the Flask app
flask run

# 6. A local development browser should start at http://127.0.0.1:5000

# 7. Open the browser (Signup page) and enter the testing account
Email: test@example.com
Password: Test1234

# 8. Submit the form to create a test account

# 9. Open a new terminal 

# 10. Make sure the virtual environment is still active or activate it again.

# 11. Run the selenium test script:
python3 tests/test_selenium.py

# 12. You should see messages like 
✅ Signup test passed
✅ Login test passed
