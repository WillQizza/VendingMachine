"""Provider-neutral definitions shared by application agents."""

from dataclasses import dataclass
from typing import Sequence

from langchain_core.tools import BaseTool

from vending_machine.ai.config import ModelSettings


@dataclass(frozen=True)
class AgentDefinition:
    """The domain-specific inputs needed to build a tool-using agent."""

    name: str
    system_prompt: str
    tools: Sequence[BaseTool]
    model_settings: ModelSettings | None = None
