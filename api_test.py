from flask import Flask, jsonify

app = Flask(__name__)

@app.route("/")
def home():
    return """
    <h1>DriveSafe AI - API Test</h1>
    <p>Backend API is running successfully.</p>
    <a href="/api/status">Open API Status</a>
    """

@app.route("/api/status")
def api_status():
    return jsonify({
        "system": "DriveSafe AI",
        "status": "Running",
        "camera": "Connected",
        "drowsiness_detection": "Active",
        "alarm_system": "Active",
        "backend": "Flask API",
        "database": "SQLite"
    })

if __name__ == "__main__":
    app.run(debug=True)