"""Provider interface for PlayLingo external translation providers."""
from __future__ import annotations

import os
from typing import Protocol

import requests


class Provider(Protocol):
    def translate(self, text: str, src: str, dest: str) -> str: ...


class OfflineProvider:
    def __init__(self, translate_fn):
        self._translate = translate_fn

    def translate(self, text: str, src: str, dest: str) -> str:
        return self._translate(text, src, dest)


class DeepLProvider:
    """Very small DeepL provider wrapper. Requires DEEPL_API_KEY env var.

    NOTE: This implementation is minimal and intended as a starting point."

    API_URL = "https://api-free.deepl.com/v2/translate"

    def __init__(self, api_key: str | None = None):
        self.api_key = api_key or os.environ.get("DEEPL_API_KEY")
        if not self.api_key:
            raise ValueError("DEEPL_API_KEY not set")

    def translate(self, text: str, src: str, dest: str) -> str:
        data = {
            "auth_key": self.api_key,
            "text": text,
            "source_lang": src.upper(),
            "target_lang": dest.upper(),
        }
        r = requests.post(self.API_URL, data=data, timeout=10)
        r.raise_for_status()
        j = r.json()
        return j["translations"][0]["text"]
