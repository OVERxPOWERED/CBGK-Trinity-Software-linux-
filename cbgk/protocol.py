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
    def upload_matrix_buffer(dev: Device, buffer: bytearray):
        """
        Uploads a 576-byte matrix buffer to the keyboard using 0x04 0x20.
        """
        # 1. Custom Lighting Header
        hdr = bytearray(64)
        hdr[0] = 0x04
        hdr[1] = 0x20
        hdr[8] = 0x08 # Required header flag at offset 8
        dev.send_feature(hdr)
        time.sleep(0.005)

        # 2. Upload 9 chunks of 64 bytes
        for i in range(0, len(buffer), 64):
            chunk = buffer[i:i+64]
            if len(chunk) < 64:
                chunk = chunk + bytearray(64 - len(chunk))
            dev.send_feature(chunk)
            time.sleep(0.002)

        # 3. Commit packet
        commit = bytearray(64)
        commit[0] = 0x04
        commit[1] = 0x02
        dev.send_feature(commit)
        time.sleep(0.005)

        # 4. Finish packet
        finish = bytearray(64)
        finish[0] = 0x04
        finish[1] = 0xF0
        dev.send_feature(finish)
        time.sleep(0.005)

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
        mode_id: int = 1,
        speed: int = 3,
        brightness: int = 4,
        direction: int = 0,
        r: int = 0xCB,
        g: int = 0x94,
        b: int = 0xF7,
        color_type: int = 7
    ):
        """
        Configures the built-in firmware animation modes (Static, Breathing, Wave, etc.)
        and commits the setting to onboard EEPROM memory.
        """
        # Step 1: Start Lighting Config Session
        hdr = bytearray(64)
        hdr[0] = 0x04
        hdr[1] = 0x58
        dev.send_feature(hdr)
        time.sleep(0.02)

        # Step 2: Mode Header
        hdr2 = bytearray(64)
        hdr2[0] = 0x04
        hdr2[1] = 0x53
        hdr2[8] = 0x03
        dev.send_feature(hdr2)
        time.sleep(0.02)

        # Step 3: Build 192-byte Modes Table (12 modes * 16 bytes each with 0x55AA footer)
        modes_table = bytearray(192)
        for m in range(12):
            off = m * 16
            is_sel = 1 if m == mode_id else 0
            modes_table[off + 0] = m             # Mode ID
            modes_table[off + 1] = speed         # Speed (1..5)
            modes_table[off + 2] = brightness    # Brightness (0..4)
            modes_table[off + 3] = direction     # Direction (0 or 1)
            modes_table[off + 4] = color_type    # 7 = Custom User RGB
            modes_table[off + 5] = r
            modes_table[off + 6] = g
            modes_table[off + 7] = b
            modes_table[off + 11] = is_sel       # Selection Bit
            modes_table[off + 13] = 0xAA         # Magic footer 0x55AA
            modes_table[off + 14] = 0x55

        for i in range(0, len(modes_table), 64):
            dev.send_feature(modes_table[i:i+64])
            time.sleep(0.01)

        # Step 4: Active Mode Table (256 bytes)
        active_buf = bytearray(256)
        active_buf[0] = mode_id
        active_buf[1] = speed
        active_buf[2] = brightness
        active_buf[3] = direction
        active_buf[4] = color_type
        active_buf[5] = r
        active_buf[6] = g
        active_buf[7] = b
        active_buf[11] = 0x01
        active_buf[13] = 0xAA
        active_buf[14] = 0x55

        for i in range(0, len(active_buf), 64):
            dev.send_feature(active_buf[i:i+64])
            time.sleep(0.01)

        # Step 5: Save & Apply
        commit_pkt = bytearray(64)
        commit_pkt[0] = 0x04
        commit_pkt[1] = 0x02
        dev.send_feature(commit_pkt)
        time.sleep(0.02)
