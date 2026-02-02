from pathlib import Path
import tempfile

from playlingo.cli import main
from playlingo.subtitles import srt_to_subs, subs_to_srt


def sample_srt() -> str:
    return """1
00:00:00,000 --> 00:00:01,000
hello

2
00:00:01,000 --> 00:00:02,000
thank you
"""


def test_srt_conversion_roundtrip():
    txt = sample_srt()
    subs = srt_to_subs(txt)
    out = subs_to_srt(subs)
    assert "hello" in out


def test_cli_translate_srt(tmp_path: Path):
    # Create input SRT
    in_file = tmp_path / "in.srt"
    out_file = tmp_path / "out.srt"
    in_file.write_text(sample_srt(), encoding="utf-8")

    # Run CLI module directly
    rv = main(["translate-srt", "--input", str(in_file), "--output", str(out_file), "--src", "en", "--dest", "tr"])
    # main should return 0
    assert rv == 0
    text = out_file.read_text(encoding="utf-8")
    assert "merhaba" in text or "teşekkürler" in text
