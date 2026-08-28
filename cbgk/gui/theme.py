"""
Clean White / Light Theme — Cosmic Byte Trinity Reference UI.
"""

PALETTE = {
    "bg": "#F5F5F7",
    "sidebar_bg": "#FFFFFF",
    "sidebar_border": "#E8E8ED",
    "card_bg": "#FFFFFF",
    "card_border": "#E8E8ED",
    "card_hover": "#FAFAFC",
    "kbd_bg": "#1A1A1E",
    "text_primary": "#1D1D1F",
    "text_secondary": "#6E6E73",
    "text_muted": "#AEAEB2",
    "accent": "#2D2D2D",
    "nav_active_bg": "#F0F0F5",
    "nav_active_text": "#1D1D1F",
    "green_dot": "#34C759",
    "save_btn_bg": "#1D1D1F",
    "save_btn_text": "#FFFFFF",
    "slider_track": "#E5E5EA",
    "slider_fill": "#1D1D1F",
    "border_radius": "14px",
}

STYLESHEET = f"""
QMainWindow {{
    background-color: {PALETTE['bg']};
    color: {PALETTE['text_primary']};
}}

QWidget {{
    font-family: -apple-system, BlinkMacSystemFont, 'Inter', 'SF Pro Display', 'Segoe UI', sans-serif;
    font-size: 13px;
    color: {PALETTE['text_primary']};
}}

/* Sidebar */
QFrame#sidebar {{
    background-color: {PALETTE['sidebar_bg']};
    border-right: 1px solid {PALETTE['sidebar_border']};
}}

/* Glass Panel (keyboard showcase) */
QFrame.showcase-panel {{
    background-color: {PALETTE['card_bg']};
    border: 1px solid {PALETTE['card_border']};
    border-radius: 16px;
}}

/* Bottom info cards */
QFrame.info-card {{
    background-color: {PALETTE['card_bg']};
    border: 1px solid {PALETTE['card_border']};
    border-radius: 14px;
}}

QFrame.info-card:hover {{
    background-color: {PALETTE['card_hover']};
}}

/* Navigation Buttons */
QPushButton.nav-btn {{
    background-color: transparent;
    color: {PALETTE['text_secondary']};
    border: none;
    border-radius: 10px;
    padding: 10px 14px;
    font-size: 13px;
    font-weight: 500;
    text-align: left;
}}

QPushButton.nav-btn:hover {{
    background-color: #F0F0F5;
    color: {PALETTE['text_primary']};
}}

QPushButton.nav-btn:checked {{
    background-color: {PALETTE['nav_active_bg']};
    color: {PALETTE['nav_active_text']};
    font-weight: 600;
}}

/* Save to Device — dark pill */
QPushButton.btn-save {{
    background-color: {PALETTE['save_btn_bg']};
    color: {PALETTE['save_btn_text']};
    border: none;
    border-radius: 12px;
    padding: 10px 22px;
    font-size: 13px;
    font-weight: 600;
}}

QPushButton.btn-save:hover {{
    background-color: #333333;
}}

/* Ghost / secondary */
QPushButton.btn-ghost {{
    background-color: transparent;
    color: {PALETTE['text_secondary']};
    border: 1px solid {PALETTE['card_border']};
    border-radius: 10px;
    padding: 6px 14px;
    font-weight: 500;
}}

QPushButton.btn-ghost:hover {{
    background-color: #F0F0F5;
    color: {PALETTE['text_primary']};
    border-color: #D1D1D6;
}}

/* Combo */
QComboBox {{
    background-color: {PALETTE['card_bg']};
    border: 1px solid {PALETTE['card_border']};
    border-radius: 10px;
    padding: 6px 12px;
    color: {PALETTE['text_primary']};
    font-weight: 500;
}}

QComboBox::drop-down {{
    border: none;
    padding-right: 8px;
}}

QComboBox QAbstractItemView {{
    background-color: #FFFFFF;
    border: 1px solid {PALETTE['card_border']};
    border-radius: 10px;
    selection-background-color: #F0F0F5;
    color: {PALETTE['text_primary']};
    padding: 4px;
}}

/* Slider */
QSlider::groove:horizontal {{
    height: 4px;
    background: {PALETTE['slider_track']};
    border-radius: 2px;
}}

QSlider::sub-page:horizontal {{
    background: {PALETTE['slider_fill']};
    border-radius: 2px;
}}

QSlider::handle:horizontal {{
    background: {PALETTE['slider_fill']};
    width: 16px;
    height: 16px;
    margin: -6px 0;
    border-radius: 8px;
}}

QSlider::handle:horizontal:hover {{
    background: #444444;
}}

/* Scrollbar */
QScrollBar:vertical {{
    border: none;
    background: transparent;
    width: 6px;
}}

QScrollBar::handle:vertical {{
    background: #D1D1D6;
    border-radius: 3px;
}}
"""
