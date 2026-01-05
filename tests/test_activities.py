import pytest
from fastapi.testclient import TestClient
from src.app import app

client = TestClient(app)

def test_get_activities():
    response = client.get("/activities")
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, dict)
    assert "Chess Club" in data
    assert "Basketball Team" in data

def test_get_activity_details():
    response = client.get("/activities")
    assert response.status_code == 200
    data = response.json()
    chess_club = data["Chess Club"]
    assert "description" in chess_club
    assert "schedule" in chess_club
    assert "max_participants" in chess_club
    assert "participants" in chess_club
    assert isinstance(chess_club["participants"], list)

def test_signup_for_activity():
    # Test successful signup
    response = client.post("/activities/Chess%20Club/signup?email=test@example.com")
    assert response.status_code == 200
    data = response.json()
    assert "message" in data
    assert "test@example.com" in data["message"]

    # Verify the participant was added
    response = client.get("/activities")
    data = response.json()
    assert "test@example.com" in data["Chess Club"]["participants"]

def test_signup_duplicate():
    # Try to sign up the same email again
    response = client.post("/activities/Chess%20Club/signup?email=test@example.com")
    assert response.status_code == 400
    data = response.json()
    assert "detail" in data
    assert "already signed up" in data["detail"]

def test_signup_nonexistent_activity():
    response = client.post("/activities/Nonexistent%20Activity/signup?email=test@example.com")
    assert response.status_code == 404
    data = response.json()
    assert "detail" in data
    assert "Activity not found" in data["detail"]

def test_unregister_from_activity():
    # First sign up
    client.post("/activities/Basketball%20Team/signup?email=unregister@example.com")

    # Then unregister
    response = client.delete("/activities/Basketball%20Team/unregister?email=unregister@example.com")
    assert response.status_code == 200
    data = response.json()
    assert "message" in data
    assert "unregister@example.com" in data["message"]

    # Verify the participant was removed
    response = client.get("/activities")
    data = response.json()
    assert "unregister@example.com" not in data["Basketball Team"]["participants"]

def test_unregister_not_signed_up():
    response = client.delete("/activities/Basketball%20Team/unregister?email=notsignedup@example.com")
    assert response.status_code == 400
    data = response.json()
    assert "detail" in data
    assert "not signed up" in data["detail"]

def test_unregister_nonexistent_activity():
    response = client.delete("/activities/Nonexistent%20Activity/unregister?email=test@example.com")
    assert response.status_code == 404
    data = response.json()
    assert "detail" in data
    assert "Activity not found" in data["detail"]

def test_root_redirect():
    response = client.get("/")
    assert response.status_code == 200
    # FastAPI's RedirectResponse might be handled differently in tests
    # The actual redirect happens, so we check if we get the HTML content
    assert "Mergington High School" in response.text