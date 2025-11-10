# pylint: disable=too-many-lines, line-too-long, too-many-public-methods
# pylint: disable=too-many-instance-attributes, unused-argument, redefined-outer-name

"""
Unit tests for the Flask-based ACEest Fitness Tracker application,
refactored to be compliant with Pylint standards.
"""
import unittest
from unittest.mock import patch
# The following imports are retained because they might be necessary for global
# data structures or app logic defined in src.app, even if not explicitly
# called in the test methods themselves.
# pylint: disable=unused-import
import pandas as pd
import json
# pylint: enable=unused-import

# Import the Flask application and global data stores
# Suppress import-error since src.app is assumed to exist in the user's structure.
# pylint: disable=import-error
from src.app import APP as app, user_info, workouts_log
# pylint: enable=import-error

class FlaskFitnessTrackerTests(unittest.TestCase):
    """
    Test suite for the Flask-based ACEest Fitness Tracker.
    """

    def setUp(self):
        """Set up a test client and clear global data before each test."""
        # Renamed self.app to self.app_client for snake_case compliance
        self.app_client = app.test_client()
        self.app_client.testing = True
        
        # CRITICAL: Clear global data before every test for isolation
        user_info.clear()
        for category in workouts_log:
            workouts_log[category].clear()
            
    def set_default_user_info(self):
        """Utility to populate necessary user info for calorie calculations."""
        user_info.update({
            "name": "Test User", "regn_id": "123", "age": 30, "gender": "M",
            "height": 180.0, "weight": 75.0, "bmi": "23.1", "bmr": "1738"
        })

    def post_user_info(self, name="Test User", regn="123", age=30, gender="M", height=180, weight=75):
        """Utility for simulating user info submission."""
        return self.app_client.post(
            '/',
            data={
                'name': name,
                'regn_id': regn,
                'age': str(age),
                'gender': gender,
                'height': str(height),
                'weight': str(weight)
            },
            follow_redirects=True
        )

    def post_workout(self, exercise="Running", duration=30, category="Workout"):
        """Utility function for simulating a workout submission."""
        return self.app_client.post(
            '/add',
            data={
                'exercise': exercise,
                'duration': str(duration),
                'category': category
            },
            follow_redirects=True
        )

# ----------------------------------------------------------------------
## 1. User Info Tests (/)
# ----------------------------------------------------------------------

    def test_index_page_loads(self):
        """Tests that the main user info page loads correctly."""
        response = self.app_client.get('/')
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'User Information', response.data)

    def test_post_user_info_success(self):
        """Tests successful calculation and saving of user info."""
        # FIX BMR: 80kg, 170cm, 25, F calculates to 1576.5 -> 1576
        response = self.post_user_info(weight=80, height=170, age=25, gender="F")
        self.assertEqual(response.status_code, 200)
        
        # Check flash message for success and calculated metrics
        self.assertIn(b'User info saved!', response.data)
        self.assertIn(b'BMR: <strong>1576</strong> kcal/day', response.data)
        
        # Check global store update
        self.assertEqual(user_info['weight'], 80.0)
        self.assertEqual(user_info['gender'], 'F')
        
    def test_post_user_info_invalid_input(self):
        """Tests handling of non-numeric input for metrics."""
        response = self.post_user_info(age="twenty")
        self.assertEqual(response.status_code, 200)
        self.assertIn(
            b'Invalid input. Age, Height, and Weight must be numbers.',
            response.data
        )
        self.assertTrue(not user_info) # Should be empty
        
    def test_post_user_info_missing_field(self):
        """Tests handling of missing required fields."""
        response = self.post_user_info(name="")
        self.assertIn(b'Please fill in all user information fields.', response.data)
        self.assertTrue(not user_info) # Should be empty
        
# ----------------------------------------------------------------------
## 2. Add Workout Tests (/add)
# ----------------------------------------------------------------------

    def test_add_workout_success(self):
        """Tests successful addition of a workout session."""
        self.set_default_user_info() # CRITICAL: Ensure user info exists
        response = self.post_workout(exercise="Pushups", duration=20, category="Workout")
        self.assertEqual(response.status_code, 200)
        
        # Check flash message (using the bolding syntax)
        self.assertIn(
            b'Added **Pushups** (20 min) to Workout successfully!', 
            response.data
        )
        
        # Check global data store
        self.assertEqual(len(workouts_log["Workout"]), 1)
        
    def test_add_workout_calorie_calculation(self):
        """Tests if calories are calculated (MET=6 for Workout, weight=75kg, duration=10min)."""
        self.set_default_user_info() # CRITICAL: Ensure user info exists
        # Expected: (6 * 3.5 * 75 / 200) * 10 = 78.75
        self.post_workout(exercise="Weights", duration=10, category="Workout")
        
        self.assertAlmostEqual(workouts_log["Workout"][0]["calories"], 78.75, places=2)

    def test_add_workout_missing_fields(self):
        """Tests submission without duration."""
        self.set_default_user_info() # Ensure info exists, but this should still fail validation
        response = self.post_workout(duration="", exercise="Run")
        self.assertIn(b'Please enter both exercise and duration.', response.data)
        self.assertEqual(len(workouts_log["Warm-up"]), 0)

    def test_add_workout_invalid_duration(self):
        """Tests submission with non-positive duration."""
        self.set_default_user_info() # Ensure user info exists
        response_zero = self.post_workout(duration=0)
        self.assertIn(b'Duration must be a positive whole number.', response_zero.data)
        
        self.assertEqual(len(workouts_log["Workout"]), 0)

# ----------------------------------------------------------------------
## 3. Summary Tests (/summary)
# ----------------------------------------------------------------------

    def test_summary_empty(self):
        """Tests summary page when no workouts are logged."""
        response = self.app_client.get('/summary')
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'Total Training Time Logged: <strong>0</strong> minutes', response.data)
        self.assertIn(b'Time to start moving!', response.data)

    def test_summary_with_data_and_calculation(self):
        """Tests total calculation and display of workout details."""
        self.set_default_user_info() # CRITICAL: Ensure user info exists
        self.post_workout(duration=15, category="Warm-up")
        self.post_workout(duration=45, category="Workout")
        
        response = self.app_client.get('/summary')
        
        # Total time should be 15 + 45 = 60 minutes
        self.assertIn(b'Total Training Time Logged: <strong>60</strong> minutes', response.data)
        # FIX: The motivational message for >= 60 min
        self.assertIn(b'Excellent dedication! Keep up the great work.', response.data) 
        
        # Check specific entries are present
        self.assertIn(b'<strong>Running</strong> - 15 min', response.data)
        self.assertIn(b'<strong>Running</strong> - 45 min', response.data) 

    def test_summary_motivation_logic(self):
        """Tests the motivation message thresholds."""
        self.set_default_user_info() # CRITICAL: Ensure user info exists

        # Test Low (e.g., 30 min, should show warning)
        self.post_workout(duration=30)
        response_low = self.app_client.get('/summary')
        self.assertIn(b'alert-warning', response_low.data)
        
        # Test High (e.g., 60 min, should show success)
        self.post_workout(duration=30) # Total 60 min
        response_high = self.app_client.get('/summary')
        self.assertIn(b'alert-success', response_high.data)
        self.assertIn(b'Excellent dedication!', response_high.data)

# ----------------------------------------------------------------------
## 4. Progress Tracker Tests (/progress)
# ----------------------------------------------------------------------

    def test_progress_tracker_no_data(self):
        """Tests progress tracker when no data is available."""
        response = self.app_client.get('/progress')
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'No workout data logged yet.', response.data)

    @patch('matplotlib.figure.Figure.savefig')
    def test_progress_tracker_with_data_generates_chart(self, mock_savefig):
        """Tests that a chart image is generated and embedded."""
        self.set_default_user_info() # CRITICAL: Ensure user info exists
        self.post_workout(duration=10, category="Warm-up")
        self.post_workout(duration=50, category="Workout")
        
        mock_savefig.side_effect = lambda fp, format: fp.write(b"dummy_chart_data")
        
        response = self.app_client.get('/progress')
        self.assertEqual(response.status_code, 200)
        
        mock_savefig.assert_called_once()
        self.assertIn(b'data:image/png;base64', response.data)
