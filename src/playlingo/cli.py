"""CLI for PlayLingo: translate SRT subtitle files."""
from __future__ import annotations

import argparse
import logging
from pathlib import Path
from typing import Optional

from .subtitles import srt_to_subs, subs_to_srt, translate_subtitles

logger = logging.getLogger(__name__)


def _parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(prog="playlingo")
    sub = parser.add_subparsers(dest="command", required=True)

    t = sub.add_parser("translate-srt", help="Translate an SRT file")
    t.add_argument("--input", "-i", type=Path, required=True)
    t.add_argument("--output", "-o", type=Path, required=True)
    t.add_argument("--src", type=str, required=True)
    t.add_argument("--dest", type=str, required=True)
    t.add_argument("--field", type=str, default="text", help="Subtitle field to translate (default: text)")

    return parser.parse_args()


def main(argv: Optional[list[str]] = None) -> int:
    args = _parse_args() if argv is None else _parse_args()

    if args.command == "translate-srt":
        text = Path(args.input).read_text(encoding="utf-8")
        subs = srt_to_subs(text)
        translated = translate_subtitles(subs, src=args.src, dest=args.dest, field=args.field)
        out_text = subs_to_srt(translated)
        Path(args.output).write_text(out_text, encoding="utf-8")
        logger.info("Wrote translated SRT to %s", args.output)
        return 0

    return 2


if __name__ == "__main__":
    raise SystemExit(main())
