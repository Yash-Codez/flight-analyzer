import os
import glob
import pandas as pd
from flask import Flask, jsonify, send_from_directory

app = Flask(__name__, static_folder='static')

def get_latest_csv():
    """Finds the most recently created CSV file in the flight_results directory."""
    results_dir = os.path.join(os.path.dirname(__file__), 'flight_results')
    if not os.path.exists(results_dir):
        return None
    
    csv_files = glob.glob(os.path.join(results_dir, '*.csv'))
    if not csv_files:
        return None
    
    # Sort files by modification time, descending
    latest_file = max(csv_files, key=os.path.getmtime)
    return latest_file

@app.route('/')
def index():
    """Serve the main dashboard UI."""
    return send_from_directory(app.static_folder, 'index.html')

@app.route('/<path:path>')
def serve_static(path):
    """Serve other static files like CSS and JS."""
    return send_from_directory(app.static_folder, path)

@app.route('/api/flights')
def get_flights():
    """API endpoint to get the latest flight data."""
    latest_csv = get_latest_csv()
    if not latest_csv:
        return jsonify({"error": "No flight data found. Run the bot first."}), 404
        
    try:
        # Read the CSV using pandas
        df = pd.read_csv(latest_csv)
        
        # Replace NaN/NaT values with a string or None for proper JSON serialization
        df = df.fillna("N/A")
        
        # Convert to list of dictionaries
        flights = df.to_dict(orient='records')
        
        return jsonify({
            "status": "success",
            "file_used": os.path.basename(latest_csv),
            "total_records": len(flights),
            "data": flights
        })
    except Exception as e:
        return jsonify({"error": f"Failed to parse data: {str(e)}"}), 500

if __name__ == '__main__':
    print("[STARTING] Flight Price Analyzer Dashboard...")
    print("[INFO] Open http://localhost:5000 in your browser")
    app.run(debug=True, host='0.0.0.0', port=5000)
