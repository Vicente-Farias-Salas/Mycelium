"""Unit tests for the LLM Connector."""

import pytest
import os
from micelio.agent.llm_connector import LLMConnector

@pytest.mark.asyncio
async def test_llm_connector_simulated_fallback():
    """Test the fallback mode when no API keys are present."""
    # Ensure no API key
    if "OPENAI_API_KEY" in os.environ:
        del os.environ["OPENAI_API_KEY"]
        
    connector = LLMConnector(default_model="gpt-4o-mini")
    
    response = await connector.generate_response(
        system_prompt="You are a helpful agent.",
        user_message="Hello World"
    )
    
    assert "Simulated AI Response" in response
    assert "Hello World" in response

@pytest.mark.asyncio
async def test_llm_connector_error_handling(monkeypatch):
    """Test error handling when litellm throws an exception."""
    
    async def mock_acompletion(*args, **kwargs):
        raise Exception("LiteLLM API Error")
        
    import litellm
    monkeypatch.setattr(litellm, "acompletion", mock_acompletion)
    
    connector = LLMConnector(default_model="dummy/model")
    
    with pytest.raises(Exception, match="LiteLLM API Error"):
        await connector.generate_response(
            system_prompt="System",
            user_message="User"
        )
