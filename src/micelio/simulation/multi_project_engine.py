"""MultiProjectCollaborationEngine: Orchestrates 4 flagship projects across all 40 agents with assistance requests."""

from pathlib import Path
from typing import Any
import uuid
from pydantic import BaseModel, ConfigDict

from micelio.agent.workspace_bootstrapper import WorkspaceBootstrapper
from micelio.core.synapse_bus import SynapseBus
from micelio.domain.models import (
    LivingProject,
    MembershipStatus,
    NutrientPackage,
    ProjectMembership,
    ProjectStatus,
    SynapseEvent,
    SynapseEventType,
    TriadBriefing,
)
from micelio.simulation.company_roster import get_40_employee_roster
from micelio.storage.database import DatabaseManager
from micelio.storage.repositories import (
    SqliteEventRepository,
    SqliteMembershipRepository,
    SqliteNutrientRepository,
    SqliteProjectRepository,
)


class MultiProjectSimulationResult(BaseModel):
    """Immutable report of the multi-project enterprise collaboration."""
    model_config = ConfigDict(frozen=True)

    success: bool
    total_projects: int
    total_agents_enrolled: int
    assistance_requests_count: int
    assistance_fulfilled_count: int
    assistance_fulfillment_rate: float
    summary: str


class MultiProjectCollaborationEngine:
    """Coordinates 4 enterprise projects, assigning 40 agents with cross-area help requests."""

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
        self._roster = get_40_employee_roster()

    async def run_all_enterprise_projects(self) -> MultiProjectSimulationResult:
        """Run all 4 flagship projects and coordinate 40 agents with inter-departmental assistance."""
        project_definitions = self._get_project_definitions()
        total_requests = 0
        total_fulfilled = 0
        enrolled_agents_set: set[str] = set()

        for p_def in project_definitions:
            project, nutrient = self._create_project_and_nutrient(p_def)
            self._enroll_and_bootstrap_team(project, nutrient, p_def["assigned_range"])
            reqs, fuls = await self._simulate_assistance_dialogue(project.id, p_def["assistance_pairs"])
            total_requests += reqs
            total_fulfilled += fuls

            # Track enrolled agents
            for emp_pair in self._roster[p_def["assigned_range"][0] : p_def["assigned_range"][1]]:
                enrolled_agents_set.add(emp_pair[1].agent_id)

        rate = (total_fulfilled / total_requests) if total_requests > 0 else 1.0
        return MultiProjectSimulationResult(
            success=True,
            total_projects=len(project_definitions),
            total_agents_enrolled=len(enrolled_agents_set),
            assistance_requests_count=total_requests,
            assistance_fulfilled_count=total_fulfilled,
            assistance_fulfillment_rate=rate,
            summary=(
                f"40 agentes colaborando en {len(project_definitions)} macro-proyectos. "
                f"{total_requests} solicitudes de asistencia resueltas entre departamentos."
            ),
        )

    def _create_project_and_nutrient(self, p_def: dict[str, Any]) -> tuple[LivingProject, NutrientPackage]:
        """Persist project entity and nutrient package."""
        project = LivingProject(
            id=p_def["id"],
            title=p_def["title"],
            vision=p_def["vision"],
            creator_id=p_def["creator_id"],
            status=ProjectStatus.ACTIVE_OFFICE,
            shared_contracts=p_def["contracts"],
        )
        nutrient = NutrientPackage(
            project_id=project.id,
            distilled_specs=p_def["specs"],
            interfaces=p_def["interfaces"],
            constraints=p_def["constraints"],
        )
        self._project_repo.save(project)
        self._nutrient_repo.save(nutrient)
        return project, nutrient

    def _enroll_and_bootstrap_team(
        self,
        project: LivingProject,
        nutrient: NutrientPackage,
        member_range: tuple[int, int],
    ) -> None:
        """Enroll members and bootstrap local folders with tailored cross-area briefings."""
        members_slice = self._roster[member_range[0] : member_range[1]]
        for member, profile in members_slice:
            membership = ProjectMembership(
                id=f"mem-{project.id}-{member.id}",
                project_id=project.id,
                member_id=member.id,
                role_in_project=f"{member.name} — Especialista en {member.department.value}",
                status=MembershipStatus.JOINED,
            )

            briefing = TriadBriefing(
                what_arrived=f"{nutrient.distilled_specs} [Foco Departamental: {member.department.value}]",
                what_was_done="Contratos base definidos por Líderes de Área en la Oficina Virtual de Mycelium.",
                what_to_do=(
                    f"Ejecutar tareas de {member.department.value}. "
                    "Colaboración Interdepartamental: Emitir ASSISTANCE_REQUEST si requieres specs de otros agentes."
                ),
            )
            slug = f"{project.id}_{member.id}"
            dir_path = self._bootstrapper.bootstrap_project(project, nutrient, briefing, slug)
            self._membership_repo.save(
                membership.model_copy(update={"local_workspace_path": str(dir_path)})
            )

    async def _simulate_assistance_dialogue(
        self,
        project_id: str,
        dialogue_pairs: list[dict[str, Any]],
    ) -> tuple[int, int]:
        """Publish ASSISTANCE_REQUEST and ASSISTANCE_FULFILLED events between agents."""
        req_count = 0
        ful_count = 0

        for item in dialogue_pairs:
            # 1. Assistance Request
            req_event = SynapseEvent(
                event_id=f"req-{uuid.uuid4().hex[:6]}",
                project_id=project_id,
                source_agent_id=item["requester_agent"],
                target_agent_id=item["helper_agent"],
                event_type=SynapseEventType.ASSISTANCE_REQUEST,
                payload={"question": item["question"], "domain": item["domain"]},
            )
            self._event_repo.save(req_event)
            await self._bus.publish(req_event)
            req_count += 1

            # 2. Assistance Fulfilled
            ful_event = SynapseEvent(
                event_id=f"ful-{uuid.uuid4().hex[:6]}",
                project_id=project_id,
                source_agent_id=item["helper_agent"],
                target_agent_id=item["requester_agent"],
                event_type=SynapseEventType.ASSISTANCE_FULFILLED,
                payload={"answer": item["answer"], "status": "RESOLVED"},
            )
            self._event_repo.save(ful_event)
            await self._bus.publish(ful_event)
            ful_count += 1

        return req_count, ful_count

    @staticmethod
    def _get_project_definitions() -> list[dict[str, Any]]:
        """Definitions for the 4 enterprise flagship projects."""
        return [
            {
                "id": "PRJ-INFRA",
                "title": "Core A2A Mesh & Distributed Event Broker",
                "vision": "Malla A2A de latencia sub-milisegundo para comunicación entre agentes",
                "creator_id": "emp-011",  # Vicente CTO
                "assigned_range": (10, 20),  # Engineering & Data/AI (10 agentes)
                "specs": "Broker asíncrono con SQLite WAL, WebSockets y compresión de nutrientes",
                "interfaces": {"POST /events": "SynapseEvent"},
                "constraints": ("latencia < 200us", "cero fugas de memoria"),
                "contracts": {"protocol": "synapse_v2"},
                "assistance_pairs": [
                    {
                        "requester_agent": "agt-013",  # Esteban Backend
                        "helper_agent": "agt-024",     # Loreto DBA
                        "domain": "Database Indexing",
                        "question": "¿Estrategia de índices para consultas concurrentes de eventos?",
                        "answer": "Índice compuesto en (project_id, timestamp) y modo PRAGMA synchronous=NORMAL.",
                    },
                    {
                        "requester_agent": "agt-022",  # Mauricio DevSecOps
                        "helper_agent": "agt-030",     # Veronica PenTester
                        "domain": "Security Audit",
                        "question": "¿Auditoría de vectores de Path Traversal en bootstrapper?",
                        "answer": "Sanitización regex estricta validada contra null bytes y escapes de ruta.",
                    },
                ],
            },
            {
                "id": "PRJ-AI",
                "title": "Predictive Churn & Enterprise Deal AI",
                "vision": "Modelos predictivos de cierre de acuerdos y alertas tempranas de churn",
                "creator_id": "emp-002",  # Rodrigo CRO
                "assigned_range": (0, 10),  # Commercial & Product (10 agentes)
                "specs": "Pipeline de scoring de leads y telemetría de retención de cuentas",
                "interfaces": {"GET /predict-churn": "ScorePayload"},
                "constraints": ("AUC > 0.88", "explicabilidad de variables"),
                "contracts": {"model": "xgboost_v3"},
                "assistance_pairs": [
                    {
                        "requester_agent": "agt-017",  # Carlos Data Scientist
                        "helper_agent": "agt-003",     # Camila Enterprise AE
                        "domain": "Feature Engineering",
                        "question": "¿Qué variables comerciales determinan mayor riesgo de churn?",
                        "answer": "Inactividad > 14 días y reducción del 40% en invocaciones a la API.",
                    },
                    {
                        "requester_agent": "agt-019",  # Natalia MLOps
                        "helper_agent": "agt-023",     # Felipe SRE
                        "domain": "Compute Resources",
                        "question": "¿Qué cuotas de recursos asignamos al microservicio de inferencia?",
                        "answer": "4 vCPUs y 8GB RAM con réplicas horizontales en Kubernetes.",
                    },
                ],
            },
            {
                "id": "PRJ-PORTAL",
                "title": "Enterprise Self-Service Customer Experience Portal",
                "vision": "Portal autoservicio B2B para directivos y colaboradores con UI refinada",
                "creator_id": "emp-006",  # Sofia CPO
                "assigned_range": (30, 40),  # Design & Customer Success (10 agentes)
                "specs": "Dashboard responsivo con monitor de oficina de agentes en tiempo real",
                "interfaces": {"GET /portal/stats": "PortalMetrics"},
                "constraints": ("contraste WCAG AAA", "first contentful paint < 0.6s"),
                "contracts": {"ui_library": "ui_craft_dark"},
                "assistance_pairs": [
                    {
                        "requester_agent": "agt-033",  # Cristobal Frontend
                        "helper_agent": "agt-014",     # Carolina Sr Fullstack
                        "domain": "Authentication",
                        "question": "¿Formato de token y cabecera para la sesión de WebSocket?",
                        "answer": "Usa query param ?token=JWT con validación HMAC SHA-256.",
                    },
                    {
                        "requester_agent": "agt-037",  # Fabiola CSM
                        "helper_agent": "agt-010",     # Paula Tech Writer
                        "domain": "Documentation",
                        "question": "¿Podemos redactar la guía rápida para administradores de cuenta?",
                        "answer": "Guía completada y disponible en docs/guia_admin_enterprise.md.",
                    },
                ],
            },
            {
                "id": "PRJ-COMPLIANCE",
                "title": "Automated SOC2 & Continuous Audit Engine",
                "vision": "Trazabilidad inmutable y certificación continua de seguridad",
                "creator_id": "emp-021",  # Hernan VP Ops
                "assigned_range": (20, 30),  # Operations & QA (10 agentes)
                "specs": "Registro criptográfico de eventos A2A y auditoría de accesos por tenant",
                "interfaces": {"GET /audit/report": "AuditReport"},
                "constraints": ("inmutabilidad absoluta", "retención de logs 365 días"),
                "contracts": {"compliance_standard": "soc2_type_2"},
                "assistance_pairs": [
                    {
                        "requester_agent": "agt-038",  # Gonzalo Solutions
                        "helper_agent": "agt-022",     # Mauricio DevSecOps
                        "domain": "Regulatory Compliance",
                        "question": "¿Cómo demostramos al auditor bancario que no hay fugas de contexto?",
                        "answer": "Todo paquete de nutrientes se somete al filtro de destilación sin PII.",
                    },
                    {
                        "requester_agent": "agt-039",  # Rocio L3 Support
                        "helper_agent": "agt-013",     # Esteban Backend
                        "domain": "Incident Resolution",
                        "question": "¿Comando para rastrear la cronología exacta de un fallo A2A?",
                        "answer": "Usa GET /api/projects/{id}/events con filtro por timestamp.",
                    },
                ],
            },
        ]
