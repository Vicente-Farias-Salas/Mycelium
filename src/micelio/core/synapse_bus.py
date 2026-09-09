"""Real-time Synapse Bus for Agent-to-Agent Office Communication."""

import asyncio
from collections.abc import Awaitable, Callable
from collections import defaultdict
from micelio.domain.models import SynapseEvent

EventCallback = Callable[[SynapseEvent], Awaitable[None]]


class SynapseBus:
    """In-memory asynchronous event bus supporting targeted & broadcast A2A messages."""

    def __init__(self) -> None:
        # project_id -> list of (agent_id, callback)
        self._subscribers: dict[str, list[tuple[str, EventCallback]]] = defaultdict(list)
        # project_id -> list of events
        self._history: dict[str, list[SynapseEvent]] = defaultdict(list)
        self._lock = asyncio.Lock()

    def subscribe(self, project_id: str, agent_id: str, callback: EventCallback) -> None:
        """Subscribe an agent to project events."""
        # Avoid duplicate subscriptions
        current = self._subscribers[project_id]
        self._subscribers[project_id] = [
            (aid, cb) for (aid, cb) in current if aid != agent_id
        ] + [(agent_id, callback)]

    def unsubscribe(self, project_id: str, agent_id: str) -> None:
        """Unsubscribe an agent from project events."""
        if project_id in self._subscribers:
            self._subscribers[project_id] = [
                (aid, cb) for (aid, cb) in self._subscribers[project_id] if aid != agent_id
            ]

    def record_event(self, event: SynapseEvent) -> None:
        """Store an event into immutable history."""
        self._history[event.project_id].append(event)

    def get_project_history(self, project_id: str) -> tuple[SynapseEvent, ...]:
        """Return an immutable snapshot of events for a project."""
        return tuple(self._history.get(project_id, []))

    async def publish(self, event: SynapseEvent) -> None:
        """Dispatch event to subscribed agents (broadcast or targeted) and log it."""
        self.record_event(event)
        subscribers = self._subscribers.get(event.project_id, [])
        tasks: list[asyncio.Task[None]] = []

        for agent_id, callback in subscribers:
            should_deliver = (
                event.target_agent_id == "BROADCAST"
                or event.target_agent_id == agent_id
            )
            if should_deliver:
                tasks.append(asyncio.create_task(self._safe_dispatch(callback, event)))

        if tasks:
            await asyncio.gather(*tasks, return_exceptions=True)

    @staticmethod
    async def _safe_dispatch(callback: EventCallback, event: SynapseEvent) -> None:
        """Deliver event safely without crashing the bus if a callback raises."""
        try:
            await callback(event)
        except Exception:  # noqa: BLE001
            # In production, this would go to structured logging
            pass
