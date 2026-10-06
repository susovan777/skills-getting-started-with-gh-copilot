import pytest
from fastapi.testclient import TestClient

import src.app as app_module


@pytest.fixture
def test_activities(monkeypatch):
    activities = {
        "Chess Club": {
            "description": "Learn chess strategies",
            "schedule": "Fridays, 3:30 PM",
            "max_participants": 3,
            "participants": ["alex@example.edu", "sam@example.edu"],
        }
    }
    monkeypatch.setattr(app_module, "activities", activities)
    return activities


@pytest.fixture
def client():
    with TestClient(app_module.app) as test_client:
        yield test_client


def test_get_activities_returns_available_activities(client, test_activities):
    # Arrange
    expected_activities = test_activities

    # Act
    response = client.get("/activities")

    # Assert
    assert response.status_code == 200
    assert response.json() == expected_activities


def test_signup_adds_participant(client, test_activities):
    # Arrange
    activity_name = "Chess Club"
    email = "taylor@example.edu"

    # Act
    response = client.post(
        f"/activities/{activity_name.replace(' ', '%20')}/signup",
        params={"email": email},
    )

    # Assert
    assert response.status_code == 200
    assert response.json() == {"message": f"Signed up {email} for {activity_name}"}
    assert email in test_activities[activity_name]["participants"]


def test_signup_rejects_duplicate_participant(client, test_activities):
    # Arrange
    activity_name = "Chess Club"
    email = test_activities[activity_name]["participants"][0]
    original_participants = test_activities[activity_name]["participants"].copy()

    # Act
    response = client.post(
        f"/activities/{activity_name.replace(' ', '%20')}/signup",
        params={"email": email},
    )

    # Assert
    assert response.status_code == 400
    assert response.json()["detail"] == "Student already signed up for this activity"
    assert test_activities[activity_name]["participants"] == original_participants


def test_signup_rejects_unknown_activity(client):
    # Arrange
    activity_name = "Robotics Club"

    # Act
    response = client.post(
        f"/activities/{activity_name.replace(' ', '%20')}/signup",
        params={"email": "taylor@example.edu"},
    )

    # Assert
    assert response.status_code == 404
    assert response.json()["detail"] == "Activity not found"


def test_unregister_removes_participant_and_preserves_others(
    client, test_activities
):
    # Arrange
    activity_name = "Chess Club"
    email = "alex@example.edu"
    remaining_participants = ["sam@example.edu"]

    # Act
    response = client.delete(
        f"/activities/{activity_name.replace(' ', '%20')}/participants",
        params={"email": email},
    )

    # Assert
    assert response.status_code == 200
    assert response.json() == {"message": f"Unregistered {email} from {activity_name}"}
    assert test_activities[activity_name]["participants"] == remaining_participants


def test_unregister_rejects_nonparticipant(client, test_activities):
    # Arrange
    activity_name = "Chess Club"
    email = "taylor@example.edu"
    original_participants = test_activities[activity_name]["participants"].copy()

    # Act
    response = client.delete(
        f"/activities/{activity_name.replace(' ', '%20')}/participants",
        params={"email": email},
    )

    # Assert
    assert response.status_code == 404
    assert response.json()["detail"] == "Student is not signed up for this activity"
    assert test_activities[activity_name]["participants"] == original_participants


def test_unregister_rejects_unknown_activity(client):
    # Arrange
    activity_name = "Robotics Club"

    # Act
    response = client.delete(
        f"/activities/{activity_name.replace(' ', '%20')}/participants",
        params={"email": "taylor@example.edu"},
    )

    # Assert
    assert response.status_code == 404
    assert response.json()["detail"] == "Activity not found"