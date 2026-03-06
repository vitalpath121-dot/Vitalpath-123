import os
import copy
from datetime import datetime
from flask import Flask, render_template, request, jsonify, session
from firebase_admin import credentials, initialize_app, firestore
import geopy.geocoders
from geopy.exc import GeocoderTimedOut
import logging

app = Flask(__name__)
app.secret_key = 'your-secret-key-here'

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

try:
    cred = credentials.Certificate('path/to/serviceAccountKey.json')
    initialize_app(cred)
    db = firestore.client()
    logger.info("✅ Firebase initialized successfully")
except Exception as e:
    logger.error(f"❌ Firebase initialization error: {e}")
    db = None

MOCK_USER = {
    "user_id": "sarah_id",
    "name": "Sarah",
    "activity": "30-min walk logged"
}

MOCK_MEALS = [
    {"type": "Breakfast", "name": "Overnight Oats", "done": True, "icon": "🥣"},
    {"type": "Lunch", "name": "Grilled Chicken Salad", "done": True, "icon": "🥗"},
    {"type": "Dinner", "name": "Sheet Pan Salmon & Veggies", "done": True, "icon": "🍽️"},
]

def sync_with_database(user_id, meals):
    try:
        if db is None:
            return {"success": False, "message": "Firebase not initialized"}
        db.collection('users').document(user_id).collection('plans').add({
            'date': datetime.now(),
            'meals': meals,
        })
        logger.info(f"✅ Plan synced for user {user_id}")
        return {"success": True, "message": "✅ Plan synced to database!"}
    except Exception as e:
        logger.error(f"❌ Error syncing to database: {e}")
        return {"success": False, "message": f"❌ Error syncing: {str(e)}"}

def get_user_meals(user_id):
    try:
        if db is None:
            return MOCK_MEALS
        plans = db.collection('users').document(user_id).collection('plans').limit(1).stream()
        for plan in plans:
            return plan.get('meals', MOCK_MEALS)
        return MOCK_MEALS
    except Exception as e:
        logger.error(f"Error fetching meals: {e}")
        return MOCK_MEALS

def get_location_from_ip(ip_address=None):
    try:
        geolocator = geopy.geocoders.Nominatim(user_agent="vitalpath_app")
        if ip_address:
            return {"latitude": 40.7128, "longitude": -74.0060}
        return {"latitude": 40.7128, "longitude": -74.0060}
    except GeocoderTimedOut:
        logger.warning("Geolocation timeout")
        return {"latitude": 40.7128, "longitude": -74.0060}
    except Exception as e:
        logger.error(f"Geolocation error: {e}")
        return {"latitude": 40.7128, "longitude": -74.0060}

def generate_smart_meals(meals, latitude, longitude):
    try:
        new_meals = copy.deepcopy(meals)
        if latitude > 45 or latitude < -45:
            new_meals[2]['name'] = "🌡️ Warm Lentil Soup with Bread"
            new_meals[2]['icon'] = "🍲"
        else:
            new_meals[2]['name'] = "🌴 Fresh Poke Bowl with Mango Salsa"
            new_meals[2]['icon'] = "🍲"
        logger.info(f"✅ Smart meals generated for location: ({latitude}, {longitude})")
        return new_meals
    except Exception as e:
        logger.error(f"Error generating smart meals: {e}")
        return meals

@app.route('/')
def home():
    if 'user_id' not in session:
        session['user_id'] = MOCK_USER['user_id']
    if 'user_name' not in session:
        session['user_name'] = MOCK_USER['name']
    user_id = session.get('user_id', MOCK_USER['user_id'])
    user_name = session.get('user_name', MOCK_USER['name'])
    activity = MOCK_USER['activity']
    meals = get_user_meals(user_id)
    formatted_date = datetime.now().strftime('%A, %b. %d')
    return render_template('index.html', user_name=user_name, activity=activity, meals=meals, formatted_date=formatted_date)

@app.route('/api/generate-meals', methods=['POST'])
def generate_meals_api():
    try:
        user_id = session.get('user_id', MOCK_USER['user_id'])
        data = request.get_json()
        if data is None:
            data = {}
        latitude = data.get('latitude')
        longitude = data.get('longitude')
        if not latitude or not longitude:
            client_ip = request.remote_addr
            location = get_location_from_ip(client_ip)
            latitude = location['latitude']
            longitude = location['longitude']
        current_meals = get_user_meals(user_id)
        new_meals = generate_smart_meals(current_meals, latitude, longitude)
        sync_result = sync_with_database(user_id, new_meals)
        return jsonify({
            "success": True,
            "message": f"🤖 AI: New meals generated for your location! Lat: {latitude:.2f}, Lon: {longitude:.2f}",
            "meals": new_meals,
            "location": {"latitude": latitude, "longitude": longitude}
        })
    except Exception as e:
        logger.error(f"Error in generate_meals_api: {e}")
        return jsonify({"success": False, "message": f"Error: {str(e)}"}), 500

@app.route('/api/sync', methods=['POST'])
def sync_api():
    try:
        user_id = session.get('user_id', MOCK_USER['user_id'])
        data = request.get_json()
        if data is None:
            data = {}
        meals = data.get('meals', MOCK_MEALS)
        result = sync_with_database(user_id, meals)
        return jsonify(result)
    except Exception as e:
        logger.error(f"Error in sync_api: {e}")
        return jsonify({"success": False, "message": f"Error: {str(e)}"}), 500

@app.route('/api/meals', methods=['GET'])
def get_meals():
    try:
        user_id = session.get('user_id', MOCK_USER['user_id'])
        meals = get_user_meals(user_id)
        return jsonify({"success": True, "meals": meals})
    except Exception as e:
        logger.error(f"Error fetching meals: {e}")
        return jsonify({"success": False, "message": str(e)}), 500

@app.route('/api/location', methods=['POST'])
def update_location():
    try:
        data = request.get_json()
        if data is None:
            data = {}
        latitude = data.get('latitude')
        longitude = data.get('longitude')
        session['latitude'] = latitude
        session['longitude'] = longitude
        logger.info(f"Location received: {latitude}, {longitude}")
        return jsonify({"success": True, "message": "Location updated"})
    except Exception as e:
        logger.error(f"Error updating location: {e}")
        return jsonify({"success": False, "message": f"Error: {str(e)}"}), 500

@app.route('/health')
def health():
    return jsonify({"status": "🟢 VitalPath API is running"}), 200

@app.errorhandler(404)
def not_found(error):
    return jsonify({"error": "Endpoint not found"}), 404

@app.errorhandler(500)
def server_error(error):
    logger.error(f"Server error: {error}")
    return jsonify({"error": "Internal server error"}), 500

if __name__ == '__main__':
    logger.info("🚀 Starting VitalPath API...")
    app.run(debug=False, host='0.0.0