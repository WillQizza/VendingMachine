import json
import sys
import unittest
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import patch
from uuid import UUID

from langchain_core.messages import AIMessage, AIMessageChunk, HumanMessage


sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from vending_machine.conversations import ConversationManager, ConversationNotFoundError


class FakeGraph:
    def __init__(self, chunks: list[str] | None = None, final_response: str = "") -> None:
        self.chunks = chunks or []
        self.final_response = final_response
        self.stream_calls: list[tuple[dict, dict, str]] = []

    def stream(self, values: dict, config: dict, stream_mode: str):
        self.stream_calls.append((values, config, stream_mode))
        for chunk in self.chunks:
            yield AIMessageChunk(content=chunk), {}

    def get_state(self, config: dict) -> SimpleNamespace:
        return SimpleNamespace(
            values={"messages": [AIMessage(content=self.final_response)]}
        )


class ConversationManagerTests(unittest.TestCase):
    def setUp(self) -> None:
        self.graphs: list[FakeGraph] = []
        self.build_vending_machine_graph = patch(
            "vending_machine.conversations.build_vending_machine_graph",
            side_effect=self._build_graph,
        )
        self.mock_build_vending_machine_graph = self.build_vending_machine_graph.start()

    def tearDown(self) -> None:
        self.build_vending_machine_graph.stop()

    def _build_graph(self, **_kwargs) -> FakeGraph:
        graph = FakeGraph(chunks=["Hello", " there"])
        self.graphs.append(graph)
        return graph

    def test_start_conversation_builds_graph_with_server_currency(self) -> None:
        manager = ConversationManager(currency="usd")

        conversation_id = manager.start_conversation()

        UUID(conversation_id)
        self.mock_build_vending_machine_graph.assert_called_once_with(
            session_id=conversation_id,
            currency="usd",
        )
        conversation = manager.get_conversation(conversation_id)
        self.assertEqual(
            conversation.config,
            {"configurable": {"thread_id": conversation_id}},
        )

    def test_stream_message_reuses_the_same_graph_and_thread(self) -> None:
        manager = ConversationManager(currency="CAD")
        conversation_id = manager.start_conversation()

        first_events = list(manager.stream_message(conversation_id, "What is available?"))
        second_events = list(manager.stream_message(conversation_id, "How much is it?"))

        self.assertEqual(
            first_events[:2],
            [
                'event: token\ndata: {"text": "Hello"}\n\n',
                'event: token\ndata: {"text": " there"}\n\n',
            ],
        )
        self.assertEqual(
            self._event_data(first_events[-1]),
            {"conversation_id": conversation_id, "content": "Hello there"},
        )
        self.assertEqual(
            self._event_data(second_events[-1]),
            {"conversation_id": conversation_id, "content": "Hello there"},
        )

        graph = self.graphs[0]
        self.assertEqual(len(graph.stream_calls), 2)
        self.assertEqual(
            graph.stream_calls[0][0]["messages"],
            [HumanMessage(content="What is available?")],
        )
        self.assertEqual(
            graph.stream_calls[1][0]["messages"],
            [HumanMessage(content="How much is it?")],
        )
        self.assertEqual(
            graph.stream_calls[0][1],
            {"configurable": {"thread_id": conversation_id}},
        )
        self.assertEqual(graph.stream_calls[0][2], "messages")

    def test_stream_message_uses_final_state_when_no_tokens_are_streamed(self) -> None:
        self.build_vending_machine_graph.stop()
        self.build_vending_machine_graph = patch(
            "vending_machine.conversations.build_vending_machine_graph",
            return_value=FakeGraph(final_response="Use CAD 2.50."),
        )
        self.mock_build_vending_machine_graph = self.build_vending_machine_graph.start()
        manager = ConversationManager(currency="CAD")
        conversation_id = manager.start_conversation()

        events = list(manager.stream_message(conversation_id, "Price?"))

        self.assertEqual(
            events[0],
            'event: token\ndata: {"text": "Use CAD 2.50."}\n\n',
        )
        self.assertEqual(
            self._event_data(events[1]),
            {"conversation_id": conversation_id, "content": "Use CAD 2.50."},
        )

    def test_unknown_conversation_raises_not_found(self) -> None:
        manager = ConversationManager(currency="CAD")

        with self.assertRaises(ConversationNotFoundError):
            manager.get_conversation("missing")

    def _event_data(self, event: str) -> dict[str, str]:
        return json.loads(event.split("\ndata: ", maxsplit=1)[1].strip())
