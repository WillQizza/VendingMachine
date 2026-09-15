"""Definition and construction for the customer-facing vending agent."""

from typing import Any

from vending_machine.agents.base import AgentDefinition
from vending_machine.ai.config import ModelSettings
from vending_machine.graphs.tool_agent import build_tool_agent_graph
from vending_machine.prompts import build_vending_machine_prompt
from vending_machine.tools import VENDING_TOOLS


def create_vending_machine_agent(
    session_id: str,
    currency: str = "CAD",
    model_settings: ModelSettings | None = None,
) -> AgentDefinition:
    """Create the vending agent definition for one customer session."""
    return AgentDefinition(
        name="vending_machine",
        system_prompt=build_vending_machine_prompt(
            session_id=session_id,
            currency=currency,
        ),
        tools=VENDING_TOOLS,
        model_settings=model_settings,
    )


def build_vending_machine_graph(
    session_id: str,
    currency: str = "CAD",
    model_settings: ModelSettings | None = None,
    checkpointer: Any = None,
):
    """Build a vending-machine agent graph for one customer session."""
    agent = create_vending_machine_agent(
        session_id=session_id,
        currency=currency,
        model_settings=model_settings,
    )
    return build_tool_agent_graph(agent, checkpointer=checkpointer)
