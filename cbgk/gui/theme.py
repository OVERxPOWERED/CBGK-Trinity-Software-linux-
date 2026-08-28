"""
Apple / Linear-inspired Minimalist Dark Theme with Electric Violet Accents.
"""

APPLE_DARK_PALETTE = {
    "bg_main": "#0D0D11",
    "bg_sidebar": "#121216",
    "bg_card": "#17171C",
    "bg_card_hover": "#1F1F26",
    "bg_card_selected": "#211A2E",
    "border": "rgba(255, 255, 255, 0.08)",
    "border_hover": "rgba(255, 255, 255, 0.16)",
    "border_active": "#9333EA",
    "accent_purple": "#9333EA",
    "accent_purple_light": "#A855F7",
    "text_primary": "#FFFFFF",
    "text_secondary": "#9CA3AF",
    "text_muted": "#6B7280",
    "success": "#10B981",
}

APPLE_STYLESHEET = f"""
QMainWindow {{
    background-color: {APPLE_DARK_PALETTE['bg_main']};
    color: {APPLE_DARK_PALETTE['text_primary']};
}}

QWidget {{
    font-family: -apple-system, BlinkMacSystemFont, 'Inter', 'SF Pro Display', 'Segoe UI', sans-serif;
    font-size: 13px;
    color: {APPLE_DARK_PALETTE['text_primary']};
}}

/* Sidebar Rail */
QFrame#sidebar_rail {{
    background-color: {APPLE_DARK_PALETTE['bg_sidebar']};
    border-right: 1px solid {APPLE_DARK_PALETTE['border']};
}}

/* Top Breadcrumb Bar */
QFrame#top_bar {{
    background-color: {APPLE_DARK_PALETTE['bg_main']};
    border-bottom: 1px solid {APPLE_DARK_PALETTE['border']};
}}

/* Card Container */
QFrame.modern-card {{
    background-color: {APPLE_DARK_PALETTE['bg_card']};
    border: 1px solid {APPLE_DARK_PALETTE['border']};
    border-radius: 12px;
}}

QFrame.modern-card:hover {{
    border-color: {APPLE_DARK_PALETTE['border_hover']};
    background-color: {APPLE_DARK_PALETTE['bg_card_hover']};
}}

/* Selectable Cards (like Reference UI) */
QFrame.select-card {{
    background-color: {APPLE_DARK_PALETTE['bg_card']};
    border: 1px solid {APPLE_DARK_PALETTE['border']};
    border-radius: 12px;
}}

QFrame.select-card:hover {{
    border-color: {APPLE_DARK_PALETTE['border_hover']};
    background-color: {APPLE_DARK_PALETTE['bg_card_hover']};
}}

QFrame.select-card[selected="true"] {{
    border: 1.5px solid {APPLE_DARK_PALETTE['border_active']};
    background-color: {APPLE_DARK_PALETTE['bg_card_selected']};
}}

/* Sidebar Icon Buttons */
QPushButton.sidebar-btn {{
    background-color: transparent;
    border: none;
    border-radius: 10px;
    padding: 10px;
}}

QPushButton.sidebar-btn:hover {{
    background-color: {APPLE_DARK_PALETTE['bg_card_hover']};
}}

QPushButton.sidebar-btn:checked {{
    background-color: rgba(147, 51, 234, 0.20);
    border: 1px solid rgba(168, 85, 247, 0.40);
}}

/* Primary Apple Action Button (Purple Pill) */
QPushButton.btn-primary {{
    background-color: {APPLE_DARK_PALETTE['accent_purple']};
    color: #FFFFFF;
    border: none;
    border-radius: 8px;
    padding: 8px 18px;
    font-size: 13px;
    font-weight: 600;
}}

QPushButton.btn-primary:hover {{
    background-color: {APPLE_DARK_PALETTE['accent_purple_light']};
}}

QPushButton.btn-primary:pressed {{
    background-color: #7E22CE;
}}

/* Ghost / Secondary Button */
QPushButton.btn-ghost {{
    background-color: transparent;
    color: {APPLE_DARK_PALETTE['text_secondary']};
    border: 1px solid {APPLE_DARK_PALETTE['border']};
    border-radius: 8px;
    padding: 8px 16px;
    font-weight: 500;
}}

QPushButton.btn-ghost:hover {{
    background-color: {APPLE_DARK_PALETTE['bg_card_hover']};
    color: #FFFFFF;
    border-color: {APPLE_DARK_PALETTE['border_hover']};
}}

/* Apple-style Slider */
QSlider::groove:horizontal {{
    height: 4px;
    background: #27272A;
    border-radius: 2px;
}}

QSlider::sub-page:horizontal {{
    background: {APPLE_DARK_PALETTE['accent_purple']};
    border-radius: 2px;
}}

QSlider::handle:horizontal {{
    background: #FFFFFF;
    width: 16px;
    height: 16px;
    margin: -6px 0;
    border-radius: 8px;
}}

QSlider::handle:horizontal:hover {{
    background: #E4E4E7;
}}

/* Minimalist Inputs */
QLineEdit {{
    background-color: #121216;
    border: 1px solid {APPLE_DARK_PALETTE['border']};
    border-radius: 8px;
    padding: 6px 12px;
    color: #FFFFFF;
}}

QLineEdit:focus {{
    border-color: {APPLE_DARK_PALETTE['accent_purple']};
}}

/* Minimalist Combo */
QComboBox {{
    background-color: #121216;
    border: 1px solid {APPLE_DARK_PALETTE['border']};
    border-radius: 8px;
    padding: 6px 12px;
    color: #FFFFFF;
}}

QComboBox::drop-down {{
    border: none;
    padding-right: 8px;
}}

QComboBox QAbstractItemView {{
    background-color: #121216;
    border: 1px solid {APPLE_DARK_PALETTE['border']};
    border-radius: 8px;
    selection-background-color: rgba(147, 51, 234, 0.3);
    color: #FFFFFF;
    padding: 4px;
}}
"""
