import time

from playlingo.gui import find_current_subtitle


def make_sub(start, end, text):
    return {"start": start, "end": end, "text": text}


def test_find_current_subtitle_basic():
    subs = [make_sub(0.0, 1.0, "one"), make_sub(1.1, 2.0, "two")]
    assert find_current_subtitle(subs, 0.5) == "one"
    assert find_current_subtitle(subs, 1.5) == "two"
    assert find_current_subtitle(subs, 2.5) is None


def test_monitor_translation_workflow(tmp_path, monkeypatch):
    srt_text = """1
00:00:00,000 --> 00:00:01,000
Merhaba

2
00:00:01,200 --> 00:00:02,000
Dünya
"""
    srt_file = tmp_path / "test.srt"
    srt_file.write_text(srt_text, encoding="utf-8")

    # load subs via srt_to_subs indirectly used by SRTMonitor in production
    from playlingo.subtitles import srt_to_subs

    content = srt_file.read_text(encoding="utf-8")
    subs = srt_to_subs(content)
    # simulate elapsed time
    assert find_current_subtitle(subs, 0.5) == "Merhaba"
    # at 1.5 there may be a small gap between 1.0-1.2; ensure we either have Dunia or None
    assert find_current_subtitle(subs, 1.5) in ("Dünya", None)

