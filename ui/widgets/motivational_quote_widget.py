import random
from PySide6.QtWidgets import QWidget, QVBoxLayout, QLabel, QPushButton

QUOTES = [
    "Success is not final, failure is not fatal: It is the courage to continue that counts.",
    "The secret of getting ahead is getting started.",
    "Don’t watch the clock; do what it does. Keep going.",
    "The future depends on what you do today.",
    "It always seems impossible until it’s done.",
    "Believe you can and you’re halfway there.",
    "Start where you are. Use what you have. Do what you can.",
]

class MotivationalQuoteWidget(QWidget):
    """
    Rotates through motivational quotes or affirmations.
    """
    def __init__(self):
        super().__init__()
        self.setLayout(QVBoxLayout())
        self.title = QLabel("Motivational Quote")
        self.title.setStyleSheet("font-size: 16px; font-weight: bold;")
        self.layout().addWidget(self.title)
        self.quote_label = QLabel()
        self.quote_label.setWordWrap(True)
        self.layout().addWidget(self.quote_label)
        self.next_btn = QPushButton("Next Quote")
        self.next_btn.clicked.connect(self.show_next_quote)
        self.layout().addWidget(self.next_btn)
        self.show_next_quote()

    def show_next_quote(self):
        self.quote_label.setText(random.choice(QUOTES))

    def get_state(self):
        return {}

    def set_state(self, state):
        pass
