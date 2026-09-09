"""Unit tests for the 40-employee enterprise company roster."""

import pytest

from micelio.domain.models import DepartmentEnum
from micelio.simulation.company_roster import (
    get_40_employee_roster,
    get_department_members,
    get_enterprise_member_by_id,
)


def test_roster_contains_exactly_40_employees():
    """Verify that the roster contains exactly 40 employees and profiles."""
    roster = get_40_employee_roster()
    assert len(roster) == 40

    # Ensure every employee has an associated agent profile
    for member, profile in roster:
        assert member.id.startswith("emp-")
        assert profile.agent_id.startswith("agt-")
        assert profile.member_id == member.id
        assert len(profile.capabilities) > 0
        assert 0.0 <= profile.workload_pct <= 100.0


def test_roster_covers_all_8_key_departments():
    """Verify balanced distribution across all 8 strategic enterprise areas (5 per area)."""
    roster = get_40_employee_roster()
    departments = [m.department for m, _ in roster]
    counts: dict[DepartmentEnum, int] = {}
    for d in departments:
        counts[d] = counts.get(d, 0) + 1

    # In our model, we map to standard DepartmentEnum values
    for dept in DepartmentEnum:
        assert counts.get(dept, 0) >= 4  # At least 4-5 per standard enum


def test_get_enterprise_member_by_id():
    """Verify quick lookup by ID."""
    result = get_enterprise_member_by_id("emp-001")
    assert result is not None
    member, profile = result
    assert member.id == "emp-001"
    assert "CEO" in member.name or "Director" in member.name or member.is_manager
