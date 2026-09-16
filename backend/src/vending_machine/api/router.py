"""Top-level HTTP route registration."""

from fastapi import APIRouter

from vending_machine.api.conversations import router as conversations_router
from vending_machine.api.inventory import router as inventory_router


router = APIRouter()


@router.get("/")
def root() -> dict[str, str]:
    return {"status": "ok"}


router.include_router(conversations_router)
router.include_router(inventory_router)
