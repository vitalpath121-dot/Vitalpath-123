from flask import Flask

app = Flask(__name__)

@app.route('/')
def home():
    return '''<!DOCTYPE html>
<html>
<head>
    <title>VitalPath</title>
    <style>
        body { font-family: Arial; background: #f5f5f5; padding: 20px; }
        .container { max-width: 600px; margin: 0 auto; background: white; padding: 20px; border-radius: 10px; }
        h1 { color: #3AB795; text-align: center; }
        .meal { background: #f9f9f9; padding: 15px; margin: 10px 0; border-radius: 5px; border-left: 4px solid #3AB795; }
        h3 { color: #333; }
        p { color: #666; }
        button { background: #3AB795; color: white; padding: 12px 20px; border: none; border-radius: 5px; width: 100%; margin-top: 10px; cursor: pointer; }
        button:hover { background: #2a9970; }
    </style>
</head>
<body>
    <div class="container">
        <h1>✔️ VitalPath</h1>
        <p style="text-align: center;">Welcome, Sarah!</p>
        <p style="text-align: center; color: #FF9500; font-weight: bold;">Friday, March 6</p>
        
        <div class="meal"><h3>🥣 Breakfast</h3><p>Overnight Oats</p></div>
        <div class="meal"><h3>🥗 Lunch</h3><p>Grilled Chicken Salad</p></div>
        <div class="meal"><h3>🍽️ Dinner</h3><p>Sheet Pan Salmon</p></div>
        
        <div style="background: #E0F2F1; padding: 15px; margin: 20px 0; border-radius: 5px;">
            <h3>🏃 Activity</h3>
            <p>30-min walk logged</p>
        </div>
        
        <button>⬇️ Generate Meals</button>
        <button style="background: #F39237;">☁️ Sync Database</button>
    </div>
</body>
</html>'''

if __name__ == '__main__':
    app.run(debug=False, host='0.0.0.0', port=5000)
```

Click **"Commit changes"**

---

## **Step 2: Edit requirements.txt**

Replace with:
```
Flask
```

Click **"Commit changes"**

---

## **Step 3: Redeploy on Railway**

Go to Railway and click **"Redeploy"**

**Wait 2-3 minutes**

Refresh your browser at:
```
https://vitalpath-123-production.up.railway.app
