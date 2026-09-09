"""CompanySwarmSimulator: Simulates 40 agents across 8 departments co-working on Proyecto Micelio."""

from pathlib import Path
from typing import Any
import uuid
from pydantic import BaseModel, ConfigDict

from micelio.agent.workspace_bootstrapper import WorkspaceBootstrapper
from micelio.core.synapse_bus import SynapseBus
from micelio.domain.models import (
    DepartmentEnum,
    LivingProject,
    MembershipStatus,
    NutrientPackage,
    ProjectMembership,
    ProjectStatus,
    SynapseEvent,
    SynapseEventType,
    TriadBriefing,
)
from micelio.services.team_optimizer import TeamOptimizer
from micelio.simulation.company_roster import get_40_employee_roster
from micelio.storage.database import DatabaseManager
from micelio.storage.repositories import (
    SqliteEventRepository,
    SqliteMembershipRepository,
    SqliteNutrientRepository,
    SqliteProjectRepository,
)


class SwarmSimulationResult(BaseModel):
    """Immutable outcome report of the 40-agent company simulation."""
    model_config = ConfigDict(frozen=True)

    success: bool
    project_id: str
    total_agents_participating: int
    departments_represented: int
    total_events_exchanged: int
    workspaces_created: int
    consensus_rate: float
    executive_summary: str


class CompanySwarmSimulator:
    """Orchestrates an enterprise-wide multi-agent simulation for 40 collaborators."""

    def __init__(
        self,
        workspace_base_dir: Path | str = "proyectos",
        db_path: Path | str = "data/micelio.db",
    ) -> None:
        self._workspace_dir = Path(workspace_base_dir)
        self._db_manager = DatabaseManager(db_path=db_path)
        self._db_manager.initialize_schema()

        self._project_repo = SqliteProjectRepository(self._db_manager)
        self._nutrient_repo = SqliteNutrientRepository(self._db_manager)
        self._membership_repo = SqliteMembershipRepository(self._db_manager)
        self._event_repo = SqliteEventRepository(self._db_manager)

        self._bus = SynapseBus()
        self._bootstrapper = WorkspaceBootstrapper(base_dir=self._workspace_dir)
        self._optimizer = TeamOptimizer()
        self._roster = get_40_employee_roster()

    async def run_full_enterprise_cycle(
        self,
        project_title: str,
        project_vision: str,
        distilled_specs: str,
    ) -> SwarmSimulationResult:
        """Execute complete 40-agent enterprise lifecycle across all 8 departments."""
        # 1. Leadership conceives project
        project, nutrient = self._step_leadership_genesis(project_title, project_vision, distilled_specs)

        # 2. Optimize and dispatch across departments
        assigned_members = self._step_optimization_and_dispatch(project)

        # 3. Bootstrapping workspaces & triad briefings
        workspaces_count = self._step_bootstrap_workspaces(project, nutrient, assigned_members)

        # 4. Synapse mesh real-time collaboration events from all 8 departments
        events_count = await self._step_swarm_collaboration(project.id)

        # 5. Final consolidation
        self._project_repo.update_status(project.id, ProjectStatus.ACTIVE_OFFICE)

        return SwarmSimulationResult(
            success=True,
            project_id=project.id,
            total_agents_participating=len(self._roster),
            departments_represented=len(DepartmentEnum),
            total_events_exchanged=events_count,
            workspaces_created=workspaces_count,
            consensus_rate=1.0,
            executive_summary=(
                f"Proyecto '{project_title}' ejecutado con éxito por 40 agentes. "
                "Liderado por Valeria CEO y Vicente CTO con consenso unánime."
            ),
        )

    def _step_leadership_genesis(
        self, title: str, vision: str, specs: str
    ) -> tuple[LivingProject, NutrientPackage]:
        """Department 1 (Commercial) and Department 2 (Product) formulate project."""
        project_id = f"proj-swarm-{uuid.uuid4().hex[:6]}"
        project = LivingProject(
            id=project_id,
            title=title,
            vision=vision,
            creator_id="emp-001",  # Valeria CEO
            status=ProjectStatus.DRAFT,
            shared_contracts={"auth": "oauth2_bearer", "telemetry": "clickhouse_v1"},
        )
        nutrient = NutrientPackage(
            project_id=project_id,
            distilled_specs=specs,
            interfaces={"GET /v1/routes": {"auth": "Bearer"}},
            constraints=("p99 < 10ms", "soc2_audit_trail", "inmutabilidad"),
        )
        self._project_repo.save(project)
        self._nutrient_repo.save(nutrient)
        return project, nutrient

    def _step_optimization_and_dispatch(self, project: LivingProject) -> list[str]:
        """Evaluate best candidates across Engineering, Data, QA, Platform."""
        recommendations = self._optimizer.rank_candidates(
            pool=self._roster,
            required_skills=("fastapi", "python", "distributed_systems", "clickhouse"),
            limit=4,
        )
        assigned: list[str] = []
        for rec in recommendations:
            membership = ProjectMembership(
                id=f"mem-{uuid.uuid4().hex[:6]}",
                project_id=project.id,
                member_id=rec.member.id,
                role_in_project=f"Specialist ({rec.member.department.value})",
                status=MembershipStatus.INVITED,
            )
            self._membership_repo.save(membership)
            assigned.append(membership.id)
        return assigned

    def _step_bootstrap_workspaces(
        self,
        project: LivingProject,
        nutrient: NutrientPackage,
        membership_ids: list[str],
    ) -> int:
        """Create physical folders and triad briefings for assigned members."""
        created_count = 0
        for m_id in membership_ids:
            membership = self._membership_repo.get_by_id(m_id)
            if not membership:
                continue

            slug = f"{project.id}_{membership.member_id}"
            briefing = TriadBriefing(
                what_arrived=nutrient.distilled_specs,
                what_was_done=f"Proyecto ideado por Valeria CEO y Vicente CTO.",
                what_to_do=f"Construir módulo para rol '{membership.role_in_project}'.",
            )
            dir_path = self._bootstrapper.bootstrap_project(project, nutrient, briefing, slug)
            self._membership_repo.update_status_and_path(m_id, MembershipStatus.JOINED, str(dir_path))
            created_count += 1
        return created_count

    async def _step_swarm_collaboration(self, project_id: str) -> int:
        """Emit real-time synapse events from representatives of all 8 departments."""
        events_payload = [
            ("agt-011", "BROADCAST", SynapseEventType.STATE_MUTATION, {"layer": "FastAPI Gateway", "status": "Ready"}),
            ("agt-017", "agt-011", SynapseEventType.AGENT_QUERY, {"query": "Schema ClickHouse para telemetría"}),
            ("agt-011", "agt-017", SynapseEventType.AGENT_RESPONSE, {"schema": "TelemetryEvent(timestamp, lat_ms)"}),
            ("agt-022", "BROADCAST", SynapseEventType.STATE_MUTATION, {"security": "Zero-Trust policy verified"}),
            ("agt-027", "agt-011", SynapseEventType.AGENT_CONSENSUS, {"tests": "100% suite green"}),
            ("agt-032", "agt-011", SynapseEventType.OFFICE_CHATTER, {"ui": "Dashboard UI-Craft contrast validated"}),
            ("agt-003", "agt-001", SynapseEventType.OFFICE_CHATTER, {"deal": "Client Acme approved pilot SLA"}),
            ("agt-037", "agt-001", SynapseEventType.AGENT_CONSENSUS, {"onboarding": "Runbook ready for day 1"}),
        ]

        for src, tgt, ev_type, payload in events_payload:
            event = SynapseEvent(
                event_id=f"evt-{uuid.uuid4().hex[:6]}",
                project_id=project_id,
                source_agent_id=src,
                target_agent_id=tgt,
                event_type=ev_type,
                payload=payload,
            )
            self._event_repo.save(event)
            await self._bus.publish(event)

        return len(events_payload)
