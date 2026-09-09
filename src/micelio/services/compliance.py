"""SOC2 and GDPR Automated Compliance Auditor."""

import re
from typing import Any
from pydantic import BaseModel, ConfigDict
from micelio.domain.models import SynapseEvent

class AuditFinding(BaseModel):
    model_config = ConfigDict(frozen=True)
    event_id: str
    severity: str  # "LOW", "MEDIUM", "HIGH"
    description: str

class ComplianceReport(BaseModel):
    model_config = ConfigDict(frozen=True)
    project_id: str
    total_events_scanned: int
    findings: tuple[AuditFinding, ...]
    is_compliant: bool

class ComplianceAuditor:
    """Scans project events for compliance violations (e.g., PII leaks)."""
    
    # Simple heuristics for PII detection
    EMAIL_REGEX = re.compile(r"[\w\.-]+@[\w\.-]+\.\w+")
    SSN_REGEX = re.compile(r"\b\d{3}-\d{2}-\d{4}\b")
    CREDIT_CARD_REGEX = re.compile(r"\b(?:\d[ -]*?){13,16}\b")
    
    def run_audit(self, project_id: str, events: list[SynapseEvent]) -> ComplianceReport:
        """Run compliance audit on a list of project events."""
        findings = []
        
        for event in events:
            payload_str = str(event.payload)
            
            # Check for PII (Emails)
            if self.EMAIL_REGEX.search(payload_str):
                findings.append(AuditFinding(
                    event_id=event.event_id,
                    severity="HIGH",
                    description="Potential PII leak detected: Email address found in event payload."
                ))
                
            # Check for SSN
            if self.SSN_REGEX.search(payload_str):
                findings.append(AuditFinding(
                    event_id=event.event_id,
                    severity="CRITICAL",
                    description="Critical PII leak detected: Social Security Number found in event payload."
                ))
                
            # Check for Credit Cards
            if self.CREDIT_CARD_REGEX.search(payload_str):
                findings.append(AuditFinding(
                    event_id=event.event_id,
                    severity="CRITICAL",
                    description="PCI-DSS violation: Credit Card number found in event payload."
                ))
                
        is_compliant = len([f for f in findings if f.severity in ("HIGH", "CRITICAL")]) == 0
        
        return ComplianceReport(
            project_id=project_id,
            total_events_scanned=len(events),
            findings=tuple(findings),
            is_compliant=is_compliant
        )
