# src/tracker.py
"""
Core logic module for tracking workouts.

Contains the WorkoutTracker class which manages workouts independently
of any GUI or web interface.
"""
class WorkoutTracker:
    """
    Core logic for tracking workouts (separated from GUI).
    """

    def __init__(self):
        """
        Initialize a new WorkoutTracker instance with an empty workouts list.
        """
        self.workouts = []

    def add_workout(self, workout: str, duration: int) -> dict:
        """
        Add a workout to the tracker.

        Args:
            workout (str): Name of the workout activity.
            duration (int): Duration of the workout in minutes.

        Returns:
            dict: The workout entry added to the tracker.

        Raises:
            ValueError: If workout or duration is missing or duration is not an integer.
        """
        if not workout or duration is None:
            raise ValueError("Workout and duration are required")

        if not isinstance(duration, int):
            raise ValueError("Duration must be an integer")

        entry = {"workout": workout, "duration": duration}
        self.workouts.append(entry)
        return entry

    def get_workouts(self):
        """
        Retrieve all logged workouts.

        Returns:
            list: List of all workout entries.
        """
        return self.workouts
