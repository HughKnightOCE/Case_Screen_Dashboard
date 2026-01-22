from __future__ import annotations

from PySide6.QtWidgets import QWidget


def apply_base_style(widget: QWidget) -> None:
    """
    Global stylesheet for the entire app.
    Keep this file strictly about look/feel (no logic).
    """
    widget.setStyleSheet(
        """
        /* ---------------- App base ---------------- */
        QWidget {
            background: #0b0f14;
            color: #e6edf3;
            font-family: "Segoe UI";
            font-size: 14px;
        }

        /* ---------------- Panels ---------------- */
        QFrame#panel {
            background: #0f1621;
            border: 1px solid #1f2a37;
            border-radius: 14px;
        }

        QLabel#panelTitle {
            font-size: 13px;
            font-weight: 600;
            letter-spacing: 0.4px;
            color: #b6c2cf;
        }

        /* ---------------- Metric tiles ---------------- */
        QFrame#metricTile {
            background: #0b1220;
            border: 1px solid #1f2a37;
            border-radius: 14px;
        }

        QLabel#metricLabel {
            font-size: 12px;
            font-weight: 600;
            letter-spacing: 0.4px;
            color: #b6c2cf;
        }

        QLabel#metricValue {
            font-size: 28px;
            font-weight: 700;
            color: #e6edf3;
        }

        QLabel#metricUnit {
            font-size: 14px;
            font-weight: 600;
            color: #8aa0b5;
            padding-top: 10px; /* aligns baseline visually with big number */
        }
        """
    )
