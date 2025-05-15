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

# Pages
sign up page:
add an email in the email field
