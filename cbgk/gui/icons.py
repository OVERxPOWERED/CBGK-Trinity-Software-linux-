"""
Thin-stroke vector glyphs for the light Cosmic Byte Trinity UI.
"""

from PyQt6.QtGui import QIcon, QPixmap, QPainter, QColor, QPen, QPainterPath
from PyQt6.QtCore import Qt, QRectF, QPointF


def _icon(name: str, size: int = 18, color: str = "#6E6E73") -> QIcon:
    pix = QPixmap(size, size)
    pix.fill(Qt.GlobalColor.transparent)
    p = QPainter(pix)
    p.setRenderHint(QPainter.RenderHint.Antialiasing)
    pen = QPen(QColor(color), 1.4, Qt.PenStyle.SolidLine,
               Qt.PenCapStyle.RoundCap, Qt.PenJoinStyle.RoundJoin)
    p.setPen(pen)

    s = size  # shorthand

    if name == "overview":  # home
        path = QPainterPath()
        path.moveTo(s*0.15, s*0.48)
        path.lineTo(s*0.50, s*0.14)
        path.lineTo(s*0.85, s*0.48)
        p.drawPath(path)
        p.drawRect(QRectF(s*0.25, s*0.48, s*0.50, s*0.40))

    elif name == "keymap":  # 4-grid
        g = 0.04
        w = (s - s*g*3 - s*0.20) / 2
        for r in range(2):
            for c in range(2):
                x = s*0.12 + c*(w + s*g)
                y = s*0.12 + r*(w + s*g)
                p.drawRoundedRect(QRectF(x, y, w, w), 2, 2)

    elif name == "lighting":  # gear/sun
        cx, cy = s*0.5, s*0.5
        p.drawEllipse(QRectF(cx - s*0.18, cy - s*0.18, s*0.36, s*0.36))
        for a in range(0, 360, 45):
            p.save()
            p.translate(cx, cy)
            p.rotate(a)
            p.drawLine(QPointF(0, -s*0.26), QPointF(0, -s*0.40))
            p.restore()

    elif name == "macros":  # play-terminal
        path = QPainterPath()
        path.moveTo(s*0.28, s*0.22)
        path.lineTo(s*0.52, s*0.50)
        path.lineTo(s*0.28, s*0.78)
        p.drawPath(path)
        p.drawLine(QPointF(s*0.55, s*0.78), QPointF(s*0.78, s*0.78))

    elif name == "performance":  # chart / wave
        p.drawLine(QPointF(s*0.12, s*0.70), QPointF(s*0.30, s*0.40))
        p.drawLine(QPointF(s*0.30, s*0.40), QPointF(s*0.50, s*0.60))
        p.drawLine(QPointF(s*0.50, s*0.60), QPointF(s*0.70, s*0.25))
        p.drawLine(QPointF(s*0.70, s*0.25), QPointF(s*0.88, s*0.55))

    elif name == "settings":  # gear
        cx, cy = s*0.5, s*0.5
        p.drawEllipse(QRectF(cx - s*0.16, cy - s*0.16, s*0.32, s*0.32))
        for a in range(0, 360, 60):
            p.save()
            p.translate(cx, cy)
            p.rotate(a)
            p.drawLine(QPointF(0, -s*0.28), QPointF(0, -s*0.42))
            p.restore()

    elif name == "check":
        path = QPainterPath()
        path.moveTo(s*0.25, s*0.52)
        path.lineTo(s*0.42, s*0.70)
        path.lineTo(s*0.75, s*0.30)
        pen2 = QPen(QColor(color), 2.0, Qt.PenStyle.SolidLine,
                     Qt.PenCapStyle.RoundCap, Qt.PenJoinStyle.RoundJoin)
        p.setPen(pen2)
        p.drawPath(path)

    elif name == "plus":
        p.drawLine(QPointF(s*0.5, s*0.20), QPointF(s*0.5, s*0.80))
        p.drawLine(QPointF(s*0.20, s*0.5), QPointF(s*0.80, s*0.5))

    elif name == "dots":
        for cx_off in [0.30, 0.50, 0.70]:
            p.setBrush(QColor(color))
            p.drawEllipse(QPointF(s*cx_off, s*0.5), 2, 2)

    p.end()
    return QIcon(pix)


def create_glyph(name: str, size: int = 18, color: str = "#6E6E73") -> QIcon:
    return _icon(name, size, color)


def create_brand_logo(size: int = 22) -> QPixmap:
    """Simple 'CB' brand mark."""
    pix = QPixmap(size, size)
    pix.fill(Qt.GlobalColor.transparent)
    p = QPainter(pix)
    p.setRenderHint(QPainter.RenderHint.Antialiasing)
    pen = QPen(QColor("#1D1D1F"), 2.0, Qt.PenStyle.SolidLine,
               Qt.PenCapStyle.RoundCap, Qt.PenJoinStyle.MiterJoin)
    p.setPen(pen)
    path = QPainterPath()
    path.moveTo(size*0.20, size*0.50)
    path.lineTo(size*0.20, size*0.18)
    path.lineTo(size*0.50, size*0.18)
    path.moveTo(size*0.80, size*0.50)
    path.lineTo(size*0.80, size*0.82)
    path.lineTo(size*0.50, size*0.82)
    p.drawPath(path)
    p.end()
    return pix
