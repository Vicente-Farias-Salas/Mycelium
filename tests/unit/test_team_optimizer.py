"""Unit tests for TeamOptimizer (optimal team member recommendation)."""

import pytest

from micelio.domain.models import AgentProfile, DepartmentEnum, Member
from micelio.services.team_optimizer import CandidateRecommendation, TeamOptimizer


@pytest.fixture
def sample_pool() -> tuple[tuple[Member, AgentProfile], ...]:
    """Pool of members and their AI agents for testing."""
    m1 = Member(
        id="mem-1",
        name="Carlos Data",
        email="carlos@example.com",
        department=DepartmentEnum.DATA,
    )
    p1 = AgentProfile(
        agent_id="agt-carlos",
        member_id="mem-1",
        capabilities=("python", "fastapi", "pandas", "data_pipelines"),
        workload_pct=20.0,
    )

    m2 = Member(
        id="mem-2",
        name="Andrea Front",
        email="andrea@example.com",
        department=DepartmentEnum.ENGINEERING,
    )
    p2 = AgentProfile(
        agent_id="agt-andrea",
        member_id="mem-2",
        capabilities=("typescript", "react", "nextjs", "tailwind"),
        workload_pct=40.0,
    )

    m3 = Member(
        id="mem-3",
        name="Felipe Busy",
        email="felipe@example.com",
        department=DepartmentEnum.DATA,
    )
    p3 = AgentProfile(
        agent_id="agt-felipe",
        member_id="mem-3",
        capabilities=("python", "pandas", "fastapi"),
        workload_pct=95.0,  # Overworked
    )

    return ((m1, p1), (m2, p2), (m3, p3))


def test_team_optimizer_recommends_best_fit(sample_pool):
    """Verify that Carlos is ranked #1 for a data pipeline project due to skills + low workload."""
    optimizer = TeamOptimizer()
    recommendations = optimizer.rank_candidates(
        pool=sample_pool,
        required_skills=("python", "fastapi", "pandas"),
        target_department=DepartmentEnum.DATA,
        limit=2,
    )

    assert len(recommendations) == 2
    assert isinstance(recommendations[0], CandidateRecommendation)
    assert recommendations[0].member.id == "mem-1"
    assert recommendations[0].score > recommendations[1].score
    assert "carlos" in recommendations[0].rationale.lower()


def test_team_optimizer_empty_pool():
    """Verify optimizer behaves gracefully with an empty pool."""
    optimizer = TeamOptimizer()
    recommendations = optimizer.rank_candidates(
        pool=(),
        required_skills=("python",),
    )
    assert recommendations == ()
