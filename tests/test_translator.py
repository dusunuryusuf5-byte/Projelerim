import logging
import pytest

from playlingo import translate, Translator


def test_translate_en_to_tr():
    assert translate("hello", src="en", dest="tr") == "merhaba"
    assert translate("thank you", src="en", dest="tr") == "teşekkürler"


def test_translate_tr_to_en():
    assert translate("merhaba", src="tr", dest="en") == "hello"


def test_unknown_phrase_returns_original(caplog):
    caplog.set_level(logging.WARNING)
    original = "this phrase is unknown"
    result = translate(original, src="en", dest="tr")
    assert result == original
    assert any("No translation found" in rec.getMessage() for rec in caplog.records)


def test_unsupported_language_raises():
    with pytest.raises(ValueError):
        translate("hello", src="en", dest="de")


def test_same_language_raises():
    with pytest.raises(ValueError):
        translate("hello", src="en", dest="en")
