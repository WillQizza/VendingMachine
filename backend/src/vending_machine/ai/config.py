"""Runtime settings for AI-backed agents."""

import os
from dataclasses import dataclass

from dotenv import load_dotenv


@dataclass(frozen=True)
class ModelSettings:
    """Settings for one agent's language model."""

    provider: str = "openai"
    model: str = "gpt-5.2"
    temperature: float = 0.0
    max_tokens: int = 4096


@dataclass(frozen=True)
class AppSettings:
    """Application-wide settings shared by agent builders."""

    model: ModelSettings
    currency: str


def load_settings() -> AppSettings:
    """Load application settings from the process environment and .env."""
    load_dotenv()

    model_settings = ModelSettings(
        provider=os.getenv("AI_PROVIDER", "openai").strip().lower(),
        model=os.getenv("AI_MODEL", "gpt-5.2").strip(),
        temperature=_read_float("AI_TEMPERATURE", 0.0),
        max_tokens=_read_int("AI_MAX_TOKENS", 4096),
    )
    currency = os.getenv("VENDING_CURRENCY", "CAD").strip().upper()
    _validate_settings(model_settings, currency)
    return AppSettings(model=model_settings, currency=currency)


def _read_float(name: str, default: float) -> float:
    value = os.getenv(name)
    if value is None or value.strip() == "":
        return default
    try:
        return float(value)
    except ValueError as exc:
        raise ValueError(f"{name} must be a number") from exc


def _read_int(name: str, default: int) -> int:
    value = os.getenv(name)
    if value is None or value.strip() == "":
        return default
    try:
        return int(value)
    except ValueError as exc:
        raise ValueError(f"{name} must be an integer") from exc


def _validate_settings(settings: ModelSettings, currency: str) -> None:
    if settings.provider == "":
        raise ValueError("AI_PROVIDER cannot be empty")
    if settings.model == "":
        raise ValueError("AI_MODEL cannot be empty")
    if settings.temperature < 0 or settings.temperature > 2:
        raise ValueError("AI_TEMPERATURE must be between 0 and 2")
    if settings.max_tokens <= 0:
        raise ValueError("AI_MAX_TOKENS must be greater than zero")
    if currency == "":
        raise ValueError("VENDING_CURRENCY cannot be empty")
