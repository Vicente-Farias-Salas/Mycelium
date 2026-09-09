"""Unit tests for WorkspaceBootstrapper (local folder creation and triad briefing)."""

from pathlib import Path
import pytest

from micelio.agent.workspace_bootstrapper import WorkspaceBootstrapper
from micelio.domain.models import LivingProject, NutrientPackage, TriadBriefing


@pytest.fixture
def temp_workspace(tmp_path: Path) -> Path:
    """Fixture providing a clean temporary directory for workspace tests."""
    return tmp_path / "workspaces"


def test_bootstrap_creates_directory_and_briefing(temp_workspace: Path):
    """Verify bootstrapper creates local folder and writes README.md + briefing.md."""
    bootstrapper = WorkspaceBootstrapper(base_dir=temp_workspace)

    project = LivingProject(
        id="proj-42",
        title="Motor de Recomendaciones",
        vision="Optimizar matching interdepartamental con IA",
        creator_id="mem-boss",
        shared_contracts={"version": "1.0", "engine": "hybrid"},
    )
    nutrient = NutrientPackage(
        project_id="proj-42",
        distilled_specs="Construir microservicio FastAPI con scoring multivariable",
        interfaces={"GET /recommend": {"params": ["skills", "dept"]}},
        constraints=("p99 < 50ms",),
    )
    briefing = TriadBriefing(
        what_arrived="Specs de microservicio FastAPI y contratos JSON.",
        what_was_done="Agente Jefe y Agente Data diseñaron los pesos de scoring.",
        what_to_do="Escribir endpoints y suite de tests con pytest.",
    )

    project_dir = bootstrapper.bootstrap_project(
        project=project,
        nutrient=nutrient,
        briefing=briefing,
        project_slug="motor_recomendaciones",
    )

    assert project_dir.exists()
    assert project_dir.is_dir()

    readme_path = project_dir / "README.md"
    assert readme_path.exists()
    readme_content = readme_path.read_text(encoding="utf-8")
    assert "Motor de Recomendaciones" in readme_content

    briefing_path = project_dir / "briefing.md"
    assert briefing_path.exists()
    briefing_content = briefing_path.read_text(encoding="utf-8")
    assert "¿Qué llegó?" in briefing_content
    assert "¿Qué se ha hecho?" in briefing_content
    assert "¿Qué podemos hacer?" in briefing_content


def test_bootstrap_path_traversal_prevention(temp_workspace: Path):
    """Verify malicious slugs with path traversal are rejected."""
    bootstrapper = WorkspaceBootstrapper(base_dir=temp_workspace)
    project = LivingProject(
        id="proj-evil",
        title="Evil Project",
        vision="Attempt escape",
        creator_id="mem-evil",
    )
    nutrient = NutrientPackage(project_id="proj-evil", distilled_specs="None")
    briefing = TriadBriefing(what_arrived="", what_was_done="", what_to_do="")

    with pytest.raises(ValueError, match="Invalid project slug"):
        bootstrapper.bootstrap_project(
            project=project,
            nutrient=nutrient,
            briefing=briefing,
            project_slug="../escaped_dir",
        )
