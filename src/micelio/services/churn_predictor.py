"""Predictive Churn AI module for Mycelium Enterprise SaaS."""

import math
from pydantic import BaseModel, ConfigDict
from micelio.domain.billing import Tenant

class ChurnRiskScore(BaseModel):
    model_config = ConfigDict(frozen=True)
    tenant_id: str
    risk_score: float  # 0.0 to 1.0
    risk_level: str  # "LOW", "MEDIUM", "HIGH", "CRITICAL"
    key_factors: tuple[str, ...]

class ChurnPredictor:
    """Calculates heuristic and ML-based churn risks for tenants based on their activity."""
    
    def calculate_risk(self, tenant: Tenant, recent_events_count: int, support_tickets_count: int) -> ChurnRiskScore:
        """
        Calculate churn risk score.
        A heuristic model mimicking a trained ML pipeline.
        """
        score = 0.0
        factors = []
        
        # Factor 1: Engagement (Events Count)
        if recent_events_count < 100:
            score += 0.4
            factors.append("Low A2A event engagement")
        elif recent_events_count > 10000:
            score -= 0.2
            factors.append("High platform usage")
            
        # Factor 2: Support Tickets
        if support_tickets_count > 5:
            score += 0.3
            factors.append("High number of unresolved support tickets")
            
        # Factor 3: Subscription Tier
        if tenant.tier.name == "STARTER":
            score += 0.1
            factors.append("Starter tier historically has higher churn")
            
        # Normalize score
        score = min(max(score, 0.0), 1.0)
        
        if score < 0.3:
            level = "LOW"
        elif score < 0.6:
            level = "MEDIUM"
        elif score < 0.8:
            level = "HIGH"
        else:
            level = "CRITICAL"
            
        return ChurnRiskScore(
            tenant_id=tenant.tenant_id,
            risk_score=round(score, 3),
            risk_level=level,
            key_factors=tuple(factors)
        )
