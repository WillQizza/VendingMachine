"""Provider adapters used by the agent runtime."""

import os

from langchain_core.language_models.chat_models import BaseChatModel
from langchain_openai import ChatOpenAI

from vending_machine.ai.config import ModelSettings


def build_chat_model(settings: ModelSettings) -> BaseChatModel:
    """Build the chat model for an agent from provider-neutral settings."""
    if settings.provider == "openai":
        api_key = os.getenv("AI_API_KEY", "").strip()
        if api_key == "":
            raise RuntimeError("AI_API_KEY must be set to use the OpenAI provider")
        return ChatOpenAI(
            model=settings.model,
            temperature=settings.temperature,
            max_tokens=settings.max_tokens,
            streaming=True,
            api_key=api_key,
            use_responses_api=True,
        )
    else:
        raise ValueError(
            f"Unsupported AI provider '{settings.provider}'. "
            "Add its adapter in vending_machine.ai.providers."
        )
