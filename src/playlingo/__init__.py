"""Translator package for simple offline translations."""

from .translator import Translator, translate
from .subtitles import translate_subtitles, srt_to_subs, subs_to_srt
from .logging_config import setup_logging, get_memory_handler, dump_logs_to_file

__all__ = ["Translator", "translate", "translate_subtitles", "srt_to_subs", "subs_to_srt", "setup_logging", "get_memory_handler", "dump_logs_to_file"]
