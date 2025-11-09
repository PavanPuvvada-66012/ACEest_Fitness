from flask import Flask, render_template, request, redirect, url_for, flash
from datetime import datetime
import io
import base64
import matplotlib
# --- ADD THESE TWO LINES ---
matplotlib.use('Agg') # Set the backend to Agg
import matplotlib.pyplot as plt
# ---------------------------
from flask import Flask, render_template, request, redirect, url_for, flash
app = Flask(__name__)
app.secret_key = 'a_new_secret_key_for_flask_app_v2'

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
    "Weight Loss": ["Oatmeal with Fruits", "Grilled Chicken Salad", "Vegetable Soup", "Brown Rice & Veggies"],
    "Muscle Gain": ["Egg Omelet", "Chicken Breast", "Quinoa & Beans", "Protein Shake", "Greek Yogurt with Nuts"],
    "Endurance": ["Banana & Peanut Butter", "Whole Grain Pasta", "Sweet Potatoes", "Salmon & Avocado", "Trail Mix"]
}
# --------------------

# --- UTILITY: CHART GENERATOR ---
def generate_charts_base64():
    """Generates two Matplotlib charts (Bar and Pie) and returns them as base64 images."""
    # 1. Aggregate Data
    totals = {cat: sum(entry['duration'] for entry in workouts_log if entry['category'] == cat) for cat in CATEGORIES}
    categories = list(totals.keys())
    values = list(totals.values())
    
    if sum(values) == 0:
        return None # Return no image data if no workouts logged

    # 2. Setup Figure
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(10, 5))
    
    # --- Bar Chart ---
    colors = ["#007bff", "#28a745", "#ffc107"]
    ax1.bar(categories, values, color=colors)
    ax1.set_title("Time Spent per Category")
    ax1.set_ylabel("Minutes")

    # --- Pie Chart ---
    ax2.pie(values, labels=categories, autopct="%1.1f%%", startangle=90, colors=colors)
    ax2.set_title("Workout Distribution")

    plt.tight_layout()
    
    # 3. Save to In-Memory Buffer (BytesIO)
    buffer = io.BytesIO()
    plt.savefig(buffer, format='png')
    plt.close(fig) # Close the figure to free memory
    buffer.seek(0)
    
    # 4. Encode to Base64 for HTML embedding
    image_base64 = base64.b64encode(buffer.getvalue()).decode('utf-8')
    
    return image_base64

# --- ROUTES ---

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

    new_entry = {
        "category": category,
        "exercise": exercise,
        "duration": duration,
        "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    }
    workouts_log.append(new_entry)

    flash(f"Added {exercise} ({duration} min) to {category} successfully!", 'success')
    return redirect(url_for('index'))

@app.route('/summary')
def view_summary():
    """Renders the summary page."""
    categorized_workouts = {cat: [] for cat in CATEGORIES}
    total_time = 0
    
    for entry in workouts_log:
        categorized_workouts[entry['category']].append(entry)
        total_time += entry['duration']

    if total_time == 0:
        motivation_msg = "Good start! Keep moving" # Expected by test_summary_empty
    elif total_time < 60:
        motivation_msg = "Nice effort! You're building consistency"
    else: # total_time >= 60
        motivation_msg = "Excellent dedication! Keep up the great work" # Expected by test_summary_calculation & test_summary_motivation_high_time

    return render_template('summary.html', 
                       categorized_workouts=categorized_workouts, 
                       total_time=total_time,
                       categories=CATEGORIES,
                       motivation_msg=motivation_msg)   

@app.route('/chart')
def workout_chart():
    """Renders the static workout chart page."""
    return render_template('workout_chart.html', 
                           chart_data=WORKOUT_CHART_DATA, 
                           current_tab='chart')

@app.route('/diet')
def diet_chart():
    """Renders the static diet chart page."""
    return render_template('diet_chart.html', 
                           diet_plans=DIET_CHART_DATA, 
                           current_tab='diet')

@app.route('/progress')
def progress_tracker():
    """Renders the progress tracker tab, generating charts dynamically."""
    chart_image_base64 = generate_charts_base64()
    
    return render_template('progress_tracker.html', 
                           chart_image=chart_image_base64,
                           current_tab='progress')

if __name__ == '__main__':
    # You must install Matplotlib: pip install matplotlib
    app.run(debug=True, host='0.0.0.0', port=5000)
