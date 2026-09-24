from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit,
    QListWidget, QListWidgetItem, QCheckBox, QSlider, QComboBox,
    QPushButton, QGroupBox, QWidget, QMessageBox, QScrollArea
)

from app.api import MyQuranAPI
from app.config import AppConfig
from app.sound import SoundNotifier
from app.styles import THEMES

class SettingsDialog(QDialog):
    """Clean, beautifully styled Settings Dialog for ASDO."""
    settings_saved = pyqtSignal()

    def __init__(self, config: AppConfig, parent=None):
        super().__init__(parent)
        self.config = config
        self.setWindowTitle("ASDO // PENGATURAN")
        self.setMinimumSize(540, 680)
        self.resize(540, 700)
        self.setWindowFlags(self.windowFlags() & ~Qt.WindowType.WindowContextHelpButtonHint)

        self.selected_city_id = self.config.get("city_id", "1608")
        self.selected_city_name = self.config.get("city_name", "KAB. JOMBANG")

        self.init_ui()
        self.apply_dialog_style()
        self.load_cities_async()

    def init_ui(self):
        main_layout = QVBoxLayout(self)
        main_layout.setSpacing(12)
        main_layout.setContentsMargins(20, 16, 20, 16)

        # Header Title
        title_label = QLabel("AURA SALAT DESKTOP OVERLAY // SETTINGS")
        title_label.setObjectName("DialogHeader")
        main_layout.addWidget(title_label)

        # 1. City / Location Section
        city_group = QGroupBox("LOKASI & JADWAL KEMENAG")
        city_layout = QVBoxLayout(city_group)
        city_layout.setSpacing(8)
        city_layout.setContentsMargins(12, 16, 12, 12)

        self.current_city_label = QLabel(f"Kota Terpilih: {self.selected_city_name} (ID: {self.selected_city_id})")
        self.current_city_label.setObjectName("CityActiveLabel")
        city_layout.addWidget(self.current_city_label)

        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("Ketik nama kota / kabupaten (contoh: Jombang, Surabaya, Jakarta)...")
        self.search_input.textChanged.connect(self.on_search_city)
        self.search_input.setFixedHeight(30)
        city_layout.addWidget(self.search_input)

        self.city_list = QListWidget()
        self.city_list.setFixedHeight(110)
        self.city_list.itemClicked.connect(self.on_city_item_clicked)
        city_layout.addWidget(self.city_list)

        main_layout.addWidget(city_group)

        # 2. Appearance & Theme Section
        theme_group = QGroupBox("TEMA & TAMPILAN HUD")
        theme_layout = QVBoxLayout(theme_group)
        theme_layout.setSpacing(10)
        theme_layout.setContentsMargins(12, 16, 12, 12)

        # Theme Selector
        t_row = QHBoxLayout()
        t_lbl = QLabel("Warna Tema:")
        t_lbl.setFixedWidth(110)
        self.theme_combo = QComboBox()
        self.theme_combo.setFixedHeight(30)
        for key, val in THEMES.items():
            self.theme_combo.addItem(val["name"], key)
        cur_theme = self.config.get("theme", "catppuccin_mocha")
        idx = self.theme_combo.findData(cur_theme)
        if idx >= 0:
            self.theme_combo.setCurrentIndex(idx)
        t_row.addWidget(t_lbl)
        t_row.addWidget(self.theme_combo)
        theme_layout.addLayout(t_row)

        # Opacity Slider
        op_row = QHBoxLayout()
        op_lbl = QLabel("Transparansi HUD:")
        op_lbl.setFixedWidth(110)
        self.opacity_slider = QSlider(Qt.Orientation.Horizontal)
        self.opacity_slider.setRange(40, 100)
        cur_op = int(self.config.get("opacity", 0.94) * 100)
        self.opacity_slider.setValue(cur_op)
        self.opacity_val_lbl = QLabel(f"{cur_op}%")
        self.opacity_val_lbl.setFixedWidth(40)
        self.opacity_slider.valueChanged.connect(lambda v: self.opacity_val_lbl.setText(f"{v}%"))
        op_row.addWidget(op_lbl)
        op_row.addWidget(self.opacity_slider)
        op_row.addWidget(self.opacity_val_lbl)
        theme_layout.addLayout(op_row)

        main_layout.addWidget(theme_group)

        # 3. Behavior Section
        behav_group = QGroupBox("PERILAKU OVERLAY (BEHAVIOR)")
        behav_layout = QVBoxLayout(behav_group)
        behav_layout.setSpacing(8)
        behav_layout.setContentsMargins(12, 16, 12, 12)

        # Layer Mode Row
        layer_row = QHBoxLayout()
        layer_lbl = QLabel("Tingkat Lapisan:")
        layer_lbl.setFixedWidth(110)
        self.layer_combo = QComboBox()
        self.layer_combo.setFixedHeight(30)
        self.layer_combo.addItem("🖥 Menempel di Desktop Wallpaper (Di Bawah Jendela Lain)", "desktop")
        self.layer_combo.addItem("📌 Always On Top (Di Atas Semua Aplikasi)", "always_on_top")
        self.layer_combo.addItem("🗔 Jendela Normal", "normal")
        cur_layer = self.config.get("window_layer", "desktop")
        idx = self.layer_combo.findData(cur_layer)
        if idx >= 0:
            self.layer_combo.setCurrentIndex(idx)
        layer_row.addWidget(layer_lbl)
        layer_row.addWidget(self.layer_combo)
        behav_layout.addLayout(layer_row)

        self.cb_compact = QCheckBox("Mode Ringkas / Mini Bar (Tampilan horizontal tipis, hemat ruang)")
        self.cb_compact.setChecked(self.config.get("compact_mode", False))
        behav_layout.addWidget(self.cb_compact)

        self.cb_third_night = QCheckBox("Tampilkan 1/3 Malam Terakhir (Waktu Utama Salat Tahajjud & Sahur)")
        self.cb_third_night.setChecked(self.config.get("show_third_night", True))
        behav_layout.addWidget(self.cb_third_night)

        self.cb_imsak = QCheckBox("Tampilkan Waktu Imsak")
        self.cb_imsak.setChecked(self.config.get("show_imsak", False))
        behav_layout.addWidget(self.cb_imsak)

        self.cb_click_through = QCheckBox("Click-Through Mode (Mouse menembus overlay, un-lock via F9 / Tray)")
        self.cb_click_through.setChecked(self.config.get("click_through", False))
        behav_layout.addWidget(self.cb_click_through)

        # Sound Row
        sound_row = QHBoxLayout()
        self.cb_sound = QCheckBox("Suara Pengingat Azan (Gentle chime saat waktu salat tiba)")
        self.cb_sound.setChecked(self.config.get("sound_enabled", True))
        sound_row.addWidget(self.cb_sound)

        self.btn_test_sound = QPushButton("Test Suara")
        self.btn_test_sound.setFixedWidth(90)
        self.btn_test_sound.setFixedHeight(26)
        self.btn_test_sound.clicked.connect(lambda: SoundNotifier.play_adhan_chime(True))
        sound_row.addWidget(self.btn_test_sound)
        behav_layout.addLayout(sound_row)

        main_layout.addWidget(behav_group)

        # Action Buttons
        btn_layout = QHBoxLayout()
        btn_layout.setContentsMargins(0, 4, 0, 0)
        self.btn_reset_pos = QPushButton("Reset Posisi Monitor")
        self.btn_reset_pos.setFixedHeight(32)
        self.btn_reset_pos.clicked.connect(self.on_reset_position)
        btn_layout.addWidget(self.btn_reset_pos)

        btn_layout.addStretch()

        self.btn_cancel = QPushButton("Batal")
        self.btn_cancel.setFixedHeight(32)
        self.btn_cancel.clicked.connect(self.reject)
        btn_layout.addWidget(self.btn_cancel)

        self.btn_save = QPushButton("Simpan & Terapkan")
        self.btn_save.setObjectName("PrimarySaveBtn")
        self.btn_save.setFixedHeight(32)
        self.btn_save.clicked.connect(self.save_and_apply)
        btn_layout.addWidget(self.btn_save)

        main_layout.addLayout(btn_layout)

    def load_cities_async(self):
        """Populates initial list of popular cities."""
        cities = MyQuranAPI.get_cities(force_refresh=False)
        self.populate_city_list(cities[:25])

    def populate_city_list(self, cities):
        self.city_list.clear()
        for c in cities:
            item = QListWidgetItem(f"{c['lokasi']} (ID: {c['id']})")
            item.setData(Qt.ItemDataRole.UserRole, c)
            self.city_list.addItem(item)

    def on_search_city(self, text: str):
        if not text.strip():
            self.load_cities_async()
            return
        results = MyQuranAPI.search_cities(text)
        self.populate_city_list(results[:30])

    def on_city_item_clicked(self, item: QListWidgetItem):
        data = item.data(Qt.ItemDataRole.UserRole)
        if data:
            self.selected_city_id = str(data["id"])
            self.selected_city_name = data["lokasi"]
            self.current_city_label.setText(f"Kota Terpilih: {self.selected_city_name} (ID: {self.selected_city_id})")

    def on_reset_position(self):
        self.config.set("window_x", 100, auto_save=False)
        self.config.set("window_y", 100, auto_save=False)
        QMessageBox.information(self, "Posisi Direset", "Posisi overlay telah direset ke default (100, 100). Klik Simpan untuk menerapkan.")

    def save_and_apply(self):
        theme_key = self.theme_combo.currentData()
        opacity = self.opacity_slider.value() / 100.0
        selected_layer = self.layer_combo.currentData()

        updates = {
            "city_id": self.selected_city_id,
            "city_name": self.selected_city_name,
            "theme": theme_key,
            "opacity": opacity,
            "window_layer": selected_layer,
            "always_on_top": (selected_layer == "always_on_top"),
            "compact_mode": self.cb_compact.isChecked(),
            "click_through": self.cb_click_through.isChecked(),
            "sound_enabled": self.cb_sound.isChecked(),
            "show_imsak": self.cb_imsak.isChecked(),
            "show_third_night": self.cb_third_night.isChecked(),
        }
        self.config.update(updates, auto_save=True)
        self.settings_saved.emit()
        self.accept()

    def apply_dialog_style(self):
        self.setStyleSheet("""
        QDialog {
            background-color: #1e1e2e;
            color: #cdd6f4;
            font-family: 'Segoe UI', 'Consolas', sans-serif;
        }
        #DialogHeader {
            color: #cba6f7;
            font-size: 13px;
            font-weight: bold;
            letter-spacing: 1px;
            padding-bottom: 6px;
            border-bottom: 1px solid rgba(203, 166, 247, 0.35);
        }
        QGroupBox {
            color: #b4befe;
            font-size: 11px;
            font-weight: bold;
            border: 1px solid rgba(180, 190, 254, 0.25);
            border-radius: 6px;
            margin-top: 8px;
            padding-top: 14px;
        }
        QGroupBox::title {
            subcontrol-origin: margin;
            subcontrol-position: top left;
            padding: 0 6px;
            color: #cba6f7;
        }
        QLabel {
            color: #cdd6f4;
            font-size: 12px;
        }
        #CityActiveLabel {
            color: #89b4fa;
            font-weight: bold;
            font-size: 12px;
        }
        QLineEdit, QComboBox, QListWidget {
            background-color: #181825;
            color: #cdd6f4;
            border: 1px solid #45475a;
            border-radius: 4px;
            padding: 4px 8px;
            font-family: 'Segoe UI', sans-serif;
            font-size: 12px;
        }
        QLineEdit:focus, QComboBox:focus, QListWidget:focus {
            border: 1px solid #cba6f7;
        }
        QListWidget::item {
            padding: 4px 6px;
            border-radius: 3px;
        }
        QListWidget::item:selected {
            background-color: #45475a;
            color: #cba6f7;
        }
        QCheckBox {
            color: #cdd6f4;
            font-size: 12px;
            spacing: 8px;
        }
        QCheckBox::indicator {
            width: 16px;
            height: 16px;
            background-color: #181825;
            border: 1px solid #45475a;
            border-radius: 3px;
        }
        QCheckBox::indicator:hover {
            border: 1px solid #cba6f7;
        }
        QCheckBox::indicator:checked {
            background-color: #cba6f7;
            border: 1px solid #cba6f7;
            image: none;
        }
        QSlider::groove:horizontal {
            height: 4px;
            background: #313244;
            border-radius: 2px;
        }
        QSlider::sub-page:horizontal {
            background: #cba6f7;
            border-radius: 2px;
        }
        QSlider::handle:horizontal {
            background: #ffffff;
            border: 1px solid #cba6f7;
            width: 14px;
            margin-top: -5px;
            margin-bottom: -5px;
            border-radius: 7px;
        }
        QPushButton {
            background-color: #313244;
            color: #cdd6f4;
            border: 1px solid #45475a;
            border-radius: 4px;
            padding: 4px 12px;
            font-size: 12px;
            font-weight: bold;
        }
        QPushButton:hover {
            background-color: #45475a;
            color: #cba6f7;
            border-color: #cba6f7;
        }
        #PrimarySaveBtn {
            background-color: #89b4fa;
            color: #11111b;
            border: 1px solid #b4befe;
        }
        #PrimarySaveBtn:hover {
            background-color: #b4befe;
        }
        """)
