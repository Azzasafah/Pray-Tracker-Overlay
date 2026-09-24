import sys
import threading
from PyQt6.QtCore import QTimer
from PyQt6.QtWidgets import QApplication

from app.config import AppConfig
from app.overlay_window import OverlayWindow
from app.prayer_service import PrayerService
from app.settings_dialog import SettingsDialog
from app.tray_icon import ASDOTrayIcon, create_default_icon

class ASDOApp:
    """Main Application Coordinator for AuraSalat Desktop Overlay."""

    def __init__(self):
        self.app = QApplication(sys.argv)
        self.app.setApplicationName("AuraSalat Desktop Overlay")
        self.app.setApplicationDisplayName("ASDO")
        self.app.setWindowIcon(create_default_icon())
        # Keep app running in tray when overlay is hidden
        self.app.setQuitOnLastWindowClosed(False)

        # 1. Configuration
        self.config = AppConfig()

        # 2. Prayer Calculation Service
        city_id = self.config.get("city_id", "1608")
        show_imsak = self.config.get("show_imsak", False)
        show_third_night = self.config.get("show_third_night", True)
        self.prayer_service = PrayerService(
            city_id=city_id,
            show_imsak=show_imsak,
            show_third_night=show_third_night
        )

        # 3. HUD Overlay Window
        self.overlay = OverlayWindow(self.config, self.prayer_service)
        self.overlay.open_settings_requested.connect(self.open_settings)

        # 4. System Tray Icon
        self.tray = ASDOTrayIcon(self.config)
        self.tray.show()

        # Connect Tray signals
        self.tray.show_settings_requested.connect(self.open_settings)
        self.tray.toggle_overlay_requested.connect(self.toggle_overlay_visibility)
        self.tray.refresh_requested.connect(lambda: self.prayer_service.refresh_schedule(force=True))
        self.tray.reset_pos_requested.connect(self.overlay.reset_position)
        self.tray.click_through_toggled.connect(self.overlay.set_click_through)
        self.tray.layer_mode_toggled.connect(self.overlay.set_window_layer)
        self.tray.compact_mode_toggled.connect(self.overlay.set_compact_mode)
        self.tray.sound_toggled.connect(self.set_sound_enabled)

        # Connect prayer tick to update tray tooltip
        self.prayer_service.tick.connect(self.on_prayer_tick)
        self.prayer_service.prayer_alarm.connect(self.on_prayer_alarm)

        # 5. Timer for real-time 1-second ticks
        self.timer = QTimer()
        self.timer.setInterval(1000)
        self.timer.timeout.connect(self.prayer_service.update_tick)
        self.timer.start()

        # 6. Initial Schedule Fetch in background thread so UI starts instantly
        self.init_fetch_thread = threading.Thread(
            target=self.prayer_service.refresh_schedule,
            daemon=True
        )
        self.init_fetch_thread.start()

        # Show overlay
        self.overlay.show()

    def on_prayer_tick(self, state: dict):
        if state.get("has_data", False):
            self.tray.update_tooltip(
                next_prayer=state.get("next_prayer", "--"),
                next_time=state.get("next_time", "--:--"),
                countdown=state.get("countdown_str", "--:--:--"),
                city=state.get("city_name", "INDONESIA")
            )

    def on_prayer_alarm(self, prayer_name: str):
        # Show Windows tray balloon notification
        if self.prayer_service.schedule:
            time_str = self.prayer_service.schedule.get(prayer_name.lower(), "")
            self.tray.show_prayer_notification(prayer_name, time_str)

    def toggle_overlay_visibility(self):
        if self.overlay.isVisible():
            self.overlay.hide()
        else:
            self.overlay.show()
            self.overlay.raise_()

    def set_always_on_top(self, enabled: bool):
        self.config.set("always_on_top", enabled)
        from PyQt6.QtCore import Qt
        self.overlay.setWindowFlag(Qt.WindowType.WindowStaysOnTopHint, enabled)
        self.overlay.show()

    def set_sound_enabled(self, enabled: bool):
        self.config.set("sound_enabled", enabled)

    def open_settings(self):
        dialog = SettingsDialog(self.config, parent=self.overlay)
        dialog.settings_saved.connect(self.on_settings_applied)
        dialog.exec()

    def on_settings_applied(self):
        # Update prayer service
        new_city_id = self.config.get("city_id", "1608")
        self.prayer_service.show_imsak = self.config.get("show_imsak", False)
        self.prayer_service.show_third_night = self.config.get("show_third_night", True)
        self.prayer_service.set_city(new_city_id)

        # Update overlay styling & behavior
        self.overlay.apply_theme()
        self.overlay.set_compact_mode(self.config.get("compact_mode", False), save_config=False)
        self.overlay.set_window_layer(self.config.get("window_layer", "desktop"))
        self.overlay.set_click_through(self.config.get("click_through", False))
        self.tray.update_lock_state(self.config.get("click_through", False))

    def run(self) -> int:
        return self.app.exec()

if __name__ == "__main__":
    app_instance = ASDOApp()
    sys.exit(app_instance.run())
