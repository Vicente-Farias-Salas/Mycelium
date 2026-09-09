"""Agent-to-Agent Shared Contract Validator."""

from typing import Any
import jsonschema
from jsonschema.exceptions import ValidationError
from micelio.domain.models import LivingProject
# Since SynapseEventRequest is in app.py and we don't want circular imports,
# we use typing Any or redefine it loosely here, or just import it locally inside the method,
# OR we can just pass the payload directly to the validator.

class ContractViolationError(Exception):
    """Raised when an agent violates the established shared contract."""
    pass

class ContractValidator:
    """Validates Synapse Events against dynamic JSONSchemas defined in the project."""

    def validate_event(self, project: LivingProject, event: Any) -> None:
        """
        Check if the event payload matches any contract defined in the project.
        Contracts are stored in project.shared_contracts as JSONSchema dicts keyed by event_type.name.
        """
        # If no contracts defined, allow all
        if not project.shared_contracts:
            return

        event_key = event.event_type.name
        
        # Check if there is a specific contract for this event type
        contract_schema = project.shared_contracts.get(event_key)
        
        if not contract_schema:
            # Maybe there's a wildcard "ALL" contract
            contract_schema = project.shared_contracts.get("ALL")

        if contract_schema:
            try:
                jsonschema.validate(instance=event.payload, schema=contract_schema)
            except ValidationError as e:
                raise ContractViolationError(f"Agent {event.source_agent_id} violated contract for {event_key}: {e.message}")
