"""Tests for the FastAPI application"""

import pytest
from fastapi.testclient import TestClient
import sys
from pathlib import Path

# Add src directory to path so we can import app
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from app import app

# Create a test client
client = TestClient(app)


class TestActivities:
    """Test cases for activities endpoints"""

    def test_get_activities(self):
        """Test retrieving all activities"""
        response = client.get("/activities")
        assert response.status_code == 200
        activities = response.json()
        assert isinstance(activities, dict)
        assert "Chess Club" in activities
        assert "Programming Class" in activities
        assert len(activities) > 0

    def test_get_activities_structure(self):
        """Test that activities have the correct structure"""
        response = client.get("/activities")
        activities = response.json()
        
        for activity_name, activity in activities.items():
            assert "description" in activity
            assert "schedule" in activity
            assert "max_participants" in activity
            assert "participants" in activity
            assert isinstance(activity["participants"], list)


class TestSignup:
    """Test cases for signup endpoints"""

    def test_signup_success(self):
        """Test successful signup"""
        response = client.post(
            "/activities/Chess%20Club/signup?email=newstudent@mergington.edu"
        )
        assert response.status_code == 200
        data = response.json()
        assert "message" in data
        assert "newstudent@mergington.edu" in data["message"]
        assert "Chess Club" in data["message"]

    def test_signup_nonexistent_activity(self):
        """Test signup for non-existent activity"""
        response = client.post(
            "/activities/Nonexistent%20Activity/signup?email=student@mergington.edu"
        )
        assert response.status_code == 404
        data = response.json()
        assert data["detail"] == "Activity not found"

    def test_signup_already_registered(self):
        """Test signup when already registered"""
        # michael@mergington.edu is already in Chess Club
        response = client.post(
            "/activities/Chess%20Club/signup?email=michael@mergington.edu"
        )
        assert response.status_code == 400
        data = response.json()
        assert "already signed up" in data["detail"]

    def test_signup_multiple_students(self):
        """Test multiple students signing up for same activity"""
        # First signup
        response1 = client.post(
            "/activities/Art%20Studio/signup?email=student1@mergington.edu"
        )
        assert response1.status_code == 200
        
        # Second signup
        response2 = client.post(
            "/activities/Art%20Studio/signup?email=student2@mergington.edu"
        )
        assert response2.status_code == 200
        
        # Verify both are signed up
        response_get = client.get("/activities")
        activities = response_get.json()
        assert "student1@mergington.edu" in activities["Art Studio"]["participants"]
        assert "student2@mergington.edu" in activities["Art Studio"]["participants"]


class TestUnregister:
    """Test cases for unregister endpoints"""

    def test_unregister_success(self):
        """Test successful unregistration"""
        # First, sign up
        client.post("/activities/Music%20Ensemble/signup?email=testuser@mergington.edu")
        
        # Then unregister
        response = client.post(
            "/activities/Music%20Ensemble/unregister?email=testuser@mergington.edu"
        )
        assert response.status_code == 200
        data = response.json()
        assert "Unregistered" in data["message"]
        assert "testuser@mergington.edu" in data["message"]

    def test_unregister_not_registered(self):
        """Test unregistering when not registered"""
        response = client.post(
            "/activities/Debate%20Team/unregister?email=notregistered@mergington.edu"
        )
        assert response.status_code == 400
        data = response.json()
        assert "not registered" in data["detail"]

    def test_unregister_nonexistent_activity(self):
        """Test unregistering from non-existent activity"""
        response = client.post(
            "/activities/Fake%20Activity/unregister?email=student@mergington.edu"
        )
        assert response.status_code == 404
        data = response.json()
        assert data["detail"] == "Activity not found"

    def test_unregister_removes_participant(self):
        """Test that unregister removes participant from activity"""
        email = "unregister_test@mergington.edu"
        
        # Sign up
        client.post(f"/activities/Science%20Club/signup?email={email}")
        
        # Verify signed up
        response_before = client.get("/activities")
        assert email in response_before.json()["Science Club"]["participants"]
        
        # Unregister
        client.post(f"/activities/Science%20Club/unregister?email={email}")
        
        # Verify not signed up
        response_after = client.get("/activities")
        assert email not in response_after.json()["Science Club"]["participants"]
