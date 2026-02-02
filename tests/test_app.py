"""
Tests for the Mergington High School API
"""

import pytest
from fastapi.testclient import TestClient
import sys
from pathlib import Path

# Add src directory to path so we can import app
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from app import app


@pytest.fixture
def client():
    """Create a test client for the FastAPI app"""
    return TestClient(app)


@pytest.fixture
def reset_activities():
    """Reset activities to initial state before each test"""
    from app import activities
    
    initial_state = {
        "Chess Club": {
            "description": "Learn strategies and compete in chess tournaments",
            "schedule": "Fridays, 3:30 PM - 5:00 PM",
            "max_participants": 12,
            "participants": ["michael@mergington.edu", "daniel@mergington.edu"]
        },
        "Programming Class": {
            "description": "Learn programming fundamentals and build software projects",
            "schedule": "Tuesdays and Thursdays, 3:30 PM - 4:30 PM",
            "max_participants": 20,
            "participants": ["emma@mergington.edu", "sophia@mergington.edu"]
        },
        "Gym Class": {
            "description": "Physical education and sports activities",
            "schedule": "Mondays, Wednesdays, Fridays, 2:00 PM - 3:00 PM",
            "max_participants": 30,
            "participants": ["john@mergington.edu", "olivia@mergington.edu"]
        },
        "Basketball Team": {
            "description": "Competitive basketball team for intramural and inter-school games",
            "schedule": "Mondays and Wednesdays, 4:00 PM - 5:30 PM",
            "max_participants": 15,
            "participants": ["james@mergington.edu"]
        },
        "Tennis Club": {
            "description": "Learn tennis skills and participate in friendly matches",
            "schedule": "Saturdays, 10:00 AM - 11:30 AM",
            "max_participants": 16,
            "participants": ["sophia@mergington.edu", "lucas@mergington.edu"]
        },
        "Art Studio": {
            "description": "Explore painting, drawing, and sculpture techniques",
            "schedule": "Tuesdays and Thursdays, 4:30 PM - 6:00 PM",
            "max_participants": 18,
            "participants": ["isabella@mergington.edu"]
        },
        "Music Ensemble": {
            "description": "Join the school orchestra and perform at concerts",
            "schedule": "Wednesdays, 3:30 PM - 5:00 PM",
            "max_participants": 25,
            "participants": ["noah@mergington.edu", "ava@mergington.edu"]
        },
        "Debate Team": {
            "description": "Develop critical thinking and public speaking skills",
            "schedule": "Mondays and Thursdays, 3:30 PM - 4:30 PM",
            "max_participants": 14,
            "participants": ["charlotte@mergington.edu"]
        },
        "Science Club": {
            "description": "Conduct experiments and explore scientific concepts",
            "schedule": "Fridays, 3:30 PM - 5:00 PM",
            "max_participants": 20,
            "participants": ["alexander@mergington.edu", "mia@mergington.edu"]
        }
    }
    
    # Clear and reset
    activities.clear()
    activities.update(initial_state)
    
    yield
    
    # Cleanup after test
    activities.clear()
    activities.update(initial_state)


class TestGetActivities:
    """Tests for the /activities endpoint"""

    def test_get_activities(self, client, reset_activities):
        """Test retrieving all activities"""
        response = client.get("/activities")
        assert response.status_code == 200
        data = response.json()
        
        # Check that all activities are returned
        assert "Chess Club" in data
        assert "Programming Class" in data
        assert len(data) == 9
        
    def test_activity_structure(self, client, reset_activities):
        """Test that activities have correct structure"""
        response = client.get("/activities")
        data = response.json()
        
        activity = data["Chess Club"]
        assert "description" in activity
        assert "schedule" in activity
        assert "max_participants" in activity
        assert "participants" in activity
        
    def test_participants_list(self, client, reset_activities):
        """Test that participants are correctly returned"""
        response = client.get("/activities")
        data = response.json()
        
        assert "michael@mergington.edu" in data["Chess Club"]["participants"]
        assert "daniel@mergington.edu" in data["Chess Club"]["participants"]


class TestSignupForActivity:
    """Tests for the /activities/{activity_name}/signup endpoint"""

    def test_signup_success(self, client, reset_activities):
        """Test successful signup"""
        response = client.post(
            "/activities/Chess%20Club/signup",
            params={"email": "newemail@mergington.edu"}
        )
        assert response.status_code == 200
        assert "Signed up" in response.json()["message"]
        
    def test_signup_adds_participant(self, client, reset_activities):
        """Test that signup actually adds the participant"""
        email = "test@mergington.edu"
        
        # Signup
        client.post(
            "/activities/Programming%20Class/signup",
            params={"email": email}
        )
        
        # Verify participant was added
        response = client.get("/activities")
        data = response.json()
        assert email in data["Programming Class"]["participants"]
        
    def test_signup_duplicate_email(self, client, reset_activities):
        """Test that signup fails for duplicate email"""
        response = client.post(
            "/activities/Chess%20Club/signup",
            params={"email": "michael@mergington.edu"}
        )
        assert response.status_code == 400
        assert "already signed up" in response.json()["detail"]
        
    def test_signup_invalid_activity(self, client, reset_activities):
        """Test that signup fails for non-existent activity"""
        response = client.post(
            "/activities/Invalid%20Activity/signup",
            params={"email": "test@mergington.edu"}
        )
        assert response.status_code == 404
        assert "Activity not found" in response.json()["detail"]
        
    def test_signup_multiple_participants(self, client, reset_activities):
        """Test signing up multiple participants"""
        emails = ["alice@mergington.edu", "bob@mergington.edu", "charlie@mergington.edu"]
        
        for email in emails:
            response = client.post(
                "/activities/Art%20Studio/signup",
                params={"email": email}
            )
            assert response.status_code == 200
        
        # Verify all were added
        response = client.get("/activities")
        data = response.json()
        for email in emails:
            assert email in data["Art Studio"]["participants"]


class TestRootEndpoint:
    """Tests for the root endpoint"""

    def test_root_redirect(self, client):
        """Test that root redirects to static index.html"""
        response = client.get("/", follow_redirects=False)
        assert response.status_code == 307
        assert "/static/index.html" in response.headers["location"]
