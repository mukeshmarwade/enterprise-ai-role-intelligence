import os
import sys
import tempfile

# Use an isolated temp DB for tests so we don't touch the dev DB
os.environ["DATABASE_URL"] = f"sqlite:///{tempfile.mktemp(suffix='.db')}"

from fastapi.testclient import TestClient
from backend.main import app

# Use as a context manager so FastAPI's startup event (DB create + seed) actually runs
client = TestClient(app)
client.__enter__()


def test_health():
    res = client.get("/api/health")
    assert res.status_code == 200
    assert res.json() == {"status": "ok"}


def test_list_roles_returns_24():
    res = client.get("/api/roles")
    assert res.status_code == 200
    data = res.json()
    assert len(data) == 24


def test_get_role_detail():
    roles = client.get("/api/roles").json()
    role_id = roles[0]["id"]
    res = client.get(f"/api/roles/{role_id}")
    assert res.status_code == 200
    detail = res.json()
    assert "activities" in detail
    assert "reason_codes" in detail


def test_get_role_404():
    res = client.get("/api/roles/9999")
    assert res.status_code == 404


def test_compare_roles():
    res = client.get("/api/compare?role_a=Finance Analyst&role_b=Procurement Analyst")
    assert res.status_code == 200
    data = res.json()
    assert data["role_a"]["title"] == "Finance Analyst"
    assert data["role_b"]["title"] == "Procurement Analyst"
    assert "narrative" in data


def test_compare_unknown_role_404():
    res = client.get("/api/compare?role_a=Nonexistent Role&role_b=Finance Analyst")
    assert res.status_code == 404


def test_ranking():
    res = client.get("/api/rank?n=5")
    assert res.status_code == 200
    data = res.json()
    assert len(data["top_roles"]) == 5
    scores = [r["change_score"] for r in data["top_roles"]]
    assert scores == sorted(scores, reverse=True)
