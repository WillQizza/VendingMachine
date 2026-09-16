import sys
import unittest
from copy import deepcopy
from pathlib import Path
from unittest.mock import patch

from fastapi.testclient import TestClient


sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from vending_machine import tools
from vending_machine.ai.config import AppSettings, ModelSettings
from vending_machine.main import app


class InventoryApiTests(unittest.TestCase):
    def setUp(self) -> None:
        self.inventory = deepcopy(tools._INVENTORY)
        self.settings = AppSettings(model=ModelSettings(), currency="USD")

    def tearDown(self) -> None:
        tools._INVENTORY.clear()
        tools._INVENTORY.update(self.inventory)

    def test_inventory_returns_every_slot(self) -> None:
        with self._client() as client:
            response = client.get("/inventory")

        self.assertEqual(response.status_code, 200)
        payload = response.json()
        self.assertEqual([slot["slot"] for slot in payload], list(tools._INVENTORY))
        self.assertEqual(
            payload[0],
            {
                "slot": "A1",
                "name": "Cola",
                "price": 2.50,
                "stock": 4,
                "description": "You can't go wrong with this classic.",
            },
        )

    def test_inventory_reflects_stock_changes(self) -> None:
        tools._INVENTORY["A1"]["stock"] = 0

        with self._client() as client:
            response = client.get("/inventory")

        slots = {slot["slot"]: slot for slot in response.json()}
        self.assertEqual(slots["A1"]["stock"], 0)

    def test_inventory_does_not_leak_extra_fields(self) -> None:
        tools._INVENTORY["A1"]["cost_basis"] = 0.40

        with self._client() as client:
            response = client.get("/inventory")

        self.assertNotIn("cost_basis", response.json()[0])

    def _client(self) -> TestClient:
        patcher = patch(
            "vending_machine.main.load_settings",
            return_value=self.settings,
        )
        patcher.start()
        self.addCleanup(patcher.stop)
        return TestClient(app)


if __name__ == "__main__":
    unittest.main()
