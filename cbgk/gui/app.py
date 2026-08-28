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
    QButtonGroup, QSizePolicy, QInputDialog
)
from PyQt6.QtCore import Qt, QTimer, QSize, pyqtSignal
from PyQt6.QtGui import QColor, QIcon, QFont, QPixmap

from .theme import LUMINKEY_STYLESHEET, LUMINKEY_PALETTE
from .icons import create_brand_logo, create_glyph
from .keyboard_canvas import KeyboardCanvas
from .async_worker import AsyncHardwareWorker
from ..matrix import KEYS_87, LIGHTING_MODES, hex_to_rgb, rgb_to_hex
from ..device import Device, DeviceError
from ..profiles import ProfileManager
from ..daemon import send_ipc_command

QUICK_COLORS = [
    ("#CB94F7", "Lavender"),
    ("#FFFFFF", "White"),
    ("#00FFFF", "Cyan"),
    ("#FF007F", "Neon Pink"),
    ("#00FF66", "Emerald"),
    ("#FF3366", "Crimson"),
    ("#FFB800", "Amber"),
]


class MainWindow(QMainWindow):

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

        self.worker = AsyncHardwareWorker()
        self.worker.start()

        self._ensure_daemon()
        self._init_ui()
        self._load_initial_profile()

        self.status_timer = QTimer(self)
        self.status_timer.timeout.connect(self._poll_status)
        self.status_timer.start(4000)

    # ------------------------------------------------------------------
    # Daemon lifecycle
    # ------------------------------------------------------------------
    def _ensure_daemon(self):
        try:
            send_ipc_command("ping")
        except Exception:
            root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
            subprocess.Popen(
                [sys.executable, "-m", "cbgk.daemon"],
                cwd=root,
                env=dict(os.environ, PYTHONPATH=root),
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL,
                stdin=subprocess.DEVNULL,
                start_new_session=True,
            )
            time.sleep(0.3)

    # ------------------------------------------------------------------
    # UI Assembly
    # ------------------------------------------------------------------
    def _init_ui(self):
        central = QWidget(self)
        self.setCentralWidget(central)
        root = QHBoxLayout(central)
        root.setContentsMargins(0, 0, 0, 0)
        root.setSpacing(0)

        # -------- Left Sidebar --------
        sidebar = QFrame()
        sidebar.setObjectName("sidebar")
        sidebar.setFixedWidth(200)
        sl = QVBoxLayout(sidebar)
        sl.setContentsMargins(16, 16, 16, 16)
        sl.setSpacing(12)

        # Traffic lights
        tl = QHBoxLayout()
        tl.setSpacing(8)
        for c in ("#FF5F56", "#FFBD2E", "#27C93F"):
            d = QLabel()
            d.setFixedSize(12, 12)
            d.setStyleSheet(f"background-color: {c}; border-radius: 6px;")
            tl.addWidget(d)
        tl.addStretch(1)
        sl.addLayout(tl)

        sl.addSpacing(4)

        # Brand
        br = QHBoxLayout()
        br.setSpacing(8)
        logo = QLabel()
        logo.setPixmap(create_brand_logo(22))
        br.addWidget(logo)
        bl = QLabel("TRINITY 87K")
        bl.setFont(QFont("Inter", 11, QFont.Weight.Bold))
        bl.setStyleSheet("color: #FFFFFF; letter-spacing: 1px;")
        br.addWidget(bl)
        br.addStretch(1)
        sl.addLayout(br)

        sl.addSpacing(8)

        # Nav pills
        self.nav_group = QButtonGroup(self)
        self.nav_group.setExclusive(True)
        nav = [
            ("overview", "Overview", 0),
            ("lighting", "Lighting", 1),
            ("keymap", "Keymap", 2),
            ("macros", "Macros", 3),
            ("performance", "Performance", 4),
            ("settings", "Settings", 5),
        ]
        for ico, title, idx in nav:
            b = QPushButton(f"  {title}")
            b.setProperty("class", "luminkey-nav")
            b.setIcon(create_glyph(ico, 16))
            b.setIconSize(QSize(16, 16))
            b.setCheckable(True)
            if idx == 0:
                b.setChecked(True)
            b.clicked.connect(lambda _, i=idx: self.pages.setCurrentIndex(i))
            self.nav_group.addButton(b, idx)
            sl.addWidget(b)

        sl.addStretch(1)

        # Device card
        dc = QFrame()
        dc.setStyleSheet(
            "background-color: rgba(255,255,255,0.04);"
            "border: 1px solid rgba(255,255,255,0.07);"
            "border-radius: 12px; padding: 10px;"
        )
        dcl = QVBoxLayout(dc)
        dcl.setContentsMargins(10, 8, 10, 8)
        dcl.setSpacing(4)
        dcl.addWidget(self._lbl("Trinity 87K TKL", 10, bold=True))
        sr = QHBoxLayout()
        sr.setSpacing(6)
        self.status_dot = QLabel("●")
        self.status_dot.setStyleSheet("color: #27C93F; font-size: 10px;")
        self.status_text = QLabel("Connected")
        self.status_text.setStyleSheet("color: #9E9EA7; font-size: 10px;")
        sr.addWidget(self.status_dot)
        sr.addWidget(self.status_text)
        sr.addStretch(1)
        dcl.addLayout(sr)
        dcl.addWidget(self._lbl("FW 1.2.0", 8, color="#5C5C64"))
        sl.addWidget(dc)

        root.addWidget(sidebar)

        # -------- Main Content --------
        main = QWidget()
        ml = QVBoxLayout(main)
        ml.setContentsMargins(28, 18, 28, 18)
        ml.setSpacing(14)

        # Header
        hdr = QHBoxLayout()
        hdr.setSpacing(12)
        gl = QVBoxLayout()
        gl.setSpacing(2)
        self.greet = QLabel("Good evening.")
        self.greet.setFont(QFont("Inter", 18, QFont.Weight.Bold))
        self.greet.setStyleSheet("color: #FFFFFF;")
        self.sub_greet = QLabel("Your Trinity 87K is ready to go.")
        self.sub_greet.setFont(QFont("Inter", 11))
        self.sub_greet.setStyleSheet("color: #8E8E93;")
        gl.addWidget(self.greet)
        gl.addWidget(self.sub_greet)
        hdr.addLayout(gl)
        hdr.addStretch(1)

        self.profile_combo = QComboBox()
        self.profile_combo.setFixedWidth(150)
        self._populate_profiles()
        self.profile_combo.currentIndexChanged.connect(self._on_profile_changed)
        hdr.addWidget(self.profile_combo)

        btn_save = QPushButton("Save")
        btn_save.setProperty("class", "btn-ghost")
        btn_save.clicked.connect(self._save_profile)
        hdr.addWidget(btn_save)

        btn_apply = QPushButton("Apply")
        btn_apply.setProperty("class", "btn-primary")
        btn_apply.clicked.connect(self._apply_to_keyboard)
        hdr.addWidget(btn_apply)

        ml.addLayout(hdr)

        # Pages
        self.pages = QStackedWidget()
        self.pages.addWidget(self._page_overview())
        self.pages.addWidget(self._page_lighting())
        self.pages.addWidget(self._page_keymap())
        self.pages.addWidget(self._page_macros())
        self.pages.addWidget(self._page_performance())
        self.pages.addWidget(self._page_settings())
        ml.addWidget(self.pages, 1)

        root.addWidget(main, 1)

    # ------------------------------------------------------------------
    # Helper
    # ------------------------------------------------------------------
    @staticmethod
    def _lbl(text, size=11, bold=False, color="#FFFFFF"):
        l = QLabel(text)
        w = QFont.Weight.Bold if bold else QFont.Weight.Normal
        l.setFont(QFont("Inter", size, w))
        l.setStyleSheet(f"color: {color};")
        return l

    def _section(self, title):
        l = QLabel(title)
        l.setFont(QFont("Inter", 9, QFont.Weight.Bold))
        l.setStyleSheet("color: #5C5C64; letter-spacing: 1px;")
        return l

    def _card(self):
        f = QFrame()
        f.setProperty("class", "glass-card")
        return f

    # ------------------------------------------------------------------
    # Page 0 — Overview (keyboard showcase + 3 info cards)
    # ------------------------------------------------------------------
    def _page_overview(self):
        page = QWidget()
        lay = QVBoxLayout(page)
        lay.setContentsMargins(0, 0, 0, 0)
        lay.setSpacing(14)

        # Canvas (instantiate here — shared across app)
        self.canvas = KeyboardCanvas()
        self.canvas.set_active_paint_color(self.active_color)
        self.canvas.keyboardChanged.connect(self._on_canvas_changed)

        # Showcase panel
        show = QFrame()
        show.setProperty("class", "glass-panel")
        sl = QVBoxLayout(show)
        sl.setContentsMargins(20, 14, 20, 14)
        sl.setSpacing(6)

        # Top bar inside showcase
        tb = QHBoxLayout()
        tb.setSpacing(8)
        tb.addWidget(self._section("KEYBOARD MATRIX"))
        for cid, cn in [("all", "All"), ("wasd", "WASD"), ("arrows", "Arrows"), ("function", "F-Row"), ("mods", "Mods")]:
            b = QPushButton(cn)
            b.setProperty("class", "btn-ghost")
            b.setFixedHeight(24)
            b.setFont(QFont("Inter", 9))
            b.clicked.connect(lambda _, c=cid: self.canvas.select_keys_by_category(c))
            tb.addWidget(b)
        bc = QPushButton("Clear")
        bc.setProperty("class", "btn-ghost")
        bc.setFixedHeight(24)
        bc.setFont(QFont("Inter", 9))
        bc.clicked.connect(self.canvas.clear_selection)
        tb.addWidget(bc)
        tb.addStretch(1)
        # Color palette chips
        for h, nm in QUICK_COLORS:
            ch = QPushButton()
            ch.setFixedSize(18, 18)
            ch.setToolTip(nm)
            ch.setStyleSheet(
                f"background-color: {h}; border: 1px solid rgba(255,255,255,0.25);"
                f"border-radius: 9px;"
            )
            ch.clicked.connect(lambda _, c=h: self._quick_paint(c))
            tb.addWidget(ch)
        bp = QPushButton("Pick")
        bp.setProperty("class", "btn-ghost")
        bp.setFixedHeight(24)
        bp.setFont(QFont("Inter", 9))
        bp.clicked.connect(self._pick_color)
        tb.addWidget(bp)

        sl.addLayout(tb)
        sl.addWidget(self.canvas, 1)

        # Footer
        ft = QHBoxLayout()
        ft.addWidget(self._lbl("Layout   ANSI 87-Key TKL", 9, color="#5C5C64"))
        ft.addStretch(1)
        ft.addWidget(self._lbl("Polling Rate   1000 Hz", 9, color="#5C5C64"))
        sl.addLayout(ft)

        lay.addWidget(show, 1)

        # Bottom cards row
        cr = QHBoxLayout()
        cr.setSpacing(14)

        # Card 1 — mode + color
        c1 = self._card()
        c1l = QVBoxLayout(c1)
        c1l.setContentsMargins(16, 14, 16, 14)
        c1l.setSpacing(6)
        c1l.addWidget(self._lbl("Lighting Effect", 11, bold=True))
        self.mode_combo = QComboBox()
        self.mode_combo.addItem("Per-Key Custom RGB", "custom")
        for mn in LIGHTING_MODES:
            if mn != "custom":
                self.mode_combo.addItem(mn.replace("_", " ").title(), mn)
        self.mode_combo.currentIndexChanged.connect(self._on_mode_changed)
        c1l.addWidget(self.mode_combo)
        cr.addWidget(c1, 1)

        # Card 2 — brightness / speed
        c2 = self._card()
        c2l = QVBoxLayout(c2)
        c2l.setContentsMargins(16, 14, 16, 14)
        c2l.setSpacing(4)
        c2l.addWidget(self._lbl("Brightness & Speed", 11, bold=True))
        self.bright_lbl = QLabel("Brightness (100%)")
        self.bright_lbl.setStyleSheet("color: #8E8E93; font-size: 10px;")
        self.bright_slider = QSlider(Qt.Orientation.Horizontal)
        self.bright_slider.setRange(0, 4)
        self.bright_slider.setValue(4)
        self.bright_slider.valueChanged.connect(self._on_slider)
        c2l.addWidget(self.bright_lbl)
        c2l.addWidget(self.bright_slider)
        self.speed_lbl = QLabel("Speed (3)")
        self.speed_lbl.setStyleSheet("color: #8E8E93; font-size: 10px;")
        self.speed_slider = QSlider(Qt.Orientation.Horizontal)
        self.speed_slider.setRange(1, 5)
        self.speed_slider.setValue(3)
        self.speed_slider.valueChanged.connect(self._on_slider)
        c2l.addWidget(self.speed_lbl)
        c2l.addWidget(self.speed_slider)
        cr.addWidget(c2, 1)

        # Card 3 — status
        c3 = self._card()
        c3l = QHBoxLayout(c3)
        c3l.setContentsMargins(16, 14, 16, 14)
        ib = QVBoxLayout()
        ib.addWidget(self._lbl("Performance", 11, bold=True))
        ib.addWidget(self._lbl("All systems optimal.", 9, color="#8E8E93"))
        c3l.addLayout(ib, 1)
        ck = QLabel()
        ck.setPixmap(create_glyph("check", 32, "#FFFFFF").pixmap(32, 32))
        c3l.addWidget(ck, alignment=Qt.AlignmentFlag.AlignCenter)
        cr.addWidget(c3, 1)

        lay.addLayout(cr)
        return page

    # ------------------------------------------------------------------
    # Page 1 — Lighting (dedicated effect grid)
    # ------------------------------------------------------------------
    def _page_lighting(self):
        page = QWidget()
        lay = QVBoxLayout(page)
        lay.setContentsMargins(0, 0, 0, 0)
        lay.setSpacing(14)

        panel = QFrame()
        panel.setProperty("class", "glass-panel")
        pl = QVBoxLayout(panel)
        pl.setContentsMargins(24, 20, 24, 20)
        pl.setSpacing(16)

        pl.addWidget(self._section("LIGHTING EFFECTS"))
        pl.addWidget(self._lbl("Choose a lighting preset or create a custom per-key layout.", 11, color="#9E9EA7"))

        grid = QGridLayout()
        grid.setSpacing(12)
        effects = [
            ("Static", "Uniform solid color"),
            ("Breathing", "Pulsating breath"),
            ("Spectrum", "Full rainbow cycle"),
            ("Reactive", "Light on keypress"),
            ("Ripples", "Outward wave from press"),
            ("Glittering", "Random sparkle stars"),
            ("Flowing", "Color stream wave"),
            ("Explode", "Burst from keypress"),
            ("Custom RGB", "Per-key matrix coloring"),
        ]
        for i, (name, desc) in enumerate(effects):
            c = self._card()
            cl = QVBoxLayout(c)
            cl.setContentsMargins(14, 12, 14, 12)
            cl.setSpacing(4)
            cl.addWidget(self._lbl(name, 11, bold=True))
            cl.addWidget(self._lbl(desc, 9, color="#8E8E93"))
            c.setCursor(Qt.CursorShape.PointingHandCursor)
            grid.addWidget(c, i // 3, i % 3)

        pl.addLayout(grid)

        # Color palette strip
        cp = QHBoxLayout()
        cp.setSpacing(8)
        cp.addWidget(self._lbl("Quick Colors:", 10, color="#8E8E93"))
        for h, nm in QUICK_COLORS:
            ch = QPushButton()
            ch.setFixedSize(24, 24)
            ch.setToolTip(nm)
            ch.setStyleSheet(
                f"background-color: {h}; border: 2px solid rgba(255,255,255,0.2);"
                f"border-radius: 12px;"
            )
            ch.clicked.connect(lambda _, c=h: self._quick_paint(c))
            cp.addWidget(ch)
        bp = QPushButton("Custom Color...")
        bp.setProperty("class", "btn-ghost")
        bp.clicked.connect(self._pick_color)
        cp.addWidget(bp)
        cp.addStretch(1)
        pl.addLayout(cp)

        pl.addStretch(1)
        lay.addWidget(panel)
        return page

    # ------------------------------------------------------------------
    # Page 2 — Keymap
    # ------------------------------------------------------------------
    def _page_keymap(self):
        page = QWidget()
        lay = QVBoxLayout(page)
        panel = QFrame()
        panel.setProperty("class", "glass-panel")
        pl = QVBoxLayout(panel)
        pl.setContentsMargins(24, 20, 24, 20)
        pl.setSpacing(16)
        pl.addWidget(self._section("KEY REMAPPING"))
        pl.addWidget(self._lbl(
            "Select a key on the Overview keyboard, then assign a custom action below.",
            11, color="#9E9EA7",
        ))
        grid = QGridLayout()
        grid.setSpacing(12)
        actions = [
            "Media Play/Pause", "Volume Up", "Volume Down", "Mute",
            "Next Track", "Previous Track", "Calculator", "Browser",
            "Swap Ctrl/Caps", "Disable Key", "Layer Toggle", "Macro Trigger",
        ]
        for i, act in enumerate(actions):
            c = self._card()
            cl = QVBoxLayout(c)
            cl.setContentsMargins(14, 12, 14, 12)
            cl.addWidget(self._lbl(act, 10, bold=True))
            c.setCursor(Qt.CursorShape.PointingHandCursor)
            grid.addWidget(c, i // 3, i % 3)
        pl.addLayout(grid)
        pl.addStretch(1)
        lay.addWidget(panel)
        return page

    # ------------------------------------------------------------------
    # Page 3 — Macros
    # ------------------------------------------------------------------
    def _page_macros(self):
        page = QWidget()
        lay = QVBoxLayout(page)
        panel = QFrame()
        panel.setProperty("class", "glass-panel")
        pl = QVBoxLayout(panel)
        pl.setContentsMargins(24, 20, 24, 20)
        pl.setSpacing(16)
        pl.addWidget(self._section("MACRO SEQUENCES"))
        pl.addWidget(self._lbl(
            "Record keystrokes with millisecond precision and assign them to any key.",
            11, color="#9E9EA7",
        ))
        row = QHBoxLayout()
        row.setSpacing(12)
        btn_rec = QPushButton("Start Recording")
        btn_rec.setProperty("class", "btn-primary")
        row.addWidget(btn_rec)
        btn_stop = QPushButton("Stop")
        btn_stop.setProperty("class", "btn-ghost")
        row.addWidget(btn_stop)
        row.addStretch(1)
        pl.addLayout(row)
        pl.addWidget(self._lbl("Saved Macros", 11, bold=True))
        pl.addWidget(self._lbl("No macros recorded yet.", 10, color="#5C5C64"))
        pl.addStretch(1)
        lay.addWidget(panel)
        return page

    # ------------------------------------------------------------------
    # Page 4 — Performance
    # ------------------------------------------------------------------
    def _page_performance(self):
        page = QWidget()
        lay = QVBoxLayout(page)
        panel = QFrame()
        panel.setProperty("class", "glass-panel")
        pl = QVBoxLayout(panel)
        pl.setContentsMargins(24, 20, 24, 20)
        pl.setSpacing(16)
        pl.addWidget(self._section("PERFORMANCE & DIAGNOSTICS"))

        grid = QGridLayout()
        grid.setSpacing(14)

        metrics = [
            ("Polling Rate", "1000 Hz", "USB full-speed HID interrupt endpoint"),
            ("Key Debounce", "5 ms", "Hardware debounce on Sonix MCU"),
            ("N-Key Rollover", "Full NKRO", "All 87 keys simultaneous"),
            ("Matrix Scan Rate", "~16 kHz", "Firmware matrix scan frequency"),
            ("LED Refresh", "1.5 s", "Daemon keep-alive interval"),
            ("CPU Usage", "< 0.01%", "Background daemon resource impact"),
        ]
        for i, (title, value, desc) in enumerate(metrics):
            c = self._card()
            cl = QVBoxLayout(c)
            cl.setContentsMargins(16, 14, 16, 14)
            cl.setSpacing(4)
            cl.addWidget(self._lbl(title, 9, color="#8E8E93"))
            cl.addWidget(self._lbl(value, 16, bold=True))
            cl.addWidget(self._lbl(desc, 9, color="#5C5C64"))
            grid.addWidget(c, i // 3, i % 3)

        pl.addLayout(grid)
        pl.addStretch(1)
        lay.addWidget(panel)
        return page

    # ------------------------------------------------------------------
    # Page 5 — Settings
    # ------------------------------------------------------------------
    def _page_settings(self):
        page = QWidget()
        lay = QVBoxLayout(page)
        panel = QFrame()
        panel.setProperty("class", "glass-panel")
        pl = QVBoxLayout(panel)
        pl.setContentsMargins(24, 20, 24, 20)
        pl.setSpacing(16)
        pl.addWidget(self._section("SETTINGS"))

        # Daemon control
        pl.addWidget(self._lbl("Background Service", 12, bold=True))
        pl.addWidget(self._lbl(
            "The CBGK daemon runs in the background to maintain persistent lighting.\n"
            "It uses < 0.01% CPU and refreshes the LED buffer every 1.5 seconds.",
            10, color="#9E9EA7",
        ))
        dr = QHBoxLayout()
        dr.setSpacing(12)
        self.btn_daemon_start = QPushButton("Start Daemon")
        self.btn_daemon_start.setProperty("class", "btn-primary")
        self.btn_daemon_start.clicked.connect(self._ensure_daemon)
        dr.addWidget(self.btn_daemon_start)
        self.btn_daemon_stop = QPushButton("Stop Daemon")
        self.btn_daemon_stop.setProperty("class", "btn-ghost")
        self.btn_daemon_stop.clicked.connect(self._stop_daemon)
        dr.addWidget(self.btn_daemon_stop)
        dr.addStretch(1)
        pl.addLayout(dr)

        pl.addSpacing(16)

        # About
        pl.addWidget(self._lbl("About", 12, bold=True))
        pl.addWidget(self._lbl(
            "CBGK Trinity Linux Software Suite v1.0.0\n"
            "Cosmic Byte Trinity 87K TKL Gaming Keyboard\n"
            "Sonix MCU (VID 0C45 / PID 8006)\n"
            "Created by OVERxPOWERED",
            10, color="#8E8E93",
        ))

        pl.addStretch(1)
        lay.addWidget(panel)
        return page

    # ------------------------------------------------------------------
    # Actions
    # ------------------------------------------------------------------
    def _quick_paint(self, hex_color: str):
        self.active_color = hex_color
        self.canvas.set_active_paint_color(hex_color)
        self.canvas.paint_selected(hex_color)

    def _pick_color(self):
        col = QColorDialog.getColor(QColor(self.active_color), self, "Select Color")
        if col.isValid():
            self._quick_paint(col.name().upper())

    def _on_canvas_changed(self):
        """Fired when a key is painted. Does NOT auto-dispatch to keyboard."""
        self.active_mode = "custom"

    def _on_mode_changed(self, idx: int):
        self.active_mode = self.mode_combo.currentData()

    def _on_slider(self):
        self.brightness = self.bright_slider.value()
        self.speed = self.speed_slider.value()
        self.bright_lbl.setText(f"Brightness ({int(self.brightness / 4 * 100)}%)")
        self.speed_lbl.setText(f"Speed ({self.speed})")

    def _apply_to_keyboard(self):
        """User-triggered: send current state to keyboard hardware."""
        if self.active_mode == "custom":
            self.worker.submit_color(self.active_color, self.canvas.key_colors)
        else:
            self.worker.submit_mode(self.active_mode, self.active_color,
                                    self.speed, self.brightness)
        self.sub_greet.setText("Applied to keyboard.")
        QTimer.singleShot(2000, lambda: self.sub_greet.setText("Your Trinity 87K is ready to go."))

    def _stop_daemon(self):
        try:
            send_ipc_command("stop")
        except Exception:
            pass

    def _populate_profiles(self):
        self.profile_combo.blockSignals(True)
        self.profile_combo.clear()
        profiles = self.profile_mgr.list_profiles()
        active = self.profile_mgr.get_active_profile_name()
        for i, p in enumerate(profiles):
            name = p.get("name", "Profile")
            self.profile_combo.addItem(f"  {name}", name)
            if name == active:
                self.profile_combo.setCurrentIndex(i)
        self.profile_combo.blockSignals(False)

    def _on_profile_changed(self, idx: int):
        name = self.profile_combo.currentData()
        if name:
            prof = self.profile_mgr.get_profile(name)
            if prof:
                self.profile_mgr.set_active_profile_name(name)
                self.canvas.set_color_map(prof.get("per_key", {}))
                self.active_color = prof.get("color", "#CB94F7")
                self.canvas.set_active_paint_color(self.active_color)
                self.active_mode = prof.get("mode", "custom")
                self._apply_to_keyboard()

    def _save_profile(self):
        name, ok = QInputDialog.getText(self, "Save Profile", "Profile Name:")
        if ok and name.strip():
            data = {
                "name": name.strip(),
                "description": f"Saved {time.strftime('%Y-%m-%d %H:%M')}",
                "mode": self.active_mode,
                "color": self.active_color,
                "speed": self.speed,
                "brightness": self.brightness,
                "per_key": dict(self.canvas.key_colors),
            }
            self.profile_mgr.save_profile(name.strip(), data)
            self._populate_profiles()

    def _load_initial_profile(self):
        active = self.profile_mgr.get_active_profile_name()
        prof = self.profile_mgr.get_profile(active)
        if prof:
            self.canvas.set_color_map(prof.get("per_key", {}))
            self.active_color = prof.get("color", "#CB94F7")
            self.canvas.set_active_paint_color(self.active_color)

    def _poll_status(self):
        try:
            Device.find_device()
            self.status_dot.setStyleSheet("color: #27C93F;")
            self.status_text.setText("Connected")
        except DeviceError:
            self.status_dot.setStyleSheet("color: #FFBD2E;")
            self.status_text.setText("Searching...")


def main():
    app = QApplication(sys.argv)
    app.setApplicationName("Cosmic Byte Trinity")
    w = MainWindow()
    w.show()
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
