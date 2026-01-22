from PySide6.QtWidgets import QWidget, QVBoxLayout, QLabel, QTextEdit, QPushButton

class StickyNotesWidget(QWidget):
    """
    Lets you jot down quick notes or reminders. Simple text area, persistent between sessions.
    """
    def __init__(self):
        super().__init__()
        self.setLayout(QVBoxLayout())
        self.title = QLabel("Sticky Notes")
        self.title.setStyleSheet("font-size: 16px; font-weight: bold;")
        self.layout().addWidget(self.title)
        self.text_edit = QTextEdit()
        self.layout().addWidget(self.text_edit)
        self.save_btn = QPushButton("Save Notes")
        self.save_btn.clicked.connect(self.save_notes)
        self.layout().addWidget(self.save_btn)
        self._notes_file = "sticky_notes.txt"
        self.load_notes()

    def save_notes(self):
        with open(self._notes_file, "w", encoding="utf-8") as f:
            f.write(self.text_edit.toPlainText())

    def load_notes(self):
        try:
            with open(self._notes_file, "r", encoding="utf-8") as f:
                self.text_edit.setPlainText(f.read())
        except Exception:
            pass

    def get_state(self):
        return {"notes": self.text_edit.toPlainText()}

    def set_state(self, state):
        self.text_edit.setPlainText(state.get("notes", ""))
