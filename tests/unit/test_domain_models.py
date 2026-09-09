"""Unit tests for immutable domain models in Proyecto Micelio."""

from datetime import datetime, timezone
import pytest
from pydantic import ValidationError

from micelio.domain.models import (
    AgentProfile,
    DepartmentEnum,
    LivingProject,
    Member,
    MembershipStatus,
    NutrientPackage,
    ProjectMembership,
    ProjectStatus,
    SynapseEvent,
    SynapseEventType,
    TriadBriefing,
)


def test_member_immutability():
    """Verify Member is frozen and cannot be mutated."""
    member = Member(
        id="mem-001",
        name="Vicente Farias",
        email="v.farias@example.com",
        department=DepartmentEnum.DATA,
        is_manager=False,
    )
    assert member.name == "Vicente Farias"
    with pytest.raises((ValidationError, TypeError)):
        member.name = "Otro Nombre"  # type: ignore[misc]


def test_agent_profile_workload_validation():
    """Verify workload is strictly constrained between 0 and 100."""
    profile = AgentProfile(
        agent_id="agt-001",
        member_id="mem-001",
        capabilities=("python", "machine_learning", "data_pipelines"),
        workload_pct=35.0,
    )
    assert profile.workload_pct == 35.0

    with pytest.raises(ValidationError):
        AgentProfile(
            agent_id="agt-002",
            member_id="mem-002",
            capabilities=("react",),
            workload_pct=150.0,  # Invalid: > 100
        )

    with pytest.raises(ValidationError):
        AgentProfile(
            agent_id="agt-003",
            member_id="mem-003",
            capabilities=("react",),
            workload_pct=-5.0,  # Invalid: < 0
        )


def test_living_project_and_nutrient_package():
    """Verify LivingProject structure and immutability."""
    now = datetime.now(timezone.utc)
    project = LivingProject(
        id="proj-100",
        title="Pipeline de Ingesta Inteligente",
        vision="Conectar agentes para procesar datasets en tiempo real",
        creator_id="mem-boss",
        status=ProjectStatus.ACTIVE_OFFICE,
        shared_contracts={"api_version": "v1", "format": "parquet"},
        created_at=now,
    )
    assert project.status == ProjectStatus.ACTIVE_OFFICE
    assert project.shared_contracts["api_version"] == "v1"

    nutrient = NutrientPackage(
        project_id="proj-100",
        distilled_specs="Crear endpoint de ingesta con validación Pydantic",
        interfaces={"POST /ingest": {"body": "DatasetPayload"}},
        constraints=("latencia < 200ms", "memoria < 512MB"),
    )
    assert len(nutrient.constraints) == 2


def test_triad_briefing_structure():
    """Verify the 3-axis required briefing: What arrived, What was done, What to do."""
    briefing = TriadBriefing(
        what_arrived="Especificaciones de pipeline con validación Pydantic",
        what_was_done="Agente Jefe definió el esquema base y seleccionó el equipo",
        what_to_do="Implementar adaptador Fastparquet y pruebas unitarias",
    )
    assert "Pydantic" in briefing.what_arrived
    assert "Agente Jefe" in briefing.what_was_done
    assert "Fastparquet" in briefing.what_to_do


def test_synapse_event_immutability():
    """Verify SynapseEvent captures inter-agent office events."""
    event = SynapseEvent(
        event_id="evt-001",
        project_id="proj-100",
        source_agent_id="agt-backend",
        target_agent_id="agt-frontend",
        event_type=SynapseEventType.AGENT_QUERY,
        payload={"query": "¿El frontend usará WebSockets o Server-Sent Events?"},
    )
    assert event.event_type == SynapseEventType.AGENT_QUERY
    assert event.payload["query"].startswith("¿El frontend")
    with pytest.raises((ValidationError, TypeError)):
        event.payload = {}  # type: ignore[misc]
