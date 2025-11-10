import unittest
import json
# Import the Flask app instance and the data store from your app.py
from src.app import app, workouts_log 

class FitnessTrackerTests(unittest.TestCase):

    def setUp(self):
        """Set up a test client and clear the data before each test."""
        # Create a test client and set testing mode
        self.app = app.test_client()
        self.app.testing = True
        
        # Clear the in-memory log for a clean start on every test
        for category in workouts_log:
            workouts_log[category].clear()

    def post_workout(self, exercise="Running", duration=30, category="Workout"):
        """Utility function for simulating a workout submission."""
        return self.app.post(
            '/add',
            data={
                'exercise': exercise,
                'duration': duration,
                'category': category
            },
            follow_redirects=True
        )

# --- 1. Log Workouts Tests (Form Submission) ---

    def test_add_session_success(self):
        """Tests successful addition of a workout session."""
        response = self.post_workout(exercise="Squats", duration=20, category="Workout")
        
        self.assertEqual(response.status_code, 200)
        # Check if the flash message confirms success
        self.assertIn(b'Added Squats (20 min) to Workout successfully!', response.data)
        # Check if the data was logged correctly
        self.assertEqual(len(workouts_log["Workout"]), 1)
        self.assertEqual(workouts_log["Workout"][0]["duration"], 20)

    def test_add_session_missing_fields(self):
        """Tests submission without an exercise name."""
        response = self.post_workout(exercise="", duration=15)
        
        # Check if the flash message shows an error
        self.assertIn(b'Please enter both exercise and duration.', response.data)
        self.assertEqual(len(workouts_log["Workout"]), 0)

    def test_add_session_invalid_duration(self):
        """Tests submission with non-numeric duration."""
        # Flask's request.form automatically processes fields as strings, 
        # but the Python code will raise an error when converting 'ten' to int.
        response = self.app.post('/add', data={'exercise': 'Run', 'duration': 'ten', 'category': 'Workout'}, follow_redirects=True)
        
        self.assertIn(b'Duration must be a positive whole number.', response.data)
        self.assertEqual(len(workouts_log["Workout"]), 0)

    def test_add_session_zero_duration(self):
        """Tests submission with zero duration."""
        response = self.post_workout(exercise="Walk", duration=0)
        
        self.assertIn(b'Duration must be a positive whole number.', response.data)
        self.assertEqual(len(workouts_log["Workout"]), 0)

# ----------------------------------------------------------------------
# --- 2. Summary Page Tests ---

    def test_summary_empty(self):
        """Tests the summary page when no workouts have been logged."""
        response = self.app.get('/summary')
        
        self.assertEqual(response.status_code, 200)
        # Check total time is 0
        self.assertIn(b'Total Training Time Logged: 0 minutes', response.data)
        # Check motivational message for no time logged
        self.assertIn(b'No sessions logged yet. Time to start moving!', response.data)
        # Check for the "No sessions recorded" message
        self.assertIn(b'No sessions recorded.', response.data)

    def test_summary_calculation(self):
        """Tests if total time is calculated correctly."""
        self.post_workout(exercise="Run", duration=15) # 15 min
        self.post_workout(exercise="Weights", duration=45) # 45 min
        response = self.app.get('/summary')
        
        # Total time should be 15 + 45 = 60 minutes
        self.assertIn(b'Total Training Time Logged: 60 minutes', response.data)
        # Check motivational message for high time
        self.assertIn(b'Excellent dedication! Keep up the great work', response.data)

    def test_summary_categorization(self):
        """Tests if workouts are displayed under the correct categories."""
        
        # 1. Log data into specific categories
        self.post_workout(exercise="Stretching", duration=5, category="Cool-down")
        self.post_workout(exercise="Jogging", duration=10, category="Warm-up")
        
        response = self.app.get('/summary')
        
        # --- 2. Positive Content Checks (Ensures entries are present) ---
        # Check Warm-up section entry (using the bolded format)
        self.assertIn(b'**Jogging** - 10 min', response.data)
        
        # Check Cool-down section entry (using the bolded format)
        self.assertIn(b'**Stretching** - 5 min', response.data)
        
        # Check Workout section empty content (This avoids the fragile whitespace match)
        self.assertIn(b'Workout:</h3>', response.data)
        self.assertIn(b'No sessions recorded.</p>', response.data) 
        
        # --- 3. Order Check (Ensures logical categorization is correct) ---
        # Get the starting index of the category headers in the raw HTML data
        warmup_header_pos = response.data.find(b'Warm-up:')
        workout_header_pos = response.data.find(b'Workout:')
        cooldown_header_pos = response.data.find(b'Cool-down:')

        # Ensure the headers appear in the expected order: Warm-up < Workout < Cool-down
        self.assertTrue(warmup_header_pos < workout_header_pos)
        self.assertTrue(workout_header_pos < cooldown_header_pos)

    def test_summary_motivation_low_time(self):
        """Tests for the low dedication message (< 60 min)."""
        self.post_workout(duration=30) # 30 min
        self.post_workout(duration=15) # 15 min
        response = self.app.get('/summary')
        
        self.assertIn(b'Total Training Time Logged: 45 minutes', response.data)
        self.assertIn(b"Nice effort! You&#39;re building consistency.", response.data)

# ----------------------------------------------------------------------
# --- 3. Progress Tracker Tests (Chart/Data Visualization) ---

    def test_progress_tracker_no_data(self):
        """Tests progress tracker renders correctly with no logged data."""
        response = self.app.get('/progress')
        
        self.assertEqual(response.status_code, 200)
        # Should contain the "no data" message
        self.assertIn(b'No workout data logged yet. Log a session to see your progress!', response.data)
        # Should NOT contain the image tag prefix
        self.assertNotIn(b'<img src="data:image/png;base64,', response.data)

    def test_progress_tracker_with_data(self):
        """Tests progress tracker renders an image when data is present."""
        self.post_workout(exercise="Jumping Jacks", duration=10, category="Warm-up")
        response = self.app.get('/progress')
        
        self.assertEqual(response.status_code, 200)
        # Should contain the image tag prefix (indicating chart was generated)
        self.assertIn(b'<img src="data:image/png;base64,', response.data)
        # Should NOT contain the "no data" message
        self.assertNotIn(b'No workout data logged yet. Log a session to see your progress!', response.data)
        # Check total time rendering
        self.assertIn(b'Total Training Time Logged: 10 minutes', response.data)

# ----------------------------------------------------------------------
# --- 4. Static Page & Navigation Tests ---

    def test_workout_plan_content(self):
        """Tests if the workout plan page renders with expected content."""
        response = self.app.get('/plan')
        
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'Personalized Workout Plan', response.data)
        # Check for content from the plan data
        self.assertIn(b'Strength Workout (45-60 min)', response.data)
        self.assertIn(b'Push-ups (3 sets of 10-15)', response.data)

    def test_diet_guide_content(self):
        """Tests if the diet guide page renders with expected content."""
        response = self.app.get('/diet')
        
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'Best Diet Guide for Fitness Goals', response.data)
        # Check for content from the diet data
        self.assertIn(b'Weight Loss Plan:', response.data)
        self.assertIn(b'Breakfast: 3 Egg Omelet, Spinach, Whole-wheat Toast', response.data)

    def test_navigation_links(self):
        """Tests if all core navigation links are present on the layout."""
        response = self.app.get('/')
        
        self.assertEqual(response.status_code, 200)
        # Check for link texts (encoded as bytes)
        self.assertIn(b'Log Workouts', response.data)
        self.assertIn(b'Workout Plan', response.data)
        self.assertIn(b'Diet Guide', response.data)
        self.assertIn(b'Progress Tracker', response.data)

if __name__ == '__main__':
    unittest.main()
