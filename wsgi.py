from app import app

if __name__ == "__main__":
    app.run()
```

Click **"Commit new file"**

---

## **Step 4: Go to Railway Settings**

1. Click **"Settings"** tab
2. Find **"Custom Start Command"**
3. Change it to:
```
gunicorn wsgi:app
