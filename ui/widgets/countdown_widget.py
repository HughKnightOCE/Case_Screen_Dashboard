from PySide6.QtWidgets import QWidget, QVBoxLayout, QLabel, QDateTimeEdit, QPushButton
from PySide6.QtCore import QTimer, QDateTime
import datetime

class CountdownWidget(QWidget):
    """
    Lets you set a countdown to a specific date/time and shows time remaining.
    """
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setLayout(QVBoxLayout())
        self.title = QLabel("Countdown/Deadline")
        self.title.setStyleSheet("font-size: 16px; font-weight: bold;")
        self.layout().addWidget(self.title)
        self.datetime_edit = QDateTimeEdit(QDateTime.currentDateTime())
        self.layout().addWidget(self.datetime_edit)
        self.start_btn = QPushButton("Start Countdown")
        self.start_btn.clicked.connect(self.start_countdown)
        self.layout().addWidget(self.start_btn)
        self.remaining_label = QLabel("")
        self.layout().addWidget(self.remaining_label)
        self.timer = QTimer()
        self.timer.timeout.connect(self.update_remaining)

    def start_countdown(self):
        self.target_dt = self.datetime_edit.dateTime().toPython()
        self.timer.start(1000)
        self.update_remaining()

    def update_remaining(self):
        now = datetime.datetime.now()
        delta = self.target_dt - now
        if delta.total_seconds() <= 0:
            self.remaining_label.setText("Time's up!")
            self.timer.stop()
        else:
            days = delta.days
            hours, rem = divmod(delta.seconds, 3600)
            minutes, seconds = divmod(rem, 60)
            self.remaining_label.setText(f"{days}d {hours}h {minutes}m {seconds}s remaining")

    def get_state(self):
        return {"target": self.target_dt.isoformat() if hasattr(self, 'target_dt') else None}

    def set_state(self, state):
        target = state.get("target")
        if target:
            self.target_dt = datetime.datetime.fromisoformat(target)
            self.update_remaining()
