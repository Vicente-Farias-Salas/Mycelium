"""Contract Validator Tests."""

import pytest
from fastapi.testclient import TestClient
from micelio.api.app import create_app
from micelio.core.security import verify_api_key

@pytest.fixture
def client(tmp_path):
    ws_dir = tmp_path / "workspaces"
    ws_dir.mkdir()
    app = create_app(workspace_base_dir=ws_dir, db_path=tmp_path / "contract.db")
    app.dependency_overrides[verify_api_key] = lambda: "test"
    return TestClient(app)

def test_contract_validation_enforcement(client: TestClient):
    schema = {
        "type": "object",
        "properties": {
            "key": {"type": "string"}
        },
        "required": ["key"]
    }
    
    proj = client.post("/api/projects", json={
        "title": "Contract Project",
        "vision": "Vision enough to pass validation",
        "creator_id": "c1",
        "distilled_specs": "Specs enough to pass validation",
        "shared_contracts": {
            "STATE_MUTATION": schema
        }
    })
    
    pid = proj.json()["id"]

    # Should fail due to missing "key" in payload
    res1 = client.post(f"/api/projects/{pid}/events", json={
        "event_type": "STATE_MUTATION",
        "source_agent_id": "agent-1",
        "payload": {"wrong": 123}
    })
    assert res1.status_code == 400
    assert "violated contract" in res1.json()["detail"]

    # Should succeed with correct payload
    res2 = client.post(f"/api/projects/{pid}/events", json={
        "event_type": "STATE_MUTATION",
        "source_agent_id": "agent-1",
        "payload": {"key": "value"}
    })
    assert res2.status_code == 201

    # Should ignore validation for other event types without contracts
    res3 = client.post(f"/api/projects/{pid}/events", json={
        "event_type": "AGENT_QUERY",
        "source_agent_id": "agent-1",
        "payload": {"anything": "goes"}
    })
    assert res3.status_code == 201
