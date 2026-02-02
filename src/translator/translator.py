"""A tiny, deterministic translator with an in-memory phrase dictionary.

This is a simple offline translator intended for tests and demonstration.
It supports 'en' <-> 'tr' for a small set of phrases and is case-insensitive.
"""
from __future__ import annotations

import logging
from typing import Dict

logger = logging.getLogger(__name__)

_TRANSLATIONS: Dict[str, Dict[str, str]] = {
    "en->tr": {
        "hello": "merhaba",
        "goodbye": "güle güle",
        "thank you": "teşekkürler",
        "yes": "evet",
        "no": "hayır",
    },
    "tr->en": {
        "merhaba": "hello",
        "güle güle": "goodbye",
        "teşekkürler": "thank you",
        "evet": "yes",
        "hayır": "no",
    },
}


class Translator:
    """Simple translator supporting a small offline dictionary.

    Usage:
        t = Translator()
        t.translate("hello", src="en", dest="tr")  # -> "merhaba"
    """

    SUPPORTED = {"en", "tr"}

    def translate(self, text: str, src: str = "en", dest: str = "tr") -> str:
        """Translate `text` from `src` to `dest`.

        - Raises ValueError if `src` or `dest` is unsupported or equal.
        - If an exact phrase match isn't found, returns the original text and logs a warning.
        """
        src = src.lower()
        dest = dest.lower()

        if src not in self.SUPPORTED:
            logger.error("Unsupported source language: %s", src)
            raise ValueError(f"Unsupported source language: {src}")
        if dest not in self.SUPPORTED:
            logger.error("Unsupported destination language: %s", dest)
            raise ValueError(f"Unsupported destination language: {dest}")
        if src == dest:
            logger.error("Source and destination language are the same: %s", src)
            raise ValueError("Source and destination must differ")

        key = f"{src}->{dest}"
        phrase = text.strip().lower()
        translation = _TRANSLATIONS.get(key, {}).get(phrase)
        if translation is None:
            logger.warning("No translation found for '%s' (%s->%s)", text, src, dest)
            return text
        return translation


# convenience function
_translator = Translator()


def translate(text: str, src: str = "en", dest: str = "tr") -> str:
    return _translator.translate(text, src=src, dest=dest)
