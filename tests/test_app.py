from copy import deepcopy

import pytest
from fastapi.testclient import TestClient

from src.app import activities, app


@pytest.fixture
def client():
    original_activities = deepcopy(activities)
    with TestClient(app) as test_client:
        yield test_client
    activities.clear()
    activities.update(original_activities)


def test_root_redirects_to_frontend(client):
    response = client.get("/", follow_redirects=False)

    assert response.status_code == 307
    assert response.headers["location"] == "/static/index.html"


def test_get_activities_returns_available_activities(client):
    response = client.get("/activities")

    assert response.status_code == 200
    assert "Chess Club" in response.json()


def test_signup_adds_participant(client):
    response = client.post(
        "/activities/Basketball Club/signup",
        params={"email": "student@mergington.edu"},
    )

    assert response.status_code == 200
    assert response.json() == {
        "message": "Signed up student@mergington.edu for Basketball Club"
    }
    assert "student@mergington.edu" in activities["Basketball Club"]["participants"]


def test_signup_rejects_duplicate_participant(client):
    response = client.post(
        "/activities/Chess Club/signup",
        params={"email": "michael@mergington.edu"},
    )

    assert response.status_code == 400
    assert response.json()["detail"] == "Student already signed up for this activity"


def test_signup_rejects_unknown_or_full_activity(client):
    unknown_response = client.post(
        "/activities/Unknown Club/signup",
        params={"email": "student@mergington.edu"},
    )

    activities["Basketball Club"]["participants"] = [
        f"student{number}@mergington.edu"
        for number in range(activities["Basketball Club"]["max_participants"])
    ]
    full_response = client.post(
        "/activities/Basketball Club/signup",
        params={"email": "newstudent@mergington.edu"},
    )

    assert unknown_response.status_code == 404
    assert unknown_response.json()["detail"] == "Activity not found"
    assert full_response.status_code == 400
    assert full_response.json()["detail"] == "Activity is full"


def test_unregister_removes_participant(client):
    response = client.delete(
        "/activities/Chess Club/participants/michael@mergington.edu"
    )

    assert response.status_code == 200
    assert response.json() == {
        "message": "Unregistered michael@mergington.edu from Chess Club"
    }
    assert "michael@mergington.edu" not in activities["Chess Club"]["participants"]


def test_unregister_rejects_unknown_activity_or_participant(client):
    unknown_response = client.delete(
        "/activities/Unknown Club/participants/student@mergington.edu"
    )
    missing_response = client.delete(
        "/activities/Chess Club/participants/missing@mergington.edu"
    )

    assert unknown_response.status_code == 404
    assert unknown_response.json()["detail"] == "Activity not found"
    assert missing_response.status_code == 404
    assert missing_response.json()["detail"] == "Participant not found"
