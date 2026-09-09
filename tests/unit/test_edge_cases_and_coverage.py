"""Unit tests targeting edge cases, failure branches, and elevating coverage to >= 95%."""

import asyncio
from pathlib import Path
from fastapi.testclient import TestClient
import pytest

from micelio.agent.workspace_bootstrapper import WorkspaceBootstrapper
from micelio.api.app import create_app
from micelio.core.synapse_bus import SynapseBus
from micelio.domain.models import (
    DepartmentEnum,
    LivingProject,
    NutrientPackage,
    SynapseEvent,
    SynapseEventType,
    TriadBriefing,
)
from micelio.main import app as main_app
from micelio.simulation.company_roster import (
    get_department_members,
    get_enterprise_member_by_id,
)
from micelio.storage.database import DatabaseManager
from micelio.storage.repositories import (
    SqliteMembershipRepository,
    SqliteNutrientRepository,
    SqliteProjectRepository,
)


def test_main_app_instance():
    """Verify main entrypoint app instance."""
    assert main_app is not None
    assert main_app.title == "Mycelium API"


def test_synapse_bus_unsubscribe_and_exception_handling():
    """Verify unsubscribe handling and safe dispatch when a callback raises."""
    bus = SynapseBus()

    async def faulty_callback(event: SynapseEvent) -> None:
        raise RuntimeError("Simulated callback failure")

    bus.subscribe("proj-err", "agt-faulty", faulty_callback)
    bus.unsubscribe("proj-err", "agt-faulty")
    # Unsubscribe from non-existent project should be safe
    bus.unsubscribe("non-existent-proj", "agt-anyone")

    # Resubscribe and verify publish handles exception safely
    bus.subscribe("proj-err", "agt-faulty", faulty_callback)
    event = SynapseEvent(
        event_id="evt-err",
        project_id="proj-err",
        source_agent_id="agt-src",
        target_agent_id="agt-faulty",
        event_type=SynapseEventType.AGENT_QUERY,
        payload={},
    )
    # This should not raise
    asyncio.run(bus.publish(event))


def test_workspace_bootstrapper_invalid_clean_slug(tmp_path: Path):
    """Verify slug consisting only of special characters raises ValueError."""
    bootstrapper = WorkspaceBootstrapper(base_dir=tmp_path)
    project = LivingProject(id="p1", title="T", vision="V", creator_id="c")
    nutrient = NutrientPackage(project_id="p1", distilled_specs="S")
    briefing = TriadBriefing(what_arrived="", what_was_done="", what_to_do="")

    with pytest.raises(ValueError, match="does not contain valid characters"):
        bootstrapper.bootstrap_project(project, nutrient, briefing, "_____")


def test_company_roster_helpers():
    """Verify get_department_members and get_enterprise_member_by_id lookups."""
    eng_members = get_department_members(DepartmentEnum.ENGINEERING)
    assert len(eng_members) == 5

    found = get_enterprise_member_by_id("emp-011")
    assert found is not None
    assert found[0].name.startswith("Vicente CTO")

    not_found = get_enterprise_member_by_id("emp-non-existent")
    assert not_found is None


def test_repositories_non_existent_records(tmp_path: Path):
    """Verify repositories return None when looking up non-existent records."""
    db_manager = DatabaseManager(db_path=tmp_path / "none_test.db")
    db_manager.initialize_schema()

    p_repo = SqliteProjectRepository(db_manager)
    assert p_repo.get_by_id("non-existent") is None

    n_repo = SqliteNutrientRepository(db_manager)
    assert n_repo.get_by_project_id("non-existent") is None

    m_repo = SqliteMembershipRepository(db_manager)
    assert m_repo.get_by_id("non-existent") is None


def test_api_404_branches_and_decline(tmp_path: Path):
    """Verify API 404 error branches and invitation decline flow."""
    app = create_app(
        workspace_base_dir=tmp_path / "workspaces",
        db_path=tmp_path / "api_edge.db",
    )
    client = TestClient(app)

    # 404 tests on non-existent project
    assert client.get("/api/projects/fake-id/recommend-team").status_code == 404
    assert client.post("/api/projects/fake-id/dispatch", json={"member_id": "m", "role": "r"}).status_code == 404
    assert client.post("/api/projects/fake-id/events", json={"event_type": "AGENT_QUERY", "source_agent_id": "a"}).status_code == 404
    assert client.get("/api/projects/fake-id/events").status_code == 404
    assert client.get("/api/projects/fake-id/status").status_code == 404

    # 404 on respond to non-existent invite
    assert client.post("/api/invites/fake-mem/respond", json={"action": "accept"}).status_code == 404

    # Test Decline Invitation
    create_res = client.post(
        "/api/projects",
        json={
            "title": "Decline Project",
            "vision": "Test decline",
            "creator_id": "emp-001",
            "distilled_specs": "Spec",
        },
    )
    pid = create_res.json()["id"]
    invite_res = client.post(f"/api/projects/{pid}/dispatch", json={"member_id": "emp-002", "role": "Reviewer"})
    mid = invite_res.json()["id"]

    decline_res = client.post(f"/api/invites/{mid}/respond", json={"action": "decline"})
    assert decline_res.status_code == 200
    assert decline_res.json()["status"] == "DECLINED"


def test_websocket_client_messaging(tmp_path: Path):
    """Verify WebSocket handles client messages and keepalive correctly."""
    app = create_app(
        workspace_base_dir=tmp_path / "workspaces",
        db_path=tmp_path / "ws_msg.db",
    )
    client = TestClient(app)

    create_res = client.post(
        "/api/projects",
        json={"title": "WS Message", "vision": "V", "creator_id": "c", "distilled_specs": "S"},
    )
    pid = create_res.json()["id"]

    with client.websocket_connect(f"/ws/projects/{pid}/office?agent_id=agt-listener") as ws:
        ws.send_text("heartbeat_ping")
        # Ensure client disconnect is clean
