
from PySide6.QtWidgets import QWidget, QVBoxLayout, QLabel, QPushButton, QListWidget

class GitHubNotificationsWidget(QWidget):
	"""
	Shows unread notifications or PRs/issues assigned to you.
	(Demo: UI only, no real API integration yet.)
	"""
	def __init__(self, parent=None):
		super().__init__(parent)
		self.setLayout(QVBoxLayout())
		self.title = QLabel("GitHub Notifications")
		self.title.setStyleSheet("font-size: 16px; font-weight: bold;")
		self.layout().addWidget(self.title)
		self.refresh_btn = QPushButton("Refresh")
		self.layout().addWidget(self.refresh_btn)
		self.list_widget = QListWidget()
		self.layout().addWidget(self.list_widget)
		self.refresh_btn.clicked.connect(self.refresh)
		self.refresh()

	def refresh(self):
		# Demo: show placeholder notifications
		self.list_widget.clear()
		self.list_widget.addItem("No notifications (demo)")

	def get_state(self):
		return {}

	def set_state(self, state):
		pass
