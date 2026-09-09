"""Massive simulation engine for generating 240 concurrent A2A projects."""

import uuid
import random
from typing import Any
from micelio.domain.models import DepartmentEnum, SynapseEvent, SynapseEventType
from micelio.core.synapse_bus import SynapseBus
from micelio.storage.repositories import SqliteEventRepository, SqliteProjectRepository
from micelio.simulation.company_roster import get_department_members, get_40_employee_roster
from micelio.domain.models import LivingProject, ProjectStatus
from datetime import datetime, timezone

class CrunchSimulator:
    """Simulates a heavy 'crunch' workload with 240 projects across 8 sectors."""

    def __init__(self, bus: SynapseBus, event_repo: SqliteEventRepository, project_repo: SqliteProjectRepository):
        self._bus = bus
        self._event_repo = event_repo
        self._project_repo = project_repo
        self.roster = get_40_employee_roster()

    async def run_massive_simulation(self) -> tuple[int, int, int]:
        """Runs the simulation generating 240 projects and cross-department A2A traffic."""
        projects = self._generate_projects()
        
        req_count = 0
        ful_count = 0

        for prj in projects:
            project_id = prj["id"]
            
            # Save the project to DB first to avoid Foreign Key constraint failure
            living_prj = LivingProject(
                id=project_id,
                title=prj["title"],
                vision=prj["vision"],
                creator_id=prj["creator_id"],
                status=ProjectStatus.DRAFT,
                shared_contracts=prj.get("contracts", {}),
                created_at=datetime.now(timezone.utc)
            )
            self._project_repo.save(living_prj)
            
            for pair in prj["assistance_pairs"]:
                # 1. Assistance Request
                req_event = SynapseEvent(
                    event_id=f"req-{uuid.uuid4().hex}",
                    project_id=project_id,
                    source_agent_id=pair["requester_agent"],
                    target_agent_id=pair["helper_agent"],
                    event_type=SynapseEventType.ASSISTANCE_REQUEST,
                    payload={"question": pair["question"], "domain": pair["domain"]},
                )
                self._event_repo.save(req_event)
                await self._bus.publish(req_event)
                req_count += 1

                # 2. Assistance Fulfilled
                ful_event = SynapseEvent(
                    event_id=f"ful-{uuid.uuid4().hex}",
                    project_id=project_id,
                    source_agent_id=pair["helper_agent"],
                    target_agent_id=pair["requester_agent"],
                    event_type=SynapseEventType.ASSISTANCE_FULFILLED,
                    payload={"answer": pair["answer"], "status": "RESOLVED"},
                )
                self._event_repo.save(ful_event)
                await self._bus.publish(ful_event)
                ful_count += 1

        return len(projects), req_count, ful_count

    def _generate_projects(self) -> list[dict[str, Any]]:
        projects = []
        project_idx = 1
        
        departments = list(DepartmentEnum)
        # Random seed for deterministic generation in tests
        random.seed(42)
        
        domains = ["Scaling", "Refactoring", "Deployment", "Architecture", "Data Modeling", "UI/UX", "Security", "Compliance", "Sales Strategy", "Growth"]
        questions = [
            "¿Cómo optimizamos este flujo?",
            "¿Podemos reducir la latencia aquí?",
            "¿Qué patrón arquitectónico recomiendas?",
            "¿Hay algún riesgo de seguridad en este endpoint?",
            "¿Cómo mejoramos la conversión de este funnel?",
            "¿Qué métricas debemos monitorear?",
        ]
        answers = [
            "Sugiero usar caché distribuida y procesamiento asíncrono.",
            "Refactorizar a microservicios separados por dominio.",
            "Aplicar validaciones estrictas con Pydantic y sanitización.",
            "Podemos hacer A/B testing con la variante B.",
            "Añadir índices a la base de datos y optimizar queries.",
            "Implementar telemetría con Prometheus y Grafana.",
        ]

        for dept in departments:
            dept_members = get_department_members(dept)
            if not dept_members:
                continue
            
            for _ in range(30):
                creator_member, creator_profile = random.choice(dept_members)
                
                # Pick 2 random agents for assistance, prefer cross-department
                requester = random.choice(dept_members)[1].agent_id
                
                # Helper from a DIFFERENT department if possible
                other_depts = [d for d in departments if d != dept]
                helper_dept = random.choice(other_depts) if other_depts else dept
                helper_dept_members = get_department_members(helper_dept)
                helper = random.choice(helper_dept_members)[1].agent_id if helper_dept_members else requester

                assistance_pairs = [
                    {
                        "requester_agent": requester,
                        "helper_agent": helper,
                        "domain": random.choice(domains),
                        "question": random.choice(questions),
                        "answer": random.choice(answers),
                    },
                    {
                        "requester_agent": helper,
                        "helper_agent": requester,
                        "domain": random.choice(domains),
                        "question": "¿Puedes revisar la implementación propuesta?",
                        "answer": "Revisado y aprobado. Cumple con los estándares.",
                    }
                ]

                projects.append({
                    "id": f"PRJ-{dept.name}-{project_idx:03d}",
                    "title": f"Iniciativa {random.choice(domains)} {project_idx}",
                    "vision": f"Visión estratégica para {dept.name} en proyecto {project_idx}",
                    "creator_id": creator_member.id,
                    "specs": f"Especificaciones autogeneradas para {project_idx}",
                    "assistance_pairs": assistance_pairs
                })
                project_idx += 1
                
        return projects
