"""
Crisp Vector SVG Icons for CBGK Apple-style Minimalist Dark Interface.
"""

from PyQt6.QtGui import QIcon, QPixmap, QPainter, QColor, QPen, QBrush, QPainterPath
from PyQt6.QtCore import Qt, QRectF, QPointF

def create_logo_pixmap(size=32) -> QPixmap:
    pix = QPixmap(size, size)
    pix.fill(Qt.GlobalColor.transparent)
    p = QPainter(pix)
    p.setRenderHint(QPainter.RenderHint.Antialiasing)

    # Purple rounded square badge
    path = QPainterPath()
    path.addRoundedRect(QRectF(0, 0, size, size), 8, 8)
    p.fillPath(path, QColor(147, 51, 234))

    # White 4-point sparkle / star icon
    star = QPainterPath()
    mid = size / 2.0
    rad = size * 0.35
    inner = size * 0.12

    # Draw sparkle star
    star.moveTo(mid, mid - rad)
    star.quadTo(mid, mid, mid + rad, mid)
    star.quadTo(mid, mid, mid, mid + rad)
    star.quadTo(mid, mid, mid - rad, mid)
    star.quadTo(mid, mid, mid, mid - rad)

    p.fillPath(star, QColor(255, 255, 255))
    p.end()
    return pix

def create_icon_pixmap(name: str, size=24, color="#A1A1AA", active=False) -> QPixmap:
    """Generates crisp vector glyphs without external image assets."""
    pix = QPixmap(size, size)
    pix.fill(Qt.GlobalColor.transparent)
    p = QPainter(pix)
    p.setRenderHint(QPainter.RenderHint.Antialiasing)

    col = QColor(255, 255, 255) if active else QColor(color)
    pen = QPen(col, 1.8, Qt.PenStyle.SolidLine, Qt.PenCapStyle.RoundCap, Qt.PenJoinStyle.RoundJoin)
    p.setPen(pen)

    if name == "lighting": # Bulb / Sun rays / Palette
        # Central ring
        p.drawEllipse(QRectF(size*0.25, size*0.25, size*0.5, size*0.5))
        # Rays
        p.drawLine(QPointF(size*0.5, size*0.08), QPointF(size*0.5, size*0.18))
        p.drawLine(QPointF(size*0.5, size*0.82), QPointF(size*0.5, size*0.92))
        p.drawLine(QPointF(size*0.08, size*0.5), QPointF(size*0.18, size*0.5))
        p.drawLine(QPointF(size*0.82, size*0.5), QPointF(size*0.92, size*0.5))

    elif name == "keyboard": # Keyboard matrix grid
        rect = QRectF(size*0.12, size*0.22, size*0.76, size*0.56)
        p.drawRoundedRect(rect, 3, 3)
        # Internal key dots/lines
        p.drawLine(QPointF(size*0.25, size*0.38), QPointF(size*0.35, size*0.38))
        p.drawLine(QPointF(size*0.45, size*0.38), QPointF(size*0.55, size*0.38))
        p.drawLine(QPointF(size*0.65, size*0.38), QPointF(size*0.75, size*0.38))
        p.drawLine(QPointF(size*0.30, size*0.55), QPointF(size*0.70, size*0.55))

    elif name == "profiles": # Layer / Folder stack
        p.drawRoundedRect(QRectF(size*0.15, size*0.30, size*0.70, size*0.55), 3, 3)
        p.drawLine(QPointF(size*0.25, size*0.20), QPointF(size*0.75, size*0.20))
        p.drawLine(QPointF(size*0.35, size*0.12), QPointF(size*0.65, size*0.12))

    elif name == "macros": # Lightning bolt
        bolt = QPainterPath()
        bolt.moveTo(size*0.55, size*0.10)
        bolt.lineTo(size*0.25, size*0.52)
        bolt.lineTo(size*0.50, size*0.52)
        bolt.lineTo(size*0.45, size*0.90)
        bolt.lineTo(size*0.75, size*0.48)
        bolt.lineTo(size*0.50, size*0.48)
        bolt.closeSubpath()
        p.drawPath(bolt)

    elif name == "settings": # Gear cog
        p.drawEllipse(QRectF(size*0.30, size*0.30, size*0.40, size*0.40))
        # 6 Cog teeth
        for ang in range(0, 360, 60):
            p.save()
            p.translate(size*0.5, size*0.5)
            p.rotate(ang)
            p.drawLine(QPointF(0, -size*0.35), QPointF(0, -size*0.46))
            p.restore()

    elif name == "info": # Info circle
        p.drawEllipse(QRectF(size*0.15, size*0.15, size*0.70, size*0.70))
        p.drawLine(QPointF(size*0.5, size*0.40), QPointF(size*0.5, size*0.70))
        p.drawPoint(QPointF(size*0.5, size*0.28))

    p.end()
    return pix
