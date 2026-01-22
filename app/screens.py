from __future__ import annotations

from dataclasses import dataclass
from typing import List

from PySide6.QtCore import QRect
from PySide6.QtGui import QGuiApplication


@dataclass(frozen=True)
class ScreenInfo:
    index: int
    name: str
    width: int
    height: int
    x: int
    y: int

    def __str__(self) -> str:
        return f"[{self.index}] {self.name} {self.width}x{self.height} @({self.x},{self.y})"


def list_screens() -> List[ScreenInfo]:
    """
    Return all detected screens. Uses QGuiApplication so no need to pass QApplication around.
    Must be called after QApplication is created.
    """
    screens = QGuiApplication.screens()
    out: List[ScreenInfo] = []

    for i, s in enumerate(screens):
        g = s.geometry()
        out.append(
            ScreenInfo(
                index=i,
                name=s.name(),
                width=g.width(),
                height=g.height(),
                x=g.x(),
                y=g.y(),
            )
        )

    return out


def get_screen_geometry(display_index: int) -> QRect:
    """
    Return a QRect for the given display index. Falls back to primary screen if out of range.
    """
    screens = QGuiApplication.screens()
    if not screens:
        return QRect(100, 100, 800, 600)

    if display_index < 0 or display_index >= len(screens):
        s = QGuiApplication.primaryScreen() or screens[0]
    else:
        s = screens[display_index]

    return s.geometry()


def pick_display_index() -> int:
    """
    Console picker (your existing --pick flow).
    """
    infos = list_screens()
    print("\nDetected screens:\n")
    for info in infos:
        print(str(info))
    print("")
    raw = input("Pick screen index: ").strip()
    try:
        idx = int(raw)
    except ValueError:
        return -1
    return idx
