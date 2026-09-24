from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtGui import QIcon, QPixmap, QPainter, QColor, QAction
from PyQt6.QtWidgets import QSystemTrayIcon, QMenu, QApplication

from app.config import AppConfig

import os
from app.config import get_base_dir

def create_default_icon() -> QIcon:
    """Loads icon from assets or generates a crisp cyberpunk-styled icon dynamically."""
    icon_path = os.path.join(get_base_dir(), "assets", "icon.png")
    if os.path.exists(icon_path):
        return QIcon(icon_path)

    pixmap = QPixmap(64, 64)
    pixmap.fill(Qt.GlobalColor.transparent)

    painter = QPainter(pixmap)
    painter.setRenderHint(QPainter.RenderHint.Antialiasing)

    # Outer glow ring
    painter.setPen(QColor(0, 243, 255, 120))
    painter.setBrush(QColor(10, 16, 26, 240))
    painter.drawRoundedRect(4, 4, 56, 56, 12, 12)

    # Neon Crescent
    painter.setPen(Qt.PenStyle.NoPen)
    painter.setBrush(QColor(0, 243, 255))
    painter.drawEllipse(14, 14, 34, 34)

    # Inner cut to make crescent shape
    painter.setBrush(QColor(10, 16, 26, 240))
    painter.drawEllipse(22, 12, 28, 28)

    # Star accent / indicator
    painter.setBrush(QColor(0, 255, 136))
    painter.drawEllipse(38, 22, 6, 6)

    painter.end()
    return QIcon(pixmap)

class ASDOTrayIcon(QSystemTrayIcon):
    """System tray icon controller for ASDO."""
    show_settings_requested = pyqtSignal()
    toggle_overlay_requested = pyqtSignal()
    refresh_requested = pyqtSignal()
    reset_pos_requested = pyqtSignal()
    click_through_toggled = pyqtSignal(bool)
    always_on_top_toggled = pyqtSignal(bool)
    layer_mode_toggled = pyqtSignal(str)
    compact_mode_toggled = pyqtSignal(bool)
    sound_toggled = pyqtSignal(bool)

    def __init__(self, config: AppConfig, parent=None):
        super().__init__(parent)
        self.config = config
        self.setIcon(create_default_icon())
        self.setToolTip("AuraSalat Desktop Overlay (ASDO)")

        self.init_menu()
        self.activated.connect(self.on_tray_activated)

    def init_menu(self):
        menu = QMenu()
        menu.setStyleSheet("""
        QMenu {
            background-color: #0f172a;
            color: #f8fafc;
            border: 1px solid #00f3ff;
            font-family: 'Consolas', 'Segoe UI', monospace;
            font-size: 11px;
            padding: 4px;
        }
        QMenu::item {
            padding: 5px 20px 5px 24px;
            border-radius: 3px;
        }
        QMenu::item:selected {
            background-color: #0284c7;
            color: #ffffff;
        }
        QMenu::separator {
            height: 1px;
            background: #334155;
            margin: 4px 8px;
        }
        """)

        self.action_toggle = QAction("👁 Tampilkan / Sembunyikan Overlay", self)
        self.action_toggle.triggered.connect(self.toggle_overlay_requested.emit)
        menu.addAction(self.action_toggle)

        self.action_settings = QAction("⚙ Pengaturan (Settings)...", self)
        self.action_settings.triggered.connect(self.show_settings_requested.emit)
        menu.addAction(self.action_settings)

        self.action_refresh = QAction("🔄 Segarkan Jadwal (Refresh)", self)
        self.action_refresh.triggered.connect(self.refresh_requested.emit)
        menu.addAction(self.action_refresh)

        menu.addSeparator()

        cur_layer = self.config.get("window_layer", "desktop")

        self.action_desktop = QAction("🖥 Mode Desktop (Menempel Wallpaper)", self)
        self.action_desktop.setCheckable(True)
        self.action_desktop.setChecked(cur_layer == "desktop")
        self.action_desktop.triggered.connect(lambda: self.layer_mode_toggled.emit("desktop"))
        menu.addAction(self.action_desktop)

        self.action_ontop = QAction("📌 Always On Top", self)
        self.action_ontop.setCheckable(True)
        self.action_ontop.setChecked(cur_layer == "always_on_top")
        self.action_ontop.triggered.connect(lambda: self.layer_mode_toggled.emit("always_on_top"))
        menu.addAction(self.action_ontop)

        self.action_compact = QAction("↕ Mode Ringkas (Mini Bar)", self)
        self.action_compact.setCheckable(True)
        self.action_compact.setChecked(self.config.get("compact_mode", False))
        self.action_compact.triggered.connect(lambda c: self.compact_mode_toggled.emit(c))
        menu.addAction(self.action_compact)

        self.action_lock = QAction("🔒 Click-Through Mode (Tembus Mouse)", self)
        self.action_lock.setCheckable(True)
        self.action_lock.setChecked(self.config.get("click_through", False))
        self.action_lock.triggered.connect(lambda c: self.click_through_toggled.emit(c))
        menu.addAction(self.action_lock)

        self.action_sound = QAction("🔊 Suara Azan", self)
        self.action_sound.setCheckable(True)
        self.action_sound.setChecked(self.config.get("sound_enabled", True))
        self.action_sound.triggered.connect(lambda c: self.sound_toggled.emit(c))
        menu.addAction(self.action_sound)

        menu.addSeparator()

        self.action_reset = QAction("⛶ Reset Posisi Monitor", self)
        self.action_reset.triggered.connect(self.reset_pos_requested.emit)
        menu.addAction(self.action_reset)

        self.action_quit = QAction("❌ Keluar (Exit ASDO)", self)
        self.action_quit.triggered.connect(QApplication.instance().quit)
        menu.addAction(self.action_quit)

        self.setContextMenu(menu)

    def on_tray_activated(self, reason):
        if reason == QSystemTrayIcon.ActivationReason.Trigger:
            from PyQt6.QtGui import QCursor
            menu = self.contextMenu()
            if menu:
                menu.popup(QCursor.pos())
        elif reason == QSystemTrayIcon.ActivationReason.DoubleClick:
            self.toggle_overlay_requested.emit()

    def update_tooltip(self, next_prayer: str, next_time: str, countdown: str, city: str):
        tip = f"AuraSalat Overlay - {city}\nBerikutnya: {next_prayer} ({next_time})\nSisa Waktu: {countdown}"
        self.setToolTip(tip)

    def update_lock_state(self, is_locked: bool):
        self.action_lock.setChecked(is_locked)

    def show_prayer_notification(self, prayer_name: str, time_str: str):
        """Displays Windows balloon/toast notification."""
        self.showMessage(
            f"Waktu Salat {prayer_name} Telah Tiba!",
            f"Pukul {time_str} WIB - Mari tunaikan salat tepat waktu.",
            QSystemTrayIcon.MessageIcon.Information,
            7000
        )
