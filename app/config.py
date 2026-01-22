from __future__ import annotations

import json
from dataclasses import dataclass, asdict
from pathlib import Path
from typing import Any

CONFIG_PATH = Path(__file__).resolve().parents[1] / "config.json"

# Slot-based layout (2 columns x 3 rows, with a fixed blank in mid-right)
SLOTS: list[str] = ["top_left", "top_right", "mid_left", "bottom_left", "bottom_right"]

WIDGET_TYPES: list[str] = [
    "university",
    "metrics",
    "todo",
    "focus_timer",
    "logs",
    "blank",
    "break_reminder",
    "focus_streak",
    "distraction_blocker",
    "hydration_reminder",
    "pomodoro_cycles",
    # New widgets
    "calendar",
    "weather",
    "habit_tracker",
    "motivational_quote",
    "system_stats",
    "countdown",
    "sticky_notes",
    "media_controls",
    "focus_music",
    "github_notifications",
]

DEFAULT_LAYOUT: dict[str, str] = {
    "top_left": "university",
    "top_right": "metrics",
    "mid_left": "todo",
    "bottom_left": "focus_timer",
    "bottom_right": "logs",
}

PRESETS: dict[str, dict[str, str]] = {
    "productivity_2col": DEFAULT_LAYOUT,
    "metrics_focus": {
        "top_left": "metrics",
        "top_right": "focus_timer",
        "mid_left": "todo",
        "bottom_left": "logs",
        "bottom_right": "university",
    },
    "minimal": {
        "top_left": "metrics",
        "top_right": "logs",
        "mid_left": "todo",
        "bottom_left": "blank",
        "bottom_right": "blank",
    },
    "study_mode": {
        "top_left": "university",
        "top_right": "focus_timer",
        "mid_left": "todo",
        "bottom_left": "metrics",
        "bottom_right": "logs",
    },
    "system_monitor": {
        "top_left": "metrics",
        "top_right": "logs",
        "mid_left": "metrics",
        "bottom_left": "logs",
        "bottom_right": "blank",
    },
    "adhd_focus": {
        "top_left": "focus_streak",
        "top_right": "break_reminder",
        "mid_left": "hydration_reminder",
        "bottom_left": "pomodoro_cycles",
        "bottom_right": "distraction_blocker",
    },
}


@dataclass
class AppConfig:
    display_index: int = -1  # -1 means "not chosen yet"
    layout: dict[str, str] = None  # type: ignore[assignment]
    widget_order: list[str] = None


def _normalise_layout(layout: Any) -> dict[str, str]:
    # Start with defaults
    merged = dict(DEFAULT_LAYOUT)

    if isinstance(layout, str):
        preset = PRESETS.get(layout)
        if preset:
            merged = dict(preset)

    if isinstance(layout, dict):
        for k in SLOTS:
            v = layout.get(k)
            if isinstance(v, str) and v in WIDGET_TYPES:
                merged[k] = v

    return merged


def _normalise_order(order: Any) -> list[str]:
    # Return validated ordering of widgets. Default: all WIDGET_TYPES excluding 'blank'
    default = [w for w in WIDGET_TYPES if w != "blank"]
    if not isinstance(order, list):
        return default

    cleaned: list[str] = []
    for item in order:
        if isinstance(item, str) and item in WIDGET_TYPES and item not in cleaned:
            cleaned.append(item)

    # Append any missing widgets at end (preserve defaults)
    for w in default:
        if w not in cleaned:
            cleaned.append(w)

    return cleaned


def load_config() -> AppConfig:
    if not CONFIG_PATH.exists():
        cfg = AppConfig(display_index=-1, layout=dict(DEFAULT_LAYOUT))
        save_config(cfg)
        return cfg

    try:
        data = json.loads(CONFIG_PATH.read_text(encoding="utf-8"))
    except Exception:
        cfg = AppConfig(display_index=-1, layout=dict(DEFAULT_LAYOUT))
        save_config(cfg)
        return cfg

    display_index = -1
    if isinstance(data, dict):
        di = data.get("display_index", -1)
        if isinstance(di, int):
            display_index = di

    layout = _normalise_layout(data.get("layout") if isinstance(data, dict) else None)
    order = _normalise_order(data.get("widget_order") if isinstance(data, dict) else None)
    return AppConfig(display_index=display_index, layout=layout, widget_order=order)


def save_config(cfg: AppConfig) -> None:
    payload = asdict(cfg)
    # dataclass may have layout=None if constructed oddly
    if not isinstance(payload.get("layout"), dict):
        payload["layout"] = dict(DEFAULT_LAYOUT)
    if not isinstance(payload.get("widget_order"), list):
        payload["widget_order"] = [w for w in WIDGET_TYPES if w != "blank"]

    CONFIG_PATH.write_text(json.dumps(payload, indent=2), encoding="utf-8")
