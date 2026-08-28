"""
Material 3 Liquid Glass Desktop Control Center for Cosmic Byte Trinity.
"""

import sys
import os
import subprocess
from typing import Dict, List, Optional

from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QGridLayout, QLabel, QPushButton, QComboBox, QSlider, QLineEdit,
    QStackedWidget, QFrame, QColorDialog, QScrollArea, QMessageBox,
    QCheckBox, QButtonGroup
)
from PyQt6.QtCore import Qt, QTimer, QSize
from PyQt6.QtGui import QColor, QIcon, QFont, QPixmap

from .theme import STYLESHEET, M3_PALETTE
from .keyboard_canvas import KeyboardCanvas
from ..matrix import KEYS_87, LIGHTING_MODES, hex_to_rgb, rgb_to_hex
from ..device import Device, DeviceError
from ..protocol import Protocol
from ..profiles import ProfileManager
from ..daemon import send_ipc_command, Daemon

QUICK_COLORS = [
    ("#CB94F7", "Lavender"),
    ("#00FFFF", "Cyan"),
    ("#FF007F", "Neon Pink"),
    ("#00FF66", "Emerald"),
    ("#FF3366", "Crimson"),
    ("#FFB800", "Amber"),
    ("#00D4FF", "Ice Blue"),
    ("#FFFFFF", "White"),
]

class MainWindow(QMainWindow):
    """Main Application Window with Material 3 Liquid Glass Aesthetics."""

    def __init__(self):
        super().__init__()
        self.setWindowTitle("Cosmic Byte Trinity - Control Center")
        self.resize(980, 720)
        self.setMinimumSize(880, 640)
        self.setStyleSheet(STYLESHEET)

        self.profile_mgr = ProfileManager()
        self.active_color = "#CB94F7"
        self.active_mode = "custom"
        self.speed = 3
        self.brightness = 4
        self.direction = 0

        self._init_ui()
        self._load_initial_state()

        # Status check timer
        self.status_timer = QTimer(self)
        self.status_timer.timeout.connect(self._check_device_status)
        self.status_timer.start(2500)

    def _init_ui(self):
        central_widget = QWidget(self)
        self.setCentralWidget(central_widget)
        main_layout = QVBoxLayout(central_widget)
        main_layout.setContentsMargins(20, 16, 20, 16)
        main_layout.setSpacing(14)

        # 1. Header Bar
        header = QHBoxLayout()
        header.setSpacing(12)

        # Title & Subtitle
        title_box = QVBoxLayout()
        title_box.setSpacing(2)
        title_lbl = QLabel("COSMIC BYTE TRINITY")
        title_lbl.setFont(QFont("Inter", 15, QFont.Weight.Bold))
        title_lbl.setStyleSheet(f"color: {M3_PALETTE['primary']}; letter-spacing: 1.5px;")

        sub_lbl = QLabel("Linux Control Center • 87-Key TKL RGB")
        sub_lbl.setFont(QFont("Inter", 10))
        sub_lbl.setStyleSheet(f"color: {M3_PALETTE['text_muted']};")
        title_box.addWidget(title_lbl)
        title_box.addWidget(sub_lbl)
        header.addLayout(title_box)

        header.addStretch(1)

        # Device Connection Status Pill
        self.conn_pill = QFrame()
        self.conn_pill.setObjectName("conn_pill")
        self.conn_pill.setStyleSheet(f"""
            QFrame#conn_pill {{
                background-color: {M3_PALETTE['surface_glass']};
                border: 1px solid {M3_PALETTE['outline']};
                border-radius: 14px;
                padding: 4px 14px;
            }}
        """)
        conn_layout = QHBoxLayout(self.conn_pill)
        conn_layout.setContentsMargins(8, 4, 8, 4)
        conn_layout.setSpacing(8)

        self.conn_dot = QLabel("●")
        self.conn_dot.setStyleSheet("color: #7CE38B; font-size: 14px;")
        self.conn_lbl = QLabel("Checking connection...")
        self.conn_lbl.setFont(QFont("Inter", 11, QFont.Weight.Medium))
        conn_layout.addWidget(self.conn_dot)
        conn_layout.addWidget(self.conn_lbl)
        header.addWidget(self.conn_pill)

        main_layout.addLayout(header)

        # 2. Pill Navigation Bar
        nav_container = QFrame()
        nav_container.setStyleSheet(f"""
            background-color: {M3_PALETTE['surface_glass']};
            border: 1px solid {M3_PALETTE['outline']};
            border-radius: 22px;
            padding: 2px;
        """)
        nav_layout = QHBoxLayout(nav_container)
        nav_layout.setContentsMargins(4, 4, 4, 4)
        nav_layout.setSpacing(6)

        self.nav_group = QButtonGroup(self)
        self.nav_group.setExclusive(True)

        tabs_info = [
            ("🌟 Lighting Studio", 0),
            ("📁 Profiles", 1),
            ("⌨️ Key Remap", 2),
            ("⚡ Macros", 3),
        ]

        for title, idx in tabs_info:
            btn = QPushButton(title)
            btn.setProperty("class", "nav-pill")
            btn.setCheckable(True)
            if idx == 0:
                btn.setChecked(True)
            btn.clicked.connect(lambda _, i=idx: self.pages_stack.setCurrentIndex(i))
            self.nav_group.addButton(btn, idx)
            nav_layout.addWidget(btn)

        nav_layout.addStretch(1)
        main_layout.addWidget(nav_container)

        # 3. Stacked Pages
        self.pages_stack = QStackedWidget()
        self.pages_stack.addWidget(self._build_lighting_page())
        self.pages_stack.addWidget(self._build_profiles_page())
        self.pages_stack.addWidget(self._build_remap_page())
        self.pages_stack.addWidget(self._build_macros_page())
        main_layout.addWidget(self.pages_stack, 1)

        # 4. Bottom Global Action Bar
        bottom_bar = QHBoxLayout()
        bottom_bar.setSpacing(12)

        self.status_msg = QLabel("Ready.")
        self.status_msg.setStyleSheet(f"color: {M3_PALETTE['text_secondary']};")
        bottom_bar.addWidget(self.status_msg, 1)

        self.btn_daemon = QPushButton("Start Background Service")
        self.btn_daemon.setProperty("class", "action-secondary")
        self.btn_daemon.clicked.connect(self._toggle_daemon)
        bottom_bar.addWidget(self.btn_daemon)

        self.btn_apply = QPushButton("Apply to Keyboard (EEPROM)")
        self.btn_apply.setProperty("class", "action-primary")
        self.btn_apply.clicked.connect(self._apply_to_hardware)
        bottom_bar.addWidget(self.btn_apply)

        main_layout.addLayout(bottom_bar)

    def _build_lighting_page(self) -> QWidget:
        page = QWidget()
        layout = QVBoxLayout(page)
        layout.setContentsMargins(0, 4, 0, 0)
        layout.setSpacing(12)

        # Keyboard Canvas Card
        canvas_card = QFrame()
        canvas_card.setProperty("class", "glass-card")
        c_layout = QVBoxLayout(canvas_card)
        c_layout.setContentsMargins(12, 12, 12, 12)
        c_layout.setSpacing(8)

        # Canvas Top Tools
        tools_layout = QHBoxLayout()
        tools_layout.setSpacing(8)
        tools_lbl = QLabel("Interactive 87-Key Matrix:")
        tools_lbl.setFont(QFont("Inter", 11, QFont.Weight.DemiBold))
        tools_layout.addWidget(tools_lbl)

        for cat_name, label in [("all", "All"), ("wasd", "WASD"), ("arrows", "Arrows"), ("function", "F-Keys"), ("mods", "Modifiers")]:
            btn = QPushButton(label)
            btn.setProperty("class", "action-secondary")
            btn.setFixedHeight(28)
            btn.clicked.connect(lambda _, c=cat_name: self.canvas.select_keys_by_category(c))
            tools_layout.addWidget(btn)

        btn_clear = QPushButton("Clear Selection")
        btn_clear.setProperty("class", "action-secondary")
        btn_clear.setFixedHeight(28)
        btn_clear.clicked.connect(lambda: self.canvas.clear_selection())
        tools_layout.addWidget(btn_clear)

        tools_layout.addStretch(1)
        c_layout.addLayout(tools_layout)

        # The interactive canvas
        self.canvas = KeyboardCanvas()
        self.canvas.selectionChanged.connect(self._on_key_selection_changed)
        c_layout.addWidget(self.canvas)
        layout.addWidget(canvas_card, 1)

        # Bottom Controls Grid (Mode Settings + Color Studio)
        bottom_grid = QHBoxLayout()
        bottom_grid.setSpacing(12)

        # Card 1: Mode & Animation
        mode_card = QFrame()
        mode_card.setProperty("class", "glass-card")
        m_layout = QVBoxLayout(mode_card)
        m_layout.setContentsMargins(16, 14, 16, 14)
        m_layout.setSpacing(10)

        m_title = QLabel("Animation Mode")
        m_title.setFont(QFont("Inter", 12, QFont.Weight.Bold))
        m_title.setStyleSheet(f"color: {M3_PALETTE['primary']};")
        m_layout.addWidget(m_title)

        # Mode Combo
        self.mode_combo = QComboBox()
        self.mode_combo.addItem("Per-Key Custom RGB", "custom")
        for mode_name in LIGHTING_MODES:
            if mode_name != "custom":
                self.mode_combo.addItem(mode_name.replace("_", " ").title(), mode_name)
        self.mode_combo.currentIndexChanged.connect(self._on_mode_changed)
        m_layout.addWidget(self.mode_combo)

        # Speed Slider
        speed_box = QHBoxLayout()
        speed_lbl = QLabel("Speed:")
        speed_lbl.setFixedWidth(70)
        self.speed_slider = QSlider(Qt.Orientation.Horizontal)
        self.speed_slider.setRange(1, 5)
        self.speed_slider.setValue(3)
        self.speed_slider.valueChanged.connect(self._on_param_changed)
        speed_box.addWidget(speed_lbl)
        speed_box.addWidget(self.speed_slider)
        m_layout.addLayout(speed_box)

        # Brightness Slider
        bright_box = QHBoxLayout()
        bright_lbl = QLabel("Brightness:")
        bright_lbl.setFixedWidth(70)
        self.bright_slider = QSlider(Qt.Orientation.Horizontal)
        self.bright_slider.setRange(0, 4)
        self.bright_slider.setValue(4)
        self.bright_slider.valueChanged.connect(self._on_param_changed)
        bright_box.addWidget(bright_lbl)
        bright_box.addWidget(self.bright_slider)
        m_layout.addLayout(bright_box)

        bottom_grid.addWidget(mode_card, 1)

        # Card 2: Color Studio
        color_card = QFrame()
        color_card.setProperty("class", "glass-card")
        c_layout2 = QVBoxLayout(color_card)
        c_layout2.setContentsMargins(16, 14, 16, 14)
        c_layout2.setSpacing(10)

        c_title = QLabel("Color Palette")
        c_title.setFont(QFont("Inter", 12, QFont.Weight.Bold))
        c_title.setStyleSheet(f"color: {M3_PALETTE['primary']};")
        c_layout2.addWidget(c_title)

        # Quick Palette Chips
        chips_layout = QHBoxLayout()
        chips_layout.setSpacing(6)
        for hex_code, name in QUICK_COLORS:
            chip = QPushButton()
            chip.setFixedSize(28, 28)
            chip.setToolTip(name)
            chip.setStyleSheet(f"""
                QPushButton {{
                    background-color: {hex_code};
                    border: 2px solid rgba(255,255,255,0.2);
                    border-radius: 14px;
                }}
                QPushButton:hover {{
                    border: 2px solid #FFFFFF;
                }}
            """)
            chip.clicked.connect(lambda _, h=hex_code: self._set_active_color(h))
            chips_layout.addWidget(chip)
        chips_layout.addStretch(1)
        c_layout2.addLayout(chips_layout)

        # Custom Hex & Color Picker Button
        hex_row = QHBoxLayout()
        hex_row.setSpacing(8)

        self.color_preview = QLabel()
        self.color_preview.setFixedSize(32, 32)
        self.color_preview.setStyleSheet(f"background-color: {self.active_color}; border-radius: 8px; border: 1px solid rgba(255,255,255,0.2);")
        hex_row.addWidget(self.color_preview)

        self.hex_input = QLineEdit(self.active_color)
        self.hex_input.setFixedWidth(90)
        self.hex_input.textChanged.connect(self._on_hex_text_changed)
        hex_row.addWidget(self.hex_input)

        btn_picker = QPushButton("Pick Color...")
        btn_picker.setProperty("class", "action-secondary")
        btn_picker.clicked.connect(self._open_color_picker)
        hex_row.addWidget(btn_picker)

        self.btn_paint_selected = QPushButton("Paint Selected Keys")
        self.btn_paint_selected.setProperty("class", "action-primary")
        self.btn_paint_selected.clicked.connect(self._paint_selected_keys)
        hex_row.addWidget(self.btn_paint_selected)

        c_layout2.addLayout(hex_row)
        bottom_grid.addWidget(color_card, 1)

        layout.addLayout(bottom_grid)
        return page

    def _build_profiles_page(self) -> QWidget:
        page = QWidget()
        layout = QVBoxLayout(page)
        layout.setContentsMargins(10, 10, 10, 10)
        layout.setSpacing(14)

        header_box = QHBoxLayout()
        p_lbl = QLabel("Saved Profiles")
        p_lbl.setFont(QFont("Inter", 14, QFont.Weight.Bold))
        header_box.addWidget(p_lbl)
        header_box.addStretch(1)

        btn_new_prof = QPushButton("+ Save Current as New Profile")
        btn_new_prof.setProperty("class", "action-primary")
        btn_new_prof.clicked.connect(self._save_current_profile_dialog)
        header_box.addWidget(btn_new_prof)
        layout.addLayout(header_box)

        # Profiles Grid
        self.profiles_scroll = QScrollArea()
        self.profiles_scroll.setWidgetResizable(True)
        self.profiles_scroll.setStyleSheet("background: transparent; border: none;")

        self.profiles_container = QWidget()
        self.profiles_layout = QGridLayout(self.profiles_container)
        self.profiles_layout.setSpacing(12)
        self.profiles_scroll.setWidget(self.profiles_container)
        layout.addWidget(self.profiles_scroll, 1)

        self._refresh_profiles_grid()
        return page

    def _build_remap_page(self) -> QWidget:
        page = QWidget()
        layout = QVBoxLayout(page)
        card = QFrame()
        card.setProperty("class", "glass-card")
        c_layout = QVBoxLayout(card)
        c_layout.setContentsMargins(24, 24, 24, 24)
        c_layout.setSpacing(12)

        title = QLabel("⌨️ 87-Key Custom Remapping")
        title.setFont(QFont("Inter", 14, QFont.Weight.Bold))
        title.setStyleSheet(f"color: {M3_PALETTE['primary']};")
        c_layout.addWidget(title)

        desc = QLabel(
            "Select any key on the Lighting Studio canvas, then choose a target action below.\n"
            "Remappings are saved into your profile and executed via Linux evdev / uinput hooks."
        )
        desc.setStyleSheet(f"color: {M3_PALETTE['text_secondary']};")
        c_layout.addWidget(desc)

        grid = QGridLayout()
        grid.setSpacing(10)

        grid.addWidget(QLabel("Selected Key:"), 0, 0)
        self.remap_key_lbl = QLabel("None (Select a key on canvas)")
        self.remap_key_lbl.setFont(QFont("Inter", 12, QFont.Weight.Bold))
        grid.addWidget(self.remap_key_lbl, 0, 1)

        grid.addWidget(QLabel("Remap Action:"), 1, 0)
        self.remap_action_combo = QComboBox()
        self.remap_action_combo.addItems([
            "Default (No Remap)",
            "Media: Play / Pause",
            "Media: Volume Up",
            "Media: Volume Down",
            "Media: Mute",
            "Media: Next Track",
            "Media: Previous Track",
            "Special: Calculator",
            "Special: Browser",
            "Modifier: Left Ctrl",
            "Modifier: Caps Lock",
        ])
        grid.addWidget(self.remap_action_combo, 1, 1)

        c_layout.addLayout(grid)
        c_layout.addStretch(1)
        layout.addWidget(card)
        return page

    def _build_macros_page(self) -> QWidget:
        page = QWidget()
        layout = QVBoxLayout(page)
        card = QFrame()
        card.setProperty("class", "glass-card")
        c_layout = QVBoxLayout(card)
        c_layout.setContentsMargins(24, 24, 24, 24)
        c_layout.setSpacing(12)

        title = QLabel("⚡ Macro Sequence Studio")
        title.setFont(QFont("Inter", 14, QFont.Weight.Bold))
        title.setStyleSheet(f"color: {M3_PALETTE['primary']};")
        c_layout.addWidget(title)

        desc = QLabel(
            "Record keystrokes with millisecond delay precision.\n"
            "Assign macros to any key for instant gaming combos."
        )
        desc.setStyleSheet(f"color: {M3_PALETTE['text_secondary']};")
        c_layout.addWidget(desc)

        btn_rec = QPushButton("🔴 Start Recording Macro")
        btn_rec.setProperty("class", "action-secondary")
        btn_rec.setFixedWidth(200)
        c_layout.addWidget(btn_rec)

        c_layout.addStretch(1)
        layout.addWidget(card)
        return page

    def _set_active_color(self, hex_code: str):
        self.active_color = hex_code
        self.hex_input.setText(hex_code)
        self.color_preview.setStyleSheet(f"background-color: {hex_code}; border-radius: 8px; border: 1px solid rgba(255,255,255,0.2);")

    def _on_hex_text_changed(self, text: str):
        if text.startswith("#") and len(text) in [4, 7]:
            self.active_color = text
            self.color_preview.setStyleSheet(f"background-color: {text}; border-radius: 8px; border: 1px solid rgba(255,255,255,0.2);")

    def _open_color_picker(self):
        col = QColorDialog.getColor(QColor(self.active_color), self, "Choose RGB Lighting Color")
        if col.isValid():
            self._set_active_color(col.name().upper())

    def _on_key_selection_changed(self, selected_keys: List[any]):
        if selected_keys:
            names = ", ".join([k.name for k in selected_keys[:5]])
            if len(selected_keys) > 5:
                names += f" (+{len(selected_keys)-5} more)"
            self.status_msg.setText(f"Selected {len(selected_keys)} keys: {names}")
            self.remap_key_lbl.setText(selected_keys[0].name)
        else:
            self.status_msg.setText("Ready.")
            self.remap_key_lbl.setText("None (Select a key on canvas)")

    def _paint_selected_keys(self):
        selected = [k for k in KEYS_87 if k.matrix_idx in self.canvas.selected_keys]
        if not selected:
            # Paint entire keyboard
            self.canvas.set_all_colors(self.active_color)
            self.status_msg.setText(f"Painted entire keyboard with {self.active_color}")
        else:
            for k in selected:
                self.canvas.set_key_color(k.name, self.active_color)
            self.status_msg.setText(f"Painted {len(selected)} keys with {self.active_color}")

    def _on_mode_changed(self, idx: int):
        self.active_mode = self.mode_combo.currentData()
        self.status_msg.setText(f"Selected mode: {self.mode_combo.currentText()}")

    def _on_param_changed(self):
        self.speed = self.speed_slider.value()
        self.brightness = self.bright_slider.value()

    def _apply_to_hardware(self):
        """Sends active configuration to keyboard & background daemon."""
        self.status_msg.setText("Transmitting to keyboard hardware...")
        QApplication.processEvents()

        mode = self.active_mode
        color = self.active_color
        r, g, b = hex_to_rgb(color)

        # 1. Update Daemon via IPC if running
        try:
            if mode == "custom":
                send_ipc_command("set_color", color=color)
            else:
                send_ipc_command("set_mode", mode=mode, color=color, speed=self.speed, brightness=self.brightness)
            self.status_msg.setText(f"[✔] Successfully applied {mode.capitalize()} mode via Daemon!")
            return
        except ConnectionError:
            pass

        # 2. Fallback Direct Hardware transmission
        try:
            with Device() as dev:
                if mode == "custom":
                    Protocol.set_solid_color(dev, r, g, b)
                else:
                    mode_id = LIGHTING_MODES.get(mode, 1)
                    Protocol.set_preset_mode(
                        dev,
                        mode_id=mode_id,
                        speed=self.speed,
                        brightness=self.brightness,
                        r=r,
                        g=g,
                        b=b
                    )
            self.status_msg.setText("[✔] Successfully committed settings to keyboard EEPROM!")
        except DeviceError as e:
            QMessageBox.warning(self, "Device Error", str(e))
            self.status_msg.setText(f"[!] Error: {e}")

    def _toggle_daemon(self):
        try:
            send_ipc_command("ping")
            # Daemon is running, send stop
            send_ipc_command("stop")
            self.btn_daemon.setText("Start Background Service")
            self.status_msg.setText("Background daemon stopped.")
        except ConnectionError:
            # Daemon is stopped, start it
            cmd = [sys.executable, "-m", "cbgk.daemon"]
            subprocess.Popen(
                cmd,
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL,
                stdin=subprocess.DEVNULL,
                start_new_session=True
            )
            self.btn_daemon.setText("Stop Background Service")
            self.status_msg.setText("Background daemon started.")

    def _check_device_status(self):
        """Periodic status update for device and daemon."""
        try:
            resp = send_ipc_command("status")
            data = resp.get("data", {})
            if data.get("connected"):
                self.conn_dot.setStyleSheet("color: #7CE38B;")
                self.conn_lbl.setText("Trinity 87K (Wired)")
            else:
                self.conn_dot.setStyleSheet("color: #FFB800;")
                self.conn_lbl.setText("Daemon Active (Wireless)")
            self.btn_daemon.setText("Stop Background Service")
        except ConnectionError:
            try:
                path = Device.find_device()
                self.conn_dot.setStyleSheet("color: #7CE38B;")
                self.conn_lbl.setText("Trinity 87K (Direct)")
            except DeviceError:
                self.conn_dot.setStyleSheet("color: #F2B8B5;")
                self.conn_lbl.setText("Not Connected")
            self.btn_daemon.setText("Start Background Service")

    def _refresh_profiles_grid(self):
        # Clear existing
        while self.profiles_layout.count():
            item = self.profiles_layout.takeAt(0)
            if item.widget():
                item.widget().deleteLater()

        profiles = self.profile_mgr.list_profiles()
        active_name = self.profile_mgr.get_active_profile_name()

        for idx, p in enumerate(profiles):
            card = QFrame()
            card.setProperty("class", "glass-card")
            c_layout = QVBoxLayout(card)
            c_layout.setContentsMargins(16, 16, 16, 16)
            c_layout.setSpacing(8)

            p_name = p.get("name", "Untitled")
            is_active = p_name == active_name

            t_row = QHBoxLayout()
            name_lbl = QLabel(p_name)
            name_lbl.setFont(QFont("Inter", 13, QFont.Weight.Bold))
            if is_active:
                name_lbl.setStyleSheet(f"color: {M3_PALETTE['primary']};")
            t_row.addWidget(name_lbl)
            t_row.addStretch(1)

            if is_active:
                badge = QLabel("ACTIVE")
                badge.setStyleSheet("background: #7CE38B; color: #000; padding: 2px 8px; border-radius: 8px; font-weight: bold; font-size: 10px;")
                t_row.addWidget(badge)
            c_layout.addLayout(t_row)

            desc_lbl = QLabel(p.get("description", ""))
            desc_lbl.setStyleSheet(f"color: {M3_PALETTE['text_secondary']};")
            c_layout.addWidget(desc_lbl)

            btn_activate = QPushButton("Activate Profile")
            btn_activate.setProperty("class", "action-primary" if not is_active else "action-secondary")
            btn_activate.clicked.connect(lambda _, name=p_name: self._activate_profile(name))
            c_layout.addWidget(btn_activate)

            row = idx // 2
            col = idx % 2
            self.profiles_layout.addWidget(card, row, col)

    def _activate_profile(self, name: str):
        prof = self.profile_mgr.get_profile(name)
        if prof:
            self.profile_mgr.set_active_profile_name(name)
            self.canvas.set_color_map(prof.get("per_key", {}))
            self._set_active_color(prof.get("color", "#CB94F7"))
            self._apply_to_hardware()
            self._refresh_profiles_grid()

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
            self._refresh_profiles_grid()
            self.status_msg.setText(f"Profile '{name.strip()}' saved!")

    def _load_initial_state(self):
        active_name = self.profile_mgr.get_active_profile_name()
        prof = self.profile_mgr.get_profile(active_name)
        if prof:
            self.canvas.set_color_map(prof.get("per_key", {}))
            self._set_active_color(prof.get("color", "#CB94F7"))
        self._check_device_status()

def main():
    app = QApplication(sys.argv)
    app.setApplicationName("CBGK Control Center")
    window = MainWindow()
    window.show()
    sys.exit(app.exec())

if __name__ == "__main__":
    main()
