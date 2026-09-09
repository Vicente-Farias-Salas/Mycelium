"""Integration tests for the 40-agent enterprise swarm simulation."""

from pathlib import Path
import pytest

from micelio.simulation.company_swarm import CompanySwarmSimulator, SwarmSimulationResult


@pytest.fixture
def swarm_workspace(tmp_path: Path) -> Path:
    """Fixture providing isolated workspace for the 40-agent swarm."""
    return tmp_path / "swarm_projects"


@pytest.mark.asyncio
async def test_40_agent_company_swarm_execution(swarm_workspace: Path, tmp_path: Path):
    """Verify that all 40 agents across 8 departments participate in the project simulation."""
    db_path = tmp_path / "swarm_micelio.db"
    simulator = CompanySwarmSimulator(
        workspace_base_dir=swarm_workspace,
        db_path=db_path,
    )

    result = await simulator.run_full_enterprise_cycle(
        project_title="AI Enterprise Gateway SaaS",
        project_vision="B2B AI routing with sub-millisecond telemetry and SOC2 compliance",
        distilled_specs="FastAPI gateway with JWT validation, ClickHouse analytics and WebSocket office mesh",
    )

    assert isinstance(result, SwarmSimulationResult)
    assert result.success is True
    assert result.total_agents_participating == 40
    assert result.departments_represented == 8
    assert result.total_events_exchanged >= 8
    assert result.workspaces_created >= 2
    assert result.consensus_rate == 1.0  # 100% consensus achieved
    assert "Valeria CEO" in result.executive_summary
    assert "Vicente CTO" in result.executive_summary
