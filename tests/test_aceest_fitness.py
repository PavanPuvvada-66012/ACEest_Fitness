import unittest
import os
from src.app import app, WORKOUTS

class FitnessTrackerTests(unittest.TestCase):

    # --- Setup and Teardown ---
    @classmethod
    def setUpClass(cls):
        """Set up Flask app configuration for testing."""
        app.config['TESTING'] = True
        app.config['WTF_CSRF_ENABLED'] = False
        app.config['DEBUG'] = False
        # Create a test client
        cls.client = app.test_client()
        # Ensure templates are found
        cls.runner = app.test_cli_runner()

    def setUp(self):
        """Reset the global WORKOUTS data before each test."""
        for key in WORKOUTS:
            WORKOUTS[key] = []

    # --- Test Cases for Route Access ---
    
    def test_1_home_page_access(self):
        """Tests that the main index page loads successfully."""
        response = self.client.get('/', follow_redirects=True)
        self.assertEqual(response.status_code, 200)
        self.assertIn(b"ACEest Fitness & Gym Tracker", response.data)

    def test_2_summary_page_access_no_data(self):
        """Tests accessing the summary page when no data is logged (should redirect)."""
        response = self.client.get('/summary', follow_redirects=True)
        # Should redirect back to index
        self.assertEqual(response.status_code, 200) 
        # Check for the 'No sessions logged yet!' flash message content
        self.assertIn(b"No sessions logged yet!", response.data)

    # --- Test Cases for Data Submission (POST /add) ---
    
    def test_3_add_valid_workout(self):
        """Tests successful logging of a valid workout session."""
        response = self.client.post(
            '/add',
            data={
                'category': 'Workout',
                'workout': 'Running',
                'duration': '45'
            },
            follow_redirects=True
        )
        self.assertEqual(response.status_code, 200)
        # Verify success flash message appears on index page
        self.assertIn(b"Added Running (45 min) to Workout successfully!", response.data)
        # Verify data is stored globally
        self.assertEqual(len(WORKOUTS['Workout']), 1)
        self.assertEqual(WORKOUTS['Workout'][0]['exercise'], 'Running')

    def test_4_add_invalid_duration_non_numeric(self):
        """Tests input validation for non-numeric duration."""
        response = self.client.post(
            '/add',
            data={
                'category': 'Warm-up',
                'workout': 'Stretching',
                'duration': 'twenty'
            },
            follow_redirects=True
        )
        self.assertEqual(response.status_code, 200)
        self.assertIn(b"Duration must be a valid positive number.", response.data)
        self.assertEqual(len(WORKOUTS['Warm-up']), 0) # Should not be logged

    def test_5_add_invalid_duration_empty(self):
        """Tests input validation for empty duration."""
        response = self.client.post(
            '/add',
            data={
                'category': 'Warm-up',
                'workout': 'Stretching',
                'duration': ''
            },
            follow_redirects=True
        )
        self.assertEqual(response.status_code, 200)
        self.assertIn(b"Please enter both exercise and duration.", response.data)
        
    def test_6_add_invalid_duration_zero(self):
        """Tests input validation for zero duration."""
        response = self.client.post(
            '/add',
            data={
                'category': 'Warm-up',
                'workout': 'Stretching',
                'duration': '0'
            },
            follow_redirects=True
        )
        self.assertEqual(response.status_code, 200)
        self.assertIn(b"Duration must be a valid positive number.", response.data)

    def test_7_add_invalid_workout_empty(self):
        """Tests input validation for empty workout name."""
        response = self.client.post(
            '/add',
            data={
                'category': 'Cool-down',
                'workout': '',
                'duration': '10'
            },
            follow_redirects=True
        )
        self.assertEqual(response.status_code, 200)
        self.assertIn(b"Please enter both exercise and duration.", response.data)

    # --- Test Cases for Summary Logic ---

    def test_8_summary_page_with_data_and_total_time(self):
        """Tests that the summary page displays data and calculates total time correctly."""
        # Log data directly to the global variable for setup
        WORKOUTS['Workout'].append({'exercise': 'Lifting', 'duration': 60, 'timestamp': '2025-11-10 10:00:00'})
        WORKOUTS['Cool-down'].append({'exercise': 'Stretching', 'duration': 15, 'timestamp': '2025-11-10 11:00:00'})
        
        response = self.client.get('/summary')
        self.assertEqual(response.status_code, 200)
        
        # Check for individual entries
        self.assertIn(b"Lifting - 60 min", response.data)
        self.assertIn(b"Stretching - 15 min", response.data)

        # Check for total time (60 + 15 = 75)
        self.assertIn(b"Total Time Spent: 75 minutes", response.data)

    def test_9_summary_page_motivational_message_low(self):
        """Tests the motivational message logic for low total time (< 30 min)."""
        WORKOUTS['Warm-up'].append({'exercise': 'Walk', 'duration': 20, 'timestamp': '...'})
        response = self.client.get('/summary')
        self.assertIn(b"Good start! Keep moving", response.data)

    def test_10_summary_page_motivational_message_medium(self):
        """Tests the motivational message logic for medium total time (30-59 min)."""
        WORKOUTS['Workout'].append({'exercise': 'Cardio', 'duration': 45, 'timestamp': '...'})
        response = self.client.get('/summary')
        self.assertIn(b"Nice effort! You", response.data)

    def test_11_summary_page_motivational_message_high(self):
        """Tests the motivational message logic for high total time (>= 60 min)."""
        WORKOUTS['Workout'].append({'exercise': 'H.I.I.T.', 'duration': 70, 'timestamp': '...'})
        response = self.client.get('/summary')
        self.assertIn(b"Excellent dedication! Keep up the great work", response.data)

if __name__ == '__main__':
    unittest.main()