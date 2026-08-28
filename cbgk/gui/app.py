"""
LuminKey / Apple Monochrome Liquid Glass Desktop Interface for Cosmic Byte Trinity.
"""

import sys
import os
import time
import subprocess
from typing import Dict, List, Optional

from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QGridLayout, QLabel, QPushButton, QComboBox, QSlider, QLineEdit,
    QStackedWidget, QFrame, QColorDialog, QScrollArea, QMessageBox,
    QButtonGroup, QSizePolicy
)
from PyQt6.QtCore import Qt, QTimer, QSize, pyqtSignal
from PyQt6.QtGui import QColor, QIcon, QFont, QPixmap

from .theme import LUMINKEY_STYLESHEET, LUMINKEY_PALETTE
from .icons import create_brand_logo, create_glyph
from .keyboard_canvas import KeyboardCanvas
from .async_worker import AsyncHardwareWorker
from ..matrix import KEYS_87, LIGHTING_MODES, hex_to_rgb, rgb_to_hex
from ..device import Device, DeviceError
from ..protocol import Protocol
from ..profiles import ProfileManager
from ..daemon import send_ipc_command

MONO_PALETTES = [
    ("#CB94F7", "Lavender"),
    ("#FFFFFF", "White"),
    ("#00FFFF", "Cyan"),
    ("#FF007F", "Neon Pink"),
    ("#00FF66", "Emerald"),
    ("#FF3366", "Crimson"),
    ("#FFB800", "Amber"),
]

class MainWindow(QMainWindow):
    """LuminKey / Apple Monochrome Desktop Experience."""

    def __init__(self):
        super().__init__()
        self.setWindowTitle("Cosmic Byte Trinity")
        self.resize(1120, 780)
        self.setMinimumSize(980, 700)
        self.setStyleSheet(LUMINKEY_STYLESHEET)

        self.profile_mgr = ProfileManager()
        self.active_color = "#CB94F7"
        self.active_mode = "custom"
        self.speed = 3
        self.brightness = 4

        # Background async worker for zero-latency hardware communication
        self.worker = AsyncHardwareWorker()
        self.worker.start()

        # Ensure background daemon is active
        self._ensure_background_daemon()

        self._init_ui()
        self._load_initial_profile()

        # Status check timer
        self.status_timer = QTimer(self)
        self.status_timer.timeout.connect(self._check_device_status)
        self.status_timer.start(3000)

    def _ensure_background_daemon(self):
        try:
            send_ipc_command("ping")
        except ConnectionError:
            project_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
            env = dict(os.environ, PYTHONPATH=project_dir)
            cmd = [sys.executable, "-m", "cbgk.daemon"]
            subprocess.Popen(
                cmd,
                cwd=project_dir,
                env=env,
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL,
                stdin=subprocess.DEVNULL,
                start_new_session=True
            )
            time.sleep(0.3)

    def _init_ui(self):
        central = QWidget(self)
        self.setCentralWidget(central)
        root = QHBoxLayout(central)
        root.setContentsMargins(0, 0, 0, 0)
        root.setSpacing(0)

        # -------------------------------------------------------------
        # 1. Left Translucent Sidebar
        # -------------------------------------------------------------
        sidebar = QFrame()
        sidebar.setObjectName("sidebar")
        sidebar.setFixedWidth(200)
        s_layout = QVBoxLayout(sidebar)
        s_layout.setContentsMargins(16, 16, 16, 16)
        s_layout.setSpacing(14)

        # A. macOS Traffic Light Window Dots
        traffic = QHBoxLayout()
        traffic.setSpacing(8)
        for col in [LUMINKEY_PALETTE["traffic_red"], LUMINKEY_PALETTE["traffic_yellow"], LUMINKEY_PALETTE["traffic_green"]]:
            dot = QLabel()
            dot.setFixedSize(12, 12)
            dot.setStyleSheet(f"background-color: {col}; border-radius: 6px;")
            traffic.addWidget(dot)
        traffic.addStretch(1)
        s_layout.addLayout(traffic)

        s_layout.addSpacing(6)

        # B. Brand Header (Logo + Text)
        brand = QHBoxLayout()
        brand.setSpacing(10)
        logo_lbl = QLabel()
        logo_lbl.setPixmap(create_brand_logo(24))
        brand.addWidget(logo_lbl)
        brand_text = QLabel("TRINITY 87K")
        brand_text.setFont(QFont("-apple-system", 12, QFont.Weight.Bold))
        brand_text.setStyleSheet("color: #FFFFFF; letter-spacing: 1px;")
        brand.addWidget(brand_text)
        brand.addStretch(1)
        s_layout.addLayout(brand)

        s_layout.addSpacing(10)

        # C. Navigation Pills (Overview, Keymap, Lighting, Macros, Performance, Settings)
        self.nav_group = QButtonGroup(self)
        self.nav_group.setExclusive(True)

        nav_items = [
            ("overview", "Overview", 0),
            ("keymap", "Keymap", 1),
            ("lighting", "Lighting", 2),
            ("macros", "Macros", 3),
            ("performance", "Performance", 4),
            ("settings", "Settings", 5),
        ]

        for icon_name, title, idx in nav_items:
            btn = QPushButton(f"  {title}")
            btn.setProperty("class", "luminkey-nav")
            btn.setIcon(create_glyph(icon_name, 16))
            btn.setIconSize(QSize(16, 16))
            btn.setCheckable(True)
            if idx == 0:
                btn.setChecked(True)
            btn.clicked.connect(lambda _, i=idx: self.pages_stack.setCurrentIndex(i))
            self.nav_group.addButton(btn, idx)
            s_layout.addWidget(btn)

        s_layout.addStretch(1)

        # D. Bottom Device Card (Matching Reference UI)
        dev_card = QFrame()
        dev_card.setStyleSheet("background-color: rgba(255, 255, 255, 0.04); border: 1px solid rgba(255, 255, 255, 0.07); border-radius: 12px; padding: 10px;")
        dc_layout = QVBoxLayout(dev_card)
        dc_layout.setContentsMargins(10, 8, 10, 8)
        dc_layout.setSpacing(4)

        dev_title = QLabel("Trinity 87K TKL")
        dev_title.setFont(QFont("-apple-system", 10, QFont.Weight.DemiBold))
        dev_title.setStyleSheet("color: #FFFFFF;")
        dc_layout.addWidget(dev_title)

        status_row = QHBoxLayout()
        status_row.setSpacing(6)
        self.status_dot = QLabel("●")
        self.status_dot.setStyleSheet("color: #27C93F; font-size: 10px;")
        self.status_lbl = QLabel("Connected")
        self.status_lbl.setFont(QFont("-apple-system", 9))
        self.status_lbl.setStyleSheet("color: #9E9EA7;")
        status_row.addWidget(self.status_dot)
        status_row.addWidget(self.status_lbl)
        status_row.addStretch(1)
        dc_layout.addLayout(status_row)

        fw_row = QHBoxLayout()
        fw_lbl = QLabel("FW 1.2.0")
        fw_lbl.setFont(QFont("-apple-system", 8))
        fw_lbl.setStyleSheet("color: #5C5C64;")
        fw_row.addWidget(fw_lbl)
        fw_row.addStretch(1)
        dc_layout.addLayout(fw_row)

        s_layout.addWidget(dev_card)
        root.addWidget(sidebar)

        # -------------------------------------------------------------
        # 2. Main Content Canvas
        # -------------------------------------------------------------
        main_content = QWidget()
        m_layout = QVBoxLayout(main_content)
        m_layout.setContentsMargins(28, 20, 28, 20)
        m_layout.setSpacing(16)

        # A. Greeting Header & Profile Dropdown
        header = QHBoxLayout()
        header.setSpacing(12)

        greet_box = QVBoxLayout()
        greet_box.setSpacing(3)
        self.greet_lbl = QLabel("Good evening.")
        self.greet_lbl.setFont(QFont("-apple-system", 18, QFont.Weight.Bold))
        self.greet_lbl.setStyleSheet("color: #FFFFFF; letter-spacing: -0.5px;")

        self.sub_greet = QLabel("Your Trinity 87K is ready to go.")
        self.sub_greet.setFont(QFont("-apple-system", 11))
        self.sub_greet.setStyleSheet("color: #8E8E93;")
        greet_box.addWidget(self.greet_lbl)
        greet_box.addWidget(self.sub_greet)
        header.addLayout(greet_box)

        header.addStretch(1)

        # Top Right Profile Selector Pill
        self.profile_combo = QComboBox()
        self.profile_combo.setFixedWidth(140)
        self._populate_profiles_dropdown()
        self.profile_combo.currentIndexChanged.connect(self._on_profile_dropdown_changed)
        header.addWidget(self.profile_combo)

        btn_more = QPushButton("···")
        btn_more.setProperty("class", "btn-ghost")
        btn_more.setFixedSize(36, 32)
        btn_more.clicked.connect(self._save_current_profile_dialog)
        header.addWidget(btn_more)

        m_layout.addLayout(header)

        # B. Stacked View Pages
        self.pages_stack = QStackedWidget()
        self.pages_stack.addWidget(self._build_overview_page())
        self.pages_stack.addWidget(self._build_placeholder_page("Keymap Studio"))
        self.pages_stack.addWidget(self._build_placeholder_page("Lighting Effects Studio"))
        self.pages_stack.addWidget(self._build_placeholder_page("Macros Studio"))
        self.pages_stack.addWidget(self._build_placeholder_page("Performance & Polling"))
        self.pages_stack.addWidget(self._build_placeholder_page("Settings"))

        m_layout.addWidget(self.pages_stack, 1)
        root.addWidget(main_content, 1)

    def _build_overview_page(self) -> QWidget:
        page = QWidget()
        layout = QVBoxLayout(page)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(14)

        # Create canvas first
        self.canvas = KeyboardCanvas()
        self.canvas.set_active_paint_color(self.active_color)
        self.canvas.keyboardChanged.connect(self._on_canvas_modified)

        # -------------------------------------------------------------
        # Hero Keyboard Showcase Panel (Matching Reference UI)
        # -------------------------------------------------------------
        showcase = QFrame()
        showcase.setProperty("class", "glass-panel")
        sc_layout = QVBoxLayout(showcase)
        sc_layout.setContentsMargins(20, 16, 20, 14)
        sc_layout.setSpacing(8)

        # Top Showcase Header
        sc_header = QHBoxLayout()
        sc_header.setSpacing(8)

        # Quick select buttons in monochrome
        sc_title = QLabel("KEYBOARD MATRIX")
        sc_title.setFont(QFont("-apple-system", 9, QFont.Weight.Bold))
        sc_title.setStyleSheet("color: #5C5C64; letter-spacing: 1px;")
        sc_header.addWidget(sc_title)

        for cat_id, cat_name in [("all", "All"), ("wasd", "WASD"), ("arrows", "Arrows"), ("function", "F-Row")]:
            b = QPushButton(cat_name)
            b.setProperty("class", "btn-ghost")
            b.setFixedHeight(24)
            b.setFont(QFont("-apple-system", 9))
            b.clicked.connect(lambda _, c=cat_id: self.canvas.select_keys_by_category(c))
            sc_header.addWidget(b)

        b_clear = QPushButton("Clear")
        b_clear.setProperty("class", "btn-ghost")
        b_clear.setFixedHeight(24)
        b_clear.setFont(QFont("-apple-system", 9))
        b_clear.clicked.connect(self.canvas.clear_selection)
        sc_header.addWidget(b_clear)

        sc_header.addStretch(1)

        # Battery / Connection Badge in Top Right of Showcase
        self.bat_lbl = QLabel("⚡ 100%  •  USB-C Wired")
        self.bat_lbl.setFont(QFont("-apple-system", 9, QFont.Weight.Medium))
        self.bat_lbl.setStyleSheet("color: #8E8E93;")
        sc_header.addWidget(self.bat_lbl)

        sc_layout.addLayout(sc_header)
        sc_layout.addWidget(self.canvas)

        # Showcase Bottom Specs Row
        sc_footer = QHBoxLayout()
        sc_footer.setSpacing(16)

        layout_badge = QLabel("⌨  Layout   ANSI (87-Key TKL)")
        layout_badge.setFont(QFont("-apple-system", 9, QFont.Weight.Medium))
        layout_badge.setStyleSheet("color: #5C5C64;")
        sc_footer.addWidget(layout_badge)

        sc_footer.addStretch(1)

        poll_badge = QLabel("⚡  Polling Rate   1000 Hz")
        poll_badge.setFont(QFont("-apple-system", 9, QFont.Weight.Medium))
        poll_badge.setStyleSheet("color: #5C5C64;")
        sc_footer.addWidget(poll_badge)

        sc_layout.addLayout(sc_footer)
        layout.addWidget(showcase, 1)

        # -------------------------------------------------------------
        # Bottom 3 Parameter Cards Grid (Matching Reference UI)
        # -------------------------------------------------------------
        cards_row = QHBoxLayout()
        cards_row.setSpacing(14)

        # Card 1: Lighting Mode
        card_mode = QFrame()
        card_mode.setProperty("class", "glass-card")
        cm_layout = QVBoxLayout(card_mode)
        cm_layout.setContentsMargins(16, 14, 16, 14)
        cm_layout.setSpacing(8)

        cm_title = QLabel("Lighting Effect")
        cm_title.setFont(QFont("-apple-system", 11, QFont.Weight.Bold))
        cm_title.setStyleSheet("color: #FFFFFF;")
        cm_layout.addWidget(cm_title)

        self.mode_combo = QComboBox()
        self.mode_combo.addItem("Per-Key Custom RGB", "custom")
        for m_name in LIGHTING_MODES:
            if m_name != "custom":
                self.mode_combo.addItem(m_name.replace("_", " ").title(), m_name)
        self.mode_combo.currentIndexChanged.connect(self._on_mode_combo_changed)
        cm_layout.addWidget(self.mode_combo)

        # Quick Palette Chips
        chips_row = QHBoxLayout()
        chips_row.setSpacing(6)
        for col_hex, name in MONO_PALETTES:
            btn_col = QPushButton()
            btn_col.setFixedSize(20, 20)
            btn_col.setToolTip(name)
            btn_col.setStyleSheet(f"background-color: {col_hex}; border: 1px solid rgba(255,255,255,0.2); border-radius: 10px;")
            btn_col.clicked.connect(lambda _, h=col_hex: self._set_active_color(h))
            chips_row.addWidget(btn_col)

        btn_pick = QPushButton("Picker...")
        btn_pick.setProperty("class", "btn-ghost")
        btn_pick.setFixedHeight(22)
        btn_pick.clicked.connect(self._open_color_picker)
        chips_row.addWidget(btn_pick)
        chips_row.addStretch(1)
        cm_layout.addLayout(chips_row)

        cards_row.addWidget(card_mode, 1)

        # Card 2: Brightness & Speed Sliders
        card_sliders = QFrame()
        card_sliders.setProperty("class", "glass-card")
        cs_layout = QVBoxLayout(card_sliders)
        cs_layout.setContentsMargins(16, 14, 16, 14)
        cs_layout.setSpacing(6)

        cs_title = QLabel("Brightness & Speed")
        cs_title.setFont(QFont("-apple-system", 11, QFont.Weight.Bold))
        cs_title.setStyleSheet("color: #FFFFFF;")
        cs_layout.addWidget(cs_title)

        # Brightness
        b_row = QHBoxLayout()
        self.bright_val_lbl = QLabel("Brightness (100%)")
        self.bright_val_lbl.setFont(QFont("-apple-system", 9))
        self.bright_val_lbl.setStyleSheet("color: #8E8E93;")
        self.bright_slider = QSlider(Qt.Orientation.Horizontal)
        self.bright_slider.setRange(0, 4)
        self.bright_slider.setValue(4)
        self.bright_slider.valueChanged.connect(self._on_sliders_adjusted)
        b_row.addWidget(self.bright_val_lbl)
        b_row.addWidget(self.bright_slider)
        cs_layout.addLayout(b_row)

        # Speed
        s_row = QHBoxLayout()
        self.speed_val_lbl = QLabel("Animation Speed (3)")
        self.speed_val_lbl.setFont(QFont("-apple-system", 9))
        self.speed_val_lbl.setStyleSheet("color: #8E8E93;")
        self.speed_slider = QSlider(Qt.Orientation.Horizontal)
        self.speed_slider.setRange(1, 5)
        self.speed_slider.setValue(3)
        self.speed_slider.valueChanged.connect(self._on_sliders_adjusted)
        s_row.addWidget(self.speed_val_lbl)
        s_row.addWidget(self.speed_slider)
        cs_layout.addLayout(s_row)

        cards_row.addWidget(card_sliders, 1)

        # Card 3: Performance Status (Matching Reference UI Checkmark Card)
        card_perf = QFrame()
        card_perf.setProperty("class", "glass-card")
        cp_layout = QHBoxLayout(card_perf)
        cp_layout.setContentsMargins(16, 14, 16, 14)
        cp_layout.setSpacing(12)

        info_box = QVBoxLayout()
        info_box.setSpacing(4)
        perf_title = QLabel("Performance")
        perf_title.setFont(QFont("-apple-system", 11, QFont.Weight.Bold))
        perf_title.setStyleSheet("color: #FFFFFF;")
        perf_sub = QLabel("All systems optimal.\nHardware sync active.")
        perf_sub.setFont(QFont("-apple-system", 9))
        perf_sub.setStyleSheet("color: #8E8E93;")
        info_box.addWidget(perf_title)
        info_box.addWidget(perf_sub)
        cp_layout.addLayout(info_box, 1)

        # Circular checkmark badge
        check_badge = QLabel()
        check_badge.setPixmap(create_glyph("check", 32, "#FFFFFF").pixmap(32, 32))
        cp_layout.addWidget(check_badge, alignment=Qt.AlignmentFlag.AlignCenter)

        cards_row.addWidget(card_perf, 1)

        layout.addLayout(cards_row)
        return page

    def _build_placeholder_page(self, title: str) -> QWidget:
        page = QWidget()
        layout = QVBoxLayout(page)
        card = QFrame()
        card.setProperty("class", "glass-panel")
        c_layout = QVBoxLayout(card)
        c_layout.setContentsMargins(32, 32, 32, 32)
        c_layout.setSpacing(12)

        lbl = QLabel(title)
        lbl.setFont(QFont("-apple-system", 16, QFont.Weight.Bold))
        lbl.setStyleSheet("color: #FFFFFF;")
        c_layout.addWidget(lbl)

        desc = QLabel("Configure custom settings, key mappings, and macros for your Trinity 87K.")
        desc.setStyleSheet("color: #8E8E93;")
        c_layout.addWidget(desc)
        c_layout.addStretch(1)
        layout.addWidget(card)
        return page

    def _set_active_color(self, hex_color: str):
        self.active_color = hex_color
        self.canvas.set_active_paint_color(hex_color)

        selected = [k for k in KEYS_87 if k.matrix_idx in self.canvas.selected_keys]
        if selected:
            for k in selected:
                self.canvas.set_key_color(k.name, hex_color, notify=False)
            self._dispatch_custom_matrix()
        elif self.active_mode != "custom":
            self._dispatch_preset_mode(self.active_mode)

    def _open_color_picker(self):
        col = QColorDialog.getColor(QColor(self.active_color), self, "Select Color")
        if col.isValid():
            self._set_active_color(col.name().upper())

    def _on_canvas_modified(self):
        """Called when a key is painted on canvas."""
        self.active_mode = "custom"
        self._dispatch_custom_matrix()

    def _on_mode_combo_changed(self, idx: int):
        self.active_mode = self.mode_combo.currentData()
        if self.active_mode != "custom":
            self._dispatch_preset_mode(self.active_mode)
        else:
            self._dispatch_custom_matrix()

    def _on_sliders_adjusted(self):
        self.brightness = self.bright_slider.value()
        self.speed = self.speed_slider.value()
        b_pct = int((self.brightness / 4.0) * 100)
        self.bright_val_lbl.setText(f"Brightness ({b_pct}%)")
        self.speed_val_lbl.setText(f"Animation Speed ({self.speed})")

        if self.active_mode != "custom":
            self._dispatch_preset_mode(self.active_mode)

    def _dispatch_custom_matrix(self):
        """Asynchronously dispatches custom matrix to hardware without lagging UI."""
        self.worker.submit_color(self.active_color, self.canvas.key_colors)

    def _dispatch_preset_mode(self, mode_name: str):
        """Asynchronously dispatches preset mode to hardware without lagging UI."""
        self.worker.submit_mode(mode_name, self.active_color, self.speed, self.brightness)

    def _populate_profiles_dropdown(self):
        self.profile_combo.blockSignals(True)
        self.profile_combo.clear()
        profiles = self.profile_mgr.list_profiles()
        active = self.profile_mgr.get_active_profile_name()
        for idx, p in enumerate(profiles):
            name = p.get("name", "Profile")
            self.profile_combo.addItem(f"  {name}", name)
            if name == active:
                self.profile_combo.setCurrentIndex(idx)
        self.profile_combo.blockSignals(False)

    def _on_profile_dropdown_changed(self, idx: int):
        p_name = self.profile_combo.currentData()
        if p_name:
            self._activate_profile(p_name)

    def _activate_profile(self, name: str):
        prof = self.profile_mgr.get_profile(name)
        if prof:
            self.profile_mgr.set_active_profile_name(name)
            self.canvas.set_color_map(prof.get("per_key", {}))
            self.active_color = prof.get("color", "#CB94F7")
            self.canvas.set_active_paint_color(self.active_color)
            self.active_mode = prof.get("mode", "custom")
            if self.active_mode == "custom":
                self._dispatch_custom_matrix()
            else:
                self._dispatch_preset_mode(self.active_mode)

    def _save_current_profile_dialog(self):
        from PyQt6.QtWidgets import QInputDialog
        name, ok = QInputDialog.getText(self, "Save Profile", "Enter Profile Name:")
        if ok and name.strip():
            data = {
                "name": name.strip(),
                "description": f"Custom profile saved on {time.strftime('%Y-%m-%d')}",
                "mode": self.active_mode,
                "color": self.active_color,
                "speed": self.speed,
                "brightness": self.brightness,
                "per_key": dict(self.canvas.key_colors)
            }
            self.profile_mgr.save_profile(name.strip(), data)
            self._populate_profiles_dropdown()

    def _load_initial_profile(self):
        active = self.profile_mgr.get_active_profile_name()
        prof = self.profile_mgr.get_profile(active)
        if prof:
            self.canvas.set_color_map(prof.get("per_key", {}))
            self.active_color = prof.get("color", "#CB94F7")
            self.canvas.set_active_paint_color(self.active_color)

    def _check_device_status(self):
        try:
            Device.find_device()
            self.status_dot.setStyleSheet("color: #27C93F;")
            self.status_lbl.setText("Connected")
        except DeviceError:
            self.status_dot.setStyleSheet("color: #FFBD2E;")
            self.status_lbl.setText("Searching...")

def main():
    app = QApplication(sys.argv)
    app.setApplicationName("Cosmic Byte Trinity")
    window = MainWindow()
    window.show()
    sys.exit(app.exec())

if __name__ == "__main__":
    main()
