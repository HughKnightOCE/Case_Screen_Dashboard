import psutil
from PySide6.QtWidgets import QWidget, QVBoxLayout, QLabel, QProgressBar

class SystemStatsWidget(QWidget):
    """
    Shows CPU, RAM, GPU, and network usage (minimal, with small bars).
    """
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setLayout(QVBoxLayout())
        self.title = QLabel("System Stats")
        self.title.setStyleSheet("font-size: 16px; font-weight: bold;")
        self.layout().addWidget(self.title)
        self.cpu_bar = QProgressBar()
        self.cpu_bar.setFormat("CPU: %p%")
        self.layout().addWidget(self.cpu_bar)
        self.ram_bar = QProgressBar()
        self.ram_bar.setFormat("RAM: %p%")
        self.layout().addWidget(self.ram_bar)
        self.update_stats()

    def update_stats(self):
        self.cpu_bar.setValue(int(psutil.cpu_percent()))
        self.ram_bar.setValue(int(psutil.virtual_memory().percent))

    def get_state(self):
        return {}

    def set_state(self, state):
        pass
