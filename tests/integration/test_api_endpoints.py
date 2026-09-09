"""Integration tests for FastAPI REST & WebSocket endpoints in Proyecto Micelio."""

from fastapi.testclient import TestClient
import pytest

from micelio.api.app import create_app
from micelio.domain.models import DepartmentEnum, ProjectStatus
from micelio.core.security import verify_api_key


@pytest.fixture
def client(tmp_path) -> TestClient:
    """Fixture providing test client configured with a temporary workspace."""
    ws_dir = tmp_path / "workspaces"
    ws_dir.mkdir()
    app = create_app(workspace_base_dir=ws_dir, db_path=tmp_path / "micelio.db")
    app.dependency_overrides[verify_api_key] = lambda: "test"
    return TestClient(app)


def test_create_project_flow(client: TestClient):
    """Verify creating a project via API."""
    payload = {
        "title": "Sistema de Detección de Anomalías",
        "vision": "Analizar telemetría IoT en tiempo real",
        "creator_id": "mem-boss",
        "distilled_specs": "Pipeline con Kafka y PySpark",
        "shared_contracts": {"input": "telemetry_v1"},
        "required_skills": ["python", "iot", "data_pipelines"],
        "target_department": "DATA",
    }
    response = client.post("/api/projects", json=payload)
    assert response.status_code == 201
    data = response.json()
    assert data["title"] == "Sistema de Detección de Anomalías"
    assert data["status"] == ProjectStatus.DRAFT.value
    assert "id" in data


def test_team_recommendation_flow(client: TestClient):
    """Verify recommendation endpoint suggests team members."""
    # 1. Create project
    proj_res = client.post(
        "/api/projects",
        json={
            "title": "Pipeline de Métricas",
            "vision": "Dashboard de métricas financieras",
            "creator_id": "mem-boss",
            "distilled_specs": "FastAPI + ClickHouse",
            "required_skills": ["python", "data_pipelines"],
            "target_department": "DATA",
        },
    )
    project_id = proj_res.json()["id"]

    # 2. Query team recommendations
    rec_res = client.get(f"/api/projects/{project_id}/recommend-team")
    assert rec_res.status_code == 200
    recommendations = rec_res.json()
    assert len(recommendations) > 0
    assert "member" in recommendations[0]
    assert "score" in recommendations[0]


def test_dispatch_and_accept_invite_flow(client: TestClient):
    """Verify dispatching invite, accepting, and triggering local folder bootstrap."""
    # 1. Create project
    proj_res = client.post(
        "/api/projects",
        json={
            "title": "App Colaborativa",
            "vision": "Frontend en React y backend en FastAPI",
            "creator_id": "mem-boss",
            "distilled_specs": "Diseño con UI-Craft",
            "required_skills": ["react", "typescript"],
            "target_department": "ENGINEERING",
        },
    )
    project_id = proj_res.json()["id"]

    # 2. Dispatch invitation to a member
    dispatch_res = client.post(
        f"/api/projects/{project_id}/dispatch",
        json={"member_id": "mem-dev", "role": "Frontend Architect"},
    )
    assert dispatch_res.status_code == 200
    membership = dispatch_res.json()
    membership_id = membership["id"]
    assert membership["status"] == "INVITED"

    # 3. Accept invitation
    accept_res = client.post(
        f"/api/invites/{membership_id}/respond",
        json={"action": "accept", "project_slug": "app_colaborativa_dev"},
    )
    assert accept_res.status_code == 200
    accepted_data = accept_res.json()
    assert accepted_data["status"] == "JOINED"
    assert "proyectos" in accepted_data["local_workspace_path"] or "app_colaborativa" in accepted_data["local_workspace_path"]


def test_synapse_office_event_flow(client: TestClient):
    """Verify publishing and retrieving Synapse events in the Virtual Office."""
    # 1. Create project
    proj_res = client.post(
        "/api/projects",
        json={
            "title": "Office Test",
            "vision": "A2A Office chatter",
            "creator_id": "mem-boss",
            "distilled_specs": "Spec enough to pass validation",
            "required_skills": ["python"],
        },
    )
    project_id = proj_res.json()["id"]

    # 2. Publish event
    event_payload = {
        "event_type": "AGENT_QUERY",
        "source_agent_id": "agt-data",
        "target_agent_id": "agt-backend",
        "payload": {"question": "¿El schema soporta streaming?"},
    }
    event_res = client.post(f"/api/projects/{project_id}/events", json=event_payload)
    assert event_res.status_code == 201

    # 3. Retrieve history
    history_res = client.get(f"/api/projects/{project_id}/events")
    assert history_res.status_code == 200
    history = history_res.json()
    assert len(history) == 1
    assert history[0]["event_type"] == "AGENT_QUERY"
    assert history[0]["payload"]["question"] == "¿El schema soporta streaming?"

def test_rate_limit_office_event(client: TestClient):
    """Verify rate limiter blocks >20 events per second."""
    proj_res = client.post(
        "/api/projects",
        json={
            "title": "Rate Limit Test",
            "vision": "Check 429",
            "creator_id": "mem-boss",
            "distilled_specs": "Spec enough to pass validation",
            "required_skills": ["python"],
        },
    )
    project_id = proj_res.json()["id"]

    event_payload = {
        "event_type": "AGENT_QUERY",
        "source_agent_id": "agt-spammer",
        "target_agent_id": "agt-backend",
        "payload": {},
    }
    
    # 20 allowed
    for _ in range(20):
        client.post(f"/api/projects/{project_id}/events", json=event_payload)
        
    # 21st should be blocked
    res = client.post(f"/api/projects/{project_id}/events", json=event_payload)
    assert res.status_code == 429


def test_predict_churn_endpoint(client: TestClient):
    """Verify predictive churn scoring endpoint."""
    response = client.get("/api/tenants/t-123/predict-churn?events_count=10&tickets_count=6")
    assert response.status_code == 200
    data = response.json()
    assert data["tenant_id"] == "t-123"
    assert data["risk_level"] in ("HIGH", "CRITICAL")
    
    response2 = client.get("/api/tenants/t-456/predict-churn?events_count=15000&tickets_count=0")
    assert response2.status_code == 200
    data2 = response2.json()
    assert data2["risk_level"] == "LOW"

    response3 = client.get("/api/tenants/t-789/predict-churn?events_count=15000&tickets_count=0&failed_audits=3")
    assert response3.status_code == 200
    data3 = response3.json()
    assert data3["risk_level"] in ("MEDIUM", "HIGH", "CRITICAL")

def test_audit_project_endpoint(client: TestClient):
    """Verify SOC2/GDPR compliance audit endpoint."""
    proj_res = client.post(
        "/api/projects",
        json={
            "title": "Audit Test",
            "vision": "Check compliance",
            "creator_id": "mem-boss",
            "distilled_specs": "Spec enough to pass validation",
            "required_skills": ["python"],
        },
    )
    project_id = proj_res.json()["id"]

    event_payload = {
        "event_type": "AGENT_QUERY",
        "source_agent_id": "agt-data",
        "target_agent_id": "agt-backend",
        "payload": {"question": "Here is my secret email: test@example.com"},
    }
    client.post(f"/api/projects/{project_id}/events", json=event_payload)

    audit_res = client.get(f"/api/projects/{project_id}/audit")
    assert audit_res.status_code == 200
    audit_data = audit_res.json()
    
    assert audit_data["is_compliant"] is False
    assert len(audit_data["findings"]) == 1
    assert audit_data["findings"][0]["severity"] == "HIGH"


def test_frontend_portal(client: TestClient):
    """Verify that the frontend portal is mounted and returns 200."""
    response = client.get("/portal/")
    assert response.status_code == 200
    assert "text/html" in response.headers["content-type"]

def test_analytics_overview_endpoint(client: TestClient):
    """Verify that analytics overview returns correct counters."""
    # Insert one project to ensure count > 0
    client.post(
        "/api/projects",
        json={
            "title": "Analytics Test",
            "vision": "Check counts",
            "creator_id": "mem-1",
            "distilled_specs": "Spec enough to pass validation",
            "required_skills": ["python"],
        },
    )
    
    response = client.get("/api/analytics/overview")
    assert response.status_code == 200
    data = response.json()
    assert "total_projects" in data
    assert data["total_projects"] > 0
    assert "total_events" in data

def test_global_analytics_live_feed(client: TestClient):
    """Verify that the global websocket receives events."""
    proj_res = client.post(
        "/api/projects",
        json={
            "title": "WS Test",
            "vision": "Check WS enough to pass validation",
            "creator_id": "mem-1",
            "distilled_specs": "Spec enough to pass validation",
            "required_skills": ["python"],
        },
    )
    project_id = proj_res.json()["id"]

    with client.websocket_connect("/ws/analytics/live") as websocket:
        # Emit an event to trigger a broadcast
        client.post(
            f"/api/projects/{project_id}/events",
            json={
                "event_type": "AGENT_QUERY",
                "source_agent_id": "test-ws-agent",
                "target_agent_id": "BROADCAST",
                "payload": {"status": "testing_ws"},
            },
        )
        # We should receive the event on the websocket
        data = websocket.receive_json()
        assert data["source_agent_id"] == "test-ws-agent"
        assert data["payload"]["status"] == "testing_ws"

def test_prometheus_metrics_endpoint(client: TestClient):
    """Verify that the prometheus metrics endpoint exposes metrics."""
    response = client.get("/metrics")
    assert response.status_code == 200
    assert "text/plain" in response.headers["content-type"]
    text = response.text
    assert "http_requests_total" in text
    assert "http_request_duration_seconds" in text
    assert "synapse_events_emitted_total" in text
