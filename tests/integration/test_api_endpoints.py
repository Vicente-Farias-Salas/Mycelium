"""Integration tests for FastAPI REST & WebSocket endpoints in Proyecto Micelio."""

from fastapi.testclient import TestClient
import pytest

from micelio.api.app import create_app
from micelio.domain.models import DepartmentEnum, ProjectStatus


@pytest.fixture
def client(tmp_path) -> TestClient:
    """Fixture providing test client configured with a temporary workspace."""
    app = create_app(workspace_base_dir=tmp_path / "workspaces")
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
            "distilled_specs": "Spec",
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
