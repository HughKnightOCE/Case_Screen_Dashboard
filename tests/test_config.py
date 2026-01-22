import json
import tempfile
from pathlib import Path

from app.config import AppConfig, load_config, save_config, _normalise_layout, DEFAULT_LAYOUT


def test_normalise_layout_dict():
    layout = {"top_left": "metrics", "invalid": "unknown"}
    result = _normalise_layout(layout)
    assert result["top_left"] == "metrics"
    assert result["top_right"] == DEFAULT_LAYOUT["top_right"]


def test_normalise_layout_string():
    result = _normalise_layout("productivity_2col")
    assert result == DEFAULT_LAYOUT


def test_load_save_config():
    with tempfile.TemporaryDirectory() as tmp:
        config_path = Path(tmp) / "config.json"
        # Mock the path
        import app.config
        original_path = app.config.CONFIG_PATH
        app.config.CONFIG_PATH = config_path

        cfg = AppConfig(display_index=1, layout={"top_left": "logs"})
        save_config(cfg)
        loaded = load_config()
        assert loaded.display_index == 1
        assert loaded.layout["top_left"] == "logs"

        # Restore
        app.config.CONFIG_PATH = original_path