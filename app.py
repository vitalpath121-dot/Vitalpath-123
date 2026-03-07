from flask import Flask

app = Flask(__name__)

@app.route('/')
def home():
    return '<h1>VitalPath</h1><p>App Working!</p>'

if __name__ == '__main__':
    app.run(debug=False)
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>VitalPath</title>
    <style>
        * { margin: 0; padding: 0; box-sizing: border-box; }
        body { font-family: Arial, sans-serif; background: #f5f5f5; padding: 20px; }
        .container { max-width: 600px; margin: 0 auto; background: white; padding: 20px; border-radius: 10px; box-shadow: 0 2px 10px rgba(0,0,0,0.1); }
        h1 { color: #3AB795; text-align: center; margin-bottom: 10px; }
        .info { text-align: center; color: #666; margin-bottom: 20px; }
        .date { color: #FF9500; font-weight: bold; }
        .meal { background: #f9f9f9; padding: 15px; margin: 10px 0; border-radius: 5px; border-left: 4px solid #3AB795; }
        .meal h3 { color: #333; margin-bottom: 5px; }
        .meal p { color: #666; font-size: 14px; }
        .activity { background: #E0F2F1; padding: 15px; margin: 20px 0; border-radius: 5px; }
        .activity h3 { color: #333; }
        .activity p { color: #666; }
        button { background: #3AB795; color: white; padding: 12px 20px; border: none; border-radius: 5px; cursor: pointer; width: 100%; margin-top: 10px; font-size: 14px; font-weight: bold; transition: background 0.3s; }
        button:hover { background: #2a9970; }
        .orange-btn { background: #F39237; }
        .orange-btn:hover { background: #e67e1f; }
    </style>
</head>
<body>
    <div class="container">
        <h1>✔️ VitalPath</h1>
        <div class="info">
            <p>Welcome Back, <strong>{{ user_name }}!</strong></p>
            <p class="date">{{ formatted_date }}</p>
        </div>
        
        <h2 style="color: #333; font-size: 16px; margin: 20px 0 10px 0;">Today's Meals</h2>
        <div id="meals">
            {% for meal in meals %}
            <div class="meal">
                <h3>{{ meal.icon }} {{ meal.type }}</h3>
                <p>{{ meal.name }}</p>
            </div>
            {% endfor %}
        </div>
        
        <div class="activity">
            <h3>🏃 Activity</h3>
            <p>30-min walk logged</p>
        </div>
        
        <button class="orange-btn">⬇️ Generate Tomorrow's Meals</button>
        <button>☁️ Sync to Database</button>
    </div>
</body>
</html>
from app import app

if __name__ == "__main__":
    app.run()
```
web: python app.py
