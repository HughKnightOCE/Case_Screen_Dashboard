import requests
from PySide6.QtWidgets import QWidget, QVBoxLayout, QLabel, QHBoxLayout
from PySide6.QtGui import QPixmap
import datetime

class WeatherWidget(QWidget):
    """
    Minimal weather widget: shows current weather and short forecast for a chosen location.
    """
    def __init__(self, location="Melbourne,AU"):
        super().__init__()
        self.location = location
        self.setLayout(QVBoxLayout())
        self.title = QLabel(f"Weather – {self.location}")
        self.title.setStyleSheet("font-size: 16px; font-weight: bold;")
        self.layout().addWidget(self.title)
        self.weather_label = QLabel("Loading weather...")
        self.layout().addWidget(self.weather_label)
        self.icon_label = QLabel()
        self.layout().addWidget(self.icon_label)
        self.refresh_weather()

    def refresh_weather(self):
        # Use Open-Meteo (no API key required)
        lat, lon = self._get_lat_lon(self.location)
        if lat is None or lon is None:
            self.weather_label.setText("Location not found.")
            self.weather_label.setStyleSheet("color: #ff8800;")
            return
        url = f"https://api.open-meteo.com/v1/forecast?latitude={lat}&longitude={lon}&current_weather=true"
        try:
            resp = requests.get(url, timeout=5)
            data = resp.json()
            weather = data.get("current_weather", {})
            temp = weather.get("temperature")
            code = weather.get("weathercode")
            desc = self._weather_desc(code)
            self.weather_label.setText(f"{desc}, {temp}°C")
            self.weather_label.setStyleSheet("color: #ffffff;")
            self.icon_label.setPixmap(self._icon_for_code(code))
        except requests.exceptions.ConnectionError:
            self.weather_label.setText("No internet connection")
            self.weather_label.setStyleSheet("color: #ff8800;")
        except Exception as e:
            self.weather_label.setText(f"Weather unavailable ({str(e)[:30]})")
            self.weather_label.setStyleSheet("color: #ff8800;")

    def _get_lat_lon(self, location):
        # Simple lookup for demo (expand with geocoding API if needed)
        locations = {
            "Melbourne,AU": (-37.8136, 144.9631),
            "Sydney,AU": (-33.8688, 151.2093),
            "London,UK": (51.5074, -0.1278),
            "New York,US": (40.7128, -74.0060),
        }
        return locations.get(location, (None, None))

    def _weather_desc(self, code):
        # Open-Meteo weather codes
        descs = {
            0: "Clear",
            1: "Mainly clear",
            2: "Partly cloudy",
            3: "Overcast",
            45: "Fog",
            48: "Depositing rime fog",
            51: "Drizzle",
            61: "Rain",
            71: "Snow",
            80: "Rain showers",
            95: "Thunderstorm",
        }
        return descs.get(code, "Unknown")

    def _icon_for_code(self, code):
        # Placeholder: return empty pixmap
        return QPixmap()

    def get_state(self):
        return {"location": self.location}

    def set_state(self, state):
        self.location = state.get("location", self.location)
        self.title.setText(f"Weather – {self.location}")
        self.refresh_weather()
