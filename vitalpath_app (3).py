import os
import copy
from datetime import datetime
from flask import Flask, render_template, request, jsonify, session
from firebase_admin import credentials, initialize_app, firestore
import geopy.geocoders
from geopy.exc import GeocoderTimedOut
import logging

# Initialize Flask app
app = Flask(__name__)
app.secret_key = 'your-secret-key-here'  # Change this to a secure key

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# =====================================================
# FIREBASE INITIALIZATION
# =====================================================
# Initialize Firebase (Download your service account key from Firebase Console)
try:
    cred = credentials.Certificate('path/to/serviceAccountKey.json')  # Update this path
    initialize_app(cred)
    db = firestore.client()
    logger.info("✅ Firebase initialized successfully")
except Exception as e:
    logger.error(f"❌ Firebase initialization error: {e}")
    db = None

# =====================================================
# MOCK DATA
# =====================================================
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

# =====================================================
# DATABASE LOGIC
# =====================================================
def sync_with_database(user_id, meals):
    """Save meal plan to Firebase Firestore"""
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
    """Retrieve user's meals from Firestore"""
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

# =====================================================
# GEOLOCATION & SMART RECOMMENDATIONS
# =====================================================
def get_location_from_ip(ip_address=None):
    """Get user's approximate location"""
    try:
        # Using geolocator (works without GPS like in web)
        geolocator = geopy.geocoders.Nominatim(user_agent="vitalpath_app")
        
        # For web apps, we get location from client-side or use IP geolocation
        # This is a fallback - in production use IP geolocation API
        if ip_address:
            # You would use an IP geolocation service here
            # Example: https://ip-api.com/json/{ip}
            return {"latitude": 40.7128, "longitude": -74.0060}  # Default: NYC
        
        return {"latitude": 40.7128, "longitude": -74.0060}
    except GeocoderTimedOut:
        logger.warning("Geolocation timeout")
        return {"latitude": 40.7128, "longitude": -74.0060}
    except Exception as e:
        logger.error(f"Geolocation error: {e}")
        return {"latitude": 40.7128, "longitude": -74.0060}

def generate_smart_meals(meals, latitude, longitude):
    """Generate meal recommendations based on location and activity"""
    try:
        # Logic based on Location
        # If user is in a cold area (high latitude), suggest warm foods
        # If user is in warm area, suggest fresh/cold foods
        
        new_meals = copy.deepcopy(meals)
        
        if latitude > 45 or latitude < -45:
            # Cold regions
            new_meals[2]['name'] = "🌡️ Warm Lentil Soup with Bread"
            new_meals[2]['icon'] = "🍲"
        else:
            # Warm regions
            new_meals[2]['name'] = "🌴 Fresh Poke Bowl with Mango Salsa"
            new_meals[2]['icon'] = "🍲"
        
        logger.info(f"✅ Smart meals generated for location: ({latitude}, {longitude})")
        return new_meals
    except Exception as e:
        logger.error(f"Error generating smart meals: {e}")
        return meals

# =====================================================
# ROUTES
# =====================================================

@app.route('/')
def home():
    """Main page - Display user's meal plan"""
    # Initialize session data if not exists
    if 'user_id' not in session:
        session['user_id'] = MOCK_USER['user_id']
    if 'user_name' not in session:
        session['user_name'] = MOCK_USER['name']
    
    user_id = session.get('user_id', MOCK_USER['user_id'])
    user_name = session.get('user_name', MOCK_USER['name'])
    activity = MOCK_USER['activity']
    
    meals = get_user_meals(user_id)
    formatted_date = datetime.now().strftime('%A, %b. %d')
    
    return render_template('index.html', 
                         user_name=user_name,
                         activity=activity,
                         meals=meals,
                         formatted_date=formatted_date)

@app.route('/api/generate-meals', methods=['POST'])
def generate_meals_api():
    """API endpoint to generate smart meals based on location"""
    try:
        user_id = session.get('user_id', MOCK_USER['user_id'])
        
        # Get location (from request or auto-detect)
        data = request.get_json()
        if data is None:
            data = {}
        
        latitude = data.get('latitude')
        longitude = data.get('longitude')
        
        if not latitude or not longitude:
            # Fallback to IP-based location
            client_ip = request.remote_addr
            location = get_location_from_ip(client_ip)
            latitude = location['latitude']
            longitude = location['longitude']
        
        # Generate smart meals
        current_meals = get_user_meals(user_id)
        new_meals = generate_smart_meals(current_meals, latitude, longitude)
        
        # Save to database
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
    """API endpoint to sync meals to Firebase"""
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
    """API endpoint to get current meals"""
    try:
        user_id = session.get('user_id', MOCK_USER['user_id'])
        meals = get_user_meals(user_id)
        return jsonify({"success": True, "meals": meals})
    except Exception as e:
        logger.error(f"Error fetching meals: {e}")
        return jsonify({"success": False, "message": str(e)}), 500

@app.route('/api/location', methods=['POST'])
def update_location():
    """API endpoint to receive client-side geolocation"""
    try:
        data = request.get_json()
        if data is None:
            data = {}
        
        latitude = data.get('latitude')
        longitude = data.get('longitude')
        
        # Store in session or database
        session['latitude'] = latitude
        session['longitude'] = longitude
        
        logger.info(f"Location received: {latitude}, {longitude}")
        return jsonify({"success": True, "message": "Location updated"})
    except Exception as e:
        logger.error(f"Error updating location: {e}")
        return jsonify({"success": False, "message": f"Error: {str(e)}"}), 500

@app.route('/health')
def health():
    """Health check endpoint"""
    return jsonify({"status": "🟢 VitalPath API is running"}), 200

@app.errorhandler(404)
def not_found(error):
    """Handle 404 errors"""
    return jsonify({"error": "Endpoint not found"}), 404

@app.errorhandler(500)
def server_error(error):
    """Handle 500 errors"""
    logger.error(f"Server error: {error}")
    return jsonify({"error": "Internal server error"}), 500

# =====================================================
# MAIN
# =====================================================
if __name__ == '__main__':
    # Run Flask app
    logger.info("🚀 Starting VitalPath API...")
    app.run(debug=False, host='0.0.0.0', port=5000)
