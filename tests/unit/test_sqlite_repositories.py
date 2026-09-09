"""Unit tests for SQLite WAL durable repositories."""

from pathlib import Path
import pytest

from micelio.domain.models import (
    LivingProject,
    MembershipStatus,
    NutrientPackage,
    ProjectMembership,
    ProjectStatus,
    SynapseEvent,
    SynapseEventType,
)
from micelio.storage.database import DatabaseManager
from micelio.storage.repositories import (
    SqliteEventRepository,
    SqliteMembershipRepository,
    SqliteNutrientRepository,
    SqliteProjectRepository,
)


@pytest.fixture
def db_manager(tmp_path: Path) -> DatabaseManager:
    """Fixture providing an isolated SQLite database in WAL mode."""
    db_path = tmp_path / "test_micelio.db"
    manager = DatabaseManager(db_path=db_path)
    manager.initialize_schema()
    return manager


@pytest.fixture
def sample_project(db_manager: DatabaseManager) -> LivingProject:
    """Helper fixture to insert a parent project to satisfy foreign keys."""
    repo = SqliteProjectRepository(db_manager)
    project = LivingProject(
        id="proj-db-1",
        title="Trading System",
        vision="Sub-millisecond signals",
        creator_id="emp-011",
        status=ProjectStatus.DRAFT,
        shared_contracts={"schema": "v1"},
    )
    repo.save(project)
    return project


def test_project_repository_crud(db_manager: DatabaseManager):
    """Verify persisting and reading a LivingProject from SQLite."""
    repo = SqliteProjectRepository(db_manager)

    project = LivingProject(
        id="proj-db-test",
        title="Trading System",
        vision="Sub-millisecond signals",
        creator_id="emp-011",
        status=ProjectStatus.DRAFT,
        shared_contracts={"schema": "v1"},
    )

    repo.save(project)
    retrieved = repo.get_by_id("proj-db-test")
    assert retrieved is not None
    assert retrieved.id == "proj-db-test"
    assert retrieved.title == "Trading System"
    assert retrieved.shared_contracts["schema"] == "v1"

    # Update status
    repo.update_status("proj-db-test", ProjectStatus.ACTIVE_OFFICE)
    updated = repo.get_by_id("proj-db-test")
    assert updated is not None
    assert updated.status == ProjectStatus.ACTIVE_OFFICE


def test_nutrient_repository_crud(db_manager: DatabaseManager, sample_project: LivingProject):
    """Verify storing and retrieving NutrientPackage."""
    repo = SqliteNutrientRepository(db_manager)
    nutrient = NutrientPackage(
        project_id=sample_project.id,
        distilled_specs="Spec in detail",
        interfaces={"endpoint": "/quote"},
        constraints=("p99 < 1ms", "zero copy"),
    )
    repo.save(nutrient)
    retrieved = repo.get_by_project_id(sample_project.id)
    assert retrieved is not None
    assert retrieved.distilled_specs == "Spec in detail"
    assert "p99 < 1ms" in retrieved.constraints


def test_membership_repository_crud(db_manager: DatabaseManager, sample_project: LivingProject):
    """Verify persisting and querying project memberships."""
    repo = SqliteMembershipRepository(db_manager)
    membership = ProjectMembership(
        id="mem-db-1",
        project_id=sample_project.id,
        member_id="emp-017",
        role_in_project="Lead Data Scientist",
        status=MembershipStatus.INVITED,
    )
    repo.save(membership)

    retrieved = repo.get_by_id("mem-db-1")
    assert retrieved is not None
    assert retrieved.member_id == "emp-017"
    assert retrieved.status == MembershipStatus.INVITED

    # Accept membership
    repo.update_status_and_path(
        membership_id="mem-db-1",
        status=MembershipStatus.JOINED,
        workspace_path="proyectos/trading_ds",
    )
    updated = repo.get_by_id("mem-db-1")
    assert updated is not None
    assert updated.status == MembershipStatus.JOINED
    assert updated.local_workspace_path == "proyectos/trading_ds"


def test_synapse_event_repository(db_manager: DatabaseManager, sample_project: LivingProject):
    """Verify persisting and reading office Synapse events."""
    repo = SqliteEventRepository(db_manager)
    event = SynapseEvent(
        event_id="evt-db-1",
        project_id=sample_project.id,
        source_agent_id="agt-017",
        target_agent_id="agt-011",
        event_type=SynapseEventType.STATE_MUTATION,
        payload={"contract": "order_book_v2"},
    )
    repo.save(event)

    events = repo.get_by_project(sample_project.id)
    assert len(events) == 1
    assert events[0].event_id == "evt-db-1"
    assert events[0].payload["contract"] == "order_book_v2"

def test_schema_indexes_created(db_manager: DatabaseManager):
    """Verify that performance indexes exist in the schema."""
    query = "SELECT name FROM sqlite_master WHERE type='index';"
    with db_manager.get_connection() as conn:
        indexes = [row["name"] for row in conn.execute(query).fetchall()]
    assert "idx_memberships_project_id" in indexes
    assert "idx_events_project_id" in indexes
    assert "idx_events_timestamp" in indexes
