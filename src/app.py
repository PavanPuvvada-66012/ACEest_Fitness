# app.py
"""
Flask web application for ACEest Fitness Tracker.

Provides endpoints to view workouts, add new workouts via POST,
and renders the homepage.
"""
from flask import Flask, render_template, request, redirect, url_for, flash
from datetime import datetime

app = Flask(__name__)
# Used for flash() messages
app.secret_key = 'super_secret_key_for_fitness' 

# Global variable to store workout data (In-memory storage)
# This mimics the self.workouts dictionary from the Tkinter app
WORKOUTS = {"Warm-up": [], "Workout": [], "Cool-down": []}

@app.route('/')
def index():
    """
    Renders the main workout logging page.
    """
    # Check if there are any existing workouts to show the 'View Summary' button
    has_workouts = any(WORKOUTS.values()) 
    
    # Render the main template, passing necessary data
    return render_template('index.html', 
                           categories=WORKOUTS.keys(),
                           has_workouts=has_workouts)

@app.route('/add', methods=['POST'])
def add_workout():
    """
    Handles the form submission to add a new workout entry.
    """
    category = request.form.get('category')
    workout = request.form.get('workout', '').strip()
    duration_str = request.form.get('duration', '').strip()

    # 1. Input Validation
    if not workout or not duration_str:
        flash("Please enter both exercise and duration.", 'error')
        return redirect(url_for('index'))

    try:
        duration = int(duration_str)
        if duration <= 0:
            raise ValueError("Duration must be a positive number.")
    except ValueError:
        flash("Duration must be a valid positive number.", 'error')
        return redirect(url_for('index'))

    # 2. Data Logging (similar to self.add_workout)
    if category in WORKOUTS:
        entry = {
            "exercise": workout,
            "duration": duration,
            "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        }
        WORKOUTS[category].append(entry)
        flash(f"Added {workout} ({duration} min) to {category} successfully!", 'success')
    else:
        flash("Invalid category selected.", 'error')
        
    return redirect(url_for('index'))

@app.route('/summary')
def view_summary():
    """
    Renders the workout summary page.
    """
    # Check if any sessions are logged
    if not any(WORKOUTS.values()):
        flash("No sessions logged yet!", 'info')
        return redirect(url_for('index'))
    
    total_time = sum(entry['duration'] for sessions in WORKOUTS.values() for entry in sessions)
    
    # Determine the motivational message based on total_time
    if total_time < 30:
        msg = "Good start! Keep moving 💪"
    elif total_time < 60:
        msg = "Nice effort! You're building consistency 🔥"
    else:
        msg = "Excellent dedication! Keep up the great work 🏆"

    return render_template('summary.html', 
                           workouts=WORKOUTS, 
                           total_time=total_time, 
                           motivational_message=msg)

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
