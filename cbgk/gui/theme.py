"""
Material 3 Design Tokens & Liquid Glassmorphism Styling for CBGK GUI.
Matches Caelestia / Hyprland / Arch Linux Material You aesthetic.
"""

M3_PALETTE = {
    "primary": "#CB94F7",               # Signature Lavender
    "on_primary": "#2B114F",
    "primary_container": "rgba(203, 148, 247, 0.22)",
    "on_primary_container": "#EADBFF",
    "secondary": "#CCC2DC",
    "background": "rgba(16, 14, 22, 0.88)",
    "surface": "rgba(24, 21, 33, 0.75)",
    "surface_glass": "rgba(34, 30, 47, 0.65)",
    "surface_glass_hover": "rgba(50, 44, 69, 0.80)",
    "surface_glass_active": "rgba(65, 57, 90, 0.90)",
    "surface_container_high": "rgba(42, 37, 58, 0.80)",
    "outline": "rgba(255, 255, 255, 0.10)",
    "outline_bright": "rgba(203, 148, 247, 0.45)",
    "specular": "rgba(255, 255, 255, 0.18)",
    "text_primary": "#EDE7F6",
    "text_secondary": "#B3AABF",
    "text_muted": "#7E758C",
    "success": "#7CE38B",
    "error": "#F2B8B5",
}

STYLESHEET = f"""
QMainWindow {{
    background-color: {M3_PALETTE['background']};
    color: {M3_PALETTE['text_primary']};
}}

QWidget {{
    font-family: 'Inter', 'Roboto', 'Segoe UI', sans-serif;
    font-size: 13px;
    color: {M3_PALETTE['text_primary']};
}}

/* Glass Containers / Cards */
QFrame.glass-card {{
    background-color: {M3_PALETTE['surface_glass']};
    border: 1px solid {M3_PALETTE['outline']};
    border-radius: 16px;
}}

QFrame.glass-card-high {{
    background-color: {M3_PALETTE['surface_container_high']};
    border: 1px solid {M3_PALETTE['outline']};
    border-radius: 16px;
}}

/* Pill Navigation Buttons */
QPushButton.nav-pill {{
    background-color: transparent;
    color: {M3_PALETTE['text_secondary']};
    border: none;
    border-radius: 20px;
    padding: 8px 20px;
    font-size: 13px;
    font-weight: 600;
}}

QPushButton.nav-pill:hover {{
    background-color: {M3_PALETTE['surface_glass_hover']};
    color: {M3_PALETTE['text_primary']};
}}

QPushButton.nav-pill:checked {{
    background-color: {M3_PALETTE['primary_container']};
    color: {M3_PALETTE['primary']};
    border: 1px solid {M3_PALETTE['outline_bright']};
}}

/* Action Buttons */
QPushButton.action-primary {{
    background-color: {M3_PALETTE['primary']};
    color: {M3_PALETTE['on_primary']};
    border: none;
    border-radius: 12px;
    padding: 10px 24px;
    font-size: 13px;
    font-weight: 700;
}}

QPushButton.action-primary:hover {{
    background-color: #DAB3FA;
}}

QPushButton.action-primary:pressed {{
    background-color: #B774EB;
}}

QPushButton.action-secondary {{
    background-color: {M3_PALETTE['surface_glass']};
    color: {M3_PALETTE['text_primary']};
    border: 1px solid {M3_PALETTE['outline']};
    border-radius: 12px;
    padding: 10px 20px;
    font-weight: 600;
}}

QPushButton.action-secondary:hover {{
    background-color: {M3_PALETTE['surface_glass_hover']};
    border-color: {M3_PALETTE['outline_bright']};
}}

/* Combo Box */
QComboBox {{
    background-color: {M3_PALETTE['surface_glass']};
    border: 1px solid {M3_PALETTE['outline']};
    border-radius: 10px;
    padding: 8px 14px;
    color: {M3_PALETTE['text_primary']};
    font-weight: 500;
}}

QComboBox:hover {{
    border-color: {M3_PALETTE['outline_bright']};
}}

QComboBox::drop-down {{
    border: none;
    padding-right: 10px;
}}

QComboBox QAbstractItemView {{
    background-color: #1E1B29;
    border: 1px solid {M3_PALETTE['outline']};
    border-radius: 10px;
    selection-background-color: {M3_PALETTE['primary_container']};
    selection-color: {M3_PALETTE['primary']};
    padding: 4px;
}}

/* Sliders */
QSlider::groove:horizontal {{
    height: 8px;
    background: {M3_PALETTE['surface_glass']};
    border-radius: 4px;
    border: 1px solid {M3_PALETTE['outline']};
}}

QSlider::sub-page:horizontal {{
    background: {M3_PALETTE['primary']};
    border-radius: 4px;
}}

QSlider::handle:horizontal {{
    background: #FFFFFF;
    border: 2px solid {M3_PALETTE['primary']};
    width: 18px;
    height: 18px;
    margin: -5px 0;
    border-radius: 9px;
}}

QSlider::handle:horizontal:hover {{
    background: {M3_PALETTE['primary']};
    border-color: #FFFFFF;
}}

/* Line Edit */
QLineEdit {{
    background-color: {M3_PALETTE['surface_glass']};
    border: 1px solid {M3_PALETTE['outline']};
    border-radius: 10px;
    padding: 8px 14px;
    color: {M3_PALETTE['text_primary']};
}}

QLineEdit:focus {{
    border: 1px solid {M3_PALETTE['primary']};
}}

/* ScrollBar */
QScrollBar:vertical {{
    border: none;
    background: transparent;
    width: 8px;
    margin: 0px;
}}

QScrollBar::handle:vertical {{
    background: {M3_PALETTE['surface_glass_hover']};
    min-height: 20px;
    border-radius: 4px;
}}

QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {{
    height: 0px;
}}
"""
