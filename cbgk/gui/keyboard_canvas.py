"""
Interactive Vector-rendered 87-Key Mechanical Keyboard Canvas with Backlit LED Shaders.
"""

from typing import Dict, List, Set, Optional, Tuple
from PyQt6.QtWidgets import QWidget
from PyQt6.QtCore import Qt, QRectF, QPointF, pyqtSignal
from PyQt6.QtGui import (
    QPainter, QColor, QBrush, QPen, QFont, QPainterPath,
    QRadialGradient, QLinearGradient
)

from ..matrix import KEYS_87, KeyInfo, hex_to_rgb, rgb_to_hex

class KeyboardCanvas(QWidget):
    """Interactive Graphical 87-Key Mechanical Keyboard Widget."""

    selectionChanged = pyqtSignal(list) # Emits list of selected KeyInfo objects
    keyClicked = pyqtSignal(object)      # Emits KeyInfo on click

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setMinimumSize(820, 290)
        self.setMouseTracking(True)

        # Color mapping: Key name -> Hex color string
        self.key_colors: Dict[str, str] = {k.name: "#CB94F7" for k in KEYS_87}

        # Selection state
        self.selected_keys: Set[int] = set() # Set of key matrix indices
        self.hovered_key: Optional[KeyInfo] = None

        # Drag selection box
        self.drag_start: Optional[QPointF] = None
        self.drag_current: Optional[QPointF] = None

    def set_key_color(self, key_name: str, color_hex: str):
        """Sets the LED color for a specific key."""
        self.key_colors[key_name] = color_hex
        self.update()

    def set_all_colors(self, color_hex: str):
        """Sets all keys to a uniform color."""
        for k in KEYS_87:
            self.key_colors[k.name] = color_hex
        self.update()

    def set_color_map(self, color_map: Dict[str, str]):
        """Sets the full color map."""
        self.key_colors.update(color_map)
        self.update()

    def select_keys_by_category(self, category: str):
        """Quick selection helper (e.g. 'all', 'wasd', 'arrows', 'nav', 'function')."""
        self.selected_keys.clear()
        if category == "all":
            self.selected_keys = {k.matrix_idx for k in KEYS_87}
        elif category == "wasd":
            self.selected_keys = {k.matrix_idx for k in KEYS_87 if k.name.lower() in ["w", "a", "s", "d"]}
        elif category == "arrows":
            self.selected_keys = {k.matrix_idx for k in KEYS_87 if k.category == "arrow"}
        elif category == "function":
            self.selected_keys = {k.matrix_idx for k in KEYS_87 if k.category == "function"}
        elif category == "nav":
            self.selected_keys = {k.matrix_idx for k in KEYS_87 if k.category == "nav"}
        elif category == "mods":
            self.selected_keys = {k.matrix_idx for k in KEYS_87 if k.category == "mod"}

        self._emit_selection()
        self.update()

    def clear_selection(self):
        self.selected_keys.clear()
        self._emit_selection()
        self.update()

    def _emit_selection(self):
        selected = [k for k in KEYS_87 if k.matrix_idx in self.selected_keys]
        self.selectionChanged.emit(selected)

    def _calculate_geometry(self) -> Tuple[float, float, float, float]:
        """Calculates scaling factors based on widget dimensions."""
        pad_x = 24.0
        pad_y = 20.0
        avail_w = self.width() - (pad_x * 2)
        avail_h = self.height() - (pad_y * 2)

        # 87-key TKL grid is roughly 18.5 units wide and 6.4 units tall
        unit_w = avail_w / 18.5
        unit_h = avail_h / 6.4
        unit_size = min(unit_w, unit_h)

        offset_x = (self.width() - (18.5 * unit_size)) / 2
        offset_y = (self.height() - (6.4 * unit_size)) / 2

        return offset_x, offset_y, unit_size, unit_size

    def _get_key_rect(self, k: KeyInfo, off_x: float, off_y: float, u_w: float, u_h: float) -> QRectF:
        gap = 4.0
        x = off_x + (k.x * u_w) + (gap / 2)
        y = off_y + (k.y * u_h) + (gap / 2)
        w = (k.width * u_w) - gap
        h = (k.height * u_h) - gap
        return QRectF(x, y, w, h)

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        painter.setRenderHint(QPainter.RenderHint.TextAntialiasing)

        off_x, off_y, u_w, u_h = self._calculate_geometry()

        # 1. Draw Keyboard Outer Case (Liquid Glass Chassis)
        case_rect = QRectF(off_x - 12, off_y - 12, (18.5 * u_w) + 24, (6.4 * u_h) + 24)
        case_path = QPainterPath()
        case_path.addRoundedRect(case_rect, 18, 18)

        # Case Background gradient
        case_grad = QLinearGradient(case_rect.topLeft(), case_rect.bottomLeft())
        case_grad.setColorAt(0.0, QColor(26, 23, 36, 210))
        case_grad.setColorAt(1.0, QColor(14, 12, 20, 240))
        painter.fillPath(case_path, case_grad)

        # Case Specular Edge
        case_pen = QPen(QColor(255, 255, 255, 30), 1.5)
        painter.strokePath(case_path, case_pen)

        # 2. Draw Keys and Backlight LEDs
        font_main = QFont("Inter", int(u_h * 0.22), QFont.Weight.DemiBold)
        painter.setFont(font_main)

        for k in KEYS_87:
            rect = self._get_key_rect(k, off_x, off_y, u_w, u_h)
            color_hex = self.key_colors.get(k.name, "#CB94F7")
            r, g, b = hex_to_rgb(color_hex)
            led_color = QColor(r, g, b)

            is_selected = k.matrix_idx in self.selected_keys
            is_hovered = self.hovered_key and self.hovered_key.matrix_idx == k.matrix_idx

            # A. Draw Under-Key LED Glow Halo
            glow_rect = rect.adjusted(-6, -6, 6, 6)
            glow_grad = QRadialGradient(rect.center(), rect.width() * 0.85)
            glow_grad.setColorAt(0.0, QColor(r, g, b, 140))
            glow_grad.setColorAt(0.5, QColor(r, g, b, 50))
            glow_grad.setColorAt(1.0, QColor(r, g, b, 0))
            painter.fillRect(glow_rect, QBrush(glow_grad))

            # B. Draw Keycap Body
            key_path = QPainterPath()
            key_path.addRoundedRect(rect, 6, 6)

            # Keycap surface fill
            if is_selected:
                key_fill = QColor(60, 48, 85, 240)
            elif is_hovered:
                key_fill = QColor(48, 42, 65, 230)
            else:
                key_fill = QColor(32, 28, 44, 220)

            painter.fillPath(key_path, key_fill)

            # C. Keycap Border / LED Accent
            if is_selected:
                border_pen = QPen(QColor(203, 148, 247, 255), 2.0)
            elif is_hovered:
                border_pen = QPen(QColor(255, 255, 255, 120), 1.5)
            else:
                border_pen = QPen(QColor(r, g, b, 70), 1.0)

            painter.strokePath(key_path, border_pen)

            # D. Keycap Specular Top Highlight
            top_line = QRectF(rect.x() + 4, rect.y() + 1, rect.width() - 8, 1)
            painter.fillRect(top_line, QColor(255, 255, 255, 45))

            # E. Draw Legend Text with Glowing LED Tint
            painter.setPen(QPen(QColor(240, 235, 250, 230)))
            text_rect = rect.adjusted(4, 2, -4, -2)
            painter.drawText(text_rect, Qt.AlignmentFlag.AlignCenter, k.name)

        # 3. Draw Drag Selection Box
        if self.drag_start and self.drag_current:
            drag_rect = QRectF(self.drag_start, self.drag_current).normalized()
            painter.fillRect(drag_rect, QColor(203, 148, 247, 40))
            painter.setPen(QPen(QColor(203, 148, 247, 180), 1.0, Qt.PenStyle.DashLine))
            painter.drawRect(drag_rect)

    def _find_key_at(self, pos: QPointF) -> Optional[KeyInfo]:
        off_x, off_y, u_w, u_h = self._calculate_geometry()
        for k in KEYS_87:
            rect = self._get_key_rect(k, off_x, off_y, u_w, u_h)
            if rect.contains(pos):
                return k
        return None

    def mousePressEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton:
            key = self._find_key_at(event.position())
            if key:
                if event.modifiers() & Qt.KeyboardModifier.ControlModifier:
                    # Toggle single key in multi-selection
                    if key.matrix_idx in self.selected_keys:
                        self.selected_keys.remove(key.matrix_idx)
                    else:
                        self.selected_keys.add(key.matrix_idx)
                else:
                    # Select single key
                    self.selected_keys = {key.matrix_idx}
                self.keyClicked.emit(key)
                self._emit_selection()
                self.update()
            else:
                # Start drag selection
                self.drag_start = event.position()
                self.drag_current = event.position()
                if not (event.modifiers() & Qt.KeyboardModifier.ControlModifier):
                    self.selected_keys.clear()
                    self._emit_selection()
                self.update()

    def mouseMoveEvent(self, event):
        if self.drag_start:
            self.drag_current = event.position()
            drag_rect = QRectF(self.drag_start, self.drag_current).normalized()
            off_x, off_y, u_w, u_h = self._calculate_geometry()
            for k in KEYS_87:
                k_rect = self._get_key_rect(k, off_x, off_y, u_w, u_h)
                if drag_rect.intersects(k_rect):
                    self.selected_keys.add(k.matrix_idx)
            self._emit_selection()
            self.update()
        else:
            prev_hover = self.hovered_key
            self.hovered_key = self._find_key_at(event.position())
            if prev_hover != self.hovered_key:
                self.update()

    def mouseReleaseEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton:
            self.drag_start = None
            self.drag_current = None
            self.update()
