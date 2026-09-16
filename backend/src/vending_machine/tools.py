import threading

from langchain_core.tools import tool

# Temporary until I get around to setting up the database stuff
_INVENTORY = {
    "A1": {"name": "Cola", "price": 2.50, "stock": 4, "description": "You can't go wrong with this classic."},
    "A2": {"name": "Sparkling Water", "price": 2.00, "stock": 2, "description": "Sparkles just like it should!"},
    "A3": {"name": "Iced Tea", "price": 2.75, "stock": 0, "description": "Refreshing drink!"},
    "B1": {"name": "Salted Pretzels", "price": 1.75, "stock": 7, "description": "Salty, yet satisfying!"},
}
_INVENTORY_LOCK = threading.Lock()


def list_inventory_slots() -> list[dict]:
    """Shared with the inventory router. 
        TODO: Need to replace this later once I setup the db"""
    with _INVENTORY_LOCK:
        return [{"slot": slot, **item} for slot, item in _INVENTORY.items()]


@tool
def list_inventory() -> list[dict]:
    """List every slot with its name, price, description, and remaining stock."""
    return list_inventory_slots()


@tool
def purchase_item(slot: str) -> dict:
    """Charge for a slot and dispense its item after payment is captured."""
    normalized_slot = slot.upper()
    with _INVENTORY_LOCK:
        item = _INVENTORY.get(normalized_slot)
        if item is None:
            return {"paid": False, "reason": f"No slot {slot} in this machine."}
        elif item["stock"] <= 0:
            return {"paid": False, "reason": "Out of stock."}
        else:
            item["stock"] -= 1
            return {
                "paid": True,
                "dispensed": True,
                "slot": normalized_slot,
                "name": item["name"],
                "amount": item["price"],
            }


VENDING_TOOLS = [list_inventory, purchase_item]
