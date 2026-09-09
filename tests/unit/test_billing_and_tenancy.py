"""Unit tests for multi-tenancy and commercial SaaS subscription quotas."""

import pytest

from micelio.domain.billing import SubscriptionTier, Tenant, TenantQuotaManager


def test_tenant_creation_and_quota():
    """Verify tenant configuration and default tier quotas."""
    tenant = Tenant(
        tenant_id="tenant-acme",
        name="Acme Corp",
        tier=SubscriptionTier.STARTER,
        max_active_projects=3,
        max_events_per_project=100,
    )
    assert tenant.tier == SubscriptionTier.STARTER
    assert tenant.max_active_projects == 3


def test_quota_manager_enforces_limits():
    """Verify TenantQuotaManager prevents exceeding subscription project quotas."""
    manager = TenantQuotaManager()
    tenant = Tenant(
        tenant_id="tenant-small",
        name="Small Agency",
        tier=SubscriptionTier.STARTER,
        max_active_projects=2,
    )
    manager.register_tenant(tenant)

    # 1st project: OK
    assert manager.can_create_project("tenant-small", current_active_projects=0) is True
    # 2nd project: OK
    assert manager.can_create_project("tenant-small", current_active_projects=1) is True
    # 3rd project: Blocked!
    assert manager.can_create_project("tenant-small", current_active_projects=2) is False


def test_enterprise_tier_unlimited():
    """Verify ENTERPRISE tier has unlimited headroom."""
    manager = TenantQuotaManager()
    enterprise_tenant = Tenant(
        tenant_id="tenant-mega",
        name="Global Bank",
        tier=SubscriptionTier.ENTERPRISE,
        max_active_projects=9999,
    )
    manager.register_tenant(enterprise_tenant)
    assert manager.can_create_project("tenant-mega", current_active_projects=500) is True
