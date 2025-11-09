from flask import Flask, render_template, request, redirect, url_for, flash
from datetime import datetime

app = Flask(__name__)
app.secret_key = 'a_new_secret_key_for_flash_messages' 

# --- DATA STORES ---
# In-memory storage for logged workouts
workouts_log = []
CATEGORIES = ["Warm-up", "Workout", "Cool-down"]

# Static data for the Workout Chart Tab
WORKOUT_CHART_DATA = {
    "Warm-up": ["5 min Jog", "Jumping Jacks", "Arm Circles", "Leg Swings", "Dynamic Stretching"],
    "Workout": ["Push-ups", "Squats", "Plank", "Lunges", "Burpees", "Crunches"],
    "Cool-down": ["Slow Walking", "Static Stretching", "Deep Breathing", "Yoga Poses"]
}

# Static data for the Diet Chart Tab
DIET_CHART_DATA = {
    "Weight Loss": ["Oatmeal with Fruits", "Grilled Chicken Salad", "Vegetable Soup", "Brown Rice & Stir-fry Veggies"],
    "Muscle Gain": ["Egg Omelet", "Chicken Breast", "Quinoa & Beans", "Protein Shake", "Greek Yogurt with Nuts"],
    "Endurance": ["Banana & Peanut Butter", "Whole Grain Pasta", "Sweet Potatoes", "Salmon & Avocado", "Trail Mix"]
}
# --------------------

# --- LOG WORKOUTS TAB (Home) ---
@app.route('/')
def index():
    """Renders the main workout logging form."""
    return render_template('index.html', categories=CATEGORIES, current_tab='log')

@app.route('/add', methods=['POST'])
def add_workout():
    """Handles the form submission to add a new workout."""
    category = request.form.get('category')
    exercise = request.form.get('exercise').strip()
    duration_str = request.form.get('duration').strip()

    # Input validation
    if not exercise or not duration_str:
        flash('Please enter both exercise and duration.', 'error')
        return redirect(url_for('index'))

    try:
        duration = int(duration_str)
        if duration <= 0:
             raise ValueError
    except ValueError:
        flash('Duration must be a positive number.', 'error')
        return redirect(url_for('index'))

    if category not in CATEGORIES:
         flash('Invalid workout category selected.', 'error')
         return redirect(url_for('index'))

    # Create the new entry
    new_entry = {
        "category": category,
        "exercise": exercise,
        "duration": duration,
        "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    }
    workouts_log.append(new_entry)

    flash(f"Added {exercise} ({duration} min) to {category} successfully!", 'success')
    return redirect(url_for('index'))

# --- WORKOUT CHART TAB ---
@app.route('/chart')
def workout_chart():
    """Renders the static workout chart page."""
    return render_template('workout_chart.html', 
                           chart_data=WORKOUT_CHART_DATA, 
                           current_tab='chart')

# --- DIET CHART TAB ---
@app.route('/diet')
def diet_chart():
    """Renders the static diet chart page."""
    return render_template('diet_chart.html', 
                           diet_plans=DIET_CHART_DATA, 
                           current_tab='diet')

# --- SUMMARY (Modal/Separate Page based on Tkinter's behavior) ---
@app.route('/summary')
def view_summary():
    """Renders the summary page with categorized workout data."""
    
    categorized_workouts = {cat: [] for cat in CATEGORIES}
    total_time = 0
    
    for entry in workouts_log:
        categorized_workouts[entry['category']].append(entry)
        total_time += entry['duration']

    # Determine the motivational message
    if total_time < 30:
        msg = "Good start! Keep moving 💪"
    elif total_time < 60:
        msg = "Nice effort! You're building consistency 🔥"
    else:
        msg = "Excellent dedication! Keep up the great work 🏆"

    return render_template('summary.html', 
                           categorized_workouts=categorized_workouts, 
                           total_time=total_time,
                           categories=CATEGORIES,
                           motivation_msg=msg)


if __name__ == '__main__':
    # Ensure you create a 'templates' directory in the same folder as app.py
    app.run(debug=True, host='0.0.0.0', port=5000)
