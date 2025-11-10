# pylint: disable=global-statement, invalid-name, unused-argument, redefined-outer-name
# pylint: disable=too-many-locals, too-many-statements, too-many-branches

"""
Flask application for the ACEest Fitness Tracker.
Includes routes for user info, workout logging, summary, and progress tracking.
"""
import io
import base64
from datetime import datetime
from flask import Flask, render_template, request, redirect, url_for, flash
from matplotlib.figure import Figure
import matplotlib.pyplot as plt
# pylint: disable=unused-import
import pandas as pd # Retained for potential future use or cleaner data handling
# pylint: enable=unused-import

# Ensure the plot style is set for non-interactive rendering
plt.style.use('ggplot')

# Initialize Flask app
APP = Flask(__name__)
# IMPORTANT: Flask needs a secret key for session management (used by flash messages)
APP.secret_key = 'your_super_secret_key_here'

# --- Global In-Memory Data Stores ---
# Key: Category, Value: List of entries
workouts_log = {"Warm-up": [], "Workout": [], "Cool-down": []}
user_info = {} # Stores name, regn_id, weight, height, BMI, BMR

# --- Constants (Renamed to follow Pylint's UPPER_CASE convention for constants) ---
MET_CONSTANTS = {
    "Warm-up": 3.0,
    "Workout": 6.0,
    "Cool-down": 2.5
}
WORKOUT_CATEGORIES = list(workouts_log.keys())

# --- Utility Functions ---
def calculate_metrics(weight_kg, height_cm, age, gender):
    """Calculates BMI and BMR (Harris-Benedict revised approximation) based on user inputs."""
    # Calculate BMI
    bmi = weight_kg / ((height_cm/100)**2)

    # Calculate BMR
    # Harris-Benedict revised BMR formula (Approximation)
    if gender.upper() == "M":
        bmr = 10 * weight_kg + 6.25 * height_cm - 5 * age + 5
    else: # Assuming Female (F)
        bmr = 10 * weight_kg + 6.25 * height_cm - 5 * age - 161
        
    return bmi, bmr

def calculate_calories(category, duration_min, weight_kg):
    """Calculates estimated calories burned."""
    # Formula: (MET * 3.5 * weight_kg / 200) * duration_min
    met = MET_CONSTANTS.get(category, 5) # Default MET is 5
    
    calories = (met * 3.5 * weight_kg / 200) * duration_min
    return calories

# -----------------------------------------------------------
## 1. User Info / Home Page
# -----------------------------------------------------------

@APP.route('/', methods=['GET', 'POST'])
def index():
    """Handles the user information form submission and display."""
    # Accessing mutable global state is necessary for this simple in-memory app
    global user_info

    if request.method == 'POST':
        # Removed redundant .strip() where request.form[] already returns a string
        name = request.form['name']
        regn_id = request.form['regn_id']
        gender = request.form['gender'].upper()
        
        # Use a list to check for emptyness, as requested in original logic
        if not all([name, regn_id, gender]):
            flash("Please fill in all user information fields.", 'danger')
            return redirect(url_for('index'))
            
        try:
            # Type conversion and validation
            age = int(request.form['age'])
            height_cm = float(request.form['height'])
            weight_kg = float(request.form['weight'])

            if gender not in ["M", "F"]:
                 flash("Gender must be 'M' or 'F'.", 'danger')
                 return redirect(url_for('index'))
            
            if not all([age > 0, height_cm > 0, weight_kg > 0]):
                flash("Age, Height, and Weight must be positive numbers.", 'danger')
                return redirect(url_for('index'))

            bmi, bmr = calculate_metrics(weight_kg, height_cm, age, gender)

            user_info.clear() # Clear existing info
            user_info.update({
                "name": name, 
                "regn_id": regn_id, 
                "age": age, 
                "gender": gender,
                "height": height_cm, 
                "weight": weight_kg, 
                "bmi": f"{bmi:.1f}", 
                "bmr": f"{bmr:.0f}"
            })
            
            flash(
                f"User info saved! BMI={user_info['bmi']}, BMR={user_info['bmr']} kcal/day", 
                'success'
            )
            return redirect(url_for('index'))

        except ValueError:
            flash("Invalid input. Age, Height, and Weight must be numbers.", 'danger')
        except Exception as err:
            flash(f"An unexpected error occurred: {err}", 'danger')
        
    return render_template('index.html', user_info=user_info)


# -----------------------------------------------------------
## 2. Log Workouts Page (The 'add' Route)
# -----------------------------------------------------------

@APP.route('/add', methods=['GET', 'POST'])
def add_workout():
    """Handles logging a new workout session."""
    if request.method == 'POST':
        category = request.form.get('category')
        exercise = request.form.get('exercise').strip()
        duration_str = request.form.get('duration').strip()

        if not exercise or not duration_str:
            flash("Please enter both exercise and duration.", 'danger')
            return redirect(url_for('add_workout'))

        try:
            duration = int(duration_str)
            if duration <= 0:
                # Raise ValueError to be caught by the block below
                raise ValueError
        except ValueError:
            flash("Duration must be a positive whole number.", 'danger')
            return redirect(url_for('add_workout'))
            
        if category not in WORKOUT_CATEGORIES:
             flash("Invalid workout category selected.", 'danger')
             return redirect(url_for('add_workout'))

        # Get weight from user_info, default to 70kg if not set
        weight = user_info.get("weight", 70.0) 
        calories = calculate_calories(category, duration, weight)
        
        entry = {
            "exercise": exercise, 
            "duration": duration, 
            "calories": calories, 
            "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        }
        
        workouts_log[category].append(entry)
        
        flash(
            f"Added **{exercise}** ({duration} min) to {category} successfully! 💪", 
            'success'
        )

        return redirect(url_for('add_workout'))

    return render_template('add_workout.html', categories=WORKOUT_CATEGORIES)


# -----------------------------------------------------------
## 3. Summary Page
# -----------------------------------------------------------

@APP.route('/summary')
def summary():
    """Calculates and displays the summary of all logged workouts."""
    # Use sum with a generator expression for cleaner calculation
    total_time = sum(
        sum(entry['duration'] for entry in sessions) 
        for sessions in workouts_log.values()
    )
    
    # Simple motivation logic
    if total_time == 0:
        motivation = "Time to start moving!"
        alert_class = "info"
    elif total_time < 60:
        motivation = "Nice effort! You're building consistency."
        alert_class = "warning"
    else:
        motivation = "Excellent dedication! Keep up the great work."
        alert_class = "success"

    # Organize data for the template
    summary_data = {
        category: sessions for category, sessions in workouts_log.items()
    }
    
    return render_template('summary.html', 
                           summary_data=summary_data, 
                           total_time=total_time,
                           motivation=motivation,
                           alert_class=alert_class)

# -----------------------------------------------------------
## 4. Progress Tracker (Chart Generation)
# -----------------------------------------------------------

@APP.route('/progress')
def progress_tracker():
    """Generates and embeds workout progress charts."""
    # Calculate total minutes per category
    totals = {
        cat: sum(entry['duration'] for entry in sessions) 
        for cat, sessions in workouts_log.items()
    }
    total_minutes = sum(totals.values())

    if total_minutes == 0:
        return render_template('progress.html', chart_img=None, total_minutes=0)

    # Convert to pandas Series for cleaner plotting preparation
    data_series = pd.Series(totals).sort_index()
    
    # Create the Matplotlib figure
    fig = Figure(figsize=(8, 5), dpi=100, facecolor='#FFFFFF')
    chart_colors = ['#2196F3', '#4CAF50', '#FFC107'] # Blue, Green, Yellow

    # --- Subplot 1: Bar Chart ---
    # Pylint: disable=invalid-name, multiple-statements
    ax1 = fig.add_subplot(121)
    ax1.bar(data_series.index, data_series.values, color=chart_colors)
    ax1.set_title("Total Minutes per Category", fontsize=10)
    ax1.set_ylabel("Total Minutes", fontsize=8)
    ax1.tick_params(axis='x', labelsize=8)
    ax1.tick_params(axis='y', labelsize=8)
    # Tidy up chart
    ax1.spines['right'].set_visible(False)
    ax1.spines['top'].set_visible(False)
    ax1.grid(axis='y', linestyle='--', alpha=0.6)
    # Pylint: enable=invalid-name, multiple-statements
    
    # --- Subplot 2: Pie Chart ---
    # Pylint: disable=invalid-name
    ax2 = fig.add_subplot(122)
    # Filter out categories with 0 minutes for the pie chart
    pie_data = data_series[data_series > 0]
    
    # Use the same color scheme, mapped to the existing data
    pie_colors = [
        chart_colors[i] for i, cat in enumerate(WORKOUT_CATEGORIES) 
        if totals[cat] > 0
    ]
    
    ax2.pie(
        pie_data.values, 
        labels=pie_data.index, 
        autopct="%1.1f%%", 
        startangle=90, 
        colors=pie_colors, 
        wedgeprops={"edgecolor":'white', 'linewidth': 1},
        textprops={'fontsize': 8}
    )
    ax2.set_title("Workout Distribution (%)", fontsize=10)
    ax2.axis('equal')
    # Pylint: enable=invalid-name

    fig.tight_layout(pad=2.0)
    
    # Convert plot to PNG image (in-memory)
    buf = io.BytesIO()
    fig.savefig(buf, format="png")
    data_uri = base64.b64encode(buf.getbuffer()).decode("ascii")
    chart_img = f"data:image/png;base64,{data_uri}"

    return render_template('progress.html', chart_img=chart_img, total_minutes=total_minutes)

# -----------------------------------------------------------
## 5. Static Pages (Workout Plan and Diet Guide)
# -----------------------------------------------------------

@APP.route('/plan')
def workout_plan():
    """Renders the static workout plan guide."""
    plan_data = {
        "Warm-up (5-10 min)": [
            "5 min light cardio (Jog/Cycle) to raise heart rate.",
            "Jumping Jacks (30 reps) for dynamic mobility.",
            "Arm Circles (15 Fwd/Bwd) to prepare shoulders."
        ],
        "Strength & Cardio (45-60 min)": [
            "Push-ups (3 sets of 10-15) - Upper body strength.",
            "Squats (3 sets of 15-20) - Lower body foundation.",
            "Plank (3 sets of 60 seconds) - Core stabilization.",
            "Lunges (3 sets of 10/leg) - Balance and leg development."
        ],
        "Cool-down (5 min)": [
            "Slow Walking - Bring heart rate down gradually.",
            "Static Stretching (Hold 30s each) - Focus on major muscle groups.",
            "Deep Breathing Exercises - Aid recovery and relaxation."
        ]
    }
    return render_template('plan.html', plan_data=plan_data)

@APP.route('/diet')
def diet_guide():
    """Renders the static diet guide."""
    diet_data = {
        "Goal: Muscle Gain Focus (High Protein)": [
            "Breakfast: 3 Egg Omelet, Spinach, Whole-wheat Toast",
            "Lunch: Chicken Breast Salad, Quinoa, Mixed Greens",
            "Snack: Protein Shake, Apple",
            "Dinner: Salmon Fillet, Sweet Potato, Asparagus"
        ],
        "Goal: Weight Loss Focus (Calorie Deficit)": [
            "Breakfast: Oatmeal with Berries and Chia Seeds",
            "Lunch: Lentil Soup, Small Whole-grain Roll",
            "Snack: Handful of Almonds",
            "Dinner: Lean Turkey Mince Stir-fry with low-carb veggies"
        ]
    }
    return render_template('diet.html', diet_data=diet_data)


# -----------------------------------------------------------
## 6. Run Application
# -----------------------------------------------------------

if __name__ == '__main__':
    # Use APP instead of app for Pylint compliance
    APP.run(debug=True, host='0.0.0.0', port=5000)