from __future__ import annotations

from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QListWidget,
    QListWidgetItem,
    QPushButton,
    QVBoxLayout,
    QWidget,
)

from ui.widgets import Panel
from app.state import AppState, TodoItem


class LogsPanel(Panel):
    """
    Placeholder logs panel.
    (We will wire real logging later.)
    """

    def __init__(self, title: str = "logs", parent: QWidget | None = None) -> None:
        super().__init__(title, parent)

        self.text = QListWidget(self)
        self.body_layout.addWidget(self.text, 1)

    def append_line(self, line: str) -> None:
        if not line:
            return
        self.text.addItem(line)
        self.text.scrollToBottom()


class SensorsPanel(Panel):
    """
    Placeholder sensors panel.
    """

    def __init__(self, title: str = "sensors", parent: QWidget | None = None) -> None:
        super().__init__(title, parent)

        placeholder = QLabel("sensors placeholder", self)
        placeholder.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.body_layout.addWidget(placeholder, 1)


class TodoPanel(Panel):
    """
    Uni / productivity to-do list panel.
    - Enter text + Add
    - Double-click an item to toggle done
    - Delete removes selected item
    """

    def __init__(self, title: str = "to-do", parent: QWidget | None = None) -> None:
        super().__init__(title, parent)

        self.list = QListWidget(self)
        self.input = QLineEdit(self)
        self.input.setPlaceholderText("add a task and press enter")
        self.btn_add = QPushButton("add", self)
        self.btn_delete = QPushButton("delete", self)

        top = QHBoxLayout()
        top.setContentsMargins(0, 0, 0, 0)
        top.setSpacing(6)
        top.addWidget(self.input, 1)
        top.addWidget(self.btn_add)
        top.addWidget(self.btn_delete)

        container = QWidget(self)
        container.setLayout(top)

        self.body_layout.addWidget(container)
        self.body_layout.addWidget(self.list, 1)

        self.btn_add.clicked.connect(self._on_add_clicked)
        self.btn_delete.clicked.connect(self._on_delete_clicked)
        self.input.returnPressed.connect(self._on_add_clicked)
        self.list.itemDoubleClicked.connect(self._on_item_double_clicked)

    def set_items(self, items: list[TodoItem]) -> None:
        self.list.clear()
        for t in items:
            self._add_list_item(t)

    def get_items(self) -> list[TodoItem]:
        items: list[TodoItem] = []
        for i in range(self.list.count()):
            it = self.list.item(i)
            text = it.data(Qt.ItemDataRole.UserRole) or ""
            done = bool(it.checkState() == Qt.CheckState.Checked)
            text = str(text).strip()
            if text:
                items.append(TodoItem(text=text, done=done))
        return items

    def _add_list_item(self, todo: TodoItem) -> None:
        it = QListWidgetItem(self.list)
        it.setData(Qt.ItemDataRole.UserRole, todo.text)
        it.setText(todo.text)
        it.setFlags(it.flags() | Qt.ItemFlag.ItemIsUserCheckable | Qt.ItemFlag.ItemIsSelectable | Qt.ItemFlag.ItemIsEnabled)
        it.setCheckState(Qt.CheckState.Checked if todo.done else Qt.CheckState.Unchecked)
        self.list.addItem(it)

    def _on_add_clicked(self) -> None:
        text = self.input.text().strip()
        if not text:
            return
        self._add_list_item(TodoItem(text=text, done=False))
        self.input.clear()

    def _on_delete_clicked(self) -> None:
        row = self.list.currentRow()
        if row < 0:
            return
        self.list.takeItem(row)

    def _on_item_double_clicked(self, item: QListWidgetItem) -> None:
        item.setCheckState(
            Qt.CheckState.Unchecked if item.checkState() == Qt.CheckState.Checked else Qt.CheckState.Checked
        )
