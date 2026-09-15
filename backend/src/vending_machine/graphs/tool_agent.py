"""Reusable LangGraph loop for agents that can call tools."""

from typing import Any

from langchain_core.messages import SystemMessage
from langgraph.checkpoint.memory import InMemorySaver
from langgraph.graph import END, START, MessagesState, StateGraph
from langgraph.prebuilt import ToolNode, tools_condition

from vending_machine.agents.base import AgentDefinition
from vending_machine.ai.config import load_settings
from vending_machine.ai.providers import build_chat_model


def build_tool_agent_graph(
    definition: AgentDefinition,
    checkpointer: Any = None,
):
    """Build an assistant-to-tools loop from a domain-specific agent definition."""
    tools = list(definition.tools)
    model_settings = definition.model_settings
    if model_settings is None:
        model_settings = load_settings().model
    model = build_chat_model(model_settings).bind_tools(tools)
    system_message = SystemMessage(content=definition.system_prompt)

    # Graph Nodes
    def assistant(state: MessagesState) -> dict:
        response = model.invoke([system_message] + state["messages"])
        return {"messages": [response]}

    # Loop Wiring
    # assistant -> tools -> assistant, until the model answers without a tool call.
    builder = (
        StateGraph(MessagesState)
        .add_node("assistant", assistant)
        .add_node("tools", ToolNode(tools))
        .add_edge(START, "assistant")
        .add_conditional_edges("assistant", tools_condition, {"tools": "tools", END: END})
        .add_edge("tools", "assistant")
    )
    if checkpointer is None:
        checkpointer = InMemorySaver()
    return builder.compile(checkpointer=checkpointer)
