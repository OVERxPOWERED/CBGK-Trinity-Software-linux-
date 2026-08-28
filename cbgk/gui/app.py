"""
Cosmic Byte Trinity — Clean White Desktop Control Center.
Layout matches the reference screenshot exactly.
"""

import sys, os, time, subprocess
from typing import Dict, List, Optional

from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QGridLayout, QLabel, QPushButton, QComboBox, QSlider,
    QStackedWidget, QFrame, QColorDialog, QScrollArea,
    QButtonGroup, QInputDialog,
)
from PyQt6.QtCore import Qt, QTimer, QSize
from PyQt6.QtGui import QColor, QIcon, QFont, QPixmap

from .theme import STYLESHEET, PALETTE
from .icons import create_brand_logo, create_glyph
from .keyboard_canvas import KeyboardCanvas
from .async_worker import AsyncHardwareWorker
from ..matrix import KEYS_87, LIGHTING_MODES, hex_to_rgb
from ..device import Device, DeviceError
from ..profiles import ProfileManager
from ..daemon import send_ipc_command

COLOR_DOTS = [
    "#FF3B30", "#FF9500", "#FFCC00", "#34C759",
    "#00C7BE", "#007AFF", "#AF52DE", "#CB94F7",
]


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Cosmic Byte Trinity")
        self.resize(1080, 740)
        self.setMinimumSize(960, 660)
        self.setStyleSheet(STYLESHEET)

        self.pmgr = ProfileManager()
        self.color = "#FFFFFF"
        self.mode = "custom"
        self.speed = 3
        self.brightness = 4

        self.worker = AsyncHardwareWorker()
        self.worker.start()
        self._boot_daemon()

        self._build()
        self._load_profile()

        self._tick = QTimer(self)
        self._tick.timeout.connect(self._poll)
        self._tick.start(4000)

    def _boot_daemon(self):
        try: send_ipc_command("ping")
        except Exception:
            root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
            subprocess.Popen(
                [sys.executable, "-m", "cbgk.daemon"], cwd=root,
                env=dict(os.environ, PYTHONPATH=root),
                stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL,
                stdin=subprocess.DEVNULL, start_new_session=True)
            time.sleep(0.3)

    # ----------------------------------------------------------------
    # Helpers
    # ----------------------------------------------------------------
    @staticmethod
    def _lbl(text, sz=13, bold=False, color=None):
        l = QLabel(text)
        w = QFont.Weight.Bold if bold else QFont.Weight.Normal
        l.setFont(QFont("Inter", sz, w))
        if color: l.setStyleSheet(f"color: {color};")
        return l

    def _card(self):
        f = QFrame(); f.setProperty("class", "info-card"); return f

    # ----------------------------------------------------------------
    # Build
    # ----------------------------------------------------------------
    def _build(self):
        cw = QWidget(self); self.setCentralWidget(cw)
        root = QHBoxLayout(cw); root.setContentsMargins(0,0,0,0); root.setSpacing(0)

        # ---- SIDEBAR ----
        sb = QFrame(); sb.setObjectName("sidebar"); sb.setFixedWidth(210)
        sl = QVBoxLayout(sb); sl.setContentsMargins(16,20,16,16); sl.setSpacing(10)

        # Brand
        br = QHBoxLayout(); br.setSpacing(8)
        bl = QLabel("COSMIC BYTE"); bl.setFont(QFont("Inter", 10, QFont.Weight.Bold))
        bl.setStyleSheet("color: #1D1D1F; letter-spacing: 1.5px;")
        sep = QLabel("|"); sep.setStyleSheet("color: #AEAEB2;")
        bt = QLabel("TRINITY"); bt.setFont(QFont("Inter", 10, QFont.Weight.Medium))
        bt.setStyleSheet("color: #6E6E73; letter-spacing: 1px;")
        br.addWidget(bl); br.addWidget(sep); br.addWidget(bt); br.addStretch(1)
        sl.addLayout(br)
        sl.addSpacing(16)

        # Nav
        self.nav_grp = QButtonGroup(self); self.nav_grp.setExclusive(True)
        for ico, title, idx in [
            ("overview","Overview",0), ("keymap","Keymap",1), ("lighting","Lighting",2),
            ("macros","Macros",3), ("performance","Performance",4), ("settings","Settings",5),
        ]:
            b = QPushButton(f"  {title}")
            b.setProperty("class", "nav-btn")
            b.setIcon(create_glyph(ico, 16, "#6E6E73"))
            b.setIconSize(QSize(16,16))
            b.setCheckable(True)
            if idx==0: b.setChecked(True)
            b.clicked.connect(lambda _,i=idx: self.pages.setCurrentIndex(i))
            self.nav_grp.addButton(b, idx)
            sl.addWidget(b)

        sl.addStretch(1)

        # Bottom: theme toggle + version
        btm = QHBoxLayout(); btm.setSpacing(8)
        for ico_n in ["lighting","settings"]:
            ib = QPushButton()
            ib.setFixedSize(36,36)
            ib.setIcon(create_glyph(ico_n, 16, "#AEAEB2"))
            ib.setIconSize(QSize(16,16))
            ib.setStyleSheet("border: 1px solid #E8E8ED; border-radius: 10px; background: #FAFAFC;")
            btm.addWidget(ib)
        btm.addStretch(1)
        sl.addLayout(btm)

        vbox = QFrame()
        vbox.setStyleSheet("background-color: #F0F0F5; border-radius: 12px; padding: 10px;")
        vl = QHBoxLayout(vbox); vl.setContentsMargins(12,8,12,8)
        vi = QVBoxLayout()
        vi.addWidget(self._lbl("v1.2.0", 9, bold=True, color="#1D1D1F"))
        vi.addWidget(self._lbl("Check for updates", 9, color="#6E6E73"))
        vl.addLayout(vi); vl.addStretch(1)
        sl.addWidget(vbox)

        root.addWidget(sb)

        # ---- MAIN CONTENT ----
        main = QWidget()
        ml = QVBoxLayout(main); ml.setContentsMargins(28,20,28,20); ml.setSpacing(14)

        # Header row
        hdr = QHBoxLayout(); hdr.setSpacing(10)
        hl = QVBoxLayout(); hl.setSpacing(2)
        hl.addWidget(self._lbl("Cosmic Byte Trinity", 20, bold=True, color="#1D1D1F"))
        sr = QHBoxLayout(); sr.setSpacing(6)
        self.dot = QLabel("●"); self.dot.setStyleSheet("color: #34C759; font-size: 12px;")
        self.conn_lbl = QLabel("Connected"); self.conn_lbl.setStyleSheet("color: #34C759; font-size: 12px;")
        sr.addWidget(self.dot); sr.addWidget(self.conn_lbl); sr.addStretch(1)
        hl.addLayout(sr)
        hdr.addLayout(hl)
        hdr.addStretch(1)

        # Profile combo
        self.prof_combo = QComboBox(); self.prof_combo.setFixedWidth(140)
        self._fill_profiles()
        self.prof_combo.currentIndexChanged.connect(self._on_profile)
        hdr.addWidget(self.prof_combo)
        b_plus = QPushButton(); b_plus.setFixedSize(34,34)
        b_plus.setIcon(create_glyph("plus", 14, "#6E6E73")); b_plus.setIconSize(QSize(14,14))
        b_plus.setProperty("class", "btn-ghost"); b_plus.clicked.connect(self._save_profile)
        hdr.addWidget(b_plus)
        b_dots = QPushButton(); b_dots.setFixedSize(34,34)
        b_dots.setIcon(create_glyph("dots", 14, "#6E6E73")); b_dots.setIconSize(QSize(14,14))
        b_dots.setProperty("class", "btn-ghost")
        hdr.addWidget(b_dots)

        ml.addLayout(hdr)

        # Stacked pages
        self.pages = QStackedWidget()
        self.pages.addWidget(self._pg_overview())
        self.pages.addWidget(self._pg_stub("Keymap", "Assign custom key actions and swap modifiers."))
        self.pages.addWidget(self._pg_lighting())
        self.pages.addWidget(self._pg_stub("Macros", "Record and assign multi-key macro sequences."))
        self.pages.addWidget(self._pg_performance())
        self.pages.addWidget(self._pg_settings())
        ml.addWidget(self.pages, 1)

        # Bottom-right: Save to Device
        bbar = QHBoxLayout(); bbar.addStretch(1)
        self.btn_save_dev = QPushButton("  Save to Device")
        self.btn_save_dev.setProperty("class", "btn-save")
        self.btn_save_dev.setIcon(create_glyph("check", 16, "#FFFFFF"))
        self.btn_save_dev.setIconSize(QSize(16,16))
        self.btn_save_dev.clicked.connect(self._apply)
        bbar.addWidget(self.btn_save_dev)
        ml.addLayout(bbar)

        root.addWidget(main, 1)

    # ----------------------------------------------------------------
    # Page: Overview
    # ----------------------------------------------------------------
    def _pg_overview(self):
        pg = QWidget()
        lay = QVBoxLayout(pg); lay.setContentsMargins(0,0,0,0); lay.setSpacing(14)

        # Canvas
        self.canvas = KeyboardCanvas()
        self.canvas.set_active_paint_color(self.color)
        self.canvas.keyboardChanged.connect(self._on_canvas)

        # Showcase panel (white card with dark keyboard inside)
        show = QFrame(); show.setProperty("class", "showcase-panel")
        shl = QVBoxLayout(show); shl.setContentsMargins(0,0,0,0); shl.setSpacing(0)
        shl.addWidget(self.canvas, 1)

        # Footer specs row
        ft = QHBoxLayout(); ft.setContentsMargins(20,6,20,10); ft.setSpacing(20)
        ft.addWidget(self._lbl("Layout", 10, color="#AEAEB2"))
        ft.addWidget(self._lbl("ANSI (US)", 10, bold=True, color="#1D1D1F"))
        ft.addStretch(1)
        ft.addWidget(self._lbl("Polling Rate", 10, color="#AEAEB2"))
        ft.addWidget(self._lbl("1000 Hz", 10, bold=True, color="#1D1D1F"))
        shl.addLayout(ft)

        lay.addWidget(show, 1)

        # 3 bottom cards
        cr = QHBoxLayout(); cr.setSpacing(14)

        # Card 1: Lighting
        c1 = self._card()
        c1l = QVBoxLayout(c1); c1l.setContentsMargins(18,16,18,16); c1l.setSpacing(8)
        # Title with icon
        t1 = QHBoxLayout(); t1.setSpacing(6)
        t1.addWidget(QLabel()); t1.itemAt(0).widget().setPixmap(create_glyph("lighting",14,"#6E6E73").pixmap(14,14))
        t1.addWidget(self._lbl("Lighting", 12, bold=True)); t1.addStretch(1)
        c1l.addLayout(t1)

        # Effect row
        er = QHBoxLayout()
        er.addWidget(self._lbl("Effect", 11, color="#6E6E73"))
        er.addStretch(1)
        self.mode_combo = QComboBox(); self.mode_combo.setFixedWidth(120)
        self.mode_combo.addItem("Custom RGB", "custom")
        for mn in LIGHTING_MODES:
            if mn != "custom": self.mode_combo.addItem(mn.replace("_"," ").title(), mn)
        self.mode_combo.currentIndexChanged.connect(self._on_mode)
        er.addWidget(self.mode_combo)
        c1l.addLayout(er)

        # Brightness
        bbr = QHBoxLayout()
        bbr.addWidget(self._lbl("Brightness", 11, color="#6E6E73"))
        bbr.addStretch(1)
        self.bri_lbl = QLabel("100%"); self.bri_lbl.setStyleSheet("color: #1D1D1F; font-weight: 600;")
        bbr.addWidget(self.bri_lbl)
        c1l.addLayout(bbr)
        self.bri_slider = QSlider(Qt.Orientation.Horizontal)
        self.bri_slider.setRange(0,4); self.bri_slider.setValue(4)
        self.bri_slider.valueChanged.connect(self._on_slider)
        c1l.addWidget(self.bri_slider)

        # Color dots
        dots = QHBoxLayout(); dots.setSpacing(8)
        for h in COLOR_DOTS:
            d = QPushButton(); d.setFixedSize(22,22)
            d.setStyleSheet(f"background-color: {h}; border: 2px solid rgba(0,0,0,0.08); border-radius: 11px;")
            d.clicked.connect(lambda _,c=h: self._paint(c))
            dots.addWidget(d)
        # + button
        dp = QPushButton(); dp.setFixedSize(22,22)
        dp.setStyleSheet("background-color: #F0F0F5; border: 1.5px dashed #AEAEB2; border-radius: 11px;")
        dp.clicked.connect(self._pick)
        dots.addWidget(dp)
        dots.addStretch(1)
        c1l.addLayout(dots)
        cr.addWidget(c1, 1)

        # Card 2: Performance
        c2 = self._card()
        c2l = QVBoxLayout(c2); c2l.setContentsMargins(18,16,18,16); c2l.setSpacing(8)
        t2 = QHBoxLayout(); t2.setSpacing(6)
        t2.addWidget(QLabel()); t2.itemAt(0).widget().setPixmap(create_glyph("performance",14,"#6E6E73").pixmap(14,14))
        t2.addWidget(self._lbl("Performance", 12, bold=True)); t2.addStretch(1)
        c2l.addLayout(t2)

        # Speed slider
        sp = QHBoxLayout()
        sp.addWidget(self._lbl("Animation Speed", 11, color="#6E6E73"))
        sp.addStretch(1)
        self.spd_lbl = QLabel("3"); self.spd_lbl.setStyleSheet("color: #1D1D1F; font-weight: 600;")
        sp.addWidget(self.spd_lbl)
        c2l.addLayout(sp)
        self.spd_slider = QSlider(Qt.Orientation.Horizontal)
        self.spd_slider.setRange(1,5); self.spd_slider.setValue(3)
        self.spd_slider.valueChanged.connect(self._on_slider)
        c2l.addWidget(self.spd_slider)

        # Quick select buttons
        qs = QHBoxLayout(); qs.setSpacing(6)
        for cid, cn in [("all","All"),("wasd","WASD"),("arrows","Arrows"),("function","F-Row"),("mods","Mods")]:
            b = QPushButton(cn); b.setProperty("class","btn-ghost")
            b.setFixedHeight(26); b.setFont(QFont("Inter",9))
            b.clicked.connect(lambda _,c=cid: self.canvas.select_keys_by_category(c))
            qs.addWidget(b)
        bcl = QPushButton("Clear"); bcl.setProperty("class","btn-ghost")
        bcl.setFixedHeight(26); bcl.setFont(QFont("Inter",9))
        bcl.clicked.connect(self.canvas.clear_selection)
        qs.addWidget(bcl)
        c2l.addLayout(qs)
        cr.addWidget(c2, 1)

        # Card 3: Device Info
        c3 = self._card()
        c3l = QVBoxLayout(c3); c3l.setContentsMargins(18,16,18,16); c3l.setSpacing(6)
        t3 = QHBoxLayout(); t3.setSpacing(6)
        t3.addWidget(QLabel()); t3.itemAt(0).widget().setPixmap(create_glyph("settings",14,"#6E6E73").pixmap(14,14))
        t3.addWidget(self._lbl("Device Info", 12, bold=True)); t3.addStretch(1)
        c3l.addLayout(t3)

        for lbl, val in [("Firmware Version","1.2.0"),("Hardware Version","1.0"),
                          ("Serial Number","CBT87X24B000123")]:
            r = QHBoxLayout()
            r.addWidget(self._lbl(lbl, 10, color="#6E6E73"))
            r.addStretch(1)
            r.addWidget(self._lbl(val, 10, bold=True, color="#1D1D1F"))
            c3l.addLayout(r)

        c3l.addSpacing(6)
        rst = QPushButton("Reset to Default"); rst.setProperty("class","btn-ghost")
        rst.setFixedHeight(28)
        c3l.addWidget(rst)
        cr.addWidget(c3, 1)

        lay.addLayout(cr)
        return pg

    # ----------------------------------------------------------------
    # Page: Lighting (full)
    # ----------------------------------------------------------------
    def _pg_lighting(self):
        pg = QWidget(); lay = QVBoxLayout(pg); lay.setContentsMargins(0,0,0,0); lay.setSpacing(14)
        panel = QFrame(); panel.setProperty("class","showcase-panel")
        pl = QVBoxLayout(panel); pl.setContentsMargins(24,20,24,20); pl.setSpacing(14)
        pl.addWidget(self._lbl("Lighting Effects", 14, bold=True, color="#1D1D1F"))
        pl.addWidget(self._lbl("Choose a preset or create custom per-key colors.", 11, color="#6E6E73"))

        grid = QGridLayout(); grid.setSpacing(12)
        effects = ["Static","Breathing","Spectrum","Reactive","Ripples","Glittering","Flowing","Explode","Custom RGB"]
        for i, n in enumerate(effects):
            c = self._card(); cl = QVBoxLayout(c); cl.setContentsMargins(14,12,14,12)
            cl.addWidget(self._lbl(n, 11, bold=True, color="#1D1D1F"))
            c.setCursor(Qt.CursorShape.PointingHandCursor)
            grid.addWidget(c, i//3, i%3)
        pl.addLayout(grid)

        # Color strip
        cp = QHBoxLayout(); cp.setSpacing(8)
        cp.addWidget(self._lbl("Quick Colors:", 10, color="#6E6E73"))
        for h in COLOR_DOTS:
            d = QPushButton(); d.setFixedSize(26,26)
            d.setStyleSheet(f"background-color: {h}; border: 2px solid rgba(0,0,0,0.08); border-radius: 13px;")
            d.clicked.connect(lambda _,c=h: self._paint(c))
            cp.addWidget(d)
        bp = QPushButton("Custom..."); bp.setProperty("class","btn-ghost"); bp.clicked.connect(self._pick)
        cp.addWidget(bp); cp.addStretch(1)
        pl.addLayout(cp)
        pl.addStretch(1)
        lay.addWidget(panel)
        return pg

    # ----------------------------------------------------------------
    # Page: Performance
    # ----------------------------------------------------------------
    def _pg_performance(self):
        pg = QWidget(); lay = QVBoxLayout(pg); lay.setContentsMargins(0,0,0,0); lay.setSpacing(14)
        panel = QFrame(); panel.setProperty("class","showcase-panel")
        pl = QVBoxLayout(panel); pl.setContentsMargins(24,20,24,20); pl.setSpacing(14)
        pl.addWidget(self._lbl("Performance & Diagnostics", 14, bold=True, color="#1D1D1F"))
        grid = QGridLayout(); grid.setSpacing(14)
        metrics = [("Polling Rate","1000 Hz"),("Key Debounce","5 ms"),("N-Key Rollover","Full NKRO"),
                   ("Matrix Scan","~16 kHz"),("LED Refresh","1.5 s"),("CPU Usage","< 0.01%")]
        for i,(t,v) in enumerate(metrics):
            c = self._card(); cl = QVBoxLayout(c); cl.setContentsMargins(16,14,16,14); cl.setSpacing(4)
            cl.addWidget(self._lbl(t, 9, color="#AEAEB2"))
            cl.addWidget(self._lbl(v, 18, bold=True, color="#1D1D1F"))
            grid.addWidget(c, i//3, i%3)
        pl.addLayout(grid); pl.addStretch(1)
        lay.addWidget(panel)
        return pg

    # ----------------------------------------------------------------
    # Page: Settings
    # ----------------------------------------------------------------
    def _pg_settings(self):
        pg = QWidget(); lay = QVBoxLayout(pg); lay.setContentsMargins(0,0,0,0); lay.setSpacing(14)
        panel = QFrame(); panel.setProperty("class","showcase-panel")
        pl = QVBoxLayout(panel); pl.setContentsMargins(24,20,24,20); pl.setSpacing(14)
        pl.addWidget(self._lbl("Settings", 14, bold=True, color="#1D1D1F"))
        pl.addWidget(self._lbl("Background Service", 12, bold=True, color="#1D1D1F"))
        pl.addWidget(self._lbl("The daemon maintains persistent lighting (< 0.01% CPU).", 11, color="#6E6E73"))
        dr = QHBoxLayout(); dr.setSpacing(12)
        bs = QPushButton("Start Daemon"); bs.setProperty("class","btn-save"); bs.clicked.connect(self._boot_daemon)
        dr.addWidget(bs)
        bst = QPushButton("Stop Daemon"); bst.setProperty("class","btn-ghost")
        bst.clicked.connect(lambda: (send_ipc_command("stop") if True else None))
        dr.addWidget(bst); dr.addStretch(1)
        pl.addLayout(dr)
        pl.addSpacing(16)
        pl.addWidget(self._lbl("About", 12, bold=True, color="#1D1D1F"))
        pl.addWidget(self._lbl("CBGK Trinity Linux Suite v1.0.0\nSonix MCU (0C45:8006)\nBy OVERxPOWERED", 10, color="#6E6E73"))
        pl.addStretch(1)
        lay.addWidget(panel)
        return pg

    # ----------------------------------------------------------------
    # Stub page
    # ----------------------------------------------------------------
    def _pg_stub(self, title, desc):
        pg = QWidget(); lay = QVBoxLayout(pg)
        panel = QFrame(); panel.setProperty("class","showcase-panel")
        pl = QVBoxLayout(panel); pl.setContentsMargins(24,20,24,20); pl.setSpacing(14)
        pl.addWidget(self._lbl(title, 14, bold=True, color="#1D1D1F"))
        pl.addWidget(self._lbl(desc, 11, color="#6E6E73"))
        pl.addStretch(1)
        lay.addWidget(panel)
        return pg

    # ----------------------------------------------------------------
    # Actions
    # ----------------------------------------------------------------
    def _paint(self, c):
        self.color = c; self.canvas.set_active_paint_color(c)
        self.canvas.paint_selected(c)

    def _pick(self):
        c = QColorDialog.getColor(QColor(self.color), self, "Select Color")
        if c.isValid(): self._paint(c.name().upper())

    def _on_canvas(self): self.mode = "custom"
    def _on_mode(self, _): self.mode = self.mode_combo.currentData()

    def _on_slider(self):
        self.brightness = self.bri_slider.value()
        self.speed = self.spd_slider.value()
        self.bri_lbl.setText(f"{int(self.brightness/4*100)}%")
        self.spd_lbl.setText(str(self.speed))

    def _apply(self):
        if self.mode == "custom":
            self.worker.submit_color(self.color, self.canvas.key_colors)
        else:
            self.worker.submit_mode(self.mode, self.color, self.speed, self.brightness)

    def _fill_profiles(self):
        self.prof_combo.blockSignals(True); self.prof_combo.clear()
        active = self.pmgr.get_active_profile_name()
        for i, p in enumerate(self.pmgr.list_profiles()):
            n = p.get("name","Profile")
            self.prof_combo.addItem(f"  {n}", n)
            if n == active: self.prof_combo.setCurrentIndex(i)
        self.prof_combo.blockSignals(False)

    def _on_profile(self, _):
        n = self.prof_combo.currentData()
        if not n: return
        prof = self.pmgr.get_profile(n)
        if prof:
            self.pmgr.set_active_profile_name(n)
            self.canvas.set_color_map(prof.get("per_key",{}))
            self.color = prof.get("color","#FFFFFF")
            self.canvas.set_active_paint_color(self.color)
            self.mode = prof.get("mode","custom")
            self._apply()

    def _save_profile(self):
        n, ok = QInputDialog.getText(self, "Save Profile", "Name:")
        if ok and n.strip():
            self.pmgr.save_profile(n.strip(), {
                "name":n.strip(), "description":f"Saved {time.strftime('%Y-%m-%d %H:%M')}",
                "mode":self.mode, "color":self.color,
                "speed":self.speed, "brightness":self.brightness,
                "per_key":dict(self.canvas.key_colors),
            })
            self._fill_profiles()

    def _load_profile(self):
        prof = self.pmgr.get_profile(self.pmgr.get_active_profile_name())
        if prof:
            self.canvas.set_color_map(prof.get("per_key",{}))
            self.color = prof.get("color","#FFFFFF")
            self.canvas.set_active_paint_color(self.color)

    def _poll(self):
        try:
            Device.find_device()
            self.dot.setStyleSheet("color: #34C759; font-size: 12px;")
            self.conn_lbl.setText("Connected"); self.conn_lbl.setStyleSheet("color: #34C759; font-size: 12px;")
        except DeviceError:
            self.dot.setStyleSheet("color: #FF9500; font-size: 12px;")
            self.conn_lbl.setText("Searching..."); self.conn_lbl.setStyleSheet("color: #FF9500; font-size: 12px;")


def main():
    app = QApplication(sys.argv)
    app.setApplicationName("Cosmic Byte Trinity")
    w = MainWindow(); w.show()
    sys.exit(app.exec())

if __name__ == "__main__":
    main()
