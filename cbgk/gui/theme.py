"""
LuminKey / Apple Monochrome Liquid Glass Theme.
Pure Black & White with Translucent Frosted Glass.
"""

LUMINKEY_PALETTE = {
    "bg_window": "#08080A",
    "bg_sidebar": "rgba(14, 14, 17, 0.85)",
    "bg_card": "rgba(22, 22, 27, 0.70)",
    "bg_card_hover": "rgba(32, 32, 38, 0.80)",
    "bg_card_selected": "rgba(42, 42, 50, 0.90)",
    "border": "rgba(255, 255, 255, 0.08)",
    "border_hover": "rgba(255, 255, 255, 0.18)",
    "border_active": "rgba(255, 255, 255, 0.35)",
    "text_primary": "#FFFFFF",
    "text_secondary": "#9E9EA7",
    "text_muted": "#5C5C64",
    "pill_active": "rgba(255, 255, 255, 0.12)",
    "pill_hover": "rgba(255, 255, 255, 0.06)",
    "traffic_red": "#FF5F56",
    "traffic_yellow": "#FFBD2E",
    "traffic_green": "#27C93F",
}

LUMINKEY_STYLESHEET = f"""
QMainWindow {{
    background-color: {LUMINKEY_PALETTE['bg_window']};
    color: {LUMINKEY_PALETTE['text_primary']};
}}

QWidget {{
    font-family: -apple-system, BlinkMacSystemFont, 'Inter', 'SF Pro Display', 'Roboto', sans-serif;
    font-size: 13px;
    color: {LUMINKEY_PALETTE['text_primary']};
}}

/* Sidebar */
QFrame#sidebar {{
    background-color: {LUMINKEY_PALETTE['bg_sidebar']};
    border-right: 1px solid {LUMINKEY_PALETTE['border']};
}}

/* Frosted Showcase & Parameter Cards */
QFrame.glass-panel {{
    background-color: {LUMINKEY_PALETTE['bg_card']};
    border: 1px solid {LUMINKEY_PALETTE['border']};
    border-radius: 16px;
}}

QFrame.glass-card {{
    background-color: {LUMINKEY_PALETTE['bg_card']};
    border: 1px solid {LUMINKEY_PALETTE['border']};
    border-radius: 14px;
}}

QFrame.glass-card:hover {{
    background-color: {LUMINKEY_PALETTE['bg_card_hover']};
    border-color: {LUMINKEY_PALETTE['border_hover']};
}}

/* LuminKey Nav Pill Buttons */
QPushButton.luminkey-nav {{
    background-color: transparent;
    color: {LUMINKEY_PALETTE['text_secondary']};
    border: none;
    border-radius: 10px;
    padding: 10px 14px;
    font-size: 13px;
    font-weight: 500;
    text-align: left;
}}

QPushButton.luminkey-nav:hover {{
    background-color: {LUMINKEY_PALETTE['pill_hover']};
    color: #FFFFFF;
}}

QPushButton.luminkey-nav:checked {{
    background-color: {LUMINKEY_PALETTE['pill_active']};
    color: #FFFFFF;
    font-weight: 600;
    border: 1px solid rgba(255, 255, 255, 0.14);
}}

/* Action Buttons */
QPushButton.btn-primary {{
    background-color: #FFFFFF;
    color: #000000;
    border: none;
    border-radius: 8px;
    padding: 8px 18px;
    font-size: 13px;
    font-weight: 600;
}}

QPushButton.btn-primary:hover {{
    background-color: #E5E5EA;
}}

QPushButton.btn-ghost {{
    background-color: rgba(255, 255, 255, 0.05);
    color: #FFFFFF;
    border: 1px solid {LUMINKEY_PALETTE['border']};
    border-radius: 8px;
    padding: 7px 14px;
    font-weight: 500;
}}

QPushButton.btn-ghost:hover {{
    background-color: rgba(255, 255, 255, 0.10);
    border-color: {LUMINKEY_PALETTE['border_hover']};
}}

/* Apple-style Slider */
QSlider::groove:horizontal {{
    height: 4px;
    background: rgba(255, 255, 255, 0.12);
    border-radius: 2px;
}}

QSlider::sub-page:horizontal {{
    background: #FFFFFF;
    border-radius: 2px;
}}

QSlider::handle:horizontal {{
    background: #FFFFFF;
    width: 14px;
    height: 14px;
    margin: -5px 0;
    border-radius: 7px;
    border: 1px solid rgba(0, 0, 0, 0.3);
}}

/* Combobox */
QComboBox {{
    background-color: rgba(255, 255, 255, 0.06);
    border: 1px solid {LUMINKEY_PALETTE['border']};
    border-radius: 8px;
    padding: 6px 12px;
    color: #FFFFFF;
}}

QComboBox::drop-down {{
    border: none;
    padding-right: 8px;
}}

QComboBox QAbstractItemView {{
    background-color: #16161B;
    border: 1px solid {LUMINKEY_PALETTE['border']};
    border-radius: 8px;
    selection-background-color: rgba(255, 255, 255, 0.15);
    color: #FFFFFF;
    padding: 4px;
}}

/* Scrollbar */
QScrollBar:vertical {{
    border: none;
    background: transparent;
    width: 6px;
}}

QScrollBar::handle:vertical {{
    background: rgba(255, 255, 255, 0.12);
    border-radius: 3px;
}}
"""
