"""Unit tests for the Churn Predictor service."""

from micelio.domain.billing import SubscriptionTier, Tenant
from micelio.services.churn_predictor import ChurnPredictor, ChurnRiskScore

def test_calculate_high_risk_churn():
    """Test high risk calculation for low engagement and high support tickets."""
    tenant = Tenant(
        id="tenant-123",
        name="Acme Corp",
        subscription_tier=SubscriptionTier.STARTER
    )
    predictor = ChurnPredictor()
    
    result = predictor.calculate_risk(tenant, recent_events_count=50, support_tickets_count=10)
    
    assert isinstance(result, ChurnRiskScore)
    assert result.tenant_id == "tenant-123"
    assert result.risk_level in ("HIGH", "CRITICAL")
    assert "Low A2A event engagement" in result.key_factors
    assert "High number of unresolved support tickets" in result.key_factors

def test_calculate_low_risk_churn():
    """Test low risk calculation for high engagement."""
    tenant = Tenant(
        id="tenant-456",
        name="Tech Giant",
        subscription_tier=SubscriptionTier.ENTERPRISE
    )
    predictor = ChurnPredictor()
    
    result = predictor.calculate_risk(tenant, recent_events_count=15000, support_tickets_count=1)
    
    assert result.risk_level == "LOW"
    assert result.risk_score == 0.0
    assert "High platform usage" in result.key_factors
