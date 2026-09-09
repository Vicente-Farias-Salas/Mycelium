"""Unit tests for real-time SynapseBus (inter-agent office communication)."""

import asyncio
import pytest

from micelio.core.synapse_bus import SynapseBus
from micelio.domain.models import SynapseEvent, SynapseEventType


@pytest.mark.asyncio
async def test_synapse_bus_subscribe_and_broadcast():
    """Verify agents can subscribe to a project and receive broadcast events."""
    bus = SynapseBus()
    received_agent_1: list[SynapseEvent] = []
    received_agent_2: list[SynapseEvent] = []

    async def callback_1(event: SynapseEvent) -> None:
        received_agent_1.append(event)

    async def callback_2(event: SynapseEvent) -> None:
        received_agent_2.append(event)

    bus.subscribe(project_id="proj-1", agent_id="agt-1", callback=callback_1)
    bus.subscribe(project_id="proj-1", agent_id="agt-2", callback=callback_2)

    event = SynapseEvent(
        event_id="evt-bcast",
        project_id="proj-1",
        source_agent_id="agt-boss",
        target_agent_id="BROADCAST",
        event_type=SynapseEventType.OFFICE_CHATTER,
        payload={"msg": "Bienvenidos a la oficina virtual del proyecto"},
    )

    await bus.publish(event)
    await asyncio.sleep(0.01)

    assert len(received_agent_1) == 1
    assert len(received_agent_2) == 1
    assert received_agent_1[0].event_id == "evt-bcast"
    assert received_agent_2[0].event_id == "evt-bcast"


@pytest.mark.asyncio
async def test_synapse_bus_targeted_message():
    """Verify targeted A2A messages reach only the intended agent."""
    bus = SynapseBus()
    received_agent_1: list[SynapseEvent] = []
    received_agent_2: list[SynapseEvent] = []

    async def callback_1(event: SynapseEvent) -> None:
        received_agent_1.append(event)

    async def callback_2(event: SynapseEvent) -> None:
        received_agent_2.append(event)

    bus.subscribe(project_id="proj-2", agent_id="agt-backend", callback=callback_1)
    bus.subscribe(project_id="proj-2", agent_id="agt-frontend", callback=callback_2)

    event = SynapseEvent(
        event_id="evt-target",
        project_id="proj-2",
        source_agent_id="agt-backend",
        target_agent_id="agt-frontend",
        event_type=SynapseEventType.AGENT_QUERY,
        payload={"schema": "UserDTO"},
    )

    await bus.publish(event)
    await asyncio.sleep(0.01)

    # Only frontend should receive it
    assert len(received_agent_1) == 0
    assert len(received_agent_2) == 1
    assert received_agent_2[0].payload["schema"] == "UserDTO"


def test_synapse_bus_immutable_history():
    """Verify event history returns an immutable tuple and tracks project events."""
    bus = SynapseBus()
    event = SynapseEvent(
        event_id="evt-hist",
        project_id="proj-3",
        source_agent_id="agt-1",
        target_agent_id="BROADCAST",
        event_type=SynapseEventType.STATE_MUTATION,
        payload={"diff": "Added index.html"},
    )

    bus.record_event(event)
    history = bus.get_project_history("proj-3")
    assert isinstance(history, tuple)
    assert len(history) == 1
    assert history[0].event_id == "evt-hist"

    # Empty project history
    assert bus.get_project_history("non-existent") == ()
