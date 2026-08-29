"""
Keyboard physical layout geometry, HID scancodes, and Sonix LED matrix mapping.
"""

from typing import Dict, List, Tuple, Optional
from dataclasses import dataclass

@dataclass
class KeyInfo:
    code: int           # USB HID Keycode (0x04 = A, etc.)
    name: str           # Display name (e.g. "Esc", "Enter")
    matrix_idx: int     # Onboard LED matrix index (1 to 126)
    x: float            # Unit grid X position (0.0 to 18.0)
    y: float            # Unit grid Y position (0.0 to 5.0)
    width: float        # Unit width (1.0 = standard 1u key, 2.25 = Enter, etc.)
    height: float = 1.0 # Unit height
    category: str = "alpha" # alpha, function, nav, arrow, mod, special

# Complete 87-Key TKL Layout Definitions (ANSI Standard)
KEYS_87: List[KeyInfo] = [
    # Row 0: Function Row
    KeyInfo(0x29, "Esc",   1,   0.00, 0.0, 1.00, category="function"),
    KeyInfo(0x3A, "F1",    2,   2.00, 0.0, 1.00, category="function"),
    KeyInfo(0x3B, "F2",    3,   3.00, 0.0, 1.00, category="function"),
    KeyInfo(0x3C, "F3",    4,   4.00, 0.0, 1.00, category="function"),
    KeyInfo(0x3D, "F4",    5,   5.00, 0.0, 1.00, category="function"),
    KeyInfo(0x3E, "F5",    6,   6.50, 0.0, 1.00, category="function"),
    KeyInfo(0x3F, "F6",    7,   7.50, 0.0, 1.00, category="function"),
    KeyInfo(0x40, "F7",    8,   8.50, 0.0, 1.00, category="function"),
    KeyInfo(0x41, "F8",    9,   9.50, 0.0, 1.00, category="function"),
    KeyInfo(0x42, "F9",    10, 11.00, 0.0, 1.00, category="function"),
    KeyInfo(0x43, "F10",   11, 12.00, 0.0, 1.00, category="function"),
    KeyInfo(0x44, "F11",   12, 13.00, 0.0, 1.00, category="function"),
    KeyInfo(0x45, "F12",   13, 14.00, 0.0, 1.00, category="function"),
    KeyInfo(0x46, "PrtSc", 112, 15.25, 0.0, 1.00, category="nav"),
    KeyInfo(0x47, "ScrLk", 113, 16.25, 0.0, 1.00, category="nav"),
    KeyInfo(0x48, "Pause", 115, 17.25, 0.0, 1.00, category="nav"),

    # Row 1: Number Row
    KeyInfo(0x35, "` ~",   19,  0.00, 1.2, 1.00, category="alpha"),
    KeyInfo(0x1E, "1 !",   20,  1.00, 1.2, 1.00, category="alpha"),
    KeyInfo(0x1F, "2 @",   21,  2.00, 1.2, 1.00, category="alpha"),
    KeyInfo(0x20, "3 #",   22,  3.00, 1.2, 1.00, category="alpha"),
    KeyInfo(0x21, "4 $",   23,  4.00, 1.2, 1.00, category="alpha"),
    KeyInfo(0x22, "5 %",   24,  5.00, 1.2, 1.00, category="alpha"),
    KeyInfo(0x23, "6 ^",   25,  6.00, 1.2, 1.00, category="alpha"),
    KeyInfo(0x24, "7 &",   26,  7.00, 1.2, 1.00, category="alpha"),
    KeyInfo(0x25, "8 *",   27,  8.00, 1.2, 1.00, category="alpha"),
    KeyInfo(0x26, "9 (",   28,  9.00, 1.2, 1.00, category="alpha"),
    KeyInfo(0x27, "0 )",   29, 10.00, 1.2, 1.00, category="alpha"),
    KeyInfo(0x2D, "- _",   30, 11.00, 1.2, 1.00, category="alpha"),
    KeyInfo(0x2E, "= +",   31, 12.00, 1.2, 1.00, category="alpha"),
    KeyInfo(0x2A, "Backspace", 32, 13.00, 1.2, 2.00, category="mod"),
    KeyInfo(0x49, "Ins",   116, 15.25, 1.2, 1.00, category="nav"),
    KeyInfo(0x4A, "Home",  117, 16.25, 1.2, 1.00, category="nav"),
    KeyInfo(0x4B, "PgUp",  118, 17.25, 1.2, 1.00, category="nav"),

    # Row 2: QWERTY Row
    KeyInfo(0x2B, "Tab",   37,  0.00, 2.2, 1.50, category="mod"),
    KeyInfo(0x14, "Q",     38,  1.50, 2.2, 1.00, category="alpha"),
    KeyInfo(0x1A, "W",     39,  2.50, 2.2, 1.00, category="alpha"),
    KeyInfo(0x08, "E",     40,  3.50, 2.2, 1.00, category="alpha"),
    KeyInfo(0x15, "R",     41,  4.50, 2.2, 1.00, category="alpha"),
    KeyInfo(0x17, "T",     42,  5.50, 2.2, 1.00, category="alpha"),
    KeyInfo(0x1C, "Y",     43,  6.50, 2.2, 1.00, category="alpha"),
    KeyInfo(0x18, "U",     44,  7.50, 2.2, 1.00, category="alpha"),
    KeyInfo(0x0C, "I",     45,  8.50, 2.2, 1.00, category="alpha"),
    KeyInfo(0x12, "O",     46,  9.50, 2.2, 1.00, category="alpha"),
    KeyInfo(0x13, "P",     47, 10.50, 2.2, 1.00, category="alpha"),
    KeyInfo(0x2F, "[ {",   48, 11.50, 2.2, 1.00, category="alpha"),
    KeyInfo(0x30, "] }",   49, 12.50, 2.2, 1.00, category="alpha"),
    KeyInfo(0x31, "\\ |",  50, 13.50, 2.2, 1.50, category="alpha"),
    KeyInfo(0x4C, "Del",   119, 15.25, 2.2, 1.00, category="nav"),
    KeyInfo(0x4D, "End",   120, 16.25, 2.2, 1.00, category="nav"),
    KeyInfo(0x4E, "PgDn",  121, 17.25, 2.2, 1.00, category="nav"),

    # Row 3: ASDF Row
    KeyInfo(0x39, "Caps",  55,  0.00, 3.2, 1.75, category="mod"),
    KeyInfo(0x04, "A",     56,  1.75, 3.2, 1.00, category="alpha"),
    KeyInfo(0x16, "S",     57,  2.75, 3.2, 1.00, category="alpha"),
    KeyInfo(0x07, "D",     58,  3.75, 3.2, 1.00, category="alpha"),
    KeyInfo(0x09, "F",     59,  4.75, 3.2, 1.00, category="alpha"),
    KeyInfo(0x0A, "G",     60,  5.75, 3.2, 1.00, category="alpha"),
    KeyInfo(0x0B, "H",     61,  6.75, 3.2, 1.00, category="alpha"),
    KeyInfo(0x0D, "J",     62,  7.75, 3.2, 1.00, category="alpha"),
    KeyInfo(0x0E, "K",     63,  8.75, 3.2, 1.00, category="alpha"),
    KeyInfo(0x0F, "L",     64,  9.75, 3.2, 1.00, category="alpha"),
    KeyInfo(0x33, "; :",   65, 10.75, 3.2, 1.00, category="alpha"),
    KeyInfo(0x34, "' \"",  66, 11.75, 3.2, 1.00, category="alpha"),
    KeyInfo(0x28, "Enter", 67, 12.75, 3.2, 2.25, category="mod"),

    # Row 4: ZXCV Row
    KeyInfo(0xE1, "Shift L", 73, 0.00, 4.2, 2.25, category="mod"),
    KeyInfo(0x1D, "Z",     75,  2.25, 4.2, 1.00, category="alpha"),
    KeyInfo(0x1B, "X",     76,  3.25, 4.2, 1.00, category="alpha"),
    KeyInfo(0x06, "C",     77,  4.25, 4.2, 1.00, category="alpha"),
    KeyInfo(0x19, "V",     78,  5.25, 4.2, 1.00, category="alpha"),
    KeyInfo(0x05, "B",     79,  6.25, 4.2, 1.00, category="alpha"),
    KeyInfo(0x11, "N",     80,  7.25, 4.2, 1.00, category="alpha"),
    KeyInfo(0x10, "M",     81,  8.25, 4.2, 1.00, category="alpha"),
    KeyInfo(0x36, ", <",   82,  9.25, 4.2, 1.00, category="alpha"),
    KeyInfo(0x37, ". >",   83, 10.25, 4.2, 1.00, category="alpha"),
    KeyInfo(0x38, "/ ?",   84, 11.25, 4.2, 1.00, category="alpha"),
    KeyInfo(0xE5, "Shift R", 86, 12.25, 4.2, 2.75, category="mod"),
    KeyInfo(0x52, "Up",    124, 16.25, 4.2, 1.00, category="arrow"),

    # Row 5: Bottom Row
    KeyInfo(0xE0, "Ctrl L", 91,  0.00, 5.2, 1.25, category="mod"),
    KeyInfo(0xE3, "Win",    92,  1.25, 5.2, 1.25, category="mod"),
    KeyInfo(0xE2, "Alt L",  93,  2.50, 5.2, 1.25, category="mod"),
    KeyInfo(0x2C, "Space",  96,  3.75, 5.2, 6.25, category="mod"),
    KeyInfo(0xE6, "Alt R",  99, 10.00, 5.2, 1.25, category="mod"),
    KeyInfo(0x00, "Fn",     100, 11.25, 5.2, 1.25, category="mod"),
    KeyInfo(0x65, "Menu",   101, 12.50, 5.2, 1.25, category="mod"),
    KeyInfo(0xE4, "Ctrl R", 102, 13.75, 5.2, 1.25, category="mod"),
    KeyInfo(0x50, "Left",   123, 15.25, 5.2, 1.00, category="arrow"),
    KeyInfo(0x51, "Down",   125, 16.25, 5.2, 1.00, category="arrow"),
    KeyInfo(0x4F, "Right",  126, 17.25, 5.2, 1.00, category="arrow"),
]

# Quick Lookups
KEY_BY_CODE: Dict[int, KeyInfo] = {k.code: k for k in KEYS_87}
KEY_BY_MATRIX: Dict[int, KeyInfo] = {k.matrix_idx: k for k in KEYS_87}
KEY_BY_NAME: Dict[str, KeyInfo] = {k.name.lower(): k for k in KEYS_87}

# Lighting Preset Modes (0-indexed per Sonix firmware 0x11 command)
LIGHTING_MODES: Dict[str, int] = {
    "static": 0,
    "reactive": 1,
    "reactive_fade": 2,
    "glittering": 3,
    "falling": 4,
    "colourful": 5,
    "breathing": 6,
    "spectrum": 7,
    "outward": 8,
    "scrolling": 9,
    "rolling": 10,
    "rotating": 11,
    "explode": 12,
    "launch": 13,
    "ripples": 14,
    "flowing": 15,
    "pulsating": 16,
    "tilt": 17,
    "shuttle": 18,
    "custom": 20,
}

def hex_to_rgb(hex_str: str) -> Tuple[int, int, int]:
    """Converts #RRGGBB hex string to (R, G, B) tuple."""
    hex_str = hex_str.strip().lstrip("#")
    if len(hex_str) == 3:
        hex_str = "".join([c*2 for c in hex_str])
    if len(hex_str) != 6:
        return (0xCB, 0x94, 0xF7) # Default Lavender
    return (int(hex_str[0:2], 16), int(hex_str[2:4], 16), int(hex_str[4:6], 16))

def rgb_to_hex(r: int, g: int, b: int) -> str:
    """Converts (R, G, B) to uppercase hex string #RRGGBB."""
    return f"#{r:02X}{g:02X}{b:02X}"
