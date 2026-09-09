"""Billing and tenant tests."""

import pytest
from fastapi.testclient import TestClient
from micelio.api.app import create_app
from micelio.core.security import verify_api_key

@pytest.fixture
def client(tmp_path):
    ws_dir = tmp_path / "workspaces"
    ws_dir.mkdir()
    app = create_app(workspace_base_dir=ws_dir, db_path=tmp_path / "billing.db")
    app.dependency_overrides[verify_api_key] = lambda: "test"
    return TestClient(app)

def test_tenant_quota_exceeded(client: TestClient):
    # Register a tiny tenant with 0 quota
    res = client.post("/api/tenants", json={
        "tenant_id": "tiny-tenant",
        "name": "Tiny",
        "tier": "STARTER",
        "max_active_projects": 0
    })
    assert res.status_code == 201

    # Try creating a project for that tenant
    res2 = client.post("/api/projects", json={
        "title": "Should Fail",
        "vision": "Vision enough to pass validation",
        "creator_id": "mem-1",
        "distilled_specs": "Specs enough to pass validation",
        "tenant_id": "tiny-tenant"
    })
    assert res2.status_code == 402
    assert "Payment Required" in res2.json()["detail"]
