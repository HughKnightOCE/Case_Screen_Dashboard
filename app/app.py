from __future__ import annotations

import sys
from typing import List

from PySide6.QtGui import QFont, QIcon
import os
from pathlib import Path
from PySide6.QtWidgets import QApplication

from app.config import load_config, save_config
from app.screens import get_screen_geometry
from app.window import MainWindow
from ui.launcher import LaunchDialog


def run_app(argv: List[str] | None = None) -> int:
    args = argv if argv is not None else sys.argv[1:]

    # Create Qt app first (needed for dialogs)
    app = QApplication(sys.argv)
    app.setStyle("Fusion")
    # Use a reasonable default system font size for consistent UI scaling
    app.setFont(QFont("Segoe UI", 14))

    # Optionally set app icon if available at assets/icon.ico
    project_root = Path(__file__).resolve().parents[1]
    icon_path = project_root / "assets" / "icon.ico"
    if icon_path.exists():
        try:
            app.setWindowIcon(QIcon(str(icon_path)))
        except Exception:
            pass

    cfg = load_config()

    # Launcher conditions:
    # - user explicitly wants it: --launcher
    # - user wants to pick screen: --pick (we treat as "open launcher")
    # - first run: display_index == -1
    open_launcher = ("--launcher" in args) or ("--pick" in args) or (cfg.display_index == -1)

    if open_launcher:
        dlg = LaunchDialog(cfg)
        if dlg.exec() != 1:  # Dialog was rejected/cancelled
            return 0
        cfg = dlg.apply_to_config()
        save_config(cfg)

    geom = get_screen_geometry(cfg.display_index)
    win = MainWindow(geom, cfg)
    win.show()

    return app.exec()


if __name__ == "__main__":
    raise SystemExit(run_app())
