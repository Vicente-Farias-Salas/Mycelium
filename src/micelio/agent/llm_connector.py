"""LiteLLM Connector for Agent Intelligence."""

import os
from typing import Any
import litellm
from litellm import completion

from micelio.core.logger import logger

# To prevent litellm from telemetry logging in production environments:
litellm.telemetry = False

class LLMConnector:
    """Wrapper around LiteLLM to provide a unified interface for all agents."""

    def __init__(self, default_model: str = "gpt-4o-mini", default_temperature: float = 0.2):
        self.default_model = default_model
        self.default_temperature = default_temperature

    async def generate_response(
        self,
        system_prompt: str,
        user_message: str,
        model: str | None = None,
        temperature: float | None = None,
    ) -> str:
        """Generate an AI response using the configured provider."""
        model_name = model or self.default_model
        temp = temperature if temperature is not None else self.default_temperature

        # We assume the API Key is set in the environment variables 
        # (e.g. OPENAI_API_KEY, ANTHROPIC_API_KEY) by the platform's Config.
        
        # Fallback to dummy generation for testing if no key is set and model is generic
        if not os.environ.get("OPENAI_API_KEY") and "gpt" in model_name:
            logger.warning("No OPENAI_API_KEY set. Returning simulated response for local testing.")
            return f"Simulated AI Response to: {user_message[:20]}..."

        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_message},
        ]

        try:
            # LiteLLM abstracts the provider completely
            response = await litellm.acompletion(
                model=model_name,
                messages=messages,
                temperature=temp,
            )
            content = response.choices[0].message.content
            return content or ""
        except Exception as e:
            logger.error("LLM Generation failed", extra={"extra_ctx": {"error": str(e), "model": model_name}})
            raise
