from PySide6.QtWidgets import QWidget, QVBoxLayout, QLabel, QPushButton, QComboBox

class FocusMusicWidget(QWidget):
    """
    Plays focus/ambient sounds (rain, white noise, etc.). Simple play/stop and volume.
    (Demo: UI only, no real sound playback yet.)
    """
    def __init__(self):
        super().__init__()
        self.setLayout(QVBoxLayout())
        self.title = QLabel("Focus Music/Ambience")
        self.title.setStyleSheet("font-size: 16px; font-weight: bold;")
        self.layout().addWidget(self.title)
        self.sound_select = QComboBox()
        self.sound_select.addItems(["Rain", "White Noise", "Cafe", "Waves"])
        self.layout().addWidget(self.sound_select)
        self.play_btn = QPushButton("Play")
        self.stop_btn = QPushButton("Stop")
        self.layout().addWidget(self.play_btn)
        self.layout().addWidget(self.stop_btn)
        self.volume_label = QLabel("Volume: (demo)")
        self.layout().addWidget(self.volume_label)

    def get_state(self):
        return {"sound": self.sound_select.currentText()}

    def set_state(self, state):
        sound = state.get("sound")
        if sound:
            idx = self.sound_select.findText(sound)
            if idx >= 0:
                self.sound_select.setCurrentIndex(idx)
