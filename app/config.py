import json
import os
import sys

DEFAULT_CONFIG = {
    "city_id": "1608",
    "city_name": "KAB. JOMBANG",
    "window_x": 100,
    "window_y": 100,
    "always_on_top": False,
    "window_layer": "desktop",  # "desktop" (on wallpaper), "always_on_top", or "normal"
    "click_through": False,
    "sound_enabled": True,
    "theme": "catppuccin_mocha",
    "opacity": 0.94,
    "compact_mode": False,
    "show_imsak": False,
    "show_third_night": True,
}

def get_base_dir() -> str:
    """Get the base directory whether running as script or frozen PyInstaller exe."""
    if getattr(sys, "frozen", False):
        return os.path.dirname(sys.executable)
    return os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

CONFIG_FILE = os.path.join(get_base_dir(), "config.json")
CACHE_FILE = os.path.join(get_base_dir(), "cache_jadwal.json")
CITIES_CACHE_FILE = os.path.join(get_base_dir(), "cache_cities.json")

class AppConfig:
    """Manages application settings stored in config.json."""

    def __init__(self):
        self.data = dict(DEFAULT_CONFIG)
        self.load()

    def load(self):
        """Loads configuration from config.json if it exists."""
        if os.path.exists(CONFIG_FILE):
            try:
                with open(CONFIG_FILE, "r", encoding="utf-8") as f:
                    saved = json.load(f)
                    if isinstance(saved, dict):
                        self.data.update(saved)
            except Exception as e:
                print(f"[Config] Error loading config: {e}")

    def save(self):
        """Persists current configuration to config.json."""
        try:
            with open(CONFIG_FILE, "w", encoding="utf-8") as f:
                json.dump(self.data, f, indent=4, ensure_ascii=False)
        except Exception as e:
            print(f"[Config] Error saving config: {e}")

    def get(self, key, default=None):
        return self.data.get(key, default)

    def set(self, key, value, auto_save=True):
        self.data[key] = value
        if auto_save:
            self.save()

    def update(self, key_values: dict, auto_save=True):
        self.data.update(key_values)
        if auto_save:
            self.save()
