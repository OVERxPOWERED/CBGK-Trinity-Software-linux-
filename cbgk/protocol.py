"""
Sonix MCU packet protocol builder for Lighting, Keys, Macros & EEPROM Storage.
"""

import time
from typing import Dict, Tuple, Optional, Union
from .device import Device
from .matrix import (
    KEYS_87,
    KEY_BY_CODE,
    KEY_BY_MATRIX,
    KEY_BY_NAME,
    LIGHTING_MODES,
    hex_to_rgb,
    rgb_to_hex
)

class Protocol:
    """Implements the full Sonix MCU command set for the Cosmic Byte Trinity."""

    @staticmethod
    def read_live_matrix(dev: Device) -> bytearray:
        """
        Reads the active 576-byte (144 key entries * 4 bytes) lighting matrix from keyboard RAM.
        Format per key: [Matrix_Index, Red, Green, Blue]
        """
        matrix_data = bytearray()
        for block in range(9):
            req = bytearray(64)
            req[0] = 0x04
            req[1] = 0xF5
            req[2] = 0x01 if block == 0 else 0x00
            dev.send_feature(req)
            time.sleep(0.002)
            chunk = dev.get_feature()
            matrix_data.extend(chunk)
        return matrix_data

    @staticmethod
    def upload_matrix_buffer(dev: Device, buffer: bytearray, brightness: int = 4, speed: int = 3, r: int = 0xCB, g: int = 0x94, b: int = 0xF7):
        """
        Uploads a 576-byte matrix buffer to the keyboard using Mode 20 and 0x04 0x20.
        """
        # 1. Activate Mode 20 (Custom User Record Mode in Flash)
        hdr_mode = bytearray(64)
        hdr_mode[0] = 0x04
        hdr_mode[1] = 0x18
        dev.send_feature(hdr_mode)
        time.sleep(0.01)

        mode_pkt = bytearray(64)
        mode_pkt[0] = 0x04
        mode_pkt[1] = 0x11
        mode_pkt[2] = 0x14 # Mode 20 (Custom Lighting)
        mode_pkt[3] = speed
        mode_pkt[4] = brightness
        mode_pkt[5] = 0x00
        mode_pkt[6] = r
        mode_pkt[7] = g
        mode_pkt[8] = b
        dev.send_feature(mode_pkt)
        time.sleep(0.01)

        # 2. Custom Lighting Header
        hdr = bytearray(64)
        hdr[0] = 0x04
        hdr[1] = 0x20
        hdr[8] = 0x08 # Required header flag at offset 8
        dev.send_feature(hdr)
        time.sleep(0.005)

        # 3. Upload 9 chunks of 64 bytes
        for i in range(0, len(buffer), 64):
            chunk = buffer[i:i+64]
            if len(chunk) < 64:
                chunk = chunk + bytearray(64 - len(chunk))
            dev.send_feature(chunk)
            time.sleep(0.002)

        # 4. Commit packet
        commit = bytearray(64)
        commit[0] = 0x04
        commit[1] = 0x02
        dev.send_feature(commit)
        time.sleep(0.01)

    @classmethod
    def set_solid_color(cls, dev: Device, r: int, g: int, b: int):
        """
        Applies a solid uniform RGB color to all 87 keys on the keyboard.
        """
        buf = bytearray(576)
        for slot in range(144):
            buf[slot * 4] = slot
        for k in KEYS_87:
            off = k.matrix_idx * 4
            if off + 4 <= len(buf):
                buf[off + 1] = r
                buf[off + 2] = g
                buf[off + 3] = b
        cls.upload_matrix_buffer(dev, buf)

    @classmethod
    def set_per_key_colors(cls, dev: Device, color_map: Dict[Union[int, str], Tuple[int, int, int]], default_rgb: Tuple[int, int, int] = (0xCB, 0x94, 0xF7)):
        """
        Sets individual colors for specific keys using exact matrix_idx * 4 offsets.
        """
        buf = bytearray(576)
        for slot in range(144):
            buf[slot * 4] = slot
        def_r, def_g, def_b = default_rgb
        for k in KEYS_87:
            off = k.matrix_idx * 4
            if off + 4 <= len(buf):
                buf[off + 1] = def_r
                buf[off + 2] = def_g
                buf[off + 3] = def_b

        for key_ref, color in color_map.items():
            if isinstance(key_ref, str):
                k_info = KEY_BY_NAME.get(key_ref.lower())
                if k_info:
                    off = k_info.matrix_idx * 4
                    if off + 4 <= len(buf):
                        buf[off + 1], buf[off + 2], buf[off + 3] = color
            elif isinstance(key_ref, int):
                off = key_ref * 4
                if off + 4 <= len(buf):
                    buf[off + 1], buf[off + 2], buf[off + 3] = color

        cls.upload_matrix_buffer(dev, buf)

    @staticmethod
    def set_preset_mode(
        dev: Device,
        mode_id: int = 0,
        speed: int = 3,
        brightness: int = 4,
        direction: int = 0,
        r: int = 0xCB,
        g: int = 0x94,
        b: int = 0xF7,
        color_type: int = 0
    ):
        """
        Configures the built-in firmware animation modes (Static, Breathing, Wave, etc.)
        and commits the setting to onboard EEPROM memory.
        """
        # 1. Header packet
        h = bytearray(64)
        h[0] = 0x04
        h[1] = 0x18
        dev.send_feature(h)
        time.sleep(0.03)

        # 2. Preset Mode Packet
        m = bytearray(64)
        m[0] = 0x04
        m[1] = 0x11
        m[2] = mode_id
        m[3] = speed
        m[4] = brightness
        m[5] = direction
        m[6] = r
        m[7] = g
        m[8] = b
        m[9] = 0x00
        dev.send_feature(m)
        time.sleep(0.03)

        # 3. Commit Packet
        c = bytearray(64)
        c[0] = 0x04
        c[1] = 0x02
        dev.send_feature(c)
        time.sleep(0.03)

        # 4. Finish Packet
        f = bytearray(64)
        f[0] = 0x04
        f[1] = 0xF0
        dev.send_feature(f)
        time.sleep(0.03)
