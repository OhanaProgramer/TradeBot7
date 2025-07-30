from flask import Flask, render_template, jsonify
import json
from pathlib import Path
import subprocess
import threading
import time
import logging

app = Flask(__name__, template_folder="templates")

# Paths
BASE_PATH = Path(__file__).parent
DATA_PATH = BASE_PATH / "data"
POSITIONS_FILE = DATA_PATH / "positions.json"
STRATEGY_FILE = DATA_PATH / "strategy.json"

def load_json(file_path):
    with open(file_path, 'r') as f:
        return json.load(f)

@app.route("/")
def home():
    print(">>> / route hit")
    try:
        data = load_json(POSITIONS_FILE)
        last_updated = data.get("last_updated", "Unknown") if isinstance(data, dict) else "Unknown"
    except Exception:
        last_updated = "Unknown"
    return render_template("index.html", last_updated=last_updated)

@app.route("/test")
def test():
    print(">>> /test route hit")
    return "Test route works!"

@app.route("/api/positions")
def api_positions():
    print(">>> /api/positions route hit")
    try:
        data = load_json(POSITIONS_FILE)
        last_updated = data.get("last_updated", "Unknown") if isinstance(data, dict) else "Unknown"
        positions = data.get("positions", data) if isinstance(data, dict) else data
        return jsonify({"last_updated": last_updated, "positions": positions})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route("/strategy")
def strategy_page():
    print(">>> /strategy route hit")
    try:
        data = load_json(POSITIONS_FILE)
        positions = data["positions"] if isinstance(data, dict) and "positions" in data else data
        last_updated = data.get("last_updated", "Unknown")
        print(">>> Loaded positions count:", len(positions))
        return render_template("strategy.html", strategy=positions, last_updated=last_updated)
    except Exception as e:
        return f"Error loading strategy data: {e}", 500

@app.route("/api/update")
def update_positions_api():
    try:
        script_path = BASE_PATH / "utils" / "update_positions.py"
        app.logger.info(f"Running update_positions script at {script_path}")
        subprocess.run(["python", str(script_path)], check=True)
        app.logger.info("Positions updated successfully.")
        return jsonify({"status": "success", "message": "Positions updated."})
    except Exception as e:
        app.logger.error(f"Error updating positions: {e}")
        return jsonify({"status": "error", "message": str(e)}), 500


# Enable background thread to periodically update positions
def auto_update_positions(interval=300):
    script_path = BASE_PATH / "utils" / "update_positions.py"
    while True:
        try:
            subprocess.run(["python", str(script_path)], check=True)
        except Exception as e:
            app.logger.error(f"Auto-update error: {e}")
        time.sleep(interval)

threading.Thread(target=auto_update_positions, args=(300,), daemon=True).start()

if __name__ == "__main__":
    app.run(debug=True)