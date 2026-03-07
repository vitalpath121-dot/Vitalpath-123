from flask import Flask

app = Flask(__name__)

@app.route('/')
def home():
    return '<h1>VitalPath</h1><p>App Working!</p>'

if __name__ == '__main__':
    app.run(debug=False)
