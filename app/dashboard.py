from __future__ import annotations

from PySide6.QtWidgets import QWidget, QVBoxLayout, QLabel
from PySide6.QtCore import Qt

from .window_style import apply_base_style


class DashboardWidget(QWidget):
    def __init__(self) -> None:
        super().__init__()

        apply_base_style(self)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(24, 24, 24, 24)
        layout.setSpacing(12)

        title = QLabel("case dashboard")
        title.setAlignment(Qt.AlignCenter)

        sub = QLabel("(skeleton running — next: layout + modules)")
        sub.setAlignment(Qt.AlignCenter)

        layout.addStretch(1)
        layout.addWidget(title)
        layout.addWidget(sub)
        layout.addStretch(1)
