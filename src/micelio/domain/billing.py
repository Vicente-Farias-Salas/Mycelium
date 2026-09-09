"""Commercial B2B multi-tenancy and subscription quota models."""

from enum import Enum
from pydantic import BaseModel, ConfigDict


class SubscriptionTier(str, Enum):
    """SaaS commercial tiers for B2B accounts."""
    STARTER = "STARTER"
    PROFESSIONAL = "PROFESSIONAL"
    ENTERPRISE = "ENTERPRISE"


class Tenant(BaseModel):
    """Enterprise customer organization / tenant."""
    model_config = ConfigDict(frozen=True)

    tenant_id: str
    name: str
    tier: SubscriptionTier = SubscriptionTier.STARTER
    max_active_projects: int = 3
    max_events_per_project: int = 100


class TenantQuotaManager:
    """Evaluates and enforces operational quotas per tenant."""

    def __init__(self) -> None:
        self._tenants: dict[str, Tenant] = {}

    def register_tenant(self, tenant: Tenant) -> None:
        """Register or update a tenant configuration."""
        self._tenants[tenant.tenant_id] = tenant

    def get_tenant(self, tenant_id: str) -> Tenant | None:
        """Retrieve tenant profile."""
        return self._tenants.get(tenant_id)

    def can_create_project(self, tenant_id: str, current_active_projects: int) -> bool:
        """Check if tenant has capacity to launch another project."""
        tenant = self.get_tenant(tenant_id)
        if not tenant:
            return True  # Default permissive if tenant not registered
        return current_active_projects < tenant.max_active_projects
