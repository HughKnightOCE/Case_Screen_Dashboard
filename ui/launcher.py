from __future__ import annotations

import json
import sys
from pathlib import Path
from typing import Dict

# Add project root to path for imports
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from PySide6.QtCore import Qt, QMimeData, QSize
from PySide6.QtGui import QGuiApplication, QDrag, QColor, QFont
from PySide6.QtWidgets import (
    QDialog,
    QVBoxLayout,
    QHBoxLayout,
    QLabel,
    QPushButton,
    QComboBox,
    QGroupBox,
    QTableWidget,
    QTableWidgetItem,
    QListWidget,
    QListWidgetItem,
    QAbstractItemView,
    QSpinBox,
    QWidget,
    QFrame,
    QGridLayout,
)
from PySide6.QtGui import QDesktopServices
from PySide6.QtCore import QUrl
import webbrowser
from pathlib import Path

from app.config import PRESETS


def list_screens() -> list[str]:
    """
    Returns a list of human-readable screen descriptions.
    Uses QGuiApplication directly (no app arg required).
    """
    screens = QGuiApplication.screens()
    result: list[str] = []

    for i, s in enumerate(screens):
        geo = s.geometry()
        result.append(
            f"[{i}] {s.name()} {geo.width()}x{geo.height()} @({geo.x()},{geo.y()})"
        )

    return result


# =========================
# Draggable Widget List
# =========================

class DraggableWidgetList(QListWidget):
    """
    Custom QListWidget that properly supports dragging widget names.
    """
    
    def startDrag(self, supportedActions):
        """Override to set proper MIME data when dragging."""
        item = self.currentItem()
        if not item:
            return
        
        mime_data = QMimeData()
        mime_data.setText(item.text())
        
        drag = QDrag(self)
        drag.setMimeData(mime_data)
        drag.exec(supportedActions)


# =========================
# Layout Grid Widget (Visual Slot Editor)
# =========================

class LayoutGridCell(QFrame):
    """
    A single cell in the layout grid.
    Represents one dashboard slot and accepts drag-dropped widgets.
    """
    
    def __init__(self, slot_name: str, parent: QWidget | None = None):
        super().__init__(parent)
        self.slot_name = slot_name
        self.widget_name: str | None = None
        
        self.setFrameShape(QFrame.Shape.StyledPanel)
        self.setFrameShadow(QFrame.Shadow.Raised)
        self.setLineWidth(2)
        self.setMinimumSize(QSize(150, 100))
        self.setAcceptDrops(True)
        
        layout = QVBoxLayout(self)
        layout.setContentsMargins(8, 8, 8, 8)
        layout.setSpacing(6)
        
        # Slot label
        self.slot_label = QLabel(slot_name)
        self.slot_label.setStyleSheet("font-size: 9pt; color: #666666; font-weight: bold;")
        layout.addWidget(self.slot_label)
        
        # Widget name display
        self.widget_label = QLabel("(empty)")
        self.widget_label.setStyleSheet("font-size: 11pt; font-weight: bold; color: #00aa00;")
        self.widget_label.setWordWrap(True)
        self.widget_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(self.widget_label, 1)
        
        # Clear button
        self.clear_btn = QPushButton("×")
        self.clear_btn.setMaximumSize(QSize(30, 30))
        self.clear_btn.setStyleSheet("font-size: 12pt; padding: 2px;")
        self.clear_btn.clicked.connect(self.clear_widget)
        layout.addWidget(self.clear_btn, 0, Qt.AlignmentFlag.AlignRight)
        
        self._update_style()
    
    def set_widget(self, widget_name: str) -> None:
        """Set the widget in this slot."""
        self.widget_name = widget_name if widget_name and widget_name != "blank" else None
        self.widget_label.setText(widget_name if widget_name else "(empty)")
        self._update_style()
    
    def clear_widget(self) -> None:
        """Clear the widget from this slot."""
        self.set_widget(None)
    
    def _update_style(self) -> None:
        """Update cell appearance based on content."""
        if self.widget_name:
            self.setStyleSheet("QFrame { border: 2px solid #00aa00; background-color: #1a1a1a; border-radius: 4px; }")
        else:
            self.setStyleSheet("QFrame { border: 2px dashed #444444; background-color: #0f0f0f; border-radius: 4px; }")
    
    def dragEnterEvent(self, event):
        """Accept drag if it contains widget name."""
        if event.mimeData().hasText():
            event.acceptProposedAction()
            self.setStyleSheet("QFrame { border: 2px solid #ffaa00; background-color: #1a1a1a; border-radius: 4px; }")
    
    def dragLeaveEvent(self, event):
        """Reset style when drag leaves."""
        self._update_style()
    
    def dropEvent(self, event):
        """Accept dropped widget."""
        mime = event.mimeData()
        if mime.hasText():
            widget_name = mime.text()
            self.set_widget(widget_name)
            event.acceptProposedAction()
    
    def get_widget(self) -> str | None:
        """Get the widget assigned to this slot."""
        return self.widget_name


class LayoutGridWidget(QWidget):
    """
    Visual single-column editor for dashboard layout.
    Users drag widgets from a source list into cells (top to bottom).
    """
    
    def __init__(self, parent: QWidget | None = None):
        super().__init__(parent)
        
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(12)
        
        # Instructions
        instr = QLabel("Drag widgets from the list below to arrange your dashboard (top to bottom):")
        instr.setStyleSheet("font-size: 10pt; color: #888888;")
        layout.addWidget(instr)
        
        # Grid container
        grid_container = QWidget()
        grid_layout = QVBoxLayout(grid_container)
        grid_layout.setSpacing(8)
        grid_layout.setContentsMargins(0, 0, 0, 0)
        
        # Define slots (single column, 6 rows)
        self.slots = {
            "slot_1": 0,
            "slot_2": 1,
            "slot_3": 2,
            "slot_4": 3,
            "slot_5": 4,
            "slot_6": 5,
        }
        
        self.cells: dict[str, LayoutGridCell] = {}
        
        for slot_name in self.slots:
            cell = LayoutGridCell(slot_name, grid_container)
            cell.setMaximumHeight(80)
            self.cells[slot_name] = cell
            grid_layout.addWidget(cell)
        
        grid_layout.addStretch()
        layout.addWidget(grid_container, 1)
    
    def set_layout(self, layout_dict: dict[str, str]) -> None:
        """Load a layout into the grid."""
        for slot_name, widget_name in layout_dict.items():
            if slot_name in self.cells:
                self.cells[slot_name].set_widget(widget_name)
    
    def get_layout(self) -> dict[str, str]:
        """Get the current layout from the grid."""
        result = {}
        for slot_name, cell in self.cells.items():
            widget = cell.get_widget()
            result[slot_name] = widget if widget else "blank"
        return result


class LaunchDialog(QDialog):
    """
    Standalone launcher dialog for dashboard configuration.
    
    Responsibilities:
    - Select target screen
    - Choose layout preset
    - Adjust font size
    - Manage university tasks
    - Manage todo tasks
    - Persist configuration and state
    """

    def __init__(self, cfg) -> None:
        super().__init__()
        self.cfg = cfg
        self.setWindowTitle("Case Dashboard Launcher")
        self.setMinimumSize(700, 650)
        self.setMaximumSize(900, 800)
        
        # Main layout
        main_layout = QVBoxLayout(self)
        main_layout.setSpacing(12)
        main_layout.setContentsMargins(20, 20, 20, 20)

        # === DISPLAY SECTION ===
        display_box = QGroupBox("Display Configuration")
        display_box.setStyleSheet("QGroupBox { font-size: 11pt; font-weight: bold; padding-top: 12px; margin-top: 6px; } QGroupBox::title { subcontrol-origin: margin; top: -6px; left: 10px; padding: 0 3px; }")
        display_layout = QVBoxLayout(display_box)
        display_layout.setSpacing(8)
        display_layout.setContentsMargins(12, 16, 12, 12)
        
        display_label = QLabel("Select Display Screen:")
        display_label.setStyleSheet("font-size: 11pt;")
        self.screen_combo = QComboBox()
        self.screen_combo.addItems(list_screens())
        self.screen_combo.setStyleSheet("font-size: 11pt; padding: 4px;")
        if cfg.display_index >= 0:
            self.screen_combo.setCurrentIndex(cfg.display_index)
        self.screen_combo.setMinimumHeight(28)
        display_layout.addWidget(display_label)
        display_layout.addWidget(self.screen_combo)
        main_layout.addWidget(display_box)

        # === LAYOUT SECTION ===
        layout_box = QGroupBox("Dashboard Layout")
        layout_box.setStyleSheet("QGroupBox { font-size: 11pt; font-weight: bold; padding-top: 12px; margin-top: 6px; } QGroupBox::title { subcontrol-origin: margin; top: -6px; left: 10px; padding: 0 3px; }")
        layout_layout = QVBoxLayout(layout_box)
        layout_layout.setSpacing(8)
        layout_layout.setContentsMargins(12, 16, 12, 12)
        
        layout_label = QLabel("Choose Layout Preset:")
        layout_label.setStyleSheet("font-size: 11pt;")
        self.layout_combo = QComboBox()
        self.layout_combo.addItems(list(PRESETS.keys()))
        self.layout_combo.setStyleSheet("font-size: 11pt; padding: 4px;")
        self.layout_combo.setCurrentText("productivity_single")
        self.layout_combo.setMinimumHeight(28)
        layout_layout.addWidget(layout_label)
        layout_layout.addWidget(self.layout_combo)
        main_layout.addWidget(layout_box)

        # === FONT SIZE SECTION ===
        font_box = QGroupBox("Application Font Size")
        font_box.setStyleSheet("QGroupBox { font-size: 11pt; font-weight: bold; padding-top: 12px; margin-top: 6px; } QGroupBox::title { subcontrol-origin: margin; top: -6px; left: 10px; padding: 0 3px; }")
        font_layout = QVBoxLayout(font_box)
        font_layout.setSpacing(8)
        font_layout.setContentsMargins(12, 16, 12, 12)
        
        font_label = QLabel("Font Size (points):")
        font_label.setStyleSheet("font-size: 11pt;")
        self.font_size_spin = QSpinBox()
        self.font_size_spin.setStyleSheet("font-size: 11pt; padding: 4px;")
        self.font_size_spin.setMinimum(12)
        self.font_size_spin.setMaximum(72)
        self.font_size_spin.setValue(48)
        self.font_size_spin.setSingleStep(2)
        self.font_size_spin.setMinimumHeight(28)
        font_layout.addWidget(font_label)
        font_layout.addWidget(self.font_size_spin)
        main_layout.addWidget(font_box)

        # === UNIVERSITY TASKS SECTION ===
        uni_box = QGroupBox("University Tasks")
        uni_box.setStyleSheet("QGroupBox { font-size: 11pt; font-weight: bold; padding-top: 12px; margin-top: 6px; } QGroupBox::title { subcontrol-origin: margin; top: -6px; left: 10px; padding: 0 3px; }")
        uni_layout = QVBoxLayout(uni_box)
        uni_layout.setContentsMargins(12, 16, 12, 12)
        
        uni_manage_btn = QPushButton("Manage University Tasks")
        uni_manage_btn.setStyleSheet("font-size: 11pt; padding: 6px;")
        uni_manage_btn.setMinimumHeight(32)
        uni_manage_btn.clicked.connect(self._open_uni_dialog)
        uni_layout.addWidget(uni_manage_btn)
        main_layout.addWidget(uni_box)

        # === TODO TASKS SECTION ===
        todo_box = QGroupBox("Todo Tasks")
        todo_box.setStyleSheet("QGroupBox { font-size: 11pt; font-weight: bold; padding-top: 12px; margin-top: 6px; } QGroupBox::title { subcontrol-origin: margin; top: -6px; left: 10px; padding: 0 3px; }")
        todo_layout = QVBoxLayout(todo_box)
        todo_layout.setContentsMargins(12, 16, 12, 12)
        
        todo_manage_btn = QPushButton("Manage Todo Tasks")
        todo_manage_btn.setStyleSheet("font-size: 11pt; padding: 6px;")
        todo_manage_btn.setMinimumHeight(32)
        todo_manage_btn.clicked.connect(self._open_todo_dialog)
        todo_layout.addWidget(todo_manage_btn)
        main_layout.addWidget(todo_box)

        # === LAYOUT EDITOR SECTION (Visual Grid) ===
        editor_box = QGroupBox("Layout Editor")
        editor_box.setStyleSheet("QGroupBox { font-size: 11pt; font-weight: bold; padding-top: 12px; margin-top: 6px; } QGroupBox::title { subcontrol-origin: margin; top: -6px; left: 10px; padding: 0 3px; }")
        editor_layout = QVBoxLayout(editor_box)
        editor_layout.setContentsMargins(12, 16, 12, 12)
        editor_layout.setSpacing(12)

        # Visual grid
        self.layout_grid = LayoutGridWidget(editor_box)
        editor_layout.addWidget(self.layout_grid, 1)

        # Widget source list (for dragging)
        source_label = QLabel("Available Widgets (drag to slots):")
        source_label.setStyleSheet("font-size: 10pt; color: #888888;")
        editor_layout.addWidget(source_label)

        self.widget_source = DraggableWidgetList()
        self.widget_source.setMaximumHeight(100)
        self.widget_source.setStyleSheet("font-size: 10pt; padding: 4px;")
        self.widget_source.setSelectionMode(QAbstractItemView.SelectionMode.SingleSelection)
        
        # Populate with available widgets
        from app.config import WIDGET_TYPES
        for w in WIDGET_TYPES:
            if w != "blank":
                item = QListWidgetItem(w)
                # Make items draggable
                self.widget_source.addItem(item)
        
        # Enable dragging from list
        self.widget_source.setDragDropMode(QAbstractItemView.DragDropMode.DragOnly)
        self.widget_source.setDefaultDropAction(Qt.DropAction.CopyAction)
        editor_layout.addWidget(self.widget_source)

        # Load preset into grid
        self._refresh_grid_from_preset()
        self.layout_combo.currentTextChanged.connect(self._refresh_grid_from_preset)

        main_layout.addWidget(editor_box)

        # Add stretch to push everything to top
        main_layout.addStretch(1)

        # === BUTTONS AT BOTTOM ===
        btn_row = QHBoxLayout()
        btn_row.setSpacing(12)
        info_btn = QPushButton("Info")
        cancel_btn = QPushButton("Cancel")
        launch_btn = QPushButton("Launch Dashboard")

        info_btn.setStyleSheet("font-size: 11pt; padding: 8px; font-weight: bold;")
        cancel_btn.setStyleSheet("font-size: 11pt; padding: 8px; font-weight: bold;")
        launch_btn.setStyleSheet("font-size: 11pt; padding: 8px; font-weight: bold;")
        info_btn.setMinimumHeight(36)
        cancel_btn.setMinimumHeight(36)
        launch_btn.setMinimumHeight(36)

        info_btn.clicked.connect(self._show_info)
        cancel_btn.clicked.connect(self.reject)
        launch_btn.clicked.connect(self._accept)
        btn_row.addStretch(1)
        btn_row.addWidget(info_btn)
        btn_row.addWidget(cancel_btn)
        btn_row.addWidget(launch_btn)
        main_layout.addLayout(btn_row)

    def _show_info(self):
        dialog = QDialog(self)
        dialog.setWindowTitle("About Case Screen Dashboard")
        dialog.setModal(True)
        dialog.setMinimumSize(400, 250)
        layout = QVBoxLayout(dialog)
        layout.setSpacing(12)
        layout.setContentsMargins(24, 24, 24, 24)

        title = QLabel("Case Screen Dashboard")
        title.setStyleSheet("font-size: 14pt; font-weight: bold;")
        layout.addWidget(title)

        credits_text = (
            "Developed by H.Knight\n\n"
            "HYTE Y70ti PC Case Dashboard\n"
            "Minimal, personalized, and productivity-focused\n\n"
            "Contact: hugh.knight17@gmail.com\n"
            "GitHub: https://github.com/HughKnightOCE/Case_Screen_Dashboard\n\n"
            "See README for usage, configuration, and licensing."
        )
        credits = QLabel(credits_text)
        credits.setStyleSheet("font-size: 11pt;")
        credits.setWordWrap(True)
        layout.addWidget(credits)

        btn_row = QHBoxLayout()
        open_readme = QPushButton("Open README")
        open_readme.setStyleSheet("font-size: 11pt; padding: 6px;")
        open_readme.setMinimumHeight(32)
        open_readme.clicked.connect(lambda: webbrowser.open("https://github.com/HughKnightOCE/Case_Screen_Dashboard"))
        btn_row.addWidget(open_readme)

        ok_btn = QPushButton("OK")
        ok_btn.setStyleSheet("font-size: 11pt; padding: 8px;")
        ok_btn.setMinimumHeight(32)
        ok_btn.clicked.connect(dialog.accept)
        btn_row.addStretch(1)
        btn_row.addWidget(ok_btn)
        layout.addLayout(btn_row)

        # offer to open README local file if available
        repo_root = Path(__file__).resolve().parents[1]
        readme_path = repo_root / "README.md"
        if readme_path.exists():
            def open_local_readme():
                QDesktopServices.openUrl(QUrl.fromLocalFile(str(readme_path)))
            open_local = QPushButton("Open Local README")
            open_local.setStyleSheet("font-size: 11pt; padding: 6px;")
            open_local.clicked.connect(open_local_readme)
            layout.addWidget(open_local)

        dialog.exec()

    def _open_uni_dialog(self):
        dialog = QDialog(self)
        dialog.setWindowTitle("Manage University Tasks")
        dialog.setModal(True)
        dialog.setMinimumSize(850, 550)
        layout = QVBoxLayout(dialog)
        layout.setSpacing(12)
        layout.setContentsMargins(16, 16, 16, 16)

        title = QLabel("University Tasks")
        title.setStyleSheet("font-size: 12pt; font-weight: bold;")
        layout.addWidget(title)

        table = QTableWidget(0, 4)
        table.setHorizontalHeaderLabels(["Unit", "Task", "Due Date", "Done"])
        table.setColumnWidth(0, 120)
        table.setColumnWidth(1, 300)
        table.setColumnWidth(2, 180)
        table.setColumnWidth(3, 100)
        table.setMinimumHeight(350)
        table.setStyleSheet("font-size: 11pt; QHeaderView::section { font-size: 11pt; padding: 4px; }")
        layout.addWidget(table)

        # Load existing
        uni_file = Path(__file__).resolve().parents[1] / "uni_tasks.json"
        try:
            data = json.loads(uni_file.read_text(encoding="utf-8"))
            for item in data:
                self._add_uni_row(table, item["unit"], item["task"], item["due"], item.get("done", False))
        except:
            pass

        btn_layout = QHBoxLayout()
        btn_layout.setSpacing(8)
        add_btn = QPushButton("+ Add Task")
        delete_btn = QPushButton("- Delete Selected")
        ok_btn = QPushButton("Done")
        add_btn.setStyleSheet("font-size: 11pt; padding: 6px;")
        delete_btn.setStyleSheet("font-size: 11pt; padding: 6px;")
        ok_btn.setStyleSheet("font-size: 11pt; padding: 6px;")
        add_btn.setMinimumHeight(32)
        delete_btn.setMinimumHeight(32)
        ok_btn.setMinimumHeight(32)
        btn_layout.addWidget(add_btn)
        btn_layout.addWidget(delete_btn)
        btn_layout.addStretch()
        btn_layout.addWidget(ok_btn)
        layout.addLayout(btn_layout)

        add_btn.clicked.connect(lambda: self._add_uni_row(table, "", "", "", False))
        delete_btn.clicked.connect(lambda: self._delete_row(table))
        ok_btn.clicked.connect(dialog.accept)

        dialog.exec()

        # Save
        tasks = []
        for row in range(table.rowCount()):
            unit = table.item(row, 0).text().strip() if table.item(row, 0) else ""
            task = table.item(row, 1).text().strip() if table.item(row, 1) else ""
            due = table.item(row, 2).text().strip() if table.item(row, 2) else ""
            done = table.item(row, 3).checkState() == Qt.CheckState.Checked if table.item(row, 3) else False
            if unit or task:
                tasks.append({"unit": unit, "task": task, "due": due, "done": done})
        try:
            uni_file.write_text(json.dumps(tasks, indent=2), encoding="utf-8")
        except:
            pass

    def _open_todo_dialog(self):
        dialog = QDialog(self)
        dialog.setWindowTitle("Manage Todo Tasks")
        dialog.setModal(True)
        dialog.setMinimumSize(750, 500)
        layout = QVBoxLayout(dialog)
        layout.setSpacing(12)
        layout.setContentsMargins(16, 16, 16, 16)

        title = QLabel("Daily Todo Tasks")
        title.setStyleSheet("font-size: 12pt; font-weight: bold;")
        layout.addWidget(title)

        table = QTableWidget(0, 2)
        table.setHorizontalHeaderLabels(["Task", "Done"])
        table.setColumnWidth(0, 600)
        table.setColumnWidth(1, 100)
        table.setMinimumHeight(350)
        table.setStyleSheet("font-size: 11pt; QHeaderView::section { font-size: 11pt; padding: 4px; }")
        layout.addWidget(table)

        # Load existing
        from app.state import load_state
        try:
            state = load_state()
            for todo in state.todos:
                self._add_todo_row(table, todo.text, todo.done)
        except:
            pass

        btn_layout = QHBoxLayout()
        btn_layout.setSpacing(8)
        add_btn = QPushButton("+ Add Task")
        delete_btn = QPushButton("- Delete Selected")
        ok_btn = QPushButton("Done")
        add_btn.setStyleSheet("font-size: 11pt; padding: 6px;")
        delete_btn.setStyleSheet("font-size: 11pt; padding: 6px;")
        ok_btn.setStyleSheet("font-size: 11pt; padding: 6px;")
        add_btn.setMinimumHeight(32)
        delete_btn.setMinimumHeight(32)
        ok_btn.setMinimumHeight(32)
        btn_layout.addWidget(add_btn)
        btn_layout.addWidget(delete_btn)
        btn_layout.addStretch()
        btn_layout.addWidget(ok_btn)
        layout.addLayout(btn_layout)

        add_btn.clicked.connect(lambda: self._add_todo_row(table, "", False))
        delete_btn.clicked.connect(lambda: self._delete_row(table))
        ok_btn.clicked.connect(dialog.accept)

        dialog.exec()

        # Save
        from app.state import save_state, AppState, TodoItem
        todos = []
        for row in range(table.rowCount()):
            task = table.item(row, 0).text().strip() if table.item(row, 0) else ""
            done = table.item(row, 1).checkState() == Qt.CheckState.Checked if table.item(row, 1) else False
            if task:
                todos.append(TodoItem(text=task, done=done))
        try:
            state = AppState(todos=todos)
            save_state(state)
        except:
            pass

    def _add_uni_row(self, table: QTableWidget, unit: str, task: str, due: str, done: bool):
        row = table.rowCount()
        table.insertRow(row)
        table.setItem(row, 0, QTableWidgetItem(unit))
        table.setItem(row, 1, QTableWidgetItem(task))
        table.setItem(row, 2, QTableWidgetItem(due))
        done_item = QTableWidgetItem("")
        done_item.setFlags(done_item.flags() | Qt.ItemFlag.ItemIsUserCheckable)
        done_item.setCheckState(Qt.CheckState.Checked if done else Qt.CheckState.Unchecked)
        table.setItem(row, 3, done_item)

    def _add_todo_row(self, table: QTableWidget, task: str, done: bool):
        row = table.rowCount()
        table.insertRow(row)
        table.setItem(row, 0, QTableWidgetItem(task))
        done_item = QTableWidgetItem("")
        done_item.setFlags(done_item.flags() | Qt.ItemFlag.ItemIsUserCheckable)
        done_item.setCheckState(Qt.CheckState.Checked if done else Qt.CheckState.Unchecked)
        table.setItem(row, 1, done_item)

    def _delete_row(self, table: QTableWidget):
        row = table.currentRow()
        if row >= 0:
            table.removeRow(row)

    def _accept(self) -> None:
        """
        Persist selections into config object.
        """
        self.cfg.display_index = self.screen_combo.currentIndex()
        self.cfg.font_size = self.font_size_spin.value()
        
        # Get layout from visual grid instead of preset
        self.cfg.layout = self.layout_grid.get_layout()
        
        self.accept()

    def _refresh_grid_from_preset(self) -> None:
        """
        Load the currently selected preset into the visual grid.
        """
        preset_name = self.layout_combo.currentText()
        preset_layout = PRESETS.get(preset_name, PRESETS["productivity_single"])
        self.layout_grid.set_layout(preset_layout)

    def apply_to_config(self):
        return self.cfg
