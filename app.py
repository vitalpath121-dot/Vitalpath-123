from flask import Flask

app = Flask(__name__)

@app.route('/')
def home():
    return '<h1>VitalPath App</h1><p>Welcome Sarah!</p><p>Your app is working!</p>'

@app.route('/health')
def health():
    return 'OK', 200
