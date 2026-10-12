import copy

import pytest
from fastapi.testclient import TestClient

from src.app import activities, app


@pytest.fixture(autouse=True)
def reset_activities():
    original_activities = copy.deepcopy(activities)
    yield
    activities.clear()
    activities.update(original_activities)


client = TestClient(app)


def test_get_activities_returns_activity_list():
    # Arrange
    expected_activity_names = {"Chess Club", "Programming Class", "Gym Class", "Basketball Team"}

    # Act
    response = client.get("/activities")

    # Assert
    assert response.status_code == 200
    payload = response.json()
    assert set(payload) == expected_activity_names
    assert payload["Chess Club"]["participants"] == ["michael@mergington.edu", "daniel@mergington.edu"]


def test_signup_for_activity_adds_student_and_returns_success_message():
    # Arrange
    email = "newstudent@mergington.edu"

    # Act
    response = client.post(f"/activities/Chess Club/signup?email={email}")

    # Assert
    assert response.status_code == 200
    assert response.json() == {"message": f"Signed up {email} for Chess Club"}
    assert email in activities["Chess Club"]["participants"]


def test_signup_for_missing_activity_returns_404():
    # Arrange
    email = "student@mergington.edu"

    # Act
    response = client.post(f"/activities/Unknown Club/signup?email={email}")

    # Assert
    assert response.status_code == 404
    assert response.json() == {"detail": "Activity not found"}


def test_duplicate_signup_returns_400():
    # Arrange
    email = "michael@mergington.edu"

    # Act
    response = client.post(f"/activities/Chess Club/signup?email={email}")

    # Assert
    assert response.status_code == 400
    assert response.json() == {"detail": "Student already signed up for this activity"}


def test_unregister_from_activity_removes_student():
    # Arrange
    email = "daniel@mergington.edu"

    # Act
    response = client.delete(f"/activities/Chess Club/signup?email={email}")

    # Assert
    assert response.status_code == 200
    assert response.json() == {"message": f"Unregistered {email} from Chess Club"}
    assert email not in activities["Chess Club"]["participants"]
