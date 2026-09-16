"""HTTP routes for the vending-machine inventory."""

from fastapi import APIRouter

from vending_machine.api.schemas import InventorySlot
from vending_machine.tools import list_inventory_slots


router = APIRouter()


@router.get("/inventory", response_model=list[InventorySlot])
def get_inventory() -> list[dict]:
    """Return all slots in the machine."""
    return list_inventory_slots()
