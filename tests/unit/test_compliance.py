"""Unit tests for the Compliance service."""

from micelio.domain.models import SynapseEvent, SynapseEventType
from micelio.services.compliance import ComplianceAuditor

def test_compliance_auditor_clean():
    """Verify clean events pass compliance."""
    event = SynapseEvent(
        event_id="evt-1",
        project_id="prj-1",
        source_agent_id="agt-1",
        target_agent_id="agt-2",
        event_type=SynapseEventType.AGENT_QUERY,
        payload={"question": "How do we scale?"}
    )
    
    auditor = ComplianceAuditor()
    report = auditor.run_audit("prj-1", [event])
    
    assert report.is_compliant
    assert report.total_events_scanned == 1
    assert len(report.findings) == 0

def test_compliance_auditor_pii_leak():
    """Verify PII leak fails compliance."""
    event = SynapseEvent(
        event_id="evt-2",
        project_id="prj-1",
        source_agent_id="agt-1",
        target_agent_id="agt-2",
        event_type=SynapseEventType.AGENT_QUERY,
        payload={"data": "User contact is test@example.com"}
    )
    
    auditor = ComplianceAuditor()
    report = auditor.run_audit("prj-1", [event])
    
    assert not report.is_compliant
    assert len(report.findings) == 1
    assert report.findings[0].severity == "HIGH"
    assert "Email" in report.findings[0].description
