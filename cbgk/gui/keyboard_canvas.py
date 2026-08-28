"""
Interactive Mechanical Keyboard Canvas — LuminKey monochrome dark style.
"""

from typing import Dict, List, Set, Optional, Tuple
from PyQt6.QtWidgets import QWidget
from PyQt6.QtCore import Qt, QRectF, QPointF, pyqtSignal
from PyQt6.QtGui import (
    QPainter, QColor, QBrush, QPen, QFont, QPainterPath,
    QRadialGradient, QLinearGradient
)

from ..matrix import KEYS_87, KeyInfo, hex_to_rgb

class KeyboardCanvas(QWidget):
    """Interactive Graphical 87-Key Mechanical Keyboard Widget."""

    selectionChanged = pyqtSignal(list)
    keyColorChanged = pyqtSignal(str, str)
    keyboardChanged = pyqtSignal()

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setMinimumSize(800, 270)
        self.setMouseTracking(True)

        # Color mapping: key_name -> hex color
        self.key_colors: Dict[str, str] = {k.name: "#CB94F7" for k in KEYS_87}
        self.active_paint_color = "#CB94F7"

        # Selection state: set of key names (not matrix_idx to avoid mismatches)
        self.selected_key_names: Set[str] = set()
        self.hovered_key: Optional[KeyInfo] = None

        # Drag selection
        self.drag_start: Optional[QPointF] = None
        self.drag_current: Optional[QPointF] = None

        # Suppress hardware dispatch while batch-painting
        self._suppress_notify = False

    def set_active_paint_color(self, color_hex: str):
        self.active_paint_color = color_hex

    def set_key_color(self, key_name: str, color_hex: str, notify=True):
        self.key_colors[key_name] = color_hex
        if notify and not self._suppress_notify:
            self.keyColorChanged.emit(key_name, color_hex)
            self.keyboardChanged.emit()
        self.update()

    def set_all_colors(self, color_hex: str):
        self._suppress_notify = True
        for k in KEYS_87:
            self.key_colors[k.name] = color_hex
        self._suppress_notify = False
        self.keyboardChanged.emit()
        self.update()

    def set_color_map(self, color_map: Dict[str, str]):
        for name, col in color_map.items():
            self.key_colors[name] = col
        self.update()

    def paint_selected(self, color_hex: str):
        """Paints all selected keys with the given color, then notifies once."""
        if not self.selected_key_names:
            self.set_all_colors(color_hex)
            return
        self._suppress_notify = True
        for name in self.selected_key_names:
            self.key_colors[name] = color_hex
        self._suppress_notify = False
        self.keyboardChanged.emit()
        self.update()

    def select_keys_by_category(self, category: str):
        self.selected_key_names.clear()
        if category == "all":
            self.selected_key_names = {k.name for k in KEYS_87}
        elif category == "wasd":
            self.selected_key_names = {k.name for k in KEYS_87 if k.name in ("W", "A", "S", "D")}
        elif category == "arrows":
            self.selected_key_names = {k.name for k in KEYS_87 if k.category == "arrow"}
        elif category == "function":
            self.selected_key_names = {k.name for k in KEYS_87 if k.category == "function"}
        elif category == "nav":
            self.selected_key_names = {k.name for k in KEYS_87 if k.category == "nav"}
        elif category == "mods":
            self.selected_key_names = {k.name for k in KEYS_87 if k.category == "mod"}
        self._emit_selection()
        self.update()

    def clear_selection(self):
        self.selected_key_names.clear()
        self._emit_selection()
        self.update()

    def _emit_selection(self):
        selected = [k for k in KEYS_87 if k.name in self.selected_key_names]
        self.selectionChanged.emit(selected)

    def _calculate_geometry(self) -> Tuple[float, float, float, float]:
        pad_x, pad_y = 16.0, 14.0
        avail_w = self.width() - pad_x * 2
        avail_h = self.height() - pad_y * 2
        unit = min(avail_w / 18.5, avail_h / 6.4)
        off_x = (self.width() - 18.5 * unit) / 2
        off_y = (self.height() - 6.4 * unit) / 2
        return off_x, off_y, unit, unit

    def _key_rect(self, k: KeyInfo, ox: float, oy: float, uw: float, uh: float) -> QRectF:
        gap = 3.0
        return QRectF(
            ox + k.x * uw + gap / 2,
            oy + k.y * uh + gap / 2,
            k.width * uw - gap,
            k.height * uh - gap,
        )

    def paintEvent(self, event):
        p = QPainter(self)
        p.setRenderHint(QPainter.RenderHint.Antialiasing)
        p.setRenderHint(QPainter.RenderHint.TextAntialiasing)

        ox, oy, uw, uh = self._calculate_geometry()

        # Chassis
        case = QRectF(ox - 12, oy - 12, 18.5 * uw + 24, 6.4 * uh + 24)
        cp = QPainterPath()
        cp.addRoundedRect(case, 14, 14)
        p.fillPath(cp, QColor(20, 20, 24))
        p.strokePath(cp, QPen(QColor(255, 255, 255, 15), 1.0))

        font = QFont("Inter", max(7, int(uh * 0.20)), QFont.Weight.DemiBold)
        p.setFont(font)

        for k in KEYS_87:
            r_rect = self._key_rect(k, ox, oy, uw, uh)
            col_hex = self.key_colors.get(k.name, "#CB94F7")
            cr, cg, cb = hex_to_rgb(col_hex)

            selected = k.name in self.selected_key_names
            hovered = self.hovered_key is not None and self.hovered_key.name == k.name

            # Subtle LED underglow
            gr = QRadialGradient(r_rect.center(), r_rect.width() * 0.7)
            gr.setColorAt(0.0, QColor(cr, cg, cb, 50))
            gr.setColorAt(1.0, QColor(cr, cg, cb, 0))
            p.fillRect(r_rect.adjusted(-3, -3, 3, 3), QBrush(gr))

            # Keycap body
            kp = QPainterPath()
            kp.addRoundedRect(r_rect, 5, 5)

            if selected:
                fill = QColor(40, 36, 50)
            elif hovered:
                fill = QColor(34, 34, 40)
            else:
                fill = QColor(28, 28, 34)
            p.fillPath(kp, fill)

            # Border
            if selected:
                bp = QPen(QColor(180, 120, 255), 1.6)
            elif hovered:
                bp = QPen(QColor(255, 255, 255, 80), 1.0)
            else:
                bp = QPen(QColor(255, 255, 255, 20), 0.6)
            p.strokePath(kp, bp)

            # Legend
            p.setPen(QPen(QColor(220, 220, 225)))
            p.drawText(r_rect.adjusted(2, 1, -2, -1), Qt.AlignmentFlag.AlignCenter, k.name)

        # Drag box
        if self.drag_start and self.drag_current:
            dr = QRectF(self.drag_start, self.drag_current).normalized()
            p.fillRect(dr, QColor(180, 140, 255, 25))
            p.setPen(QPen(QColor(180, 140, 255, 140), 1.0, Qt.PenStyle.DashLine))
            p.drawRect(dr)

    def _find_key_at(self, pos: QPointF) -> Optional[KeyInfo]:
        ox, oy, uw, uh = self._calculate_geometry()
        for k in KEYS_87:
            if self._key_rect(k, ox, oy, uw, uh).contains(pos):
                return k
        return None

    def mousePressEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton:
            key = self._find_key_at(event.position())
            if key:
                if event.modifiers() & Qt.KeyboardModifier.ControlModifier:
                    if key.name in self.selected_key_names:
                        self.selected_key_names.remove(key.name)
                    else:
                        self.selected_key_names.add(key.name)
                else:
                    self.selected_key_names = {key.name}
                    # Paint immediately
                    self.set_key_color(key.name, self.active_paint_color)
                self._emit_selection()
                self.update()
            else:
                self.drag_start = event.position()
                self.drag_current = event.position()
                if not (event.modifiers() & Qt.KeyboardModifier.ControlModifier):
                    self.selected_key_names.clear()
                    self._emit_selection()
                self.update()

    def mouseMoveEvent(self, event):
        if self.drag_start:
            self.drag_current = event.position()
            dr = QRectF(self.drag_start, self.drag_current).normalized()
            ox, oy, uw, uh = self._calculate_geometry()
            for k in KEYS_87:
                if dr.intersects(self._key_rect(k, ox, oy, uw, uh)):
                    self.selected_key_names.add(k.name)
            self._emit_selection()
            self.update()
        else:
            prev = self.hovered_key
            self.hovered_key = self._find_key_at(event.position())
            if prev != self.hovered_key:
                self.update()

    def mouseReleaseEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton:
            self.drag_start = None
            self.drag_current = None
            self.update()
