import io
import base64
from datetime import datetime, date
from flask import Flask, render_template, request, redirect, url_for, flash
from matplotlib.figure import Figure
import matplotlib.pyplot as plt
import pandas as pd # Using pandas for better data handling/summarization, though optional

# Ensure the plot style is set for non-interactive rendering
plt.style.use('ggplot')

app = Flask(__name__)
# IMPORTANT: Flask needs a secret key for session management (used by flash messages)
app.secret_key = 'your_super_secret_key_here'

# --- Global In-Memory Data Stores (Replacing Tkinter self.workouts and self.user_info) ---
# Key: Category, Value: List of entries
workouts_log = {"Warm-up": [], "Workout": [], "Cool-down": []}
user_info = {} # Stores name, regn_id, weight, height, BMI, BMR

# --- Constants ---
MET_VALUES = {
    "Warm-up": 3,
    "Workout": 6,
    "Cool-down": 2.5
}
WORKOUT_CATEGORIES = list(workouts_log.keys())

# --- Utility Functions ---
def calculate_metrics(weight_kg, height_cm, age, gender):
    """Calculates BMI and BMR based on user inputs."""
    bmi = weight_kg / ((height_cm/100)**2)
    # Harris-Benedict revised BMR formula (Approximation)
    if gender.upper() == "M":
        bmr = 10 * weight_kg + 6.25 * height_cm - 5 * age + 5
    else: # Assuming Female (F)
        bmr = 10 * weight_kg + 6.25 * height_cm - 5 * age - 161
    return bmi, bmr

def calculate_calories(category, duration, weight):
    """Calculates estimated calories burned."""
    # Default weight is 70kg if user info not set
    weight = user_info.get("weight", 70) 
    met = MET_VALUES.get(category, 5) # Default MET is 5
    # Formula: (MET * 3.5 * weight_kg / 200) * duration_min
    calories = (met * 3.5 * weight / 200) * duration
    return calories

# -----------------------------------------------------------
## 1. User Info / Home Page
# -----------------------------------------------------------

@app.route('/', methods=['GET', 'POST'])
def index():
    global user_info

    if request.method == 'POST':
        try:
            name = request.form['name'].strip()
            regn_id = request.form['regn_id'].strip()
            age = int(request.form['age'].strip())
            gender = request.form['gender'].strip().upper()
            height_cm = float(request.form['height'].strip())
            weight_kg = float(request.form['weight'].strip())

            if not all([name, regn_id, age, gender, height_cm, weight_kg]):
                flash("Please fill in all user information fields.", 'danger')
                return redirect(url_for('index'))
            
            if gender not in ["M", "F"]:
                 flash("Gender must be 'M' or 'F'.", 'danger')
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
            
            flash(f"User info saved! BMI={user_info['bmi']}, BMR={user_info['bmr']} kcal/day", 'success')
            return redirect(url_for('index'))

        except ValueError:
            flash("Invalid input. Age, Height, and Weight must be numbers.", 'danger')
        except Exception as e:
            flash(f"An unexpected error occurred: {e}", 'danger')
        
    return render_template('index.html', user_info=user_info)


# -----------------------------------------------------------
## 2. Log Workouts Page (The 'add' Route)
# -----------------------------------------------------------

@app.route('/add', methods=['GET', 'POST'])
def add_workout():
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
                raise ValueError
        except ValueError:
            flash("Duration must be a positive whole number.", 'danger')
            return redirect(url_for('add_workout'))
            
        if category not in WORKOUT_CATEGORIES:
             flash("Invalid workout category selected.", 'danger')
             return redirect(url_for('add_workout'))

        calories = calculate_calories(category, duration, user_info.get("weight", 70))
        
        entry = {
            "exercise": exercise, 
            "duration": duration, 
            "calories": calories, 
            "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        }
        
        workouts_log[category].append(entry)
        
        # Flash message using HTML formatting
        flash(f"Added **{exercise}** ({duration} min) to {category} successfully! 💪", 'success')

        return redirect(url_for('add_workout'))

    return render_template('add_workout.html', categories=WORKOUT_CATEGORIES)


# -----------------------------------------------------------
## 3. Summary Page
# -----------------------------------------------------------

@app.route('/summary')
def summary():
    total_time = sum(sum(entry['duration'] for entry in sessions) for sessions in workouts_log.values())
    
    # Simple motivation logic (based on original Tkinter app's structure)
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

@app.route('/progress')
def progress_tracker():
    totals = {cat: sum(entry['duration'] for entry in sessions) for cat, sessions in workouts_log.items()}
    values = list(totals.values())
    total_minutes = sum(values)

    if total_minutes == 0:
        return render_template('progress.html', chart_img=None, total_minutes=0)

    # Convert to DataFrame for easier plotting preparation (optional but cleaner)
    df = pd.Series(totals).sort_index()
    
    # Create the Matplotlib figure
    fig = Figure(figsize=(8, 5), dpi=100, facecolor='#FFFFFF')
    chart_colors = ['#2196F3', '#4CAF50', '#FFC107'] # Blue, Green, Yellow (Matching original palette)

    # --- Subplot 1: Bar Chart ---
    ax1 = fig.add_subplot(121)
    ax1.bar(df.index, df.values, color=chart_colors)
    ax1.set_title("Total Minutes per Category", fontsize=10)
    ax1.set_ylabel("Total Minutes", fontsize=8)
    ax1.tick_params(axis='x', labelsize=8)
    ax1.tick_params(axis='y', labelsize=8)
    ax1.spines['right'].set_visible(False)
    ax1.spines['top'].set_visible(False)
    ax1.grid(axis='y', linestyle='--', alpha=0.6)
    
    # --- Subplot 2: Pie Chart ---
    ax2 = fig.add_subplot(122)
    # Filter out categories with 0 minutes for the pie chart
    pie_data = df[df > 0]
    
    # Use the same color scheme, mapped to the existing data
    pie_colors = [chart_colors[i] for i, cat in enumerate(WORKOUT_CATEGORIES) if totals[cat] > 0]
    
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
    ax2.axis('equal') # Equal aspect ratio ensures that pie is drawn as a circle.

    fig.tight_layout(pad=2.0)
    
    # Convert plot to PNG image (in-memory)
    buf = io.BytesIO()
    fig.savefig(buf, format="png")
    data = base64.b64encode(buf.getbuffer()).decode("ascii")
    chart_img = f"data:image/png;base64,{data}"

    return render_template('progress.html', chart_img=chart_img, total_minutes=total_minutes)

# -----------------------------------------------------------
## 5. Static Pages (Workout Plan and Diet Guide)
# -----------------------------------------------------------

@app.route('/plan')
def workout_plan():
    # Placeholder data for the Workout Plan (based on content implied by the Tkinter structure)
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

@app.route('/diet')
def diet_guide():
    # Placeholder data for the Diet Guide
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
    app.run(debug=True, host='0.0.0.0', port=5000)