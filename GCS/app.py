import sys
import os

# --- PATH CONFIGURATION ---
# 1. Get the absolute path of the current file (app.py)
current_dir = os.path.dirname(os.path.abspath(__file__)) 
# result: .../directory/GCS

# 2. Go up one level to the project root ('directory')
project_root = os.path.dirname(current_dir)
# result: .../directory

# 3. Construct the full path to your target script folder
# NOTE: I am using the exact spelling you provided ("drwan..." and "msission")
target_path = os.path.join(project_root, 'scripts', 'missions' ,'drawn_polygon_mission')

# 4. Add this path to Python's system paths
if target_path not in sys.path:
    sys.path.append(target_path)

# --- IMPORT ---
# Now Python can find 'main_mission.py' as if it were in the same folder
# Ensure the function name matches exactly what is in your file (run_mission vs run_msission)
try:
    from main_mission import run_sky_guards_mission
    print("Successfully imported run_mission logic!")
except ImportError as e:
    print(f"Error importing mission script: {e}")
    print(f"I tried looking in: {target_path}")

import threading
import asyncio
from flask import Flask, render_template, request, jsonify

# Make sure main_mission.py is in the same folder or properly referenced

app = Flask(__name__)

@app.route('/')
def index():
    return render_template('index.html')

# Helper function to run async code in a separate thread
def start_mission_thread(coordinates):
    # Create a new event loop for this thread
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    # Run the mission
    loop.run_until_complete(run_sky_guards_mission(coordinates))
    loop.close()

@app.route('/deploy', methods=['POST'])
def deploy_swarm():
    data = request.get_json()
    coordinates = data.get('coordinates')
    
    if not coordinates or len(coordinates) != 4:
        return jsonify({"status": "error", "message": "Please draw exactly 4 points (Square/Rectangle)."}), 400

    print(f"Deploying Swarm to {len(coordinates)} targets...")

    # 2. LAUNCH MISSION IN BACKGROUND
    # This lets the web server respond "Success" immediately while drones fly
    mission_thread = threading.Thread(target=start_mission_thread, args=(coordinates,))
    mission_thread.start()

    return jsonify({"status": "success", "message": "Swarm deployed to corners!"})

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)