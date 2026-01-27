from PySide6.QtCore import QTimer, Qt
from PySide6.QtWidgets import QWidget, QVBoxLayout, QLabel, QHBoxLayout, QProgressBar
from PySide6.QtGui import QFont


class FanSpeedWidget(QWidget):
    """
    Displays current PC fan speeds and temperatures.
    Read-only monitoring widget that queries WMI for fan data.
    """
    
    def __init__(self, parent: QWidget | None = None):
        super().__init__(parent)
        
        self.wmi_interface = None
        self.fan_items = []
        self.temp_items = []
        
        # Try to initialize WMI (lazy import)
        try:
            import wmi
            self.wmi_interface = wmi.WMI(namespace="root\\cimv2")
        except Exception as e:
            self.wmi_interface = None
        
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
        
        # Fan speeds container
        self.fans_container = QVBoxLayout()
        self.fans_container.setSpacing(8)
        layout.addLayout(self.fans_container)
        
        # Temperatures container
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
        """Fetch and update fan/temperature data from WMI."""
        if not self.wmi_interface:
            self.status_label.setText("WMI unavailable - install python-wmi package")
            self.status_label.setStyleSheet("color: #ff8800; font-style: italic;")
            return
        
        try:
            # Clear old items
            while self.fans_container.count():
                self.fans_container.takeAt(0).widget().deleteLater()
            while self.temps_container.count():
                self.temps_container.takeAt(0).widget().deleteLater()
            
            self.fan_items.clear()
            self.temp_items.clear()
            
            # Query fans
            fans_found = False
            try:
                for fan in self.wmi_interface.Win32_Fan():
                    if fan.Name and fan.CurrentSpeed:
                        fans_found = True
                        self._add_fan_item(fan.Name, int(fan.CurrentSpeed))
            except Exception:
                pass
            
            # Query temperatures
            temps_found = False
            try:
                for temp in self.wmi_interface.Win32_TemperatureProbe():
                    if temp.Name and temp.CurrentReading:
                        temps_found = True
                        # Convert to Celsius (WMI returns in 1/10th degree Kelvin)
                        temp_c = (int(temp.CurrentReading) - 2732) / 10
                        self._add_temp_item(temp.Name, temp_c)
            except Exception:
                pass
            
            if fans_found or temps_found:
                self.status_label.setText("Live monitoring")
            else:
                self.status_label.setText("No fan/temperature data available")
        
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
