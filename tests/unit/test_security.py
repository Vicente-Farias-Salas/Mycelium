"""Security tests."""

import pytest
from fastapi.testclient import TestClient
from micelio.api.app import create_app

@pytest.fixture
def unauth_client(tmp_path):
    app = create_app(workspace_base_dir=tmp_path / "workspaces", db_path=tmp_path / "sec.db")
    return TestClient(app)

def test_api_key_required_for_project_creation(unauth_client):
    res = unauth_client.post(
        "/api/projects",
        json={
            "title": "Sec Test",
            "vision": "Vision enough to pass validation",
            "creator_id": "c",
            "distilled_specs": "Specs enough to pass validation",
        },
    )
    assert res.status_code == 401

def test_api_key_invalid(unauth_client):
    res = unauth_client.post(
        "/api/projects",
        json={
            "title": "Sec Test",
            "vision": "Vision enough to pass validation",
            "creator_id": "c",
            "distilled_specs": "Specs enough to pass validation",
        },
        headers={"X-Mycelium-API-Key": "wrong_key"}
    )
    assert res.status_code == 403
