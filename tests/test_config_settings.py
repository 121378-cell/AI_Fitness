import os
import unittest
from unittest.mock import patch

from src.config.settings import get_ai_settings, validate_ai_settings


class ConfigSettingsTests(unittest.TestCase):
    def test_validate_ai_settings_accepts_ollama_default(self):
        with patch.dict(os.environ, {"AI_PROVIDER_ORDER": "ollama"}, clear=False):
            settings = get_ai_settings()
            valid, errors = validate_ai_settings(settings)
            self.assertTrue(valid)
            self.assertEqual(errors, [])

    def test_validate_ai_settings_requires_key_when_groq_enabled(self):
        with patch.dict(os.environ, {"AI_PROVIDER_ORDER": "groq", "GROQ_API_KEY": ""}, clear=False):
            settings = get_ai_settings()
            valid, errors = validate_ai_settings(settings)
            self.assertFalse(valid)
            self.assertTrue(any("GROQ_API_KEY" in e for e in errors))

    def test_validate_ai_settings_unknown_provider(self):
        with patch.dict(os.environ, {"AI_PROVIDER_ORDER": "foo,ollama"}, clear=False):
            settings = get_ai_settings()
            valid, errors = validate_ai_settings(settings)
            self.assertFalse(valid)
            self.assertTrue(any("Unknown providers" in e for e in errors))


if __name__ == "__main__":
    unittest.main()
