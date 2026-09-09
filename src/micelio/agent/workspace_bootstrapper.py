"""WorkspaceBootstrapper for creating collaborator project folders and briefings."""

from pathlib import Path
import re
from micelio.domain.models import LivingProject, NutrientPackage, TriadBriefing


class WorkspaceBootstrapper:
    """Bootstraps physical project directories and required triad briefings."""

    def __init__(self, base_dir: Path | str = "proyectos") -> None:
        self._base_dir = Path(base_dir)

    def bootstrap_project(
        self,
        project: LivingProject,
        nutrient: NutrientPackage,
        briefing: TriadBriefing,
        project_slug: str,
    ) -> Path:
        """Create physical project folder, write README.md and triad briefing.md."""
        sanitized_slug = self._sanitize_slug(project_slug)
        project_dir = self._base_dir / sanitized_slug
        project_dir.mkdir(parents=True, exist_ok=True)

        self._write_readme(project_dir, project, nutrient)
        self._write_briefing(project_dir, project, briefing)

        return project_dir

    @staticmethod
    def _sanitize_slug(slug: str) -> str:
        """Validate and sanitize directory slug preventing path traversal."""
        if not slug or ".." in slug or "/" in slug or "\\" in slug:
            raise ValueError(f"Invalid project slug: '{slug}'. Must be safe relative name.")
        clean = re.sub(r"[^a-zA-Z0-9_\-]", "_", slug).strip("_")
        if not clean:
            raise ValueError(f"Slug '{slug}' does not contain valid characters.")
        return clean

    @staticmethod
    def _write_readme(project_dir: Path, project: LivingProject, nutrient: NutrientPackage) -> None:
        """Generate root README.md for the local workspace."""
        lines = [
            f"# {project.title}",
            "",
            f"> **Visión**: {project.vision}",
            f"> **Estado**: `{project.status.value}`",
            "",
            "## Especificaciones Destiladas (Nutrientes)",
            nutrient.distilled_specs,
            "",
            "## Restricciones Operativas",
            *(f"- {c}" for c in nutrient.constraints),
            "",
            "## Contratos Compartidos de la Oficina",
            "```json",
            str(project.shared_contracts),
            "```",
        ]
        (project_dir / "README.md").write_text("\n".join(lines), encoding="utf-8")

    @staticmethod
    def _write_briefing(project_dir: Path, project: LivingProject, briefing: TriadBriefing) -> None:
        """Generate standardized triad briefing document."""
        lines = [
            f"# Informe de Inicio — {project.title}",
            f"*Generado el: {briefing.generated_at.isoformat()}*",
            "",
            "---",
            "",
            "### 📥 1. ¿Qué llegó?",
            briefing.what_arrived,
            "",
            "### 🛠️ 2. ¿Qué se ha hecho?",
            briefing.what_was_done,
            "",
            "### 🚀 3. ¿Qué podemos hacer?",
            briefing.what_to_do,
            "",
        ]
        (project_dir / "briefing.md").write_text("\n".join(lines), encoding="utf-8")
