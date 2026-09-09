"""FastAPI application for Proyecto Micelio SaaS platform."""

from pathlib import Path
from typing import Any
import uuid
from fastapi import FastAPI, HTTPException, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, ConfigDict, Field

from micelio.agent.workspace_bootstrapper import WorkspaceBootstrapper
from micelio.core.synapse_bus import SynapseBus
from micelio.domain.models import (
    AgentProfile,
    DepartmentEnum,
    LivingProject,
    Member,
    MembershipStatus,
    NutrientPackage,
    ProjectStatus,
    SynapseEvent,
    SynapseEventType,
    TriadBriefing,
)
from micelio.services.membership_service import MembershipService
from micelio.services.team_optimizer import TeamOptimizer


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


def _seed_company_pool() -> tuple[tuple[Member, AgentProfile], ...]:
    """Seed sample organizational members and their agents."""
    return (
        (
            Member(
                id="mem-carlos",
                name="Carlos Data",
                email="carlos@empresa.com",
                department=DepartmentEnum.DATA,
            ),
            AgentProfile(
                agent_id="agt-carlos",
                member_id="mem-carlos",
                capabilities=("python", "fastapi", "data_pipelines", "clickhouse", "iot"),
                workload_pct=25.0,
            ),
        ),
        (
            Member(
                id="mem-andrea",
                name="Andrea Frontend",
                email="andrea@empresa.com",
                department=DepartmentEnum.ENGINEERING,
            ),
            AgentProfile(
                agent_id="agt-andrea",
                member_id="mem-andrea",
                capabilities=("typescript", "react", "nextjs", "tailwind", "ui-craft"),
                workload_pct=35.0,
            ),
        ),
        (
            Member(
                id="mem-dev",
                name="Vicente Architect",
                email="vicente@empresa.com",
                department=DepartmentEnum.ENGINEERING,
            ),
            AgentProfile(
                agent_id="agt-dev",
                member_id="mem-dev",
                capabilities=("python", "typescript", "fastapi", "react", "c++", "tdd"),
                workload_pct=15.0,
            ),
        ),
    )


def create_app(workspace_base_dir: Path | str = "proyectos") -> FastAPI:
    """Create and configure the FastAPI application."""
    app = FastAPI(
        title="Proyecto Micelio API",
        description="SaaS de Orquestación Colaborativa A2A con Oficina Virtual de Agentes",
        version="0.1.0",
    )

    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    # State instances
    bus = SynapseBus()
    membership_service = MembershipService()
    team_optimizer = TeamOptimizer()
    bootstrapper = WorkspaceBootstrapper(base_dir=workspace_base_dir)

    projects: dict[str, LivingProject] = {}
    nutrients: dict[str, NutrientPackage] = {}
    project_skills: dict[str, tuple[str, ...]] = {}
    project_depts: dict[str, DepartmentEnum | None] = {}
    company_pool = _seed_company_pool()

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
        projects[project_id] = project
        nutrients[project_id] = nutrient
        project_skills[project_id] = req.required_skills
        project_depts[project_id] = req.target_department
        return project

    @app.get("/api/projects/{project_id}/recommend-team")
    async def recommend_team(project_id: str) -> list[dict[str, Any]]:
        if project_id not in projects:
            raise HTTPException(status_code=404, detail="Project not found")
        skills = project_skills.get(project_id, ())
        dept = project_depts.get(project_id)
        recommendations = team_optimizer.rank_candidates(
            pool=company_pool,
            required_skills=skills,
            target_department=dept,
            limit=3,
        )
        return [r.model_dump() for r in recommendations]

    @app.post("/api/projects/{project_id}/dispatch")
    async def dispatch_invite(project_id: str, req: DispatchInviteRequest) -> dict[str, Any]:
        if project_id not in projects:
            raise HTTPException(status_code=404, detail="Project not found")
        invite = membership_service.create_invitation(
            project_id=project_id,
            member_id=req.member_id,
            role=req.role,
        )
        # Update project status to DISPATCHED
        projects[project_id] = projects[project_id].model_copy(
            update={"status": ProjectStatus.DISPATCHED}
        )
        return invite.model_dump()

    @app.post("/api/invites/{membership_id}/respond")
    async def respond_to_invite(membership_id: str, req: InviteResponseRequest) -> dict[str, Any]:
        try:
            if req.action.lower() == "decline":
                declined = membership_service.decline_invitation(membership_id)
                return declined.model_dump()

            # Accept flow: trigger local workspace bootstrap
            # Find the project
            memberships = [
                m for m in membership_service._memberships.values() if m.id == membership_id
            ]
            if not memberships:
                raise HTTPException(status_code=404, detail="Membership not found")
            m_obj = memberships[0]
            project = projects[m_obj.project_id]
            nutrient = nutrients[m_obj.project_id]

            briefing = TriadBriefing(
                what_arrived=nutrient.distilled_specs,
                what_was_done=f"Proyecto concebido por {project.creator_id}. Requerimientos y contratos definidos.",
                what_to_do=f"Configurar entorno para el rol '{m_obj.role_in_project}', validar contratos e implementar solución.",
            )

            created_dir = bootstrapper.bootstrap_project(
                project=project,
                nutrient=nutrient,
                briefing=briefing,
                project_slug=req.project_slug,
            )

            accepted = membership_service.accept_invitation(
                membership_id=membership_id,
                local_workspace_path=str(created_dir),
            )
            # Mark project active office
            projects[project.id] = projects[project.id].model_copy(
                update={"status": ProjectStatus.ACTIVE_OFFICE}
            )
            return accepted.model_dump()
        except KeyError as err:
            raise HTTPException(status_code=404, detail=str(err)) from err

    @app.post("/api/projects/{project_id}/events", status_code=201)
    async def emit_office_event(project_id: str, req: SynapseEventRequest) -> dict[str, Any]:
        if project_id not in projects:
            raise HTTPException(status_code=404, detail="Project not found")
        event = SynapseEvent(
            event_id=f"evt-{uuid.uuid4().hex[:8]}",
            project_id=project_id,
            source_agent_id=req.source_agent_id,
            target_agent_id=req.target_agent_id,
            event_type=req.event_type,
            payload=req.payload,
        )
        await bus.publish(event)
        return event.model_dump()

    @app.get("/api/projects/{project_id}/events")
    async def get_office_events(project_id: str) -> list[dict[str, Any]]:
        if project_id not in projects:
            raise HTTPException(status_code=404, detail="Project not found")
        history = bus.get_project_history(project_id)
        return [e.model_dump() for e in history]

    @app.get("/api/projects/{project_id}/status")
    async def get_project_status(project_id: str) -> dict[str, Any]:
        if project_id not in projects:
            raise HTTPException(status_code=404, detail="Project not found")
        project = projects[project_id]
        members = membership_service.get_project_members(project_id)
        return {
            "project": project.model_dump(),
            "members": [m.model_dump() for m in members],
            "active_in_office": sum(1 for m in members if m.status == MembershipStatus.JOINED),
        }

    return app
