"""
Pytest module for testing the Flask-based ACEest Fitness Tracker app.
Contains tests for adding, viewing, and validating workouts.
"""

# pylint: disable=redefined-outer-name

import pytest
from src.app import app,tracker

@pytest.fixture
def client():
    """Provides a test client for the Flask app"""
    app.config["TESTING"] = True
    tracker.workouts.clear()
    with app.test_client() as test_client:
        yield test_client

def test_homepage_loads(client):
    """Homepage should load and contain expected text"""
    response = client.get("/")
    assert response.status_code == 200
    assert b"Workout Tracker" in response.data

def test_add_valid_workout(client):
    """Should add a workout successfully via POST"""
    response = client.post("/add", json={"workout": "Running", "duration": 30})
    data = response.get_json()
    assert response.status_code == 201
    assert data["status"] == "success"
    assert data["workout"] == {"workout": "Running", "duration": 30}

def test_add_invalid_workout(client):
    """Adding invalid workout (non-numeric duration) should fail"""
    response = client.post("/add", json={"workout": "Cycling", "duration": "abc"})
    data = response.get_json()
    assert response.status_code == 400
    assert data["status"] == "error"
    assert "invalid literal for int()" in data["message"]

def test_view_workouts_empty(client):
    """Should return empty list if no workouts logged"""
    response = client.get("/workouts")
    data = response.get_json()
    assert response.status_code == 200
    assert data == []

def test_view_workouts_with_data(client):
    """Should return workouts if added previously"""
    # Add one workout
    client.post("/add", json={"workout": "Yoga", "duration": 45})
    response = client.get("/workouts")
    data = response.get_json()
    assert response.status_code == 200
    assert len(data) == 1
    assert data[0]["workout"] == "Yoga"
    assert data[0]["duration"] == 45
