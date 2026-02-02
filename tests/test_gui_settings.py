from pathlib import Path
import json

from playlingo.gui import validate_overlay_settings, save_overlay_settings, load_overlay_settings


def test_validate_overlay_settings_basic():
    good = {
        "bg": "#101010",
        "fg": "#ffffff",
        "font_family": "Arial",
        "font_size": 14,
        "alpha": 0.5,
    }
    out = validate_overlay_settings(good)
    assert out["bg"] == "#101010"
    assert out["alpha"] == 0.5


def test_validate_overlay_settings_bad_alpha():
    bad = {"alpha": 1.5}
    try:
        validate_overlay_settings(bad)
        assert False, "Should have raised ValueError for alpha"
    except ValueError:
        pass


def test_save_and_load(tmp_path):
    cfg = tmp_path / "cfg.json"
    data = {"bg": "#222222", "font_size": 18, "alpha": 0.8}
    save_overlay_settings(data, path=cfg)
    loaded = load_overlay_settings(path=cfg)
    assert loaded["bg"] == "#222222"
    assert loaded["font_size"] == 18
    assert round(loaded["alpha"], 2) == 0.8
