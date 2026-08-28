# CBGK: Cosmic Byte Trinity Linux Software Suite

A modern, high-performance Linux driver, background daemon, command-line utility, and **Material 3 Liquid Glass** graphical control center for the **Cosmic Byte Trinity RGB Gaming Keyboard (87-Key TKL)**.

![Arch Linux](https://img.shields.io/badge/Arch_Linux-Compatible-blue?logo=arch-linux)
![Python](https://img.shields.io/badge/Python-3.8+-yellow?logo=python)
![PyQt6](https://img.shields.io/badge/GUI-Material_3_PyQt6-blueviolet?logo=qt)
![License](https://img.shields.io/badge/License-MIT-green)

---

## ✨ Features

- 🎨 **Material 3 Liquid Glass Aesthetics**: Designed to seamlessly complement modern Linux desktop environments (Arch Linux, Hyprland, Caelestia, KDE, GNOME) with frosted glass panels, specular lighting, and fluid interactions.
- ⌨️ **Interactive 87-Key Canvas**: Full vector-rendered keyboard layout with real-time backlit LED glow shaders and click-to-paint customization.
- 🌈 **Full RGB Control**:
  - Uniform solid colors (HEX / RGB / Color Picker / Palette chips).
  - 21 built-in animation presets (Breathing, Wave, Spectrum Cycle, Reactive, etc.) with speed and brightness adjustment.
  - Per-key custom lighting layouts.
- ⚡ **Lightweight Background Daemon**: Non-intrusive userspace keep-alive service ensuring zero timeout drops with **`< 0.01%` CPU usage** and IPC socket support.
- 📁 **Profile Management**: Instant switching between gaming, coding, and creative color profiles stored in `~/.config/cbgk/profiles/`.
- 💻 **Complete CLI Utility**: Control keyboard lighting and profiles directly from terminal scripts, keybindings, or shell aliases.

---

## 🚀 Quick Start & Installation

### 1. Permissions (udev rule)
Ensure your non-root user has read/write permissions to the keyboard HID interface:
```bash
sudo bash -c 'cat <<EOF > /etc/udev/rules.d/98-cosmicbyte-wired.rules
SUBSYSTEM=="hidraw", ATTRS{idVendor}=="0c45", ATTRS{idProduct}=="8006", MODE="0666"
EOF'
sudo udevadm control --reload-rules && sudo udevadm trigger
```

### 2. Install Package
```bash
pip install -e .
```

---

## 🖥️ Usage

### Desktop GUI (Material 3 Liquid Glass)
Launch the graphical control center:
```bash
cbgk-gui
```

### Command Line Interface (`cbgk`)

#### Set Solid Uniform Color
```bash
cbgk color "#CB94F7"      # Signature Lavender
cbgk color "#00FFFF"      # Cyan
cbgk color "#FF007F"      # Neon Pink
```

#### Set Preset Animation Mode
```bash
cbgk mode breathing --color "#CB94F7" --speed 3 --brightness 4
cbgk mode spectrum --speed 4
cbgk mode static --color "#00FF66"
```

#### Manage Profiles
```bash
cbgk profile list
cbgk profile load "Cyberpunk Neon"
cbgk profile load "FPS Pro"
```

#### Background Daemon
```bash
cbgk daemon start         # Launches background daemon
cbgk daemon status        # Checks connection & active profile
cbgk daemon stop          # Stops the daemon
```

---

## 🛠️ Autostart Daemon (Systemd)

To have the CBGK lighting daemon start automatically on user login:
```bash
mkdir -p ~/.config/systemd/user
cp cbgk.service ~/.config/systemd/user/
systemctl --user daemon-reload
systemctl --user enable --now cbgk.service
```

---

## 🔬 Protocol & Reverse Engineering

The Cosmic Byte Trinity (Sonix MCU `0C45:8006`) uses 65-byte unnumbered USB HID Feature Reports:
- **Report ID**: `0x00`
- **Read Matrix RAM**: `[0x04, 0xF5, 0x01, ...]` (Dumps 576-byte active LED matrix).
- **Stream Matrix Buffer**: `[0x04, 0x20, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x08, ...]` followed by 9 chunks of 64 bytes.
- **EEPROM Commit / Save**: `[0x04, 0x02, ...]`.

---

## 📄 License
MIT License • Created with ❤️ for the Linux Gaming & Mechanical Keyboard Community.
