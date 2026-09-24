import ctypes
import sys
from typing import Dict, List, Optional
from PyQt6.QtCore import Qt, QPoint, QTimer, pyqtSignal
from PyQt6.QtGui import QMouseEvent, QAction, QColor, QFont, QKeySequence, QShortcut
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QFrame,
    QPushButton, QToolButton, QMenu, QApplication
)

from app.config import AppConfig
from app.prayer_service import PrayerService
from app.sound import SoundNotifier
from app.styles import get_theme, get_overlay_stylesheet

# Win32 Constants for Click-Through
GWL_EXSTYLE = -20
WS_EX_TRANSPARENT = 0x00000020
WS_EX_LAYERED = 0x00080000

class PrayerCardWidget(QFrame):
    """Individual HUD card displaying a single prayer."""
    def __init__(self, key: str, label: str, parent=None):
        super().__init__(parent)
        self.key = key
        self.setObjectName("PrayerCard")
        self.setProperty("class", "PrayerCard")
        self.setFixedWidth(68)
        self.setFixedHeight(48)
        self.setCursor(Qt.CursorShape.PointingHandCursor)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(3, 3, 3, 3)
        layout.setSpacing(2)
        layout.setAlignment(Qt.AlignmentFlag.AlignCenter)

        self.name_label = QLabel(label)
        self.name_label.setObjectName("PrayerCardName")
        self.name_label.setProperty("class", "PrayerCardName")
        self.name_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(self.name_label)

        self.time_label = QLabel("--:--")
        self.time_label.setObjectName("PrayerCardTime")
        self.time_label.setProperty("class", "PrayerCardTime")
        self.time_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(self.time_label)

    def update_state(self, time_str: str, is_next: bool, is_active: bool, is_past: bool):
        self.time_label.setText(time_str)

        self.setProperty("isNext", "true" if is_next else "false")
        self.setProperty("isPast", "true" if is_past else "false")
        self.setProperty("isActive", "true" if is_active else "false")

        self.name_label.setProperty("isNext", "true" if is_next else "false")
        self.name_label.setProperty("isPast", "true" if is_past else "false")

        self.time_label.setProperty("isNext", "true" if is_next else "false")
        self.time_label.setProperty("isPast", "true" if is_past else "false")

        # Force stylesheet re-evaluation
        self.style().unpolish(self)
        self.style().polish(self)
        self.name_label.style().unpolish(self.name_label)
        self.name_label.style().polish(self.name_label)
        self.time_label.style().unpolish(self.time_label)
        self.time_label.style().polish(self.time_label)


class OverlayWindow(QWidget):
    """
    Main HUD Overlay Window for AuraSalat Desktop Overlay (ASDO).
    Frameless, translucent, movable, click-through capable.
    Supports Desktop Wallpaper layer (doesn't cover open apps) and Compact Mini Bar.
    """
    open_settings_requested = pyqtSignal()

    def __init__(self, config: AppConfig, prayer_service: PrayerService):
        super().__init__()
        self.config = config
        self.prayer_service = prayer_service

        self.drag_position: Optional[QPoint] = None
        self.is_click_through_active: bool = False
        self.cards: Dict[str, PrayerCardWidget] = {}
        self.flash_state: bool = False

        self.init_window_flags()
        self.init_ui()
        self.init_shortcuts()
        self.apply_theme()
        self.apply_initial_layer_and_compact()
        self.restore_position()

        # Connect signals
        self.prayer_service.tick.connect(self.on_prayer_tick)
        self.prayer_service.prayer_alarm.connect(self.on_prayer_alarm)

        # Pulse timer for alerts
        self.pulse_timer = QTimer(self)
        self.pulse_timer.setInterval(600)
        self.pulse_timer.timeout.connect(self.toggle_flash)

        # Apply initial click-through state if enabled in config
        if self.config.get("click_through", False):
            self.set_click_through(True)

    def init_window_flags(self):
        """Sets frameless, translucent, tool, and desktop/top window hints."""
        flags = Qt.WindowType.FramelessWindowHint | Qt.WindowType.Tool
        layer = self.config.get("window_layer", "desktop")

        if layer == "always_on_top":
            flags |= Qt.WindowType.WindowStaysOnTopHint
        elif layer == "desktop":
            flags |= Qt.WindowType.WindowStaysOnBottomHint

        self.setWindowFlags(flags)
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground, True)
        self.setAttribute(Qt.WidgetAttribute.WA_ShowWithoutActivating, True)

    def init_shortcuts(self):
        """Global keyboard shortcuts while ASDO is active."""
        self.sc_settings = QShortcut(QKeySequence("F10"), self)
        self.sc_settings.activated.connect(self.open_settings_requested.emit)

        self.sc_lock = QShortcut(QKeySequence("F9"), self)
        self.sc_lock.activated.connect(self.toggle_click_through)

        self.sc_compact = QShortcut(QKeySequence("F8"), self)
        self.sc_compact.activated.connect(self.toggle_compact_mode)

    def init_ui(self):
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(6, 6, 6, 6)

        # Outer HUD Container Frame
        self.container = QFrame(self)
        self.container.setObjectName("HUDContainer")
        self.container_layout = QVBoxLayout(self.container)
        self.container_layout.setContentsMargins(12, 8, 12, 8)
        self.container_layout.setSpacing(6)

        # 1. Top Bar & Control Buttons
        top_bar = QHBoxLayout()
        top_bar.setSpacing(6)

        self.status_dot = QLabel("●")
        self.status_dot.setObjectName("StatusBadge")
        self.status_dot.setToolTip("Status Koneksi API Kemenag")
        top_bar.addWidget(self.status_dot)

        self.title_label = QLabel("ASDO")
        self.title_label.setObjectName("AppTitle")
        top_bar.addWidget(self.title_label)

        self.city_badge = QLabel(f"[ {self.config.get('city_name', 'KAB. JOMBANG')} ]")
        self.city_badge.setObjectName("StatusBadge")
        top_bar.addWidget(self.city_badge)

        # Compact summary label (displayed when compact mode is active)
        self.compact_summary_label = QLabel("")
        self.compact_summary_label.setObjectName("StatusBadge")
        self.compact_summary_label.setStyleSheet("color: #00ff88; font-weight: bold; margin-left: 4px;")
        self.compact_summary_label.setVisible(False)
        top_bar.addWidget(self.compact_summary_label)

        self.lock_badge = QLabel("[LOCKED 🔒]")
        self.lock_badge.setObjectName("StatusBadge")
        self.lock_badge.setStyleSheet("color: #ffaa00; font-weight: bold;")
        self.lock_badge.setVisible(False)
        top_bar.addWidget(self.lock_badge)

        top_bar.addStretch()

        # Action Buttons
        self.btn_layer = QPushButton("🖥")
        self.btn_layer.setObjectName("HeaderBtn")
        self.btn_layer.setFixedSize(28, 24)
        self.btn_layer.setCursor(Qt.CursorShape.PointingHandCursor)
        self.btn_layer.setToolTip("Ganti Mode Lapisan (Desktop Wallpaper / Always On Top)")
        self.btn_layer.clicked.connect(self.toggle_layer)
        top_bar.addWidget(self.btn_layer)

        self.btn_compact = QPushButton("↕")
        self.btn_compact.setObjectName("HeaderBtn")
        self.btn_compact.setFixedSize(28, 24)
        self.btn_compact.setCursor(Qt.CursorShape.PointingHandCursor)
        self.btn_compact.setToolTip("Beralih Mode Ringkas / Mini Bar (F8)")
        self.btn_compact.clicked.connect(self.toggle_compact_mode)
        top_bar.addWidget(self.btn_compact)

        self.btn_lock = QPushButton("🔒")
        self.btn_lock.setObjectName("HeaderBtn")
        self.btn_lock.setFixedSize(28, 24)
        self.btn_lock.setCursor(Qt.CursorShape.PointingHandCursor)
        self.btn_lock.setToolTip("Kunci Mode Click-Through (F9) - Mouse menembus overlay")
        self.btn_lock.clicked.connect(self.toggle_click_through)
        top_bar.addWidget(self.btn_lock)

        self.btn_settings = QPushButton("⚙")
        self.btn_settings.setObjectName("HeaderBtn")
        self.btn_settings.setFixedSize(28, 24)
        self.btn_settings.setCursor(Qt.CursorShape.PointingHandCursor)
        self.btn_settings.setToolTip("Buka Pengaturan (F10)")
        self.btn_settings.clicked.connect(self.open_settings_requested.emit)
        top_bar.addWidget(self.btn_settings)

        self.btn_minimize = QPushButton("🗕")
        self.btn_minimize.setObjectName("HeaderBtn")
        self.btn_minimize.setFixedSize(28, 24)
        self.btn_minimize.setCursor(Qt.CursorShape.PointingHandCursor)
        self.btn_minimize.setToolTip("Sembunyikan ke System Tray")
        self.btn_minimize.clicked.connect(self.hide)
        top_bar.addWidget(self.btn_minimize)

        self.container_layout.addLayout(top_bar)

        # 2. Hero Section (Wrapped in widget for compact hiding)
        self.hero_container = QWidget()
        hero_layout = QVBoxLayout(self.hero_container)
        hero_layout.setContentsMargins(0, 0, 0, 0)
        hero_layout.setSpacing(1)
        hero_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)

        self.next_header_label = QLabel("NEXT PRAYER: --")
        self.next_header_label.setObjectName("NextPrayerTitle")
        self.next_header_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        hero_layout.addWidget(self.next_header_label)

        self.countdown_label = QLabel("--:--:--")
        self.countdown_label.setObjectName("CountdownDisplay")
        self.countdown_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        hero_layout.addWidget(self.countdown_label)

        self.scheduled_time_label = QLabel("MEMUAT JADWAL...")
        self.scheduled_time_label.setObjectName("StatusBadge")
        self.scheduled_time_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        hero_layout.addWidget(self.scheduled_time_label)

        self.alert_banner = QLabel("⚡ WAKTU SALAT TELAH TIBA! ⚡")
        self.alert_banner.setObjectName("AlertBanner")
        self.alert_banner.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.alert_banner.setVisible(False)
        hero_layout.addWidget(self.alert_banner)

        self.container_layout.addWidget(self.hero_container)

        # 3. 1/3 Malam Terakhir Banner (Tahajjud & Sahur Indicator)
        self.third_night_label = QLabel("🌙 1/3 Malam: Menghitung...")
        self.third_night_label.setObjectName("ThirdNightLabel")
        self.third_night_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.third_night_label.setToolTip("Waktu 1/3 Malam Terakhir dihitung berdasarkan waktu Maghrib & Subuh Kemenag RI.")
        self.container_layout.addWidget(self.third_night_label)

        # 4. Prayer Schedule Cards Row Container
        self.cards_container = QWidget()
        self.cards_row = QHBoxLayout(self.cards_container)
        self.cards_row.setContentsMargins(0, 0, 0, 0)
        self.cards_row.setSpacing(5)
        self.cards_row.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.container_layout.addWidget(self.cards_container)

        # 5. Footer Bar: Date & Real-time Clock
        self.footer_container = QWidget()
        footer_layout = QHBoxLayout(self.footer_container)
        footer_layout.setContentsMargins(0, 4, 0, 0)
        footer_layout.setSpacing(8)

        self.date_label = QLabel("--, -- -- ----")
        self.date_label.setObjectName("DateLabel")
        footer_layout.addWidget(self.date_label)

        footer_layout.addStretch()

        self.time_label = QLabel("--:--:-- WIB")
        self.time_label.setObjectName("TimeLabel")
        footer_layout.addWidget(self.time_label)

        self.container_layout.addWidget(self.footer_container)

        main_layout.addWidget(self.container)

    def apply_initial_layer_and_compact(self):
        layer = self.config.get("window_layer", "desktop")
        if layer == "always_on_top":
            self.btn_layer.setText("📌")
            self.btn_layer.setToolTip("Mode: Always On Top (Klik untuk menempel di Desktop)")
        elif layer == "desktop":
            self.btn_layer.setText("🖥")
            self.btn_layer.setToolTip("Mode: Desktop Wallpaper / Di Bawah Jendela (Klik untuk Always On Top)")
        else:
            self.btn_layer.setText("🗔")
            self.btn_layer.setToolTip("Mode: Jendela Normal")

        compact = self.config.get("compact_mode", False)
        self.set_compact_mode(compact, save_config=False)

    def toggle_layer(self):
        cur = self.config.get("window_layer", "desktop")
        new_layer = "always_on_top" if cur == "desktop" else "desktop"
        self.set_window_layer(new_layer)

    def set_window_layer(self, layer: str):
        self.config.set("window_layer", layer, auto_save=True)
        self.config.set("always_on_top", (layer == "always_on_top"), auto_save=True)

        flags = Qt.WindowType.FramelessWindowHint | Qt.WindowType.Tool
        if layer == "always_on_top":
            flags |= Qt.WindowType.WindowStaysOnTopHint
            self.btn_layer.setText("📌")
            self.btn_layer.setToolTip("Mode: Always On Top (Klik untuk menempel di Desktop)")
        elif layer == "desktop":
            flags |= Qt.WindowType.WindowStaysOnBottomHint
            self.btn_layer.setText("🖥")
            self.btn_layer.setToolTip("Mode: Desktop Wallpaper / Di Bawah Jendela (Klik untuk Always On Top)")
        else:
            self.btn_layer.setText("🗔")
            self.btn_layer.setToolTip("Mode: Jendela Normal")

        self.setWindowFlags(flags)
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground, True)
        self.show()

    def toggle_compact_mode(self):
        cur = self.config.get("compact_mode", False)
        self.set_compact_mode(not cur)

    def set_compact_mode(self, enabled: bool, save_config: bool = True):
        if save_config:
            self.config.set("compact_mode", enabled, auto_save=True)

        self.hero_container.setVisible(not enabled)
        self.third_night_label.setVisible(not enabled)
        self.cards_container.setVisible(not enabled)
        self.footer_container.setVisible(not enabled)
        self.compact_summary_label.setVisible(enabled)

        self.btn_compact.setText("⤢" if enabled else "↕")
        self.btn_compact.setToolTip("Beralih ke Tampilan Penuh (F8)" if enabled else "Beralih ke Mode Ringkas / Mini Bar (F8)")
        self.adjustSize()

    def apply_theme(self):
        """Applies configured theme and opacity."""
        theme_name = self.config.get("theme", "catppuccin_mocha")
        opacity = self.config.get("opacity", 0.94)
        th = get_theme(theme_name, opacity)
        qss = get_overlay_stylesheet(th)
        self.setStyleSheet(qss)

    def rebuild_cards(self, prayer_items: List[dict]):
        """Builds or updates prayer card widgets according to current configuration."""
        existing_keys = list(self.cards.keys())
        new_keys = [item["key"] for item in prayer_items]

        if existing_keys != new_keys:
            for c in self.cards.values():
                self.cards_row.removeWidget(c)
                c.deleteLater()
            self.cards.clear()

            for item in prayer_items:
                card = PrayerCardWidget(item["key"], item["label"], self)
                self.cards[item["key"]] = card
                self.cards_row.addWidget(card)

        # Update each card
        for item in prayer_items:
            k = item["key"]
            if k in self.cards:
                self.cards[k].update_state(
                    time_str=item["time"],
                    is_next=item["is_next"],
                    is_active=item["is_active"],
                    is_past=item["is_past"]
                )

    def on_prayer_tick(self, state: dict):
        """Handles 1-second ticks from PrayerService."""
        self.city_badge.setText(f"[ {state.get('city_name', 'KAB. JOMBANG')} ]")
        self.date_label.setText(state.get("date_display", ""))
        self.time_label.setText(f"{state.get('current_time', '')} WIB")

        # Online status
        is_online = state.get("is_online", False)
        self.status_dot.setText("●" if is_online else "○")
        self.status_dot.setStyleSheet("color: #00ff88;" if is_online else "color: #ffaa00;")
        self.status_dot.setToolTip("Terhubung Online (API MyQuran Kemenag)" if is_online else "Mode Offline (Data Tersimpan)")

        # 1/3 Malam Terakhir Banner
        third_info = state.get("third_night")
        if third_info:
            if third_info["is_active_now"]:
                self.third_night_label.setText(f"✨ 1/3 MALAM TERAKHIR AKTIF ({third_info['start_str']} - {third_info['end_str']} WIB) - WAKTU TAHAJJUD ✨")
                self.third_night_label.setProperty("isActive", "true")
            else:
                self.third_night_label.setText(f"🌙 1/3 Malam Terakhir: {third_info['start_str']} s/d {third_info['end_str']} WIB")
                self.third_night_label.setProperty("isActive", "false")
            self.third_night_label.style().unpolish(self.third_night_label)
            self.third_night_label.style().polish(self.third_night_label)

        if not state.get("has_data", False):
            self.next_header_label.setText("MEMUAT JADWAL...")
            self.countdown_label.setText("--:--:--")
            self.scheduled_time_label.setText("Menghubungi server Kemenag...")
            self.compact_summary_label.setText("MEMUAT JADWAL...")
            return

        # Update Next & Countdown
        next_prayer = state.get("next_prayer", "--")
        next_time = state.get("next_time", "--:--")
        countdown_str = state.get("countdown_str", "--:--:--")
        countdown_secs = state.get("countdown_seconds", 0)

        self.next_header_label.setText(f"NEXT: {next_prayer}")
        self.countdown_label.setText(countdown_str)
        self.scheduled_time_label.setText(f"PUKUL {next_time} WIB")

        # Update Compact Mode inline summary
        third_summary = f" | 1/3 Malam: {third_info['start_str']}" if third_info else ""
        self.compact_summary_label.setText(f"NEXT: {next_prayer} -{countdown_str} ({next_time}){third_summary}")

        # Color coding for countdown
        if countdown_secs <= 900:  # < 15 minutes
            self.countdown_label.setProperty("isWarning", "true")
        else:
            self.countdown_label.setProperty("isWarning", "false")

        # Prayer Active / Adhan Alert
        is_prayer_now = state.get("is_prayer_now", False)
        if is_prayer_now:
            active_name = state.get("active_prayer_name", "")
            self.alert_banner.setText(f"⚡ WAKTU SALAT {active_name} TELAH TIBA! ⚡")
            self.alert_banner.setVisible(True)
            self.countdown_label.setProperty("isAlert", "true")
            if not self.pulse_timer.isActive():
                self.pulse_timer.start()
        else:
            self.alert_banner.setVisible(False)
            self.countdown_label.setProperty("isAlert", "false")
            if self.pulse_timer.isActive():
                self.pulse_timer.stop()

        # Update cards
        self.rebuild_cards(state.get("prayer_items", []))

        # Re-polish countdown style
        self.countdown_label.style().unpolish(self.countdown_label)
        self.countdown_label.style().polish(self.countdown_label)

    def on_prayer_alarm(self, prayer_name: str):
        """Triggered once when prayer time is reached."""
        sound_enabled = self.config.get("sound_enabled", True)
        SoundNotifier.play_adhan_chime(sound_enabled)

    def toggle_flash(self):
        """Blinks alert banner during prayer arrival."""
        self.flash_state = not self.flash_state
        self.alert_banner.setVisible(self.flash_state)

    # Mouse Events for Drag and Reposition
    def mousePressEvent(self, event: QMouseEvent):
        child = self.childAt(event.position().toPoint())
        if child and (isinstance(child, (QPushButton, QToolButton)) or isinstance(child.parent(), (QPushButton, QToolButton))):
            event.ignore()
            return

        if event.button() == Qt.MouseButton.LeftButton and not self.is_click_through_active:
            self.drag_position = event.globalPosition().toPoint() - self.frameGeometry().topLeft()
            event.accept()

    def mouseMoveEvent(self, event: QMouseEvent):
        if event.buttons() == Qt.MouseButton.LeftButton and self.drag_position is not None and not self.is_click_through_active:
            self.move(event.globalPosition().toPoint() - self.drag_position)
            event.accept()

    def mouseReleaseEvent(self, event: QMouseEvent):
        if event.button() == Qt.MouseButton.LeftButton and self.drag_position is not None:
            self.drag_position = None
            self.config.set("window_x", self.x(), auto_save=False)
            self.config.set("window_y", self.y(), auto_save=True)
            event.accept()

    def contextMenuEvent(self, event):
        """Right-click context menu."""
        if self.is_click_through_active:
            return

        menu = QMenu(self)
        menu.setStyleSheet("""
        QMenu {
            background-color: #1e1e2e;
            color: #cdd6f4;
            border: 1px solid #cba6f7;
            font-family: 'Consolas', 'Segoe UI', monospace;
            font-size: 11px;
            padding: 4px;
        }
        QMenu::item {
            padding: 5px 18px 5px 24px;
            border-radius: 3px;
        }
        QMenu::item:selected {
            background-color: #45475a;
            color: #cba6f7;
        }
        QMenu::separator {
            height: 1px;
            background: #313244;
            margin: 4px 8px;
        }
        """)

        action_settings = QAction("⚙ Pengaturan (Settings)...", self)
        action_settings.triggered.connect(self.open_settings_requested.emit)
        menu.addAction(action_settings)

        action_refresh = QAction("🔄 Segarkan Jadwal (Refresh)", self)
        action_refresh.triggered.connect(lambda: self.prayer_service.refresh_schedule(force=True))
        menu.addAction(action_refresh)

        menu.addSeparator()

        action_compact = QAction("↕ Mode Ringkas (Mini Bar)", self)
        action_compact.setCheckable(True)
        action_compact.setChecked(self.config.get("compact_mode", False))
        action_compact.triggered.connect(self.toggle_compact_mode)
        menu.addAction(action_compact)

        # Layer submenu
        cur_layer = self.config.get("window_layer", "desktop")
        action_desktop = QAction("🖥 Menempel di Desktop (Di Bawah Jendela Lain)", self)
        action_desktop.setCheckable(True)
        action_desktop.setChecked(cur_layer == "desktop")
        action_desktop.triggered.connect(lambda: self.set_window_layer("desktop"))
        menu.addAction(action_desktop)

        action_ontop = QAction("📌 Always On Top (Di Atas Semua Jendela)", self)
        action_ontop.setCheckable(True)
        action_ontop.setChecked(cur_layer == "always_on_top")
        action_ontop.triggered.connect(lambda: self.set_window_layer("always_on_top"))
        menu.addAction(action_ontop)

        action_click_through = QAction("🔒 Kunci Mode (Click-Through)", self)
        action_click_through.triggered.connect(self.toggle_click_through)
        menu.addAction(action_click_through)

        action_sound = QAction("🔊 Suara Notifikasi", self)
        action_sound.setCheckable(True)
        action_sound.setChecked(self.config.get("sound_enabled", True))
        action_sound.triggered.connect(self.toggle_sound)
        menu.addAction(action_sound)

        menu.addSeparator()

        action_reset = QAction("⛶ Reset Posisi ke Default", self)
        action_reset.triggered.connect(self.reset_position)
        menu.addAction(action_reset)

        action_hide = QAction("🗕 Sembunyikan ke Tray", self)
        action_hide.triggered.connect(self.hide)
        menu.addAction(action_hide)

        action_quit = QAction("❌ Keluar (Exit)", self)
        action_quit.triggered.connect(QApplication.instance().quit)
        menu.addAction(action_quit)

        menu.exec(event.globalPos())

    def toggle_click_through(self):
        new_state = not self.is_click_through_active
        self.set_click_through(new_state)

    def set_click_through(self, enabled: bool):
        """Enables or disables click-through on Windows using user32 API."""
        self.is_click_through_active = enabled
        self.config.set("click_through", enabled, auto_save=True)
        self.lock_badge.setVisible(enabled)

        if sys.platform == "win32":
            hwnd = int(self.winId())
            try:
                style = ctypes.windll.user32.GetWindowLongW(hwnd, GWL_EXSTYLE)
                if enabled:
                    ctypes.windll.user32.SetWindowLongW(hwnd, GWL_EXSTYLE, style | WS_EX_TRANSPARENT | WS_EX_LAYERED)
                else:
                    ctypes.windll.user32.SetWindowLongW(hwnd, GWL_EXSTYLE, style & ~WS_EX_TRANSPARENT)
            except Exception as e:
                print(f"[Overlay] Click-through error: {e}")

    def toggle_sound(self):
        cur = self.config.get("sound_enabled", True)
        self.config.set("sound_enabled", not cur, auto_save=True)

    def reset_position(self):
        self.move(100, 100)
        self.config.set("window_x", 100, auto_save=False)
        self.config.set("window_y", 100, auto_save=True)

    def restore_position(self):
        """Restores window coordinates with multi-monitor verification."""
        saved_x = self.config.get("window_x", 100)
        saved_y = self.config.get("window_y", 100)

        is_valid = False
        screens = QApplication.screens()
        for s in screens:
            geom = s.geometry()
            if geom.contains(saved_x + 50, saved_y + 50):
                is_valid = True
                break

        if is_valid:
            self.move(saved_x, saved_y)
        else:
            self.move(100, 100)
