"""Server-lifetime conversation management for vending-machine sessions."""

import json
import threading
from collections.abc import Iterator
from dataclasses import dataclass
from typing import Any
from uuid import uuid4

from langchain_core.messages import AIMessage, AIMessageChunk, HumanMessage

from vending_machine.agents.vending_machine import build_vending_machine_graph


class ConversationNotFoundError(Exception):
    """Raised when a client references an unavailable conversation."""


@dataclass
class Conversation:
    """The state needed to continue one customer conversation."""

    graph: Any
    config: dict[str, dict[str, str]]
    lock: Any


class ConversationManager:
    """Maintain in-memory LangGraph conversations for the current server process."""

    def __init__(self, currency: str) -> None:
        self._currency = currency
        self._conversations: dict[str, Conversation] = {}
        self._lock = threading.Lock()

    def start_conversation(self) -> str:
        """Create a new conversation and return its opaque identifier."""
        conversation_id = str(uuid4())
        conversation = Conversation(
            graph=build_vending_machine_graph(
                session_id=conversation_id,
                currency=self._currency,
            ),
            config={"configurable": {"thread_id": conversation_id}},
            lock=threading.Lock(),
        )
        with self._lock:
            self._conversations[conversation_id] = conversation
        return conversation_id

    def get_conversation(self, conversation_id: str) -> Conversation:
        """Return a conversation or raise when it is unavailable."""
        with self._lock:
            conversation = self._conversations.get(conversation_id)
        if conversation is None:
            raise ConversationNotFoundError(conversation_id)
        return conversation

    def stream_message(self, conversation_id: str, content: str) -> Iterator[str]:
        """Send one customer message and stream visible assistant output as SSE events."""
        conversation = self.get_conversation(conversation_id)
        response_parts: list[str] = []

        with conversation.lock:
            for message, _metadata in conversation.graph.stream(
                {"messages": [HumanMessage(content=content)]},
                config=conversation.config,
                stream_mode="messages",
            ):
                if isinstance(message, AIMessageChunk):
                    text = _content_as_text(message.content)
                    if text != "":
                        response_parts.append(text)
                        yield _format_sse_event("token", {"text": text})

            if response_parts == []:
                text = _get_final_response(conversation)
                if text != "":
                    response_parts.append(text)
                    yield _format_sse_event("token", {"text": text})

        yield _format_sse_event(
            "complete",
            {
                "conversation_id": conversation_id,
                "content": "".join(response_parts),
            },
        )


def _get_final_response(conversation: Conversation) -> str:
    state = conversation.graph.get_state(conversation.config)
    messages = state.values.get("messages", [])
    for message in reversed(messages):
        if isinstance(message, AIMessage) and message.tool_calls == []:
            return _content_as_text(message.content)
    return ""


def _content_as_text(content: Any) -> str:
    if isinstance(content, str):
        return content
    if isinstance(content, list):
        text_parts: list[str] = []
        for item in content:
            if isinstance(item, str):
                text_parts.append(item)
            elif isinstance(item, dict):
                text = item.get("text")
                if isinstance(text, str):
                    text_parts.append(text)
        return "".join(text_parts)
    return ""


def _format_sse_event(event: str, data: dict[str, str]) -> str:
    payload = json.dumps(data, ensure_ascii=False)
    return f"event: {event}\ndata: {payload}\n\n"
