# app.py
"""
Flask web application for ACEest Fitness Tracker.

Provides endpoints to view workouts, add new workouts via POST,
and renders the homepage.
"""
from flask import Flask, request, jsonify, render_template
from src.tracker import WorkoutTracker

app = Flask(__name__)
tracker = WorkoutTracker()

@app.route("/")
def home():
    """
    Render the homepage showing all logged workouts.

    Returns:
        str: Rendered HTML page.
    """
    return render_template("index.html", workouts=tracker.get_workouts())

@app.route("/add", methods=["POST"])
def add_workout():
    """
    Add a new workout via POST request.

    Accepts JSON or form data with keys 'workout' and 'duration'.
    Returns JSON response with status and added workout or error message.

    Returns:
        Response: JSON with status and workout data or error message.
    """
    data = request.form or request.json
    workout = data.get("workout")
    duration = data.get("duration")

    try:
        duration = int(duration)
        entry = tracker.add_workout(workout, duration)
        return jsonify({"status": "success", "workout": entry}), 201
    except ValueError as e:
        return jsonify({"status": "error", "message": str(e)}), 400

@app.route("/workouts", methods=["GET"])
def view_workouts():
    """
    Retrieve all logged workouts as JSON.

    Returns:
        Response: JSON list of workouts.
    """
    return jsonify(tracker.get_workouts())

if __name__ == "__main__":
    app.run(host="0.0.0.0",port=5000,debug=True)
