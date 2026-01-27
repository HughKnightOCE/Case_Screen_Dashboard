import psutil
from PySide6.QtCore import QTimer, Qt
from PySide6.QtWidgets import QWidget, QVBoxLayout, QLabel, QHBoxLayout, QProgressBar
from PySide6.QtGui import QFont


class FanSpeedWidget(QWidget):
    """
    Displays current PC system temperature and hardware status.
    Uses psutil for cross-platform temperature monitoring.
    No WMI dependency - works on all systems.
    """
    
    def __init__(self, parent: QWidget | None = None):
        super().__init__(parent)
        
        # Setup UI
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(12)
        
        # Title
        title = QLabel("Fan & Temperature Monitor")
        title_font = QFont()
        title_font.setPointSize(11)
        title_font.setBold(True)
        title.setFont(title_font)
        layout.addWidget(title)
        
        # CPU Load section
        cpu_label_header = QLabel("CPU Load")
        cpu_label_header.setStyleSheet("color: #aaaaaa; font-size: 10px; font-weight: bold;")
        layout.addWidget(cpu_label_header)
        
        self.cpu_label = QLabel("CPU Load: ---%")
        self.cpu_label.setStyleSheet("color: #cccccc; font-size: 11px;")
        layout.addWidget(self.cpu_label)
        
        self.cpu_bar = QProgressBar()
        self.cpu_bar.setMinimum(0)
        self.cpu_bar.setMaximum(100)
        self.cpu_bar.setValue(0)
        self.cpu_bar.setMaximumHeight(8)
        self.cpu_bar.setStyleSheet("background-color: #222222; border: 1px solid #444444;")
        layout.addWidget(self.cpu_bar)
        
        # Temperatures container
        temp_label_header = QLabel("Temperatures")
        temp_label_header.setStyleSheet("color: #aaaaaa; font-size: 10px; font-weight: bold; margin-top: 12px;")
        layout.addWidget(temp_label_header)
        
        self.temps_container = QVBoxLayout()
        self.temps_container.setSpacing(8)
        layout.addLayout(self.temps_container)
        
        # Status label
        self.status_label = QLabel("Initializing...")
        status_font = QFont()
        status_font.setPointSize(9)
        status_font.setItalic(True)
        self.status_label.setFont(status_font)
        self.status_label.setStyleSheet("color: #888888;")
        layout.addWidget(self.status_label)
        
        layout.addStretch()
        
        # Timer for updates
        self.update_timer = QTimer(self)
        self.update_timer.timeout.connect(self.update_data)
        self.update_timer.start(2000)  # Update every 2 seconds
        
        # Initial update
        self.update_data()
    
    def update_data(self) -> None:
        """Fetch and update system temperature data using psutil."""
        try:
            # Clear old temp items
            while self.temps_container.count():
                self.temps_container.takeAt(0).widget().deleteLater()
            
            # Get CPU load
            cpu_percent = psutil.cpu_percent(interval=0.1)
            self.cpu_label.setText(f"CPU Load: {cpu_percent:.1f}%")
            self.cpu_bar.setValue(int(cpu_percent))
            
            # Try to get temperature sensors
            temps_found = False
            try:
                temps = psutil.sensors_temperatures()
                if temps:
                    for sensor_name, sensor_temps in temps.items():
                        if sensor_temps:
                            # Use the first reading for each sensor
                            for reading in sensor_temps:
                                label = reading.label or sensor_name
                                current_temp = reading.current
                                temps_found = True
                                self._add_temp_item(label, current_temp)
                                # Only show first sensor per type
                                break
            except Exception:
                pass
            
            if temps_found:
                self.status_label.setText("Live monitoring")
            else:
                # Fallback: show CPU frequency
                try:
                    freq = psutil.cpu_freq()
                    if freq:
                        self.status_label.setText(f"CPU Freq: {freq.current:.0f} MHz (no sensors)")
                    else:
                        self.status_label.setText("No temperature sensors available")
                except Exception:
                    self.status_label.setText("No temperature sensors available")
        
        except Exception as e:
            self.status_label.setText(f"Error: {str(e)[:40]}")
    
    def _add_fan_item(self, name: str, rpm: int) -> None:
        """Add a fan speed item to the display."""
        container = QWidget()
        layout = QHBoxLayout(container)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(10)
        
        # Fan name
        name_label = QLabel(name[:30])
        name_label.setMinimumWidth(120)
        name_label.setStyleSheet("color: #aaaaaa; font-size: 10px;")
        layout.addWidget(name_label)
        
        # RPM value
        rpm_label = QLabel(f"{rpm:,} RPM")
        rpm_label.setMinimumWidth(80)
        rpm_label.setAlignment(Qt.AlignmentFlag.AlignRight)
        rpm_label.setStyleSheet("color: #00cc00; font-weight: bold; font-size: 10px;")
        layout.addWidget(rpm_label)
        
        layout.addStretch()
        
        self.fans_container.addWidget(container)
    
    def _add_temp_item(self, name: str, temp_c: float) -> None:
        """Add a temperature item to the display."""
        container = QWidget()
        layout = QHBoxLayout(container)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(10)
        
        # Temperature name
        name_label = QLabel(name[:30])
        name_label.setMinimumWidth(120)
        name_label.setStyleSheet("color: #aaaaaa; font-size: 10px;")
        layout.addWidget(name_label)
        
        # Temperature value with color coding
        temp_label = QLabel(f"{temp_c:.1f}°C")
        temp_label.setMinimumWidth(80)
        temp_label.setAlignment(Qt.AlignmentFlag.AlignRight)
        
        # Color based on temperature
        if temp_c < 40:
            color = "#00cc00"  # Green
        elif temp_c < 60:
            color = "#ffcc00"  # Yellow
        elif temp_c < 80:
            color = "#ff6600"  # Orange
        else:
            color = "#ff0000"  # Red
        
        temp_label.setStyleSheet(f"color: {color}; font-weight: bold; font-size: 10px;")
        layout.addWidget(temp_label)
        
        layout.addStretch()
        
        self.temps_container.addWidget(container)
    
    def get_state(self) -> dict:
        """Return widget state (read-only widget, no state to persist)."""
        return {}
    
    def set_state(self, state: dict) -> None:
        """Restore widget state (read-only widget, no state to restore)."""
        pass
