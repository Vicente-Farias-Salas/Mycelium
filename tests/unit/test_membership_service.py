"""Unit tests for MembershipService (project join requests & status lifecycle)."""

import pytest

from micelio.domain.models import MembershipStatus
from micelio.services.membership_service import MembershipService


def test_invitation_lifecycle():
    """Verify invitation creation, acceptance, and immutable transitions."""
    service = MembershipService()

    # 1. Create invitation
    invite = service.create_invitation(
        project_id="proj-100",
        member_id="mem-carlos",
        role="Lead Data Engineer",
    )
    assert invite.status == MembershipStatus.INVITED
    assert invite.project_id == "proj-100"
    assert invite.member_id == "mem-carlos"
    assert invite.joined_at is None

    # 2. Accept invitation
    joined = service.accept_invitation(
        membership_id=invite.id,
        local_workspace_path="proyectos/pipeline_ingesta",
    )
    assert joined.status == MembershipStatus.JOINED
    assert joined.local_workspace_path == "proyectos/pipeline_ingesta"
    assert joined.joined_at is not None

    # Verify retrieval
    members = service.get_project_members("proj-100")
    assert len(members) == 1
    assert members[0].id == invite.id
    assert members[0].status == MembershipStatus.JOINED


def test_decline_invitation():
    """Verify declining an invitation."""
    service = MembershipService()
    invite = service.create_invitation(
        project_id="proj-200",
        member_id="mem-andrea",
        role="UI Developer",
    )
    declined = service.decline_invitation(invite.id)
    assert declined.status == MembershipStatus.DECLINED


def test_invalid_membership_lookup():
    """Verify error on nonexistent membership id."""
    service = MembershipService()
    with pytest.raises(KeyError):
        service.accept_invitation("non-existent-id", "path")
