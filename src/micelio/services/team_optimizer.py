"""TeamOptimizer service to evaluate and recommend optimal collaborators."""

from pydantic import BaseModel, ConfigDict
from micelio.domain.models import AgentProfile, DepartmentEnum, Member


class CandidateRecommendation(BaseModel):
    """Immutable recommendation result with score and reasoning."""
    model_config = ConfigDict(frozen=True)

    member: Member
    agent_profile: AgentProfile
    score: float
    matched_skills: tuple[str, ...]
    rationale: str


class TeamOptimizer:
    """Calculates affinity scores between project requirements and collaborator profiles."""

    def __init__(
        self,
        skill_weight: float = 0.5,
        workload_weight: float = 0.3,
        dept_weight: float = 0.2,
    ) -> None:
        self._skill_weight = skill_weight
        self._workload_weight = workload_weight
        self._dept_weight = dept_weight

    def rank_candidates(
        self,
        pool: tuple[tuple[Member, AgentProfile], ...],
        required_skills: tuple[str, ...],
        target_department: DepartmentEnum | None = None,
        limit: int = 5,
    ) -> tuple[CandidateRecommendation, ...]:
        """Rank collaborators based on composite skill, workload and department fit."""
        if not pool:
            return ()

        recommendations: list[CandidateRecommendation] = []
        for member, profile in pool:
            score, matched = self._compute_score(member, profile, required_skills, target_department)
            rationale = self._format_rationale(member, profile, score, matched)
            recommendations.append(
                CandidateRecommendation(
                    member=member,
                    agent_profile=profile,
                    score=round(score, 3),
                    matched_skills=matched,
                    rationale=rationale,
                )
            )

        # Sort descending by score
        recommendations.sort(key=lambda r: r.score, reverse=True)
        return tuple(recommendations[:limit])

    def _compute_score(
        self,
        member: Member,
        profile: AgentProfile,
        required_skills: tuple[str, ...],
        target_dept: DepartmentEnum | None,
    ) -> tuple[float, tuple[str, ...]]:
        """Compute multivariable score for a single candidate."""
        profile_skills_lower = {s.lower() for s in profile.capabilities}
        matched = tuple(s for s in required_skills if s.lower() in profile_skills_lower)

        skill_ratio = len(matched) / len(required_skills) if required_skills else 1.0
        free_capacity_ratio = max(0.0, (100.0 - profile.workload_pct) / 100.0)
        dept_match = 1.0 if (target_dept and member.department == target_dept) else 0.5

        final_score = (
            self._skill_weight * skill_ratio
            + self._workload_weight * free_capacity_ratio
            + self._dept_weight * dept_match
        )
        return final_score, matched

    @staticmethod
    def _format_rationale(
        member: Member,
        profile: AgentProfile,
        score: float,
        matched: tuple[str, ...],
    ) -> str:
        """Generate human-readable justification for the manager."""
        return (
            f"Colaborador {member.name} ({member.department.value}) tiene match de "
            f"{len(matched)} skills y carga del {profile.workload_pct}% (Score: {score:.2f})."
        )
