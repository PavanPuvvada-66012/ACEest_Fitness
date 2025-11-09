"""Doc String PlaceHolder"""
import unittest
from src.app import app, workouts_log
"""Doc String PlaceHolder"""


class FitnessTrackerTests(unittest.TestCase):

    def setUp(self):
        """Set up a test client and clear the data before each test."""
        self.app = app.test_client()
        self.app.testing = True
        # Clear the in-memory log for a clean start on every test
        workouts_log.clear()

    # --- Utility function for posting workout data ---
    def post_workout(self, exercise="Running", duration=30, category="Workout"):
        return self.app.post(
            '/add',
            data={
                'exercise': exercise,
                'duration': duration,
                'category': category
            },
            follow_redirects=True
        )
    def test_add_session_success(self):
        """Tests successful addition of a workout session."""
        response = self.post_workout(exercise="Squats", duration=20, category="Workout")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(workouts_log), 1)
        self.assertIn(b'Added Squats (20 min) to Workout successfully!', response.data)
    def test_add_session_missing_fields(self):
        """Tests submission without an exercise name."""
        response = self.post_workout(exercise="", duration=15)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(workouts_log), 0)
        self.assertIn(b'Please enter both exercise and duration.', response.data)

    def test_add_session_invalid_duration(self):
        """Tests submission with non-numeric duration."""
        response = self.app.post('/add', data={'exercise': 'Run', 'duration': 'ten', 'category': 'Workout'}, follow_redirects=True)
        self.assertEqual(len(workouts_log), 0)
        self.assertIn(b'Duration must be a positive number.', response.data)
        
    def test_add_session_zero_duration(self):
        """Tests submission with zero duration."""
        response = self.post_workout(exercise="Walk", duration=0)
        self.assertEqual(len(workouts_log), 0)
        self.assertIn(b'Duration must be a positive number.', response.data)
    def test_summary_empty(self):
        """Tests the summary page when no workouts have been logged."""
        response = self.app.get('/summary')
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'Total Time Spent: 0 minutes', response.data)
        self.assertIn(b'Good start! Keep moving', response.data)
        self.assertIn(b'No sessions recorded.', response.data)

    def test_summary_calculation(self):
        """Tests if total time is calculated correctly."""
        self.post_workout(exercise="Run", duration=15)
        self.post_workout(exercise="Weights", duration=45)
        
        response = self.app.get('/summary')
        self.assertIn(b'Excellent dedication! Keep up the great work', response.data)
        self.assertIn(b'Total Time Spent: 60 minutes', response.data)

    def test_summary_categorization(self):
        """Tests if workouts are displayed under the correct categories."""
        self.post_workout(exercise="Stretching", duration=5, category="Warm-up")
        self.post_workout(exercise="Lifting", duration=40, category="Workout")
        
        response = self.app.get('/summary')
        self.assertIn(b'Stretching - 5 min', response.data)
        self.assertIn(b'Lifting - 40 min', response.data)

    def test_summary_motivation_high_time(self):
        """Tests for the high dedication message (>= 60 min)."""
        self.post_workout(duration=30)
        self.post_workout(duration=40)
        response = self.app.get('/summary')
        self.assertIn(b'Excellent dedication! Keep up the great work', response.data)
    def test_workout_chart_content(self):
        """Tests if the workout chart page renders with expected content."""
        response = self.app.get('/chart')
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'Personalized Workout Chart', response.data)
        # Check for a specific exercise from the static data
        self.assertIn(b'Push-ups', response.data) 
        self.assertIn(b'Dynamic Stretching', response.data)

    def test_diet_chart_content(self):
        """Tests if the diet chart page renders with expected content."""
        response = self.app.get('/diet')
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'Best Diet Chart for Fitness Goals', response.data)
        # Check for a specific diet item from the static data
        self.assertIn(b'Oatmeal with Fruits', response.data)
        self.assertIn(b'Muscle Gain Plan:', response.data)

    def test_navigation_links(self):
        """Tests if navigation links are present on the layout."""
        response = self.app.get('/')
        self.assertIn(b'href="/chart"', response.data)
        self.assertIn(b'href="/diet"', response.data)
if __name__ == '__main__':
    unittest.main()
