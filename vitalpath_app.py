from flask import Flask, render_template

app = Flask(__name__)

@app.route('/')
def home():
    user_name = "Sarah"
    formatted_date = "Friday, March 6"
    meals = [
        {"type": "Breakfast", "name": "Overnight Oats", "icon": "🥣"},
        {"type": "Lunch", "name": "Grilled Chicken Salad", "icon": "🥗"},
        {"type": "Dinner", "name": "Sheet Pan Salmon", "icon": "🍽️"},
    ]
    return render_template('index.html', user_name=user_name, formatted_date=formatted_date, meals=meals)

if __name__ == '__main__':
    app.run(debug=False, host='0.0.0.0', port=5000)
```

Click **"Commit changes"**

---

## **Step 3: Update requirements.txt**

Replace with ONLY:
```
Flask==2.3.0
