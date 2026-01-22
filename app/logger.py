from __future__ import annotations

from PySide6.QtCore import QObject, Signal


class AppLogger(QObject):
    """
    Centralised logger that broadcasts log lines to any UI subscribers.
    """
    line = Signal(str)

    def emit(self, message: str) -> None:
        self.line.emit(message)


# Global singleton instance
_logger = AppLogger()


def get_logger() -> AppLogger:
    return _logger


def log(message: str) -> None:
    """
    Call this anywhere in the project to push a log line to the UI.
    """
    _logger.emit(str(message))
