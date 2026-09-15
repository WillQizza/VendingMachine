import sys
import unittest
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import patch

from fastapi.testclient import TestClient
from langchain_core.messages import AIMessage, AIMessageChunk


sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from vending_machine.ai.config import AppSettings, ModelSettings
from vending_machine.main import app


class FakeGraph:
    def __init__(self, chunks: list[str] | None = None, fail: bool = False) -> None:
        self.chunks = chunks or []
        self.fail = fail

    def stream(self, values: dict, config: dict, stream_mode: str):
        if self.fail:
            raise RuntimeError("stream failed")
        for chunk in self.chunks:
            yield AIMessageChunk(content=chunk), {}

    def get_state(self, config: dict) -> SimpleNamespace:
        return SimpleNamespace(values={"messages": [AIMessage(content="")]})


class ConversationApiTests(unittest.TestCase):
    def setUp(self) -> None:
        self.graphs: list[FakeGraph] = []
        self.settings = AppSettings(model=ModelSettings(), currency="USD")

    def test_create_and_stream_a_conversation(self) -> None:
        with self._client() as client:
            created = client.post("/conversations")
            conversation_id = created.json()["conversation_id"]
            response = client.post(
                f"/conversations/{conversation_id}/messages",
                json={"content": "Show me a drink."},
            )

        self.assertEqual(created.status_code, 201)
        self.assertTrue(response.headers["content-type"].startswith("text/event-stream"))
        self.assertIn('event: token\ndata: {"text": "Your total is "}', response.text)
        self.assertIn('event: token\ndata: {"text": "USD 2.50."}', response.text)
        self.assertIn(
            f'event: complete\ndata: {{"conversation_id": "{conversation_id}", "content": "Your total is USD 2.50."}}',
            response.text,
        )
        self.assertEqual(len(self.graphs), 1)

    def test_unknown_conversation_returns_not_found(self) -> None:
        with self._client() as client:
            response = client.post(
                "/conversations/missing/messages",
                json={"content": "Hello"},
            )

        self.assertEqual(response.status_code, 404)
        self.assertEqual(response.json(), {"detail": "Conversation not found."})

    def test_blank_message_is_rejected(self) -> None:
        with self._client() as client:
            created = client.post("/conversations")
            conversation_id = created.json()["conversation_id"]
            response = client.post(
                f"/conversations/{conversation_id}/messages",
                json={"content": "   "},
            )

        self.assertEqual(response.status_code, 422)

    def test_stream_failures_become_sse_error_events(self) -> None:
        with self._client(fail=True) as client:
            created = client.post("/conversations")
            conversation_id = created.json()["conversation_id"]
            response = client.post(
                f"/conversations/{conversation_id}/messages",
                json={"content": "Hello"},
            )

        self.assertEqual(response.status_code, 200)
        self.assertEqual(
            response.text,
            'event: error\ndata: {"detail": "The conversation could not be completed."}\n\n',
        )

    def test_history_routes_are_not_exposed(self) -> None:
        with self._client() as client:
            created = client.post("/conversations")
            conversation_id = created.json()["conversation_id"]
            response = client.get(f"/conversations/{conversation_id}/messages")

        self.assertEqual(response.status_code, 405)

    def _client(self, fail: bool = False):
        def build_graph(**_kwargs) -> FakeGraph:
            graph = FakeGraph(
                chunks=["Your total is ", "USD 2.50."],
                fail=fail,
            )
            self.graphs.append(graph)
            return graph

        load_settings = patch(
            "vending_machine.main.load_settings",
            return_value=self.settings,
        )
        graph_builder = patch(
            "vending_machine.conversations.build_vending_machine_graph",
            side_effect=build_graph,
        )
        return _PatchedTestClient(load_settings, graph_builder)


class _PatchedTestClient:
    def __init__(self, load_settings, graph_builder) -> None:
        self.load_settings = load_settings
        self.graph_builder = graph_builder
        self.client: TestClient | None = None

    def __enter__(self) -> TestClient:
        self.load_settings.start()
        self.graph_builder.start()
        self.client = TestClient(app)
        return self.client.__enter__()

    def __exit__(self, exc_type, exc_value, traceback) -> None:
        if self.client is not None:
            self.client.__exit__(exc_type, exc_value, traceback)
        self.graph_builder.stop()
        self.load_settings.stop()
