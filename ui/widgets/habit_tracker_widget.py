from PySide6.QtWidgets import QWidget, QVBoxLayout, QLabel, QHBoxLayout, QCheckBox, QPushButton, QProgressBar
from PySide6.QtCore import QDate

class HabitTrackerWidget(QWidget):
    """
    Lets you tick off daily habits and shows streaks/progress bars.
    """
    def __init__(self, habits=None):
        super().__init__()
        self.habits = habits or ["Read", "Exercise", "No sugar"]
        self.setLayout(QVBoxLayout())
        self.title = QLabel("Habit Tracker")
        self.title.setStyleSheet("font-size: 16px; font-weight: bold;")
        self.layout().addWidget(self.title)
        self.checkboxes = []
        self.progress_bars = []
        self.streaks = {habit: 0 for habit in self.habits}
        self.completed_today = {habit: False for habit in self.habits}
        self.last_date = QDate.currentDate().toString("yyyy-MM-dd")
        self._build_ui()
        self._update_progress()

    def _build_ui(self):
        for habit in self.habits:
            row = QHBoxLayout()
            cb = QCheckBox(habit)
            cb.stateChanged.connect(lambda state, h=habit: self._on_check(h, state))
            row.addWidget(cb)
            pb = QProgressBar()
            pb.setMaximum(30)
            pb.setValue(self.streaks[habit])
            row.addWidget(pb)
            self.layout().addLayout(row)
            self.checkboxes.append(cb)
            self.progress_bars.append(pb)
        self.reset_btn = QPushButton("Reset Day")
        self.reset_btn.clicked.connect(self._reset_day)
        self.layout().addWidget(self.reset_btn)

    def _on_check(self, habit, state):
        today = QDate.currentDate().toString("yyyy-MM-dd")
        if today != self.last_date:
            self._reset_day()
        self.completed_today[habit] = bool(state)
        if state:
            self.streaks[habit] += 1
        self._update_progress()

    def _reset_day(self):
        self.last_date = QDate.currentDate().toString("yyyy-MM-dd")
        for i, habit in enumerate(self.habits):
            self.completed_today[habit] = False
            self.checkboxes[i].setChecked(False)
        self._update_progress()

    def _update_progress(self):
        for i, habit in enumerate(self.habits):
            self.progress_bars[i].setValue(self.streaks[habit])
            self.progress_bars[i].setFormat(f"Streak: {self.streaks[habit]}")

    def get_state(self):
        return {
            "habits": self.habits,
            "streaks": self.streaks,
            "completed_today": self.completed_today,
            "last_date": self.last_date
        }

    def set_state(self, state):
        self.habits = state.get("habits", self.habits)
        self.streaks = state.get("streaks", {h: 0 for h in self.habits})
        self.completed_today = state.get("completed_today", {h: False for h in self.habits})
        self.last_date = state.get("last_date", QDate.currentDate().toString("yyyy-MM-dd"))
        # Rebuild UI if habits changed
        for i, cb in enumerate(self.checkboxes):
            cb.setText(self.habits[i])
            cb.setChecked(self.completed_today[self.habits[i]])
        self._update_progress()
