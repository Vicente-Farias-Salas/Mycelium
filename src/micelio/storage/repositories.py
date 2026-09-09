"""Durable repositories using SQLite WAL for Proyecto Micelio."""

from datetime import datetime, timezone
import json
from typing import Any
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


class SqliteProjectRepository:
    """Repository for LivingProject persistence."""

    def __init__(self, db_manager: DatabaseManager) -> None:
        self._db = db_manager

    def save(self, project: LivingProject) -> None:
        """Persist or update a project."""
        query = """
            INSERT INTO projects (id, title, vision, creator_id, status, shared_contracts_json, created_at)
            VALUES (?, ?, ?, ?, ?, ?, ?)
            ON CONFLICT(id) DO UPDATE SET
                title=excluded.title,
                vision=excluded.vision,
                status=excluded.status,
                shared_contracts_json=excluded.shared_contracts_json;
        """
        with self._db.get_connection() as conn:
            conn.execute(
                query,
                (
                    project.id,
                    project.title,
                    project.vision,
                    project.creator_id,
                    project.status.value,
                    json.dumps(project.shared_contracts),
                    project.created_at.isoformat(),
                ),
            )

    def get_by_id(self, project_id: str) -> LivingProject | None:
        """Fetch project by ID."""
        query = "SELECT * FROM projects WHERE id = ?;"
        with self._db.get_connection() as conn:
            row = conn.execute(query, (project_id,)).fetchone()
            if not row:
                return None
            return LivingProject(
                id=row["id"],
                title=row["title"],
                vision=row["vision"],
                creator_id=row["creator_id"],
                status=ProjectStatus(row["status"]),
                shared_contracts=json.loads(row["shared_contracts_json"]),
                created_at=datetime.fromisoformat(row["created_at"]),
            )

    def update_status(self, project_id: str, status: ProjectStatus) -> None:
        """Update lifecycle status of a project."""
        query = "UPDATE projects SET status = ? WHERE id = ?;"
        with self._db.get_connection() as conn:
            conn.execute(query, (status.value, project_id))

    def count(self) -> int:
        """Return total number of projects."""
        query = "SELECT COUNT(*) FROM projects;"
        with self._db.get_connection() as conn:
            return conn.execute(query).fetchone()[0]


class SqliteNutrientRepository:
    """Repository for NutrientPackage persistence."""

    def __init__(self, db_manager: DatabaseManager) -> None:
        self._db = db_manager

    def save(self, nutrient: NutrientPackage) -> None:
        """Persist nutrient specifications."""
        query = """
            INSERT INTO nutrients (project_id, distilled_specs, interfaces_json, constraints_json)
            VALUES (?, ?, ?, ?)
            ON CONFLICT(project_id) DO UPDATE SET
                distilled_specs=excluded.distilled_specs,
                interfaces_json=excluded.interfaces_json,
                constraints_json=excluded.constraints_json;
        """
        with self._db.get_connection() as conn:
            conn.execute(
                query,
                (
                    nutrient.project_id,
                    nutrient.distilled_specs,
                    json.dumps(nutrient.interfaces),
                    json.dumps(nutrient.constraints),
                ),
            )

    def get_by_project_id(self, project_id: str) -> NutrientPackage | None:
        """Retrieve nutrient specs by project ID."""
        query = "SELECT * FROM nutrients WHERE project_id = ?;"
        with self._db.get_connection() as conn:
            row = conn.execute(query, (project_id,)).fetchone()
            if not row:
                return None
            return NutrientPackage(
                project_id=row["project_id"],
                distilled_specs=row["distilled_specs"],
                interfaces=json.loads(row["interfaces_json"]),
                constraints=tuple(json.loads(row["constraints_json"])),
            )


class SqliteMembershipRepository:
    """Repository for ProjectMembership lifecycle."""

    def __init__(self, db_manager: DatabaseManager) -> None:
        self._db = db_manager

    def save(self, membership: ProjectMembership) -> None:
        """Persist membership."""
        query = """
            INSERT INTO memberships (id, project_id, member_id, role_in_project, status, local_workspace_path, invited_at, joined_at)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            ON CONFLICT(id) DO UPDATE SET
                status=excluded.status,
                local_workspace_path=excluded.local_workspace_path,
                joined_at=excluded.joined_at;
        """
        joined_at_str = membership.joined_at.isoformat() if membership.joined_at else None
        with self._db.get_connection() as conn:
            conn.execute(
                query,
                (
                    membership.id,
                    membership.project_id,
                    membership.member_id,
                    membership.role_in_project,
                    membership.status.value,
                    membership.local_workspace_path,
                    membership.invited_at.isoformat(),
                    joined_at_str,
                ),
            )

    def get_by_id(self, membership_id: str) -> ProjectMembership | None:
        """Retrieve membership by ID."""
        query = "SELECT * FROM memberships WHERE id = ?;"
        with self._db.get_connection() as conn:
            row = conn.execute(query, (membership_id,)).fetchone()
            if not row:
                return None
            return self._row_to_membership(row)

    def get_by_project(self, project_id: str) -> tuple[ProjectMembership, ...]:
        """List all memberships for a project."""
        query = "SELECT * FROM memberships WHERE project_id = ?;"
        with self._db.get_connection() as conn:
            rows = conn.execute(query, (project_id,)).fetchall()
            return tuple(self._row_to_membership(r) for r in rows)

    def update_status_and_path(self, membership_id: str, status: MembershipStatus, workspace_path: str) -> None:
        """Update acceptance status and workspace directory."""
        query = """
            UPDATE memberships
            SET status = ?, local_workspace_path = ?, joined_at = ?
            WHERE id = ?;
        """
        now = datetime.now(timezone.utc).isoformat()
        with self._db.get_connection() as conn:
            conn.execute(query, (status.value, workspace_path, now, membership_id))

    @staticmethod
    def _row_to_membership(row: Any) -> ProjectMembership:
        """Helper to deserialize row into ProjectMembership."""
        joined = datetime.fromisoformat(row["joined_at"]) if row["joined_at"] else None
        return ProjectMembership(
            id=row["id"],
            project_id=row["project_id"],
            member_id=row["member_id"],
            role_in_project=row["role_in_project"],
            status=MembershipStatus(row["status"]),
            local_workspace_path=row["local_workspace_path"],
            invited_at=datetime.fromisoformat(row["invited_at"]),
            joined_at=joined,
        )


class SqliteEventRepository:
    """Repository for SynapseEvent history."""

    def __init__(self, db_manager: DatabaseManager) -> None:
        self._db = db_manager

    def save(self, event: SynapseEvent) -> None:
        """Persist office event."""
        query = """
            INSERT INTO synapse_events (event_id, project_id, source_agent_id, target_agent_id, event_type, payload_json, timestamp)
            VALUES (?, ?, ?, ?, ?, ?, ?);
        """
        with self._db.get_connection() as conn:
            conn.execute(
                query,
                (
                    event.event_id,
                    event.project_id,
                    event.source_agent_id,
                    event.target_agent_id,
                    event.event_type.value,
                    json.dumps(event.payload),
                    event.timestamp.isoformat(),
                ),
            )

    def get_by_project(self, project_id: str) -> tuple[SynapseEvent, ...]:
        """Fetch chronological event history for a project."""
        query = "SELECT * FROM synapse_events WHERE project_id = ? ORDER BY timestamp ASC;"
        with self._db.get_connection() as conn:
            rows = conn.execute(query, (project_id,)).fetchall()
            events = []
            for r in rows:
                events.append(
                    SynapseEvent(
                        event_id=r["event_id"],
                        project_id=r["project_id"],
                        source_agent_id=r["source_agent_id"],
                        target_agent_id=r["target_agent_id"],
                        event_type=SynapseEventType(r["event_type"]),
                        payload=json.loads(r["payload_json"]),
                        timestamp=datetime.fromisoformat(r["timestamp"]),
                    )
                )
            return tuple(events)

    def count(self) -> int:
        """Return total number of events."""
        query = "SELECT COUNT(*) FROM synapse_events;"
        with self._db.get_connection() as conn:
            return conn.execute(query).fetchone()[0]
