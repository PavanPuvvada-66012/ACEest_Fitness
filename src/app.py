from flask import Flask, render_template, request, redirect, url_for, flash
from datetime import datetime
import io
import base64
import matplotlib
matplotlib.use('Agg') # CRITICAL for Matplotlib in a multi-threaded web environment (e.g., Flask)
import matplotlib.pyplot as plt

app = Flask(__name__)
# A secret key is required for flash messages
app.secret_key = 'aceest_fitness_secret_key_v3' 

# --- Data Store (In-memory storage) ---
# Centralized storage mimicking the self.workouts dictionary
workouts_log = {"Warm-up": [], "Workout": [], "Cool-down": []}
CATEGORIES = list(workouts_log.keys())

# Static data for the Workout Plan Tab
WORKOUT_PLAN_DATA = {
    "Warm-up (5-10 min)": ["5 min light cardio (Jog/Cycle)", "Jumping Jacks (30 reps)", "Arm Circles (15 Fwd/Bwd)"],
    "Strength Workout (45-60 min)": ["Push-ups (3 sets of 10-15)", "Squats (3 sets of 15-20)", "Plank (3 sets of 60 seconds)", "Lunges (3 sets of 10/leg)"],
    "Cool-down (5 min)": ["Slow Walking", "Static Stretching (Hold 30s each)", "Deep Breathing Exercises"]
}

# Static data for the Diet Guide Tab
DIET_GUIDE_DATA = {
    "🎯 Weight Loss": ["Breakfast: Oatmeal with Berries", "Lunch: Grilled Chicken/Tofu Salad", "Dinner: Vegetable Soup with Lentils"],
    "💪 Muscle Gain": ["Breakfast: 3 Egg Omelet, Spinach, Whole-wheat Toast", "Lunch: Chicken Breast, Quinoa, and Steamed Veggies", "Post-Workout: Protein Shake, Greek Yogurt"],
    "🏃 Endurance Focus": ["Pre-Workout: Banana & Peanut Butter", "Lunch: Whole Grain Pasta with Light Sauce", "Dinner: Salmon & Avocado Salad"]
}
# --------------------

# --- Utility: Chart Generator ---
def generate_charts_base64():
    """Generates Matplotlib charts and returns them as a single base64 image string."""
    
    # 1. Process data
    totals = {cat: sum(entry['duration'] for entry in sessions) for cat, sessions in workouts_log.items()}
    values = list(totals.values())
    
    # Return None if no workouts logged
    if sum(values) == 0:
        return None

    categories = list(totals.keys())
    colors = ["#007bff", "#28a745", "#ffc107"] # Blue, Green, Yellow

    # 2. Setup Figure
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(7.5, 4.5), dpi=100, facecolor='white')
    
    # --- Subplot 1: Bar Chart (Time Spent) ---
    ax1.bar(categories, values, color=colors)
    ax1.set_title("Time Spent per Category (Min)", fontsize=10)
    ax1.set_ylabel("Total Minutes", fontsize=8)
    ax1.tick_params(axis='x', labelsize=8)
    ax1.tick_params(axis='y', labelsize=8)
    ax1.grid(axis='y', linestyle='--', alpha=0.7)

    # --- Subplot 2: Pie Chart (Distribution) ---
    pie_labels = [c for c, v in zip(categories, values) if v > 0]
    pie_values = [v for v in values if v > 0]
    pie_colors = [colors[i] for i, v in enumerate(values) if v > 0]
    
    ax2.pie(pie_values, labels=pie_labels, autopct="%1.1f%%", startangle=90, colors=pie_colors,
                wedgeprops={"edgecolor": "black", 'linewidth': 0.5}, textprops={'fontsize': 8})
    ax2.set_title("Workout Distribution", fontsize=10)
    ax2.axis('equal') 

    plt.tight_layout(pad=2.0)
    
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
    """Log Workouts Tab"""
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
        flash('Duration must be a positive whole number.', 'error')
        return redirect(url_for('index'))

    new_entry = {
        "exercise": exercise,
        "duration": duration,
        "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    }
    workouts_log[category].append(new_entry)

    flash(f"Added {exercise} ({duration} min) to {category} successfully! 💪", 'success')
    return redirect(url_for('index'))

@app.route('/summary')
def view_summary():
    """Renders the summary page."""
    total_time = sum(sum(entry['duration'] for entry in sessions) for sessions in workouts_log.values())
    
    # Motivational message logic
    if total_time == 0:
        motivation_msg = "No sessions logged yet. Time to start moving!"
    elif total_time < 60:
        motivation_msg = "Nice effort! You're building consistency."
    else: # total_time >= 60
        motivation_msg = "Excellent dedication! Keep up the great work."
    
    return render_template('summary.html', 
                           workouts_log=workouts_log, 
                           total_time=total_time,
                           categories=CATEGORIES,
                           motivation_msg=motivation_msg)

@app.route('/plan')
def workout_plan():
    """Workout Plan Tab"""
    return render_template('workout_plan.html', 
                           plan_data=WORKOUT_PLAN_DATA, 
                           current_tab='plan')

@app.route('/diet')
def diet_guide():
    """Diet Guide Tab"""
    return render_template('diet_guide.html', 
                           diet_plans=DIET_GUIDE_DATA, 
                           current_tab='diet')

@app.route('/progress')
def progress_tracker():
    """Progress Tracker Tab (Generates charts)"""
    chart_image_base64 = generate_charts_base64()
    
    # Calculate total minutes for display below the chart
    total_minutes = sum(sum(entry['duration'] for entry in sessions) for sessions in workouts_log.values())

    return render_template('progress_tracker.html', 
                           chart_image=chart_image_base64,
                           total_minutes=total_minutes,
                           current_tab='progress')

if __name__ == '__main__':
    # Dependencies: pip install Flask matplotlib
    app.run(debug=True, host='0.0.0.0', port=5000)