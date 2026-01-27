from PySide6.QtWidgets import QWidget, QVBoxLayout, QLabel, QPushButton, QHBoxLayout

class MediaControlsWidget(QWidget):
    """
    Controls for Spotify, YouTube Music, or system media. Play/pause, skip, show current track.
    (Demo: buttons only, no real integration yet.)
    """
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setLayout(QVBoxLayout())
        self.title = QLabel("Media Controls")
        self.title.setStyleSheet("font-size: 16px; font-weight: bold;")
        self.layout().addWidget(self.title)
        row = QHBoxLayout()
        self.play_btn = QPushButton("Play/Pause")
        self.next_btn = QPushButton("Next")
        self.prev_btn = QPushButton("Previous")
        row.addWidget(self.prev_btn)
        row.addWidget(self.play_btn)
        row.addWidget(self.next_btn)
        self.layout().addLayout(row)
        self.track_label = QLabel("Current Track: (demo)")
        self.layout().addWidget(self.track_label)

    def get_state(self):
        return {}

    def set_state(self, state):
        pass
