"""Simulation package for enterprise multi-agent swarm testing in Proyecto Micelio."""

from micelio.simulation.company_roster import (
    get_40_employee_roster,
    get_department_members,
    get_enterprise_member_by_id,
)
from micelio.simulation.company_swarm import (
    CompanySwarmSimulator,
    SwarmSimulationResult,
)
from micelio.simulation.multi_project_engine import (
    MultiProjectCollaborationEngine,
    MultiProjectSimulationResult,
)

__all__ = [
    "CompanySwarmSimulator",
    "MultiProjectCollaborationEngine",
    "MultiProjectSimulationResult",
    "SwarmSimulationResult",
    "get_40_employee_roster",
    "get_department_members",
    "get_enterprise_member_by_id",
]
