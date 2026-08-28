"""
JSON Profile Management for CBGK Keyboard configurations.
"""

import os
import json
from typing import Dict, List, Any, Optional
from .matrix import KEYS_87, rgb_to_hex, hex_to_rgb

CONFIG_DIR = os.path.expanduser("~/.config/cbgk")
PROFILES_DIR = os.path.join(CONFIG_DIR, "profiles")
CONFIG_FILE = os.path.join(CONFIG_DIR, "config.json")

DEFAULT_PROFILES = {
    "Lavender Bliss": {
        "name": "Lavender Bliss",
        "description": "Clean aesthetic lavender solid purple #CB94F7",
        "mode": "custom",
        "color": "#CB94F7",
        "brightness": 4,
        "speed": 3,
        "per_key": {k.name: "#CB94F7" for k in KEYS_87}
    },
    "Cyberpunk Neon": {
        "name": "Cyberpunk Neon",
        "description": "Vibrant cyan, hot pink and electric violet",
        "mode": "custom",
        "color": "#FF007F",
        "brightness": 4,
        "speed": 3,
        "per_key": {
            k.name: (
                "#00FFFF" if k.name.lower() in ["w", "a", "s", "d", "up", "down", "left", "right"]
                else "#FF007F" if k.category in ["mod", "nav", "function"]
                else "#7928CA"
            )
            for k in KEYS_87
        }
    },
    "FPS Pro": {
        "name": "FPS Pro",
        "description": "WASD, Space, Shift, R, and Numbers highlighted",
        "mode": "custom",
        "color": "#111118",
        "brightness": 4,
        "speed": 3,
        "per_key": {
            k.name: (
                "#00FF66" if k.name.lower() in ["w", "a", "s", "d"]
                else "#FF3366" if k.name.lower() in ["1 !", "2 @", "3 #", "4 $", "r", "e", "g", "c", "v"]
                else "#00D4FF" if k.name.lower() in ["space", "shift l", "ctrl l", "tab"]
                else "#1A1A24"
            )
            for k in KEYS_87
        }
    },
    "Matrix Hacker": {
        "name": "Matrix Hacker",
        "description": "Deep emerald green and bright terminal green",
        "mode": "custom",
        "color": "#00FF41",
        "brightness": 4,
        "speed": 3,
        "per_key": {
            k.name: (
                "#00FF41" if k.category == "alpha"
                else "#008F11"
            )
            for k in KEYS_87
        }
    }
}

class ProfileManager:
    """Handles loading, saving, and switching keyboard profiles."""

    def __init__(self):
        self.ensure_directories()
        self.init_default_profiles()

    def ensure_directories(self):
        os.makedirs(PROFILES_DIR, exist_ok=True)

    def init_default_profiles(self):
        for name, data in DEFAULT_PROFILES.items():
            filename = self._slugify(name) + ".json"
            path = os.path.join(PROFILES_DIR, filename)
            if not os.path.exists(path):
                self.save_profile(name, data)

    @staticmethod
    def _slugify(name: str) -> str:
        return "".join(c if c.isalnum() else "_" for c in name.lower()).strip("_")

    def list_profiles(self) -> List[Dict[str, Any]]:
        """Returns all available profiles."""
        profiles = []
        for filename in sorted(os.listdir(PROFILES_DIR)):
            if filename.endswith(".json"):
                path = os.path.join(PROFILES_DIR, filename)
                try:
                    with open(path, "r") as f:
                        data = json.load(f)
                        profiles.append(data)
                except Exception:
                    continue
        return profiles

    def get_profile(self, name: str) -> Optional[Dict[str, Any]]:
        """Finds a profile by exact name or slugified filename."""
        slug = self._slugify(name)
        path = os.path.join(PROFILES_DIR, slug + ".json")
        if os.path.exists(path):
            with open(path, "r") as f:
                return json.load(f)

        # Fallback linear search
        for p in self.list_profiles():
            if p.get("name", "").lower() == name.lower():
                return p
        return None

    def save_profile(self, name: str, data: Dict[str, Any]):
        """Saves a profile to JSON."""
        data["name"] = name
        slug = self._slugify(name)
        path = os.path.join(PROFILES_DIR, slug + ".json")
        with open(path, "w") as f:
            json.dump(data, f, indent=2)

    def delete_profile(self, name: str) -> bool:
        """Deletes a profile file."""
        slug = self._slugify(name)
        path = os.path.join(PROFILES_DIR, slug + ".json")
        if os.path.exists(path):
            os.remove(path)
            return True
        return False

    def get_active_profile_name(self) -> str:
        """Returns the active profile name from config.json."""
        if os.path.exists(CONFIG_FILE):
            try:
                with open(CONFIG_FILE, "r") as f:
                    cfg = json.load(f)
                    return cfg.get("active_profile", "Lavender Bliss")
            except Exception:
                pass
        return "Lavender Bliss"

    def set_active_profile_name(self, name: str):
        """Saves the active profile name into config.json."""
        cfg = {}
        if os.path.exists(CONFIG_FILE):
            try:
                with open(CONFIG_FILE, "r") as f:
                    cfg = json.load(f)
            except Exception:
                pass
        cfg["active_profile"] = name
        with open(CONFIG_FILE, "w") as f:
            json.dump(cfg, f, indent=2)
