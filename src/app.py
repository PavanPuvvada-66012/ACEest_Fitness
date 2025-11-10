"""# app.py"""
import base64
from datetime import datetime
import io
from flask import Flask, render_template, request, redirect, url_for, flash
import matplotlib.pyplot as plt
import matplotlib
matplotlib.use('Agg') # Use non-GUI backend for Matplotlib

app = Flask(__name__)
app.config['SECRET_KEY'] = 'your_secret_key_for_flash_messages' # IMPORTANT: Change this

# Global Data Store (Replaces self.workouts)
# Use a dictionary to store lists of workout entries by category
workouts_log = {
    "Warm-up": [], 
    "Workout": [], 
    "Cool-down": []
}

# Define a consistent color palette for charts and UI
COLOR_PRIMARY = "#4CAF50"    # Vibrant Green
COLOR_SECONDARY = "#2196F3"  # Bright Blue
COLOR_ACCENT = "#FFC107"     # Yellow
COLOR_DANGER = "#DC3545"     # Red

# --- Utility Function: Chart Generation ---

def create_progress_charts():
    """Generates a Matplotlib figure and returns it as a Base64-encoded PNG string."""
    totals = {cat: sum(entry['duration'] for entry in sessions)
              for cat, sessions in workouts_log.items()}
    categories = list(totals.keys())
    values = list(totals.values())
    total_minutes = sum(values)

    if total_minutes == 0:
        return None, 0 # Return None if no data

    # 1. Create Matplotlib Figure
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(9, 4), facecolor='#FFFFFF')
    chart_colors = [COLOR_SECONDARY, COLOR_PRIMARY, COLOR_ACCENT]
    # --- Subplot 1: Bar Chart (Time Spent) ---
    ax1.bar(categories, values, color=chart_colors)
    ax1.set_title("Total Minutes per Category", fontsize=10)
    ax1.set_ylabel("Total Minutes", fontsize=8)
    ax1.tick_params(axis='x', labelsize=8)
    ax1.tick_params(axis='y', labelsize=8)
    ax1.spines['right'].set_visible(False)
    ax1.spines['top'].set_visible(False)
    ax1.grid(axis='y', linestyle='-', alpha=0.3)
    # --- Subplot 2: Pie Chart (Distribution) ---
    pie_labels = [c for c, v in zip(categories, values) if v > 0]
    pie_values = [v for v in values if v > 0]
    pie_colors = [chart_colors[i] for i, v in enumerate(values) if v > 0]
    ax2.pie(pie_values, labels=pie_labels, autopct="%1.1f%%", startangle=90, colors=pie_colors,
            wedgeprops={"edgecolor": "white", 'linewidth': 1}, textprops={'fontsize': 8})
    ax2.set_title("Workout Distribution (%)", fontsize=10)
    ax2.axis('equal')
    fig.tight_layout(pad=1.5)
    # 2. Save Matplotlib Figure to a byte buffer (PNG)
    buffer = io.BytesIO()
    fig.savefig(buffer, format='png', bbox_inches='tight')
    plt.close(fig) # Close the figure to free memory
    # 3. Base64 encode the PNG for embedding in HTML
    plot_data = base64.b64encode(buffer.getvalue()).decode('utf-8')
    return plot_data, total_minutes
# --- Routes (Replaces Tkinter Tabs and Functions) ---
@app.route('/', methods=['GET', 'POST'])
@app.route('/add', methods=['GET', 'POST'])
def log_workouts():
    """DocString PlaceHolder"""
    if request.method == 'POST':
        # Retrieve form data
        category = request.form.get('category')
        exercise = request.form.get('exercise', '').strip()
        duration_str = request.form.get('duration', '').strip()
        # Input validation
        if not exercise or not duration_str:
            flash("Please enter both exercise and duration.", 'danger')
            return redirect(url_for('log_workouts'))
        try:
            duration = int(duration_str)
            if duration <= 0: raise ValueError
        except ValueError:
            flash("Duration must be a positive whole number.", 'danger')
            return redirect(url_for('log_workouts'))
        # Log the workout
        entry = {
            "exercise": exercise,
            "duration": duration,
            "timestamp": datetime.now().strftime("%Y-%m-%d") # Changed to just date for simplicity
        }
        workouts_log[category].append(entry)

        flash(f"Added **{exercise}** ({duration} min) to {category} successfully! 💪", 'success')
        return redirect(url_for('log_workouts'))
    # GET request: render the form
    return render_template('log_workouts.html', categories=workouts_log.keys())
@app.route('/summary')
def view_summary():
    """DocString PlaceHolder"""
    total_time = sum(sum(entry['duration'] for entry in sessions)
                     for sessions in workouts_log.values())
    if total_time < 1:
        motivation = "No sessions logged yet. Time to start moving!"
    elif total_time < 60:
        motivation = "Nice effort! You're building consistency."
    else:
        motivation = "Excellent dedication! Keep up the great work."
    return render_template('summary.html',
                           workouts=workouts_log,
                           total_time=total_time,
                           motivation=motivation)
@app.route('/progress')
def progress_tracker():
    """DocString PlaceHolder"""
    plot_data, total_minutes = create_progress_charts()
    return render_template('progress_tracker.html',
                           plot_data=plot_data,
                           total_minutes=total_minutes)
@app.route('/plan')
def workout_plan():
    """DocString Placeholder"""
    # Content derived from your create_workout_plan_tab method
    plan_data = {
        "Warm-up (5-10 min)": ["5 min light cardio (Jog/Cycle) to raise heart rate.", "Jumping Jacks (30 reps) for dynamic mobility.", "Arm Circles (15 Fwd/Bwd) to prepare shoulders."],
        "Strength & Cardio (45-60 min)": ["Push-ups (3 sets of 10-15) - Upper body strength.", "Squats (3 sets of 15-20) - Lower body foundation.", "Plank (3 sets of 60 seconds) - Core stabilization.", "Lunges (3 sets of 10/leg) - Balance and leg development."],
        "Cool-down (5 min)": ["Slow Walking - Bring heart rate down gradually.", "Static Stretching (Hold 30s each) - Focus on major muscle groups.", "Deep Breathing Exercises - Aid recovery and relaxation."]
    }
    return render_template('workout_plan.html', plan_data=plan_data)
@app.route('/diet')
def diet_guide():
    """DocString Placeholder"""
    # Content derived from your create_diet_guide_tab method
    diet_plans = {
        "🎯 Weight Loss Focus (Calorie Deficit)": ["Breakfast: Oatmeal with Berries (High Fiber).", "Lunch: Grilled Chicken/Tofu Salad (Lean Protein).", "Dinner: Vegetable Soup with Lentils (Low Calorie, High Volume)."],
        "💪 Muscle Gain Focus (High Protein)": ["Breakfast: 3 Egg Omelet, Spinach, Whole-wheat Toast (Protein/Carb combo).", "Lunch: Chicken Breast, Quinoa, and Steamed Veggies (Balanced Meal).", "Post-Workout: Protein Shake & Greek Yogurt (Immediate Recovery)."],
        "🏃 Endurance Focus (Complex Carbs)": ["Pre-Workout: Banana & Peanut Butter (Quick Energy).", "Lunch: Whole Grain Pasta with Light Sauce (Sustainable Carbs).", "Dinner: Salmon & Avocado Salad (Omega-3s and Healthy Fats)."]
    }
    return render_template('diet_guide.html', diet_plans=diet_plans)
if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
