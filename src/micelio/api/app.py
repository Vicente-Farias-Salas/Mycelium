"""FastAPI application for Proyecto Micelio SaaS platform with SQLite WAL & WebSockets."""

import asyncio
from pathlib import Path
from typing import Any
import uuid
from fastapi import FastAPI, HTTPException, Query, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, ConfigDict, Field

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


class ProjectCreateRequest(BaseModel):
    """Schema for creating a new project."""
    model_config = ConfigDict(frozen=True)

    title: str
    vision: str
    creator_id: str
    distilled_specs: str
    interfaces: dict[str, Any] = Field(default_factory=dict)
    constraints: tuple[str, ...] = Field(default_factory=tuple)
    shared_contracts: dict[str, Any] = Field(default_factory=dict)
    required_skills: tuple[str, ...] = Field(default_factory=tuple)
    target_department: DepartmentEnum | None = None


class DispatchInviteRequest(BaseModel):
    """Schema for dispatching project invitation."""
    model_config = ConfigDict(frozen=True)

    member_id: str
    role: str


class InviteResponseRequest(BaseModel):
    """Schema for responding to an invitation."""
    model_config = ConfigDict(frozen=True)

    action: str  # "accept" or "decline"
    project_slug: str = "proyecto_workspace"


class SynapseEventRequest(BaseModel):
    """Schema for emitting an event into the office."""
    model_config = ConfigDict(frozen=True)

    event_type: SynapseEventType
    source_agent_id: str
    target_agent_id: str = "BROADCAST"
    payload: dict[str, Any] = Field(default_factory=dict)


def create_app(
    workspace_base_dir: Path | str = "proyectos",
    db_path: Path | str = "data/micelio.db",
) -> FastAPI:
    """Create and configure the FastAPI application backed by SQLite WAL storage."""
    app = FastAPI(
        title="Mycelium API",
        description="SaaS Enterprise de Orquestación Colaborativa A2A con Oficina Virtual de Agentes",
        version="0.2.0",
    )

    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    # Initialize Storage & Core Services
    db_manager = DatabaseManager(db_path=db_path)
    db_manager.initialize_schema()

    project_repo = SqliteProjectRepository(db_manager)
    nutrient_repo = SqliteNutrientRepository(db_manager)
    membership_repo = SqliteMembershipRepository(db_manager)
    event_repo = SqliteEventRepository(db_manager)

    bus = SynapseBus()
    team_optimizer = TeamOptimizer()
    bootstrapper = WorkspaceBootstrapper(base_dir=workspace_base_dir)

    # In-memory index for optimizer search parameters
    project_skills: dict[str, tuple[str, ...]] = {}
    project_depts: dict[str, DepartmentEnum | None] = {}
    company_pool = get_40_employee_roster()

    @app.post("/api/projects", status_code=201)
    async def create_project(req: ProjectCreateRequest) -> LivingProject:
        project_id = f"proj-{uuid.uuid4().hex[:8]}"
        project = LivingProject(
            id=project_id,
            title=req.title,
            vision=req.vision,
            creator_id=req.creator_id,
            status=ProjectStatus.DRAFT,
            shared_contracts=req.shared_contracts,
        )
        nutrient = NutrientPackage(
            project_id=project_id,
            distilled_specs=req.distilled_specs,
            interfaces=req.interfaces,
            constraints=req.constraints,
        )
        project_repo.save(project)
        nutrient_repo.save(nutrient)
        project_skills[project_id] = req.required_skills
        project_depts[project_id] = req.target_department
        return project

    @app.get("/api/projects/{project_id}/recommend-team")
    async def recommend_team(project_id: str) -> list[dict[str, Any]]:
        project = project_repo.get_by_id(project_id)
        if not project:
            raise HTTPException(status_code=404, detail="Project not found")
        skills = project_skills.get(project_id, ())
        dept = project_depts.get(project_id)
        recommendations = team_optimizer.rank_candidates(
            pool=company_pool,
            required_skills=skills,
            target_department=dept,
            limit=5,
        )
        return [r.model_dump() for r in recommendations]

    @app.post("/api/projects/{project_id}/dispatch")
    async def dispatch_invite(project_id: str, req: DispatchInviteRequest) -> dict[str, Any]:
        project = project_repo.get_by_id(project_id)
        if not project:
            raise HTTPException(status_code=404, detail="Project not found")

        membership_id = f"mem-{uuid.uuid4().hex[:8]}"
        invite = ProjectMembership(
            id=membership_id,
            project_id=project_id,
            member_id=req.member_id,
            role_in_project=req.role,
            status=MembershipStatus.INVITED,
        )
        membership_repo.save(invite)
        project_repo.update_status(project_id, ProjectStatus.DISPATCHED)
        return invite.model_dump()

    @app.post("/api/invites/{membership_id}/respond")
    async def respond_to_invite(membership_id: str, req: InviteResponseRequest) -> dict[str, Any]:
        invite = membership_repo.get_by_id(membership_id)
        if not invite:
            raise HTTPException(status_code=404, detail="Membership not found")

        if req.action.lower() == "decline":
            membership_repo.update_status_and_path(membership_id, MembershipStatus.DECLINED, "")
            updated = membership_repo.get_by_id(membership_id)
            return updated.model_dump() if updated else {}

        # Accept flow
        project = project_repo.get_by_id(invite.project_id)
        nutrient = nutrient_repo.get_by_project_id(invite.project_id)
        if not project or not nutrient:
            raise HTTPException(status_code=404, detail="Project context not found")

        briefing = TriadBriefing(
            what_arrived=nutrient.distilled_specs,
            what_was_done=f"Proyecto formulado por {project.creator_id}. Contratos y especificaciones acordados.",
            what_to_do=f"Configurar workspace para rol '{invite.role_in_project}', co-trabajar con agentes de la oficina.",
        )

        created_dir = bootstrapper.bootstrap_project(
            project=project,
            nutrient=nutrient,
            briefing=briefing,
            project_slug=req.project_slug,
        )

        membership_repo.update_status_and_path(
            membership_id=membership_id,
            status=MembershipStatus.JOINED,
            workspace_path=str(created_dir),
        )
        project_repo.update_status(project.id, ProjectStatus.ACTIVE_OFFICE)
        updated = membership_repo.get_by_id(membership_id)
        return updated.model_dump() if updated else {}

    @app.post("/api/projects/{project_id}/events", status_code=201)
    async def emit_office_event(project_id: str, req: SynapseEventRequest) -> dict[str, Any]:
        project = project_repo.get_by_id(project_id)
        if not project:
            raise HTTPException(status_code=404, detail="Project not found")

        event = SynapseEvent(
            event_id=f"evt-{uuid.uuid4().hex[:8]}",
            project_id=project_id,
            source_agent_id=req.source_agent_id,
            target_agent_id=req.target_agent_id,
            event_type=req.event_type,
            payload=req.payload,
        )
        event_repo.save(event)
        await bus.publish(event)
        return event.model_dump()

    @app.get("/api/projects/{project_id}/events")
    async def get_office_events(project_id: str) -> list[dict[str, Any]]:
        project = project_repo.get_by_id(project_id)
        if not project:
            raise HTTPException(status_code=404, detail="Project not found")
        events = event_repo.get_by_project(project_id)
        return [e.model_dump() for e in events]

    @app.get("/api/projects/{project_id}/status")
    async def get_project_status(project_id: str) -> dict[str, Any]:
        project = project_repo.get_by_id(project_id)
        if not project:
            raise HTTPException(status_code=404, detail="Project not found")
        members = membership_repo.get_by_project(project_id)
        return {
            "project": project.model_dump(),
            "members": [m.model_dump() for m in members],
            "active_in_office": sum(1 for m in members if m.status == MembershipStatus.JOINED),
        }

    @app.websocket("/ws/projects/{project_id}/office")
    async def office_websocket_endpoint(
        websocket: WebSocket,
        project_id: str,
        agent_id: str = Query(default="agt-observer"),
    ) -> None:
        """Stream real-time office events directly to connected agent or human client."""
        await websocket.accept()
        queue: asyncio.Queue[SynapseEvent] = asyncio.Queue()

        async def _event_handler(event: SynapseEvent) -> None:
            await queue.put(event)

        bus.subscribe(project_id=project_id, agent_id=agent_id, callback=_event_handler)
        try:
            while True:
                # Wait for next event or keepalive check
                get_task = asyncio.create_task(queue.get())
                recv_task = asyncio.create_task(websocket.receive_text())
                done, pending = await asyncio.wait(
                    [get_task, recv_task],
                    return_when=asyncio.FIRST_COMPLETED,
                )
                for t in pending:
                    t.cancel()

                if get_task in done:
                    event = get_task.result()
                    payload = event.model_dump()
                    # Serialize datetime to ISO string
                    payload["timestamp"] = event.timestamp.isoformat()
                    await websocket.send_json(payload)
                if recv_task in done:
                    # Client sent a message, keepalive or query
                    _ = recv_task.result()
        except WebSocketDisconnect:
            pass
        finally:
            bus.unsubscribe(project_id=project_id, agent_id=agent_id)

    @app.get("/api/tenants/{tenant_id}/predict-churn")
    async def predict_churn(tenant_id: str, events_count: int = Query(0), tickets_count: int = Query(0)):
        from micelio.domain.billing import Tenant, SubscriptionTier
        from micelio.services.churn_predictor import ChurnPredictor
        
        # Simulate fetching tenant from DB
        tenant = Tenant(
            tenant_id=tenant_id,
            name=f"Tenant {tenant_id}",
            tier=SubscriptionTier.STARTER if events_count < 500 else SubscriptionTier.ENTERPRISE
        )
        
        predictor = ChurnPredictor()
        risk = predictor.calculate_risk(tenant, events_count, tickets_count)
        return risk.model_dump()

    return app
