"""Integration tests for WebSocket streaming in Proyecto Micelio."""

from fastapi.testclient import TestClient
import pytest

from micelio.api.app import create_app
from micelio.domain.models import SynapseEventType


@pytest.fixture
def ws_client(tmp_path) -> TestClient:
    """Fixture providing TestClient with SQLite and isolated workspace."""
    app = create_app(
        workspace_base_dir=tmp_path / "ws_workspaces",
        db_path=tmp_path / "ws_micelio.db",
    )
    from micelio.core.security import verify_api_key
    app.dependency_overrides[verify_api_key] = lambda: "test"
    return TestClient(app)


def test_websocket_office_event_streaming(ws_client: TestClient):
    """Verify real-time event streaming over WebSocket."""
    # 1. Create project
    res = ws_client.post(
        "/api/projects",
        json={
            "title": "WebSocket Stream Test",
            "vision": "Test live events",
            "creator_id": "emp-011",
            "distilled_specs": "Spec",
            "required_skills": ["python"],
        },
    )
    assert res.status_code == 201
    project_id = res.json()["id"]

    # 2. Connect via WebSocket
    with ws_client.websocket_connect(f"/ws/projects/{project_id}/office?agent_id=agt-test") as websocket:
        # 3. Publish an event via HTTP API
        post_res = ws_client.post(
            f"/api/projects/{project_id}/events",
            json={
                "event_type": SynapseEventType.OFFICE_CHATTER.value,
                "source_agent_id": "agt-boss",
                "target_agent_id": "BROADCAST",
                "payload": {"announcement": "Standup virtual iniciado"},
            },
        )
        assert post_res.status_code == 201

        # 4. Receive streamed event over WebSocket
        data = websocket.receive_json()
        assert data["event_type"] == SynapseEventType.OFFICE_CHATTER.value
        assert data["payload"]["announcement"] == "Standup virtual iniciado"
