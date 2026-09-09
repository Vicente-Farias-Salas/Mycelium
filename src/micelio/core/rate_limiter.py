"""Event rate limiting middleware for the SynapseBus."""

import time
from collections import defaultdict

class RateLimitExceededError(Exception):
    """Raised when an agent emits too many events in a short window."""
    pass

class AgentRateLimiter:
    """
    In-memory rate limiter using a sliding window algorithm.
    Ensures an individual agent does not flood the SynapseBus.
    """
    
    def __init__(self, max_events: int = 10, window_seconds: float = 1.0):
        self.max_events = max_events
        self.window_seconds = window_seconds
        # agent_id -> list of timestamps
        self._timestamps: dict[str, list[float]] = defaultdict(list)
        
    def check_and_record(self, agent_id: str) -> None:
        """
        Record an event for an agent and raise RateLimitExceededError if limit exceeded.
        """
        now = time.time()
        agent_history = self._timestamps[agent_id]
        
        # Prune old events outside the sliding window
        cutoff = now - self.window_seconds
        while agent_history and agent_history[0] < cutoff:
            agent_history.pop(0)
            
        if len(agent_history) >= self.max_events:
            raise RateLimitExceededError(f"Agent {agent_id} exceeded rate limit of {self.max_events} events per {self.window_seconds}s.")
            
        agent_history.append(now)
