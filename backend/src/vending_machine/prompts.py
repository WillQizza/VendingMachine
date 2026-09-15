from pathlib import Path

PROMPTS_DIR = Path(__file__).resolve().parents[2] / "prompts"


def _load_prompt(name: str) -> str:
    """Read a raw prompt file out of backend/prompts."""
    return (PROMPTS_DIR / name).read_text(encoding="utf-8")


def build_vending_machine_prompt(
    session_id: str,
    currency: str = "CAD",
    support_contact: str = "example@example.com",
) -> str:
    """Fill the placeholders in VENDING_MACHINE.md for one customer session."""
    template = _load_prompt("VENDING_MACHINE.md")
    return template.format(
        currency=currency,
        support_contact=support_contact,
        session_id=session_id,
    )
