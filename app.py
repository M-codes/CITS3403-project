from flask import Flask, render_template

app = Flask(__name__)

@app.route('/')
def home():
    # You can pass data to the HTML file as a dictionary
    return render_template('index.html', message="Hello, Flask is working!")

if __name__ == '__main__':
    app.run(debug=True)