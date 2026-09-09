"""Unit tests for the Rate Limiter."""

import time
import pytest
from micelio.core.rate_limiter import AgentRateLimiter, RateLimitExceededError

def test_rate_limiter_allows_under_limit():
    limiter = AgentRateLimiter(max_events=3, window_seconds=1.0)
    
    # Should allow 3 events immediately
    limiter.check_and_record("agt-1")
    limiter.check_and_record("agt-1")
    limiter.check_and_record("agt-1")
    
    # Different agent should be unaffected
    limiter.check_and_record("agt-2")

def test_rate_limiter_blocks_over_limit():
    limiter = AgentRateLimiter(max_events=2, window_seconds=1.0)
    
    limiter.check_and_record("agt-1")
    limiter.check_and_record("agt-1")
    
    with pytest.raises(RateLimitExceededError):
        limiter.check_and_record("agt-1")

def test_rate_limiter_window_expires():
    # Very short window
    limiter = AgentRateLimiter(max_events=1, window_seconds=0.1)
    
    limiter.check_and_record("agt-3")
    
    with pytest.raises(RateLimitExceededError):
        limiter.check_and_record("agt-3")
        
    time.sleep(0.15)
    
    # After sleep, window should clear
    limiter.check_and_record("agt-3")
