"""Security tests."""

import pytest
from fastapi.testclient import TestClient
from micelio.api.app import create_app
from micelio.core.config import config

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
    # Falls through to JWT which also fails because wrong API key isn't equal to config.api_key and there's no bearer token
    assert res.status_code == 401
    assert "Missing API Key or valid JWT Bearer token" in res.json()["detail"]

def test_jwt_authentication(unauth_client):
    # Get a JWT using the valid master API key
    res_token = unauth_client.post(
        "/api/token", 
        json={"subject": "test-tenant"},
        headers={"X-Mycelium-API-Key": config.api_key}
    )
    assert res_token.status_code == 200
    token = res_token.json()["access_token"]
    
    # Use JWT to create a project
    res_proj = unauth_client.post(
        "/api/projects",
        json={
            "title": "JWT Test",
            "vision": "Vision enough to pass validation",
            "creator_id": "c",
            "distilled_specs": "Specs enough to pass validation",
        },
        headers={"Authorization": f"Bearer {token}"}
    )
    assert res_proj.status_code == 201

def test_invalid_jwt(unauth_client):
    res = unauth_client.post(
        "/api/projects",
        json={
            "title": "JWT Test",
            "vision": "Vision enough to pass validation",
            "creator_id": "c",
            "distilled_specs": "Specs enough to pass validation",
        },
        headers={"Authorization": "Bearer not.a.valid.jwt"}
    )
    assert res.status_code == 403
    assert "Invalid token" in res.json()["detail"]
