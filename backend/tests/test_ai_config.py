import os
import sys
import unittest
from pathlib import Path
from unittest.mock import patch


sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from vending_machine.ai.config import ModelSettings, load_settings
from vending_machine.ai.providers import build_chat_model


class AiConfigTests(unittest.TestCase):
    def test_load_settings_uses_provider_neutral_environment_variables(self) -> None:
        environment = {
            "AI_PROVIDER": "openai",
            "AI_MODEL": "gpt-test",
            "AI_TEMPERATURE": "0.3",
            "AI_MAX_TOKENS": "512",
            "VENDING_CURRENCY": "usd",
        }
        with patch.dict(os.environ, environment, clear=True):
            with patch("vending_machine.ai.config.load_dotenv"):
                settings = load_settings()

        self.assertEqual(settings.model.provider, "openai")
        self.assertEqual(settings.model.model, "gpt-test")
        self.assertEqual(settings.model.temperature, 0.3)
        self.assertEqual(settings.model.max_tokens, 512)
        self.assertEqual(settings.currency, "USD")

    def test_openai_adapter_uses_the_provider_neutral_api_key(self) -> None:
        settings = ModelSettings(model="gpt-test", temperature=0.2, max_tokens=128)
        with patch.dict(os.environ, {"AI_API_KEY": "test-key"}, clear=True):
            with patch("vending_machine.ai.providers.ChatOpenAI") as chat_openai:
                build_chat_model(settings)

        chat_openai.assert_called_once_with(
            model="gpt-test",
            temperature=0.2,
            max_tokens=128,
            streaming=True,
            api_key="test-key",
            use_responses_api=True,
        )
