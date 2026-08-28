"""
Interactive Keyboard Canvas — dark chassis rendering for the light-theme UI.
"""

from typing import Dict, Set, Optional, Tuple
from PyQt6.QtWidgets import QWidget
from PyQt6.QtCore import Qt, QRectF, QPointF, pyqtSignal
from PyQt6.QtGui import (
    QPainter, QColor, QBrush, QPen, QFont, QPainterPath,
    QRadialGradient,
)

from ..matrix import KEYS_87, KeyInfo, hex_to_rgb


class KeyboardCanvas(QWidget):
    selectionChanged = pyqtSignal(list)
    keyColorChanged = pyqtSignal(str, str)
    keyboardChanged = pyqtSignal()

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setMinimumSize(780, 260)
        self.setMouseTracking(True)
        self.key_colors: Dict[str, str] = {k.name: "#FFFFFF" for k in KEYS_87}
        self.active_paint_color = "#FFFFFF"
        self.selected_key_names: Set[str] = set()
        self.hovered_key: Optional[KeyInfo] = None
        self.drag_start: Optional[QPointF] = None
        self.drag_current: Optional[QPointF] = None
        self._suppress = False

    def set_active_paint_color(self, c): self.active_paint_color = c
    def set_key_color(self, name, c, notify=True):
        self.key_colors[name] = c
        if notify and not self._suppress:
            self.keyColorChanged.emit(name, c)
            self.keyboardChanged.emit()
        self.update()

    def set_all_colors(self, c):
        self._suppress = True
        for k in KEYS_87: self.key_colors[k.name] = c
        self._suppress = False
        self.keyboardChanged.emit()
        self.update()

    def set_color_map(self, m):
        for n, c in m.items(): self.key_colors[n] = c
        self.update()

    def paint_selected(self, c):
        if not self.selected_key_names:
            self.set_all_colors(c); return
        self._suppress = True
        for n in self.selected_key_names: self.key_colors[n] = c
        self._suppress = False
        self.keyboardChanged.emit()
        self.update()

    def select_keys_by_category(self, cat):
        self.selected_key_names.clear()
        if cat == "all":
            self.selected_key_names = {k.name for k in KEYS_87}
        elif cat == "wasd":
            self.selected_key_names = {k.name for k in KEYS_87 if k.name in ("W","A","S","D")}
        elif cat == "arrows":
            self.selected_key_names = {k.name for k in KEYS_87 if k.category == "arrow"}
        elif cat == "function":
            self.selected_key_names = {k.name for k in KEYS_87 if k.category == "function"}
        elif cat == "mods":
            self.selected_key_names = {k.name for k in KEYS_87 if k.category == "mod"}
        self._emit(); self.update()

    def clear_selection(self):
        self.selected_key_names.clear(); self._emit(); self.update()

    def _emit(self):
        self.selectionChanged.emit([k for k in KEYS_87 if k.name in self.selected_key_names])

    def _geo(self):
        u = min((self.width()-32)/18.5, (self.height()-28)/6.4)
        ox = (self.width()-18.5*u)/2
        oy = (self.height()-6.4*u)/2
        return ox, oy, u, u

    def _kr(self, k, ox, oy, uw, uh):
        g = 2.5
        return QRectF(ox+k.x*uw+g, oy+k.y*uh+g, k.width*uw-2*g, k.height*uh-2*g)

    def paintEvent(self, ev):
        p = QPainter(self)
        p.setRenderHint(QPainter.RenderHint.Antialiasing)
        p.setRenderHint(QPainter.RenderHint.TextAntialiasing)
        ox, oy, uw, uh = self._geo()

        # Dark chassis
        chassis = QRectF(ox-14, oy-14, 18.5*uw+28, 6.4*uh+28)
        cp = QPainterPath()
        cp.addRoundedRect(chassis, 16, 16)
        p.fillPath(cp, QColor(26, 26, 30))

        # Rotary knob (top-right decorative)
        knob_cx = chassis.right() - 30
        knob_cy = chassis.top() + 30
        p.setBrush(QColor(40, 40, 46))
        p.setPen(QPen(QColor(60, 60, 66), 1.5))
        p.drawEllipse(QPointF(knob_cx, knob_cy), 16, 16)
        p.setPen(QPen(QColor(80, 80, 88), 1.0))
        p.drawEllipse(QPointF(knob_cx, knob_cy), 10, 10)

        fnt = QFont("Inter", max(7, int(uh*0.19)), QFont.Weight.DemiBold)
        p.setFont(fnt)

        for k in KEYS_87:
            r = self._kr(k, ox, oy, uw, uh)
            ch = self.key_colors.get(k.name, "#FFFFFF")
            cr, cg, cb = hex_to_rgb(ch)
            sel = k.name in self.selected_key_names
            hov = self.hovered_key and self.hovered_key.name == k.name

            # Subtle LED glow under key
            gr = QRadialGradient(r.center(), r.width()*0.6)
            gr.setColorAt(0, QColor(cr, cg, cb, 35))
            gr.setColorAt(1, QColor(cr, cg, cb, 0))
            p.fillRect(r.adjusted(-2,-2,2,2), QBrush(gr))

            # Keycap
            kp = QPainterPath()
            kp.addRoundedRect(r, 4, 4)
            if sel:
                p.fillPath(kp, QColor(55, 50, 68))
            elif hov:
                p.fillPath(kp, QColor(44, 44, 52))
            else:
                p.fillPath(kp, QColor(36, 36, 42))

            # Top highlight bevel
            hi = QRectF(r.x()+1, r.y()+1, r.width()-2, r.height()*0.45)
            hip = QPainterPath()
            hip.addRoundedRect(hi, 3, 3)
            p.fillPath(hip, QColor(255, 255, 255, 8))

            # Border
            if sel:
                p.strokePath(kp, QPen(QColor(120, 90, 220), 1.6))
            elif hov:
                p.strokePath(kp, QPen(QColor(255,255,255,50), 0.8))
            else:
                p.strokePath(kp, QPen(QColor(255,255,255,14), 0.5))

            # Legend
            p.setPen(QColor(210, 210, 215))
            p.drawText(r.adjusted(2,1,-2,-1), Qt.AlignmentFlag.AlignCenter, k.name)

        # Drag box
        if self.drag_start and self.drag_current:
            dr = QRectF(self.drag_start, self.drag_current).normalized()
            p.fillRect(dr, QColor(120, 90, 220, 25))
            p.setPen(QPen(QColor(120, 90, 220, 120), 1, Qt.PenStyle.DashLine))
            p.drawRect(dr)

    def _find(self, pos):
        ox, oy, uw, uh = self._geo()
        for k in KEYS_87:
            if self._kr(k, ox, oy, uw, uh).contains(pos): return k
        return None

    def mousePressEvent(self, ev):
        if ev.button() == Qt.MouseButton.LeftButton:
            k = self._find(ev.position())
            if k:
                if ev.modifiers() & Qt.KeyboardModifier.ControlModifier:
                    self.selected_key_names ^= {k.name}
                else:
                    self.selected_key_names = {k.name}
                    self.set_key_color(k.name, self.active_paint_color)
                self._emit(); self.update()
            else:
                self.drag_start = ev.position()
                self.drag_current = ev.position()
                if not (ev.modifiers() & Qt.KeyboardModifier.ControlModifier):
                    self.selected_key_names.clear(); self._emit()
                self.update()

    def mouseMoveEvent(self, ev):
        if self.drag_start:
            self.drag_current = ev.position()
            dr = QRectF(self.drag_start, self.drag_current).normalized()
            ox, oy, uw, uh = self._geo()
            for k in KEYS_87:
                if dr.intersects(self._kr(k, ox, oy, uw, uh)):
                    self.selected_key_names.add(k.name)
            self._emit(); self.update()
        else:
            prev = self.hovered_key
            self.hovered_key = self._find(ev.position())
            if prev != self.hovered_key: self.update()

    def mouseReleaseEvent(self, ev):
        if ev.button() == Qt.MouseButton.LeftButton:
            self.drag_start = None; self.drag_current = None; self.update()
