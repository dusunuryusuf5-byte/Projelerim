import logging
import pytest

from playlingo.subtitles import translate_subtitles


def test_translate_subtitles_default_field():
    subs = [{"text": "hello", "id": 1}, {"text": "thank you", "id": 2}]
    out = translate_subtitles(subs, src="en", dest="tr")
    assert out[0]["text"] == "merhaba"
    assert out[1]["text"] == "teşekkürler"
    # ensure other fields preserved
    assert out[0]["id"] == 1


def test_translate_subtitles_custom_field():
    subs = [{"caption": "hello", "id": 1}, {"caption": "merhaba", "id": 2}]
    out = translate_subtitles(subs, src="en", dest="tr", field="caption")
    assert out[0]["caption"] == "merhaba"
    # if already in dest language and provided src/dest are en->tr but caption already tr,
    # we just return translator's behavior (translator lowercases), so check second remains correct
    assert out[1]["caption"] == "merhaba"


def test_missing_field_warns(caplog):
    caplog.set_level(logging.WARNING)
    subs = [{"id": 1}, {"text": "hello", "id": 2}]
    out = translate_subtitles(subs, src="en", dest="tr")
    assert out[0].get("text") is None
    assert any("missing field 'text'" in rec.getMessage() for rec in caplog.records)


def test_non_dict_item_raises():
    with pytest.raises(TypeError):
        translate_subtitles(["not a dict"], src="en", dest="tr")


def test_unsupported_language_propagates():
    with pytest.raises(ValueError):
        translate_subtitles([{"text": "hello"}], src="en", dest="de")


def test_non_string_field_raises():
    with pytest.raises(TypeError):
        translate_subtitles([{"text": 123}], src="en", dest="tr")
