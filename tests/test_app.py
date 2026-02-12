import pytest
from fastapi.testclient import TestClient
import copy

from src.app import app, activities


client = TestClient(app)


@pytest.fixture(autouse=True)
def reset_activities():
    # snapshot and restore activities before each test to avoid cross-test mutation
    original = copy.deepcopy(activities)
    yield
    activities.clear()
    activities.update(original)


def test_get_activities():
    res = client.get("/activities")
    assert res.status_code == 200
    data = res.json()
    assert isinstance(data, dict)
    # some known activity from seeded data
    assert "Chess Club" in data


def test_signup_and_prevent_duplicate():
    email = "tester@mergington.edu"
    activity = "Chess Club"

    # first signup should succeed
    res = client.post(f"/activities/{activity}/signup?email={email}")
    assert res.status_code == 200
    assert f"Signed up {email}" in res.json().get("message", "")

    # second signup should be rejected
    res2 = client.post(f"/activities/{activity}/signup?email={email}")
    assert res2.status_code == 400
    assert "already" in res2.json().get("detail", "").lower()


def test_remove_participant():
    # michael@mergington.edu is present in seeded Chess Club
    email = "michael@mergington.edu"
    activity = "Chess Club"

    # ensure present initially
    res = client.get("/activities")
    assert email in res.json()[activity]["participants"]

    # remove participant
    res2 = client.delete(f"/activities/{activity}/participants?email={email}")
    assert res2.status_code == 200
    assert f"Removed {email}" in res2.json().get("message", "")

    # now should be absent
    res3 = client.get("/activities")
    assert email not in res3.json()[activity]["participants"]
