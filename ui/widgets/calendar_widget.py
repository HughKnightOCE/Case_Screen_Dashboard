import datetime
from PySide6.QtWidgets import QWidget, QVBoxLayout, QLabel, QListWidget, QListWidgetItem
import os

class CalendarWidget(QWidget):
    """
    Minimal agenda view for upcoming events/tasks from a local .ics file.
    """
    def __init__(self, parent=None, ics_path=None):
        super().__init__(parent)
        self.ics_path = ics_path or os.path.join(os.getcwd(), "uni_tasks.ics")
        self.setLayout(QVBoxLayout())
        self.title = QLabel("Upcoming Events")
        self.title.setStyleSheet("font-size: 16px; font-weight: bold;")
        self.layout().addWidget(self.title)
        self.list_widget = QListWidget()
        self.layout().addWidget(self.list_widget)
        self.refresh_events()

    def refresh_events(self):
        self.list_widget.clear()
        events = self._load_events()
        today = datetime.date.today()
        for event in events:
            date_str = event.get("date", "")
            summary = event.get("summary", "")
            try:
                event_date = datetime.datetime.strptime(date_str, "%Y-%m-%d").date()
            except Exception:
                continue
            if event_date >= today:
                item = QListWidgetItem(f"{event_date}: {summary}")
                self.list_widget.addItem(item)

    def _load_events(self):
        # Minimal .ics parser (only DTSTART and SUMMARY)
        events = []
        if not os.path.exists(self.ics_path):
            return events
        with open(self.ics_path, "r", encoding="utf-8") as f:
            lines = f.readlines()
        event = {}
        for line in lines:
            line = line.strip()
            if line.startswith("DTSTART"):
                date_part = line.split(":")[-1]
                try:
                    date_obj = datetime.datetime.strptime(date_part[:8], "%Y%m%d").date()
                    event["date"] = date_obj.strftime("%Y-%m-%d")
                except Exception:
                    pass
            elif line.startswith("SUMMARY"):
                event["summary"] = line.split(":", 1)[-1]
            elif line == "END:VEVENT":
                if "date" in event and "summary" in event:
                    events.append(event)
                event = {}
        return events

    def get_state(self):
        return {}

    def set_state(self, state):
        pass
