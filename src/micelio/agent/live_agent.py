"""Live AI Agent that listens to the SynapseBus and responds via LLM."""

import asyncio
from micelio.core.synapse_bus import SynapseBus
from micelio.domain.models import SynapseEvent, SynapseEventType
from micelio.agent.llm_connector import LLMConnector
from micelio.core.logger import logger
import uuid

class LiveAgent:
    """An autonomous AI agent connected to a project's SynapseBus."""

    def __init__(
        self,
        agent_id: str,
        project_id: str,
        bus: SynapseBus,
        llm: LLMConnector,
        system_prompt: str = "You are a helpful AI collaborator."
    ):
        self.agent_id = agent_id
        self.project_id = project_id
        self.bus = bus
        self.llm = llm
        self.system_prompt = system_prompt
        self._task: asyncio.Task | None = None
        self._queue: asyncio.Queue[SynapseEvent] = asyncio.Queue()

    def start(self) -> None:
        """Subscribe to the bus and start the background worker loop."""
        self.bus.subscribe(self.project_id, self.agent_id, self._on_event)
        self._task = asyncio.create_task(self._worker_loop())
        logger.info(f"Agent {self.agent_id} joined project {self.project_id}")

    async def stop(self) -> None:
        """Unsubscribe and stop the background worker."""
        self.bus.unsubscribe(self.project_id, self.agent_id)
        if self._task:
            self._task.cancel()
            try:
                await self._task
            except asyncio.CancelledError:
                pass
        logger.info(f"Agent {self.agent_id} left project {self.project_id}")

    async def _on_event(self, event: SynapseEvent) -> None:
        """Callback invoked by SynapseBus. Put event in queue to avoid blocking the bus."""
        await self._queue.put(event)

    async def _worker_loop(self) -> None:
        """Process incoming messages sequentially."""
        try:
            while True:
                event = await self._queue.get()
                
                # Check if we should respond
                # We respond if the message is targeted at us specifically
                if event.target_agent_id == self.agent_id and event.source_agent_id != self.agent_id:
                    await self._handle_direct_message(event)
                    
                self._queue.task_done()
        except asyncio.CancelledError:
            pass

    async def _handle_direct_message(self, event: SynapseEvent) -> None:
        """Use LLM to generate a response and publish it to the bus."""
        # 1. Fetch recent history from the bus for context
        history = self.bus.get_project_history(self.project_id)
        
        # 2. Build contextual prompt
        context_lines = []
        for e in history[-10:]: # last 10 events
            context_lines.append(f"[{e.source_agent_id}->{e.target_agent_id}]: {e.payload}")
        
        context_str = "\n".join(context_lines)
        user_message = (
            f"You received a direct message from {event.source_agent_id}.\n"
            f"Message: {event.payload}\n"
            f"Recent Office Context:\n{context_str}\n\n"
            f"Provide your response."
        )

        # 3. Ask LLM
        response_text = await self.llm.generate_response(
            system_prompt=self.system_prompt,
            user_message=user_message
        )

        # 4. Emit back to the bus
        response_event = SynapseEvent(
            event_id=f"evt-{uuid.uuid4().hex[:8]}",
            project_id=self.project_id,
            source_agent_id=self.agent_id,
            target_agent_id=event.source_agent_id, # Reply to sender
            event_type=SynapseEventType.AGENT_RESPONSE,
            payload={"response": response_text, "reply_to": event.event_id}
        )
        
        await self.bus.publish(response_event)
