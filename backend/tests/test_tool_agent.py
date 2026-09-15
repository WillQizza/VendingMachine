import sys
import unittest
from pathlib import Path
from unittest.mock import MagicMock, patch

from langchain_core.tools import tool


sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from vending_machine.agents.base import AgentDefinition
from vending_machine.ai.config import ModelSettings
from vending_machine.graphs.tool_agent import build_tool_agent_graph


@tool
def sample_tool() -> str:
    """Return a fixed value for the graph construction test."""
    return "ok"


class ToolAgentTests(unittest.TestCase):
    def test_explicit_model_settings_do_not_load_global_settings(self) -> None:
        settings = ModelSettings(model="test-model")
        definition = AgentDefinition(
            name="test_agent",
            system_prompt="You are a test agent.",
            tools=[sample_tool],
            model_settings=settings,
        )
        model = MagicMock()
        model.bind_tools.return_value = model

        with patch("vending_machine.graphs.tool_agent.load_settings") as load_settings:
            with patch(
                "vending_machine.graphs.tool_agent.build_chat_model",
                return_value=model,
            ) as build_chat_model:
                build_tool_agent_graph(definition)

        load_settings.assert_not_called()
        build_chat_model.assert_called_once_with(settings)
