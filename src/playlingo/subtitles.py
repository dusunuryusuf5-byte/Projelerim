"""Subtitle translation helpers for PlayLingo.

Provides functions to translate subtitles contained in dict-like structures
and to select which field to translate (e.g., 'text' or 'caption').
"""
from __future__ import annotations

import logging
from typing import Iterable, List, Dict, Any

from .translator import translate
from typing import Callable, Optional

TranslateFn = Callable[[str, str, str], str]

logger = logging.getLogger(__name__)


def translate_subtitles(
    subtitles: Iterable[Dict[str, Any]],
    src: str,
    dest: str,
    field: str = "text",
    translate_fn: Optional[TranslateFn] = None,
) -> List[Dict[str, Any]]:
    """Translate a sequence of subtitle dicts.

    - subtitles: iterable of dict-like objects (will not be mutated)
    - src/dest: language codes (e.g., 'en', 'tr')
    - field: the key in each dict to translate (default: 'text')
    - translate_fn: optional callable translate_fn(text, src, dest) -> str
      if omitted the offline `playlingo.translate` is used.

    Returns a new list with translated copies. If a subtitle doesn't contain
    the requested field, it is left unchanged and a warning is logged.
    """
    translated: List[Dict[str, Any]] = []

    if translate_fn is None:
        translate_fn = translate

    # Validate languages early using a single call
    try:
        # If languages invalid, underlying translate will raise
        _ = translate_fn("__playlingo_sanity_check__", src, dest)
    except Exception:
        logger.exception("Language validation failed for %s->%s", src, dest)
        raise
    """Translate a sequence of subtitle dicts.

    - subtitles: iterable of dict-like objects (will not be mutated)
    - src/dest: language codes (e.g., 'en', 'tr')
    - field: the key in each dict to translate (default: 'text')

    Returns a new list with translated copies. If a subtitle doesn't contain
    the requested field, it is left unchanged and a warning is logged.
    """
    translated: List[Dict[str, Any]] = []

    # Validate languages early using a single call
    try:
        # If languages invalid, underlying translate will raise
        _ = translate("__playlingo_sanity_check__", src=src, dest=dest)
    except Exception:
        logger.exception("Language validation failed for %s->%s", src, dest)
        raise

    for i, item in enumerate(subtitles):
        if not isinstance(item, dict):
            logger.error("Subtitle item at index %d is not a dict: %r", i, item)
            raise TypeError("Each subtitle must be a dict-like object")

        copy = dict(item)
        if field not in copy:
            logger.warning("Subtitle at index %d missing field '%s'; leaving unchanged", i, field)
            translated.append(copy)
            continue

        original = copy[field]
        if original is None:
            logger.warning("Subtitle at index %d has None in field '%s'; leaving unchanged", i, field)
            translated.append(copy)
            continue

        # Ensure we operate on strings
        if not isinstance(original, str):
            logger.error("Subtitle field '%s' at index %d is not a string: %r", field, i, original)
            raise TypeError("Subtitle field must be a string")

        try:
            new = translate_fn(original, src, dest)
        except Exception:
            logger.exception("Translation failed for subtitle at index %d", i)
            raise

        copy[field] = new
        translated.append(copy)

    return translated


# Helpers for SRT parsing/serialization using the `srt` library
def srt_to_subs(srt_text: str) -> List[Dict[str, Any]]:
    import srt

    subs = list(srt.parse(srt_text))
    result = []
    for sub in subs:
        result.append({"index": sub.index, "start": sub.start, "end": sub.end, "text": sub.content})
    return result


def subs_to_srt(subs: Iterable[Dict[str, Any]]) -> str:
    import srt

    srt_objs = []
    for sub in subs:
        index = sub.get("index")
        start = sub.get("start")
        end = sub.get("end")
        content = sub.get("text")
        if index is None or start is None or end is None or content is None:
            raise ValueError("Subtitle items must contain index, start, end, and text")
        srt_objs.append(srt.Subtitle(index=index, start=start, end=end, content=content))
    return srt.compose(srt_objs)
