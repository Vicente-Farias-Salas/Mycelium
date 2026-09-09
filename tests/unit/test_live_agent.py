"""Unit tests for the LiveAgent AI integration."""

import pytest
import asyncio
from unittest.mock import AsyncMock
from micelio.core.synapse_bus import SynapseBus
from micelio.agent.live_agent import LiveAgent
from micelio.domain.models import SynapseEvent, SynapseEventType


def _make_mock_llm() -> AsyncMock:
    """Create a mock LLM connector with a predictable response."""
    mock = AsyncMock()
    mock.generate_response = AsyncMock(return_value="I am a simulated response from the live agent.")
    return mock


@pytest.mark.asyncio
async def test_live_agent_responds_to_direct_message():
    """When a direct message targets the agent, it should reply via LLM."""
    bus = SynapseBus()
    llm = _make_mock_llm()

    agent = LiveAgent(
        agent_id="ai-bot",
        project_id="proj-123",
        bus=bus,
        llm=llm,
    )

    received_events: list[SynapseEvent] = []

    async def interceptor(event: SynapseEvent) -> None:
        received_events.append(event)

    # Register interceptor as "human-boss" — that's the target_agent_id 
    # the LiveAgent will reply to, so the bus will deliver to this subscriber.
    bus.subscribe("proj-123", "human-boss", interceptor)
    agent.start()

    incoming = SynapseEvent(
        event_id="evt-1",
        project_id="proj-123",
        source_agent_id="human-boss",
        target_agent_id="ai-bot",
        event_type=SynapseEventType.OFFICE_CHATTER,
        payload={"message": "Can you review this?"},
    )

    await bus.publish(incoming)

    # Wait for the agent's internal queue to drain completely.
    await asyncio.wait_for(agent._queue.join(), timeout=5.0)
    # One more tick for the response publish to propagate
    await asyncio.sleep(0.1)

    await agent.stop()

    # Filter only replies from ai-bot (the interceptor also gets the original)
    replies = [e for e in received_events if e.source_agent_id == "ai-bot"]
    assert len(replies) == 1
    reply = replies[0]
    assert reply.source_agent_id == "ai-bot"
    assert reply.target_agent_id == "human-boss"
    assert reply.event_type == SynapseEventType.AGENT_RESPONSE
    assert "I am a simulated response" in reply.payload["response"]
    assert reply.payload["reply_to"] == "evt-1"


@pytest.mark.asyncio
async def test_live_agent_ignores_broadcasts():
    """Broadcast messages should NOT trigger an LLM reply."""
    bus = SynapseBus()
    llm = _make_mock_llm()
    agent = LiveAgent(agent_id="ai-bot", project_id="proj-123", bus=bus, llm=llm)

    received_events: list[SynapseEvent] = []

    async def interceptor(event: SynapseEvent) -> None:
        if event.source_agent_id == "ai-bot":
            received_events.append(event)

    # Use BROADCAST listener to catch any potential reply
    bus.subscribe("proj-123", "observer", interceptor)
    agent.start()

    incoming = SynapseEvent(
        event_id="evt-2",
        project_id="proj-123",
        source_agent_id="human-boss",
        target_agent_id="BROADCAST",
        event_type=SynapseEventType.OFFICE_CHATTER,
        payload={"message": "Good morning everyone"},
    )
    await bus.publish(incoming)

    await asyncio.wait_for(agent._queue.join(), timeout=5.0)
    await asyncio.sleep(0.1)
    await agent.stop()

    assert len(received_events) == 0
    llm.generate_response.assert_not_called()


@pytest.mark.asyncio
async def test_live_agent_handle_direct_message_unit():
    """Directly test the _handle_direct_message method in isolation."""
    bus = SynapseBus()
    llm = _make_mock_llm()
    agent = LiveAgent(agent_id="ai-bot", project_id="proj-123", bus=bus, llm=llm)

    received_events: list[SynapseEvent] = []

    async def interceptor(event: SynapseEvent) -> None:
        received_events.append(event)

    # Subscribe as "human-boss" so the targeted reply reaches us
    bus.subscribe("proj-123", "human-boss", interceptor)

    incoming = SynapseEvent(
        event_id="evt-direct",
        project_id="proj-123",
        source_agent_id="human-boss",
        target_agent_id="ai-bot",
        event_type=SynapseEventType.OFFICE_CHATTER,
        payload={"message": "Direct test"},
    )

    await agent._handle_direct_message(incoming)

    assert len(received_events) == 1
    reply = received_events[0]
    assert reply.source_agent_id == "ai-bot"
    assert reply.target_agent_id == "human-boss"
    assert reply.event_type == SynapseEventType.AGENT_RESPONSE
    assert "I am a simulated response" in reply.payload["response"]
