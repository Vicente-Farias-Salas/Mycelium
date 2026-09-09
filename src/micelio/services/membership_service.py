"""MembershipService to manage project join requests and lifecycle."""

from datetime import datetime, timezone
import uuid
from micelio.domain.models import MembershipStatus, ProjectMembership


class MembershipService:
    """Manages project invitations, acceptance, rejection, and member listings."""

    def __init__(self) -> None:
        # membership_id -> ProjectMembership
        self._memberships: dict[str, ProjectMembership] = {}

    def create_invitation(
        self,
        project_id: str,
        member_id: str,
        role: str,
    ) -> ProjectMembership:
        """Create a new project invitation for a collaborator."""
        membership_id = f"mem-{uuid.uuid4().hex[:8]}"
        invite = ProjectMembership(
            id=membership_id,
            project_id=project_id,
            member_id=member_id,
            role_in_project=role,
            status=MembershipStatus.INVITED,
            local_workspace_path="",
            invited_at=datetime.now(timezone.utc),
            joined_at=None,
        )
        self._memberships[membership_id] = invite
        return invite

    def accept_invitation(
        self,
        membership_id: str,
        local_workspace_path: str,
    ) -> ProjectMembership:
        """Accept an invitation, registering the local workspace path."""
        invite = self._get_or_raise(membership_id)
        now = datetime.now(timezone.utc)
        # Create new immutable copy with updated status
        updated = invite.model_copy(
            update={
                "status": MembershipStatus.JOINED,
                "local_workspace_path": local_workspace_path,
                "joined_at": now,
            }
        )
        self._memberships[membership_id] = updated
        return updated

    def decline_invitation(self, membership_id: str) -> ProjectMembership:
        """Decline a project invitation."""
        invite = self._get_or_raise(membership_id)
        updated = invite.model_copy(update={"status": MembershipStatus.DECLINED})
        self._memberships[membership_id] = updated
        return updated

    def get_project_members(self, project_id: str) -> tuple[ProjectMembership, ...]:
        """Return all memberships associated with a project."""
        members = [m for m in self._memberships.values() if m.project_id == project_id]
        return tuple(members)

    def _get_or_raise(self, membership_id: str) -> ProjectMembership:
        """Retrieve membership or raise KeyError."""
        if membership_id not in self._memberships:
            raise KeyError(f"Membership '{membership_id}' not found.")
        return self._memberships[membership_id]
