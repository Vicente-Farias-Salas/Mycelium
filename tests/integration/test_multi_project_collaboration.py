"""Integration tests for Multi-Project Collaboration across all 40 agents with assistance requests."""

from pathlib import Path
import pytest

from micelio.domain.models import SynapseEventType
from micelio.simulation.multi_project_engine import (
    MultiProjectCollaborationEngine,
    MultiProjectSimulationResult,
)


@pytest.fixture
def multi_project_env(tmp_path: Path):
    """Fixture providing isolated database and workspace directories."""
    workspace_dir = tmp_path / "multi_workspaces"
    db_path = tmp_path / "multi_micelio.db"
    engine = MultiProjectCollaborationEngine(
        workspace_base_dir=workspace_dir,
        db_path=db_path,
    )
    return engine, workspace_dir


@pytest.mark.asyncio
async def test_all_40_agents_participate_in_focused_projects_with_help_requests(multi_project_env):
    """Verify that all 40 agents participate across 4 flagship projects and exchange assistance."""
    engine, workspace_dir = multi_project_env

    result = await engine.run_all_enterprise_projects()

    assert isinstance(result, MultiProjectSimulationResult)
    assert result.success is True
    assert result.total_projects == 4
    assert result.total_agents_enrolled == 40
    assert result.assistance_requests_count >= 8
    assert result.assistance_fulfilled_count >= 8
    assert result.assistance_fulfillment_rate == 1.0  # 100% of help requests fulfilled!

    # Verify that project workspaces were physically created
    created_dirs = list(workspace_dir.iterdir())
    assert len(created_dirs) >= 4

    # Verify that briefings in workspaces contain inter-departmental collaboration notes
    first_briefing = (created_dirs[0] / "briefing.md").read_text(encoding="utf-8")
    assert "### 📥 1. ¿Qué llegó?" in first_briefing
    assert "### 🛠️ 2. ¿Qué se ha hecho?" in first_briefing
    assert "### 🚀 3. ¿Qué podemos hacer?" in first_briefing
    assert "Colaboración Interdepartamental" in first_briefing or "Asistencia" in first_briefing
