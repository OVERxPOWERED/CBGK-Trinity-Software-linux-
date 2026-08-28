"""
Crisp Monochrome Vector Icons for LuminKey / Apple Minimalist Theme.
"""

from PyQt6.QtGui import QIcon, QPixmap, QPainter, QColor, QPen, QBrush, QPainterPath
from PyQt6.QtCore import Qt, QRectF, QPointF

def create_brand_logo(size=24) -> QPixmap:
    """Clean geometric connected square brand logo matching reference."""
    pix = QPixmap(size, size)
    pix.fill(Qt.GlobalColor.transparent)
    p = QPainter(pix)
    p.setRenderHint(QPainter.RenderHint.Antialiasing)

    p.setPen(QPen(QColor(255, 255, 255), 2.2, Qt.PenStyle.SolidLine, Qt.PenCapStyle.RoundCap, Qt.PenJoinStyle.MiterJoin))
    
    # Outer geometric L-shape hooks
    path = QPainterPath()
    path.moveTo(size * 0.20, size * 0.50)
    path.lineTo(size * 0.20, size * 0.20)
    path.lineTo(size * 0.50, size * 0.20)

    path.moveTo(size * 0.80, size * 0.50)
    path.lineTo(size * 0.80, size * 0.80)
    path.lineTo(size * 0.50, size * 0.80)

    p.drawPath(path)
    p.end()
    return pix

def create_glyph(name: str, size=18, color="#FFFFFF") -> QIcon:
    pix = QPixmap(size, size)
    pix.fill(Qt.GlobalColor.transparent)
    p = QPainter(pix)
    p.setRenderHint(QPainter.RenderHint.Antialiasing)

    pen = QPen(QColor(color), 1.6, Qt.PenStyle.SolidLine, Qt.PenCapStyle.RoundCap, Qt.PenJoinStyle.RoundJoin)
    p.setPen(pen)

    if name == "overview": # Home icon
        path = QPainterPath()
        path.moveTo(size * 0.15, size * 0.45)
        path.lineTo(size * 0.50, size * 0.15)
        path.lineTo(size * 0.85, size * 0.45)
        path.lineTo(size * 0.85, size * 0.85)
        path.lineTo(size * 0.15, size * 0.85)
        path.closeSubpath()
        p.drawPath(path)

    elif name == "keymap": # 4-square grid
        p.drawRoundedRect(QRectF(size*0.12, size*0.12, size*0.32, size*0.32), 2, 2)
        p.drawRoundedRect(QRectF(size*0.56, size*0.12, size*0.32, size*0.32), 2, 2)
        p.drawRoundedRect(QRectF(size*0.12, size*0.56, size*0.32, size*0.32), 2, 2)
        p.drawRoundedRect(QRectF(size*0.56, size*0.56, size*0.32, size*0.32), 2, 2)

    elif name == "lighting": # Sun rays
        p.drawEllipse(QRectF(size*0.28, size*0.28, size*0.44, size*0.44))
        for ang in range(0, 360, 45):
            p.save()
            p.translate(size*0.5, size*0.5)
            p.rotate(ang)
            p.drawLine(QPointF(0, -size*0.32), QPointF(0, -size*0.44))
            p.restore()

    elif name == "macros": # Terminal play command
        path = QPainterPath()
        path.moveTo(size*0.25, size*0.25)
        path.lineTo(size*0.50, size*0.50)
        path.lineTo(size*0.25, size*0.75)
        p.drawPath(path)
        p.drawLine(QPointF(size*0.55, size*0.75), QPointF(size*0.80, size*0.75))

    elif name == "performance": # Sliders / Tuning
        p.drawLine(QPointF(size*0.15, size*0.30), QPointF(size*0.85, size*0.30))
        p.drawLine(QPointF(size*0.15, size*0.70), QPointF(size*0.85, size*0.70))
        p.drawEllipse(QRectF(size*0.30, size*0.20, size*0.20, size*0.20))
        p.drawEllipse(QRectF(size*0.60, size*0.60, size*0.20, size*0.20))

    elif name == "settings": # Cog
        p.drawEllipse(QRectF(size*0.30, size*0.30, size*0.40, size*0.40))
        for ang in range(0, 360, 60):
            p.save()
            p.translate(size*0.5, size*0.5)
            p.rotate(ang)
            p.drawLine(QPointF(0, -size*0.32), QPointF(0, -size*0.44))
            p.restore()

    elif name == "check": # Checkmark
        p.drawEllipse(QRectF(size*0.10, size*0.10, size*0.80, size*0.80))
        path = QPainterPath()
        path.moveTo(size*0.32, size*0.52)
        path.lineTo(size*0.46, size*0.66)
        path.lineTo(size*0.70, size*0.36)
        p.drawPath(path)

    p.end()
    return QIcon(pix)
