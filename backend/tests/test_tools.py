import sys
import unittest
from concurrent.futures import ThreadPoolExecutor
from copy import deepcopy
from pathlib import Path


sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from vending_machine import tools


class VendingToolTests(unittest.TestCase):
    def setUp(self) -> None:
        self.inventory = deepcopy(tools._INVENTORY)

    def tearDown(self) -> None:
        tools._INVENTORY.clear()
        tools._INVENTORY.update(self.inventory)

    def test_purchase_item_dispenses_the_selected_item(self) -> None:
        stock_before = tools._INVENTORY["A1"]["stock"]

        result = tools.purchase_item.invoke({"slot": "a1"})

        self.assertEqual(
            result,
            {
                "paid": True,
                "dispensed": True,
                "slot": "A1",
                "name": "Cola",
                "amount": 2.50,
            },
        )
        self.assertEqual(tools._INVENTORY["A1"]["stock"], stock_before - 1)

    def test_purchase_item_does_not_dispense_an_out_of_stock_item(self) -> None:
        result = tools.purchase_item.invoke({"slot": "A3"})

        self.assertEqual(result, {"paid": False, "reason": "Out of stock."})
        self.assertEqual(tools._INVENTORY["A3"]["stock"], 0)

    def test_purchase_item_only_sells_the_last_item_once(self) -> None:
        tools._INVENTORY["A1"]["stock"] = 1

        with ThreadPoolExecutor(max_workers=2) as executor:
            first_purchase = executor.submit(tools.purchase_item.invoke, {"slot": "A1"})
            second_purchase = executor.submit(tools.purchase_item.invoke, {"slot": "A1"})
            results = [first_purchase.result(), second_purchase.result()]

        paid_results = [result for result in results if result["paid"]]
        declined_results = [result for result in results if not result["paid"]]
        self.assertEqual(len(paid_results), 1)
        self.assertEqual(len(declined_results), 1)
        self.assertEqual(tools._INVENTORY["A1"]["stock"], 0)

    def test_vending_tools_do_not_expose_a_separate_dispense_operation(self) -> None:
        self.assertEqual([tool.name for tool in tools.VENDING_TOOLS], ["list_inventory", "purchase_item"])
