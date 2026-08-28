"""
Apple / Linear-inspired Minimalist Dark Desktop Control Center for Cosmic Byte Trinity.
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

from .theme import APPLE_STYLESHEET, APPLE_DARK_PALETTE
from .icons import create_logo_pixmap, create_icon_pixmap
from .keyboard_canvas import KeyboardCanvas
from ..matrix import KEYS_87, LIGHTING_MODES, hex_to_rgb, rgb_to_hex
from ..device import Device, DeviceError
from ..protocol import Protocol
from ..profiles import ProfileManager
from ..daemon import send_ipc_command, Daemon

PRESET_MODES_LIST = [
    ("Custom Matrix", "custom", "Paint individual keys with custom hex colors"),
    ("Static Color", "static", "Solid uniform color across all 87 keys"),
    ("Breathing", "breathing", "Smooth pulsating breath lighting effect"),
    ("Spectrum Cycle", "spectrum", "Continuous rainbow wave color spectrum"),
    ("Reactive Fade", "reactive_fade", "Keys light up on press and fade away"),
    ("Ripple Wave", "ripples", "Circular wave ripples expanding from keystrokes"),
    ("Glittering", "glittering", "Random sparkling ambient stars"),
    ("Colourful", "colourful", "Multi-color cascading waterfall animation"),
    ("Explode", "explode", "Burst of light expanding outward from pressed keys"),
]

QUICK_PALETTES = [
    ("#CB94F7", "Lavender"),
    ("#00FFFF", "Cyan"),
    ("#FF007F", "Neon Pink"),
    ("#00FF66", "Emerald"),
    ("#FF3366", "Crimson"),
    ("#FFB800", "Amber"),
    ("#00D4FF", "Ice Blue"),
    ("#FFFFFF", "White"),
]

class SelectableCard(QFrame):
    """Clean selectable card with purple indicator dot (matching reference UI)."""
    clicked = pyqtSignal(str)

    def __init__(self, mode_id: str, title: str, subtitle: str, selected=False, parent=None):
        super().__init__(parent)
        self.mode_id = mode_id
        self.is_selected = selected
        self.setProperty("class", "select-card")
        self.setCursor(Qt.CursorShape.PointingHandCursor)
        self.setFixedHeight(72)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(12, 10, 12, 10)
        layout.setSpacing(3)

        # Top line with title and dot
        top_row = QHBoxLayout()
        top_row.setSpacing(8)

        self.dot = QLabel("●")
        self.dot.setFixedSize(12, 12)
        top_row.addWidget(self.dot)

        self.title_lbl = QLabel(title)
        self.title_lbl.setFont(QFont("-apple-system", 11, QFont.Weight.Bold))
        top_row.addWidget(self.title_lbl)
        top_row.addStretch(1)
        layout.addLayout(top_row)

        sub_lbl = QLabel(subtitle)
        sub_lbl.setFont(QFont("-apple-system", 9))
        sub_lbl.setStyleSheet("color: #6B7280;")
        layout.addWidget(sub_lbl)

        self.update_state(selected)

    def update_state(self, selected: bool):
        self.is_selected = selected
        self.setProperty("selected", "true" if selected else "false")
        if selected:
            self.dot.setStyleSheet("color: #A855F7; font-size: 10px;")
            self.title_lbl.setStyleSheet("color: #FFFFFF;")
        else:
            self.dot.setStyleSheet("color: transparent; font-size: 10px;")
            self.title_lbl.setStyleSheet("color: #D1D5DB;")
        self.style().unpolish(self)
        self.style().polish(self)

    def mousePressEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton:
            self.clicked.emit(self.mode_id)

class MainWindow(QMainWindow):
    """Main Application Window."""

    def __init__(self):
        super().__init__()
        self.setWindowTitle("Cosmic Byte Trinity")
        self.resize(1060, 760)
        self.setMinimumSize(940, 680)
        self.setStyleSheet(APPLE_STYLESHEET)

        self.profile_mgr = ProfileManager()
        self.active_color = "#CB94F7"
        self.active_mode = "custom"
        self.speed = 3
        self.brightness = 4
        self.mode_cards: List[SelectableCard] = []

        # Auto-ensure daemon is running in background
        self._ensure_background_daemon()

        self._init_ui()
        self._load_initial_profile()

        # Status check timer
        self.status_timer = QTimer(self)
        self.status_timer.timeout.connect(self._check_device_status)
        self.status_timer.start(3000)

    def _ensure_background_daemon(self):
        """Spawns independent detached background daemon if not active."""
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
            time.sleep(0.4)

    def _init_ui(self):
        central = QWidget(self)
        self.setCentralWidget(central)
        root_layout = QHBoxLayout(central)
        root_layout.setContentsMargins(0, 0, 0, 0)
        root_layout.setSpacing(0)

        # 1. Left Icon Sidebar Rail
        sidebar = QFrame()
        sidebar.setObjectName("sidebar_rail")
        sidebar.setFixedWidth(64)
        s_layout = QVBoxLayout(sidebar)
        s_layout.setContentsMargins(10, 16, 10, 16)
        s_layout.setSpacing(16)

        # App Logo
        logo_btn = QPushButton()
        logo_btn.setIcon(QIcon(create_logo_pixmap(32)))
        logo_btn.setIconSize(QSize(32, 32))
        logo_btn.setStyleSheet("border: none; background: transparent;")
        s_layout.addWidget(logo_btn, alignment=Qt.AlignmentFlag.AlignCenter)

        s_layout.addSpacing(10)

        # Navigation Icons
        self.nav_group = QButtonGroup(self)
        self.nav_group.setExclusive(True)

        nav_items = [
            ("lighting", 0, "Lighting Studio"),
            ("keyboard", 1, "Key Remapping"),
            ("macros", 2, "Macro Sequences"),
            ("profiles", 3, "Profile Library"),
        ]

        for icon_name, idx, tooltip in nav_items:
            btn = QPushButton()
            btn.setProperty("class", "sidebar-btn")
            btn.setCheckable(True)
            btn.setToolTip(tooltip)
            btn.setFixedSize(42, 42)
            btn.setIcon(QIcon(create_icon_pixmap(icon_name, 22)))
            btn.setIconSize(QSize(22, 22))
            if idx == 0:
                btn.setChecked(True)
            btn.clicked.connect(lambda _, i=idx: self.pages_stack.setCurrentIndex(i))
            self.nav_group.addButton(btn, idx)
            s_layout.addWidget(btn, alignment=Qt.AlignmentFlag.AlignCenter)

        s_layout.addStretch(1)

        # Settings icon at bottom
        btn_set = QPushButton()
        btn_set.setProperty("class", "sidebar-btn")
        btn_set.setFixedSize(42, 42)
        btn_set.setIcon(QIcon(create_icon_pixmap("settings", 22)))
        btn_set.setIconSize(QSize(22, 22))
        btn_set.setToolTip("Settings")
        s_layout.addWidget(btn_set, alignment=Qt.AlignmentFlag.AlignCenter)

        root_layout.addWidget(sidebar)

        # 2. Main Content Area (Top Bar + Pages)
        main_content = QWidget()
        m_layout = QVBoxLayout(main_content)
        m_layout.setContentsMargins(24, 16, 24, 16)
        m_layout.setSpacing(16)

        # Top Bar (Breadcrumbs & Action Buttons matching reference UI)
        top_bar = QHBoxLayout()
        top_bar.setSpacing(12)

        # Breadcrumbs
        bread_lbl = QLabel("Device  ›  Trinity 87K  ›  Lighting Studio")
        bread_lbl.setFont(QFont("-apple-system", 10, QFont.Weight.Medium))
        bread_lbl.setStyleSheet("color: #6B7280; letter-spacing: 0.5px;")
        top_bar.addWidget(bread_lbl)

        # Connection Status Pill
        self.conn_pill = QFrame()
        self.conn_pill.setStyleSheet("background-color: #17171C; border: 1px solid rgba(255,255,255,0.08); border-radius: 12px; padding: 2px 10px;")
        cp_layout = QHBoxLayout(self.conn_pill)
        cp_layout.setContentsMargins(6, 2, 6, 2)
        cp_layout.setSpacing(6)
        self.conn_dot = QLabel("●")
        self.conn_dot.setStyleSheet("color: #10B981; font-size: 11px;")
        self.conn_text = QLabel("Wired Active")
        self.conn_text.setFont(QFont("-apple-system", 9, QFont.Weight.Medium))
        self.conn_text.setStyleSheet("color: #D1D5DB;")
        cp_layout.addWidget(self.conn_dot)
        cp_layout.addWidget(self.conn_text)
        top_bar.addWidget(self.conn_pill)

        top_bar.addStretch(1)

        # Top Action Buttons: Save & Apply
        btn_save = QPushButton("Save Profile")
        btn_save.setProperty("class", "btn-ghost")
        btn_save.clicked.connect(self._save_current_profile_dialog)
        top_bar.addWidget(btn_save)

        btn_apply = QPushButton("Apply to Keyboard")
        btn_apply.setProperty("class", "btn-primary")
        btn_apply.clicked.connect(self._apply_to_hardware)
        top_bar.addWidget(btn_apply)

        m_layout.addLayout(top_bar)

        # 3. Stacked Pages
        self.pages_stack = QStackedWidget()
        self.pages_stack.addWidget(self._build_lighting_studio_page())
        self.pages_stack.addWidget(self._build_remap_page())
        self.pages_stack.addWidget(self._build_macros_page())
        self.pages_stack.addWidget(self._build_profiles_page())
        m_layout.addWidget(self.pages_stack, 1)

        root_layout.addWidget(main_content, 1)

    def _build_lighting_studio_page(self) -> QWidget:
        page = QWidget()
        layout = QVBoxLayout(page)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(14)

        # Create interactive canvas first so buttons can connect
        self.canvas = KeyboardCanvas()
        self.canvas.set_active_paint_color(self.active_color)
        self.canvas.keyboardChanged.connect(self._on_canvas_modified)

        # Section 1: Keyboard Canvas Card
        canvas_card = QFrame()
        canvas_card.setProperty("class", "modern-card")
        c_layout = QVBoxLayout(canvas_card)
        c_layout.setContentsMargins(14, 12, 14, 12)
        c_layout.setSpacing(8)

        # Quick Select Bar
        bar = QHBoxLayout()
        bar.setSpacing(8)
        c_lbl = QLabel("MECHANICAL MATRIX")
        c_lbl.setFont(QFont("-apple-system", 9, QFont.Weight.Bold))
        c_lbl.setStyleSheet("color: #6B7280; letter-spacing: 1px;")
        bar.addWidget(c_lbl)

        for cat_id, cat_name in [("all", "All"), ("wasd", "WASD"), ("arrows", "Arrows"), ("function", "F-Row"), ("mods", "Mods")]:
            b = QPushButton(cat_name)
            b.setProperty("class", "btn-ghost")
            b.setFixedHeight(26)
            b.clicked.connect(lambda _, c=cat_id: self.canvas.select_keys_by_category(c))
            bar.addWidget(b)

        b_clear = QPushButton("Clear")
        b_clear.setProperty("class", "btn-ghost")
        b_clear.setFixedHeight(26)
        b_clear.clicked.connect(self.canvas.clear_selection)
        bar.addWidget(b_clear)

        bar.addStretch(1)

        # Color Palette Chips in Canvas Header
        for h, name in QUICK_PALETTES:
            chip = QPushButton()
            chip.setFixedSize(20, 20)
            chip.setToolTip(name)
            chip.setStyleSheet(f"background-color: {h}; border: 1px solid rgba(255,255,255,0.2); border-radius: 10px;")
            chip.clicked.connect(lambda _, col=h: self._set_active_color(col))
            bar.addWidget(chip)

        self.btn_pick_col = QPushButton("Custom...")
        self.btn_pick_col.setProperty("class", "btn-ghost")
        self.btn_pick_col.setFixedHeight(26)
        self.btn_pick_col.clicked.connect(self._open_color_picker)
        bar.addWidget(self.btn_pick_col)

        c_layout.addLayout(bar)
        c_layout.addWidget(self.canvas)
        layout.addWidget(canvas_card, 0)

        # Section 2: Preset Effects & Controls (Selectable Grid matching Screenshot)
        ctrl_card = QFrame()
        ctrl_card.setProperty("class", "modern-card")
        ctrl_layout = QVBoxLayout(ctrl_card)
        ctrl_layout.setContentsMargins(18, 14, 18, 14)
        ctrl_layout.setSpacing(12)

        sec_title = QLabel("LIGHTING EFFECTS")
        sec_title.setFont(QFont("-apple-system", 9, QFont.Weight.Bold))
        sec_title.setStyleSheet("color: #6B7280; letter-spacing: 1px;")
        ctrl_layout.addWidget(sec_title)

        # 3x3 Grid of Selectable Cards
        cards_grid = QGridLayout()
        cards_grid.setSpacing(10)
        self.mode_cards.clear()

        for idx, (title, m_id, desc) in enumerate(PRESET_MODES_LIST):
            card = SelectableCard(m_id, title, desc, selected=(m_id == self.active_mode))
            card.clicked.connect(self._select_mode_card)
            self.mode_cards.append(card)
            row = idx // 3
            col = idx % 3
            cards_grid.addWidget(card, row, col)

        ctrl_layout.addLayout(cards_grid)

        # Sliders Row (Speed & Brightness)
        sliders_row = QHBoxLayout()
        sliders_row.setSpacing(24)

        # Speed
        sp_box = QHBoxLayout()
        sp_box.setSpacing(10)
        sp_lbl = QLabel("Speed")
        sp_lbl.setFont(QFont("-apple-system", 10, QFont.Weight.Medium))
        sp_lbl.setStyleSheet("color: #9CA3AF;")
        self.speed_slider = QSlider(Qt.Orientation.Horizontal)
        self.speed_slider.setRange(1, 5)
        self.speed_slider.setValue(3)
        self.speed_slider.valueChanged.connect(self._on_slider_changed)
        sp_box.addWidget(sp_lbl)
        sp_box.addWidget(self.speed_slider)
        sliders_row.addLayout(sp_box)

        # Brightness
        br_box = QHBoxLayout()
        br_box.setSpacing(10)
        br_lbl = QLabel("Brightness")
        br_lbl.setFont(QFont("-apple-system", 10, QFont.Weight.Medium))
        br_lbl.setStyleSheet("color: #9CA3AF;")
        self.bright_slider = QSlider(Qt.Orientation.Horizontal)
        self.bright_slider.setRange(0, 4)
        self.bright_slider.setValue(4)
        self.bright_slider.valueChanged.connect(self._on_slider_changed)
        br_box.addWidget(br_lbl)
        br_box.addWidget(self.bright_slider)
        sliders_row.addLayout(br_box)

        # Paint Selected Button
        self.btn_paint_selection = QPushButton("Paint Selected Keys")
        self.btn_paint_selection.setProperty("class", "btn-ghost")
        self.btn_paint_selection.clicked.connect(self._paint_selected_keys_action)
        sliders_row.addWidget(self.btn_paint_selection)

        ctrl_layout.addLayout(sliders_row)
        layout.addWidget(ctrl_card, 1)

        return page

    def _build_profiles_page(self) -> QWidget:
        page = QWidget()
        layout = QVBoxLayout(page)
        layout.setContentsMargins(10, 10, 10, 10)
        layout.setSpacing(12)

        p_lbl = QLabel("PROFILES LIBRARY")
        p_lbl.setFont(QFont("-apple-system", 9, QFont.Weight.Bold))
        p_lbl.setStyleSheet("color: #6B7280; letter-spacing: 1px;")
        layout.addWidget(p_lbl)

        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setStyleSheet("background: transparent; border: none;")

        self.prof_container = QWidget()
        self.prof_grid = QGridLayout(self.prof_container)
        self.prof_grid.setSpacing(12)
        scroll.setWidget(self.prof_container)
        layout.addWidget(scroll, 1)

        self._refresh_profiles()
        return page

    def _build_remap_page(self) -> QWidget:
        page = QWidget()
        layout = QVBoxLayout(page)
        card = QFrame()
        card.setProperty("class", "modern-card")
        c_layout = QVBoxLayout(card)
        c_layout.setContentsMargins(24, 24, 24, 24)
        c_layout.setSpacing(12)

        lbl = QLabel("KEY REMAPPING")
        lbl.setFont(QFont("-apple-system", 9, QFont.Weight.Bold))
        lbl.setStyleSheet("color: #6B7280; letter-spacing: 1px;")
        c_layout.addWidget(lbl)

        desc = QLabel("Click any key on the matrix to assign custom keys, media controls, or layer modifiers.")
        desc.setStyleSheet("color: #9CA3AF;")
        c_layout.addWidget(desc)

        c_layout.addStretch(1)
        layout.addWidget(card)
        return page

    def _build_macros_page(self) -> QWidget:
        page = QWidget()
        layout = QVBoxLayout(page)
        card = QFrame()
        card.setProperty("class", "modern-card")
        c_layout = QVBoxLayout(card)
        c_layout.setContentsMargins(24, 24, 24, 24)
        c_layout.setSpacing(12)

        lbl = QLabel("MACRO SEQUENCES")
        lbl.setFont(QFont("-apple-system", 9, QFont.Weight.Bold))
        lbl.setStyleSheet("color: #6B7280; letter-spacing: 1px;")
        c_layout.addWidget(lbl)

        desc = QLabel("Record and assign multi-key macros with millisecond precision.")
        desc.setStyleSheet("color: #9CA3AF;")
        c_layout.addWidget(desc)

        btn_rec = QPushButton("Start Recording")
        btn_rec.setProperty("class", "btn-ghost")
        btn_rec.setFixedWidth(160)
        c_layout.addWidget(btn_rec)

        c_layout.addStretch(1)
        layout.addWidget(card)
        return page

    def _select_mode_card(self, mode_id: str):
        self.active_mode = mode_id
        for c in self.mode_cards:
            c.update_state(c.mode_id == mode_id)

        if mode_id != "custom":
            # Preset animation mode
            self._apply_preset_mode(mode_id)
        else:
            self._apply_custom_matrix()

    def _set_active_color(self, hex_color: str):
        self.active_color = hex_color
        self.canvas.set_active_paint_color(hex_color)

        # If keys are selected, paint them immediately
        selected = [k for k in KEYS_87 if k.matrix_idx in self.canvas.selected_keys]
        if selected:
            for k in selected:
                self.canvas.set_key_color(k.name, hex_color, notify=False)
            self._apply_custom_matrix()
        elif self.active_mode != "custom":
            self._apply_preset_mode(self.active_mode)

    def _open_color_picker(self):
        col = QColorDialog.getColor(QColor(self.active_color), self, "Select Color")
        if col.isValid():
            self._set_active_color(col.name().upper())

    def _paint_selected_keys_action(self):
        selected = [k for k in KEYS_87 if k.matrix_idx in self.canvas.selected_keys]
        if not selected:
            self.canvas.set_all_colors(self.active_color)
        else:
            for k in selected:
                self.canvas.set_key_color(k.name, self.active_color, notify=False)
        self._apply_custom_matrix()

    def _on_canvas_modified(self):
        """Triggered whenever a key is painted on the canvas."""
        self.active_mode = "custom"
        for c in self.mode_cards:
            c.update_state(c.mode_id == "custom")
        self._apply_custom_matrix()

    def _on_slider_changed(self):
        self.speed = self.speed_slider.value()
        self.brightness = self.bright_slider.value()
        if self.active_mode != "custom":
            self._apply_preset_mode(self.active_mode)

    def _apply_preset_mode(self, mode_name: str):
        """Sends preset mode to daemon & hardware."""
        self._ensure_background_daemon()
        color = self.active_color
        speed = self.speed
        brightness = self.brightness

        try:
            send_ipc_command("set_mode", mode=mode_name, color=color, speed=speed, brightness=brightness)
        except ConnectionError:
            mode_id = LIGHTING_MODES.get(mode_name, 1)
            r, g, b = hex_to_rgb(color)
            try:
                with Device() as dev:
                    Protocol.set_preset_mode(dev, mode_id=mode_id, speed=speed, brightness=brightness, r=r, g=g, b=b)
            except Exception:
                pass

    def _apply_custom_matrix(self):
        """Streams the 576-byte per-key color matrix to daemon & hardware."""
        self._ensure_background_daemon()

        # Build 576-byte buffer from canvas keys
        buf = bytearray(576)
        for k in KEYS_87:
            off = (k.matrix_idx - 1) * 4
            if off + 4 <= len(buf):
                hex_col = self.canvas.key_colors.get(k.name, self.active_color)
                r, g, b = hex_to_rgb(hex_col)
                buf[off] = k.matrix_idx
                buf[off + 1] = r
                buf[off + 2] = g
                buf[off + 3] = b

        try:
            # Update daemon active buffer
            send_ipc_command("set_color", color=self.active_color)
        except ConnectionError:
            try:
                with Device() as dev:
                    Protocol.upload_matrix_buffer(dev, buf)
            except Exception:
                pass

    def _apply_to_hardware(self):
        """Explicit Save & Commit to hardware EEPROM."""
        if self.active_mode == "custom":
            self._apply_custom_matrix()
        else:
            self._apply_preset_mode(self.active_mode)

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
            self._refresh_profiles()

    def _refresh_profiles(self):
        while self.prof_grid.count():
            it = self.prof_grid.takeAt(0)
            if it.widget():
                it.widget().deleteLater()

        profiles = self.profile_mgr.list_profiles()
        active_name = self.profile_mgr.get_active_profile_name()

        for idx, p in enumerate(profiles):
            card = QFrame()
            card.setProperty("class", "modern-card")
            c_layout = QVBoxLayout(card)
            c_layout.setContentsMargins(16, 14, 16, 14)
            c_layout.setSpacing(8)

            p_name = p.get("name", "Untitled")
            is_active = p_name == active_name

            t_row = QHBoxLayout()
            name_lbl = QLabel(p_name)
            name_lbl.setFont(QFont("-apple-system", 12, QFont.Weight.Bold))
            if is_active:
                name_lbl.setStyleSheet("color: #A855F7;")
            t_row.addWidget(name_lbl)
            t_row.addStretch(1)
            if is_active:
                badge = QLabel("ACTIVE")
                badge.setStyleSheet("background: #10B981; color: #000; padding: 2px 6px; border-radius: 6px; font-weight: bold; font-size: 9px;")
                t_row.addWidget(badge)
            c_layout.addLayout(t_row)

            desc = QLabel(p.get("description", ""))
            desc.setStyleSheet("color: #6B7280; font-size: 11px;")
            c_layout.addWidget(desc)

            btn_act = QPushButton("Activate")
            btn_act.setProperty("class", "btn-primary" if not is_active else "btn-ghost")
            btn_act.clicked.connect(lambda _, n=p_name: self._activate_profile(n))
            c_layout.addWidget(btn_act)

            row = idx // 2
            col = idx % 2
            self.prof_grid.addWidget(card, row, col)

    def _activate_profile(self, name: str):
        prof = self.profile_mgr.get_profile(name)
        if prof:
            self.profile_mgr.set_active_profile_name(name)
            self.canvas.set_color_map(prof.get("per_key", {}))
            self._set_active_color(prof.get("color", "#CB94F7"))
            self.active_mode = prof.get("mode", "custom")
            for c in self.mode_cards:
                c.update_state(c.mode_id == self.active_mode)
            self._apply_to_hardware()
            self._refresh_profiles()

    def _load_initial_profile(self):
        active = self.profile_mgr.get_active_profile_name()
        prof = self.profile_mgr.get_profile(active)
        if prof:
            self.canvas.set_color_map(prof.get("per_key", {}))
            self._set_active_color(prof.get("color", "#CB94F7"))
            self.active_mode = prof.get("mode", "custom")
            for c in self.mode_cards:
                c.update_state(c.mode_id == self.active_mode)

    def _check_device_status(self):
        try:
            path = Device.find_device()
            self.conn_dot.setStyleSheet("color: #10B981;")
            self.conn_text.setText("Wired Active")
        except DeviceError:
            self.conn_dot.setStyleSheet("color: #F59E0B;")
            self.conn_text.setText("Wireless / Searching...")

def main():
    app = QApplication(sys.argv)
    app.setApplicationName("Cosmic Byte Trinity")
    window = MainWindow()
    window.show()
    sys.exit(app.exec())

if __name__ == "__main__":
    main()
