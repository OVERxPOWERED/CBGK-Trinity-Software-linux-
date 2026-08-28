"""
Non-blocking async hardware worker — reads the live matrix from the keyboard
before patching, so every key slot is correctly addressed.
"""

import threading
import queue
import time
from typing import Dict, Any, Optional
from ..device import Device, DeviceError
from ..protocol import Protocol
from ..matrix import hex_to_rgb, LIGHTING_MODES, KEYS_87, KEY_BY_NAME
from ..daemon import send_ipc_command

class AsyncHardwareWorker(threading.Thread):
    """Background worker thread — all USB I/O runs here, never on the Qt thread."""

    def __init__(self):
        super().__init__(daemon=True)
        self.queue: queue.Queue = queue.Queue(maxsize=8)
        self.running = True

    def submit_color(self, hex_color: str, key_colors: Optional[Dict[str, str]] = None):
        """Debounced: only the latest request matters."""
        self._drain()
        try:
            self.queue.put_nowait({
                "type": "color",
                "color": hex_color,
                "key_colors": dict(key_colors) if key_colors else None,
            })
        except queue.Full:
            pass

    def submit_mode(self, mode_name: str, color: str, speed: int, brightness: int):
        self._drain()
        try:
            self.queue.put_nowait({
                "type": "mode",
                "mode": mode_name,
                "color": color,
                "speed": speed,
                "brightness": brightness,
            })
        except queue.Full:
            pass

    def _drain(self):
        while not self.queue.empty():
            try:
                self.queue.get_nowait()
            except queue.Empty:
                break

    def run(self):
        while self.running:
            try:
                task = self.queue.get(timeout=0.5)
            except queue.Empty:
                continue

            try:
                t = task["type"]
                if t == "color":
                    self._do_color(task)
                elif t == "mode":
                    self._do_mode(task)
            except Exception:
                pass
            finally:
                self.queue.task_done()

    def _do_color(self, task: dict):
        hex_color = task.get("color", "#CB94F7")
        key_colors = task.get("key_colors")

        # Try daemon IPC first
        try:
            send_ipc_command("set_color", color=hex_color)
            return
        except Exception:
            pass

        # Direct hardware fallback: read live matrix → patch → upload
        try:
            with Device() as dev:
                if key_colors:
                    # Read the real live matrix from firmware RAM
                    matrix_data = Protocol.read_live_matrix(dev)
                    patched = bytearray(matrix_data)

                    # Build a lookup: matrix_idx -> (r, g, b) from the GUI color map
                    idx_to_rgb = {}
                    for k in KEYS_87:
                        col = key_colors.get(k.name, hex_color)
                        idx_to_rgb[k.matrix_idx] = hex_to_rgb(col)

                    # Patch every key entry in the real buffer
                    for i in range(0, len(patched), 4):
                        m_idx = patched[i]
                        if m_idx in idx_to_rgb:
                            r, g, b = idx_to_rgb[m_idx]
                            patched[i + 1] = r
                            patched[i + 2] = g
                            patched[i + 3] = b

                    Protocol.upload_matrix_buffer(dev, patched)
                else:
                    r, g, b = hex_to_rgb(hex_color)
                    Protocol.set_solid_color(dev, r, g, b)
        except DeviceError:
            pass

    def _do_mode(self, task: dict):
        mode_name = task.get("mode", "static")
        color = task.get("color", "#CB94F7")
        speed = task.get("speed", 3)
        brightness = task.get("brightness", 4)

        try:
            send_ipc_command("set_mode", mode=mode_name, color=color,
                             speed=speed, brightness=brightness)
            return
        except Exception:
            pass

        try:
            mode_id = LIGHTING_MODES.get(mode_name, 1)
            r, g, b = hex_to_rgb(color)
            with Device() as dev:
                Protocol.set_preset_mode(dev, mode_id=mode_id, speed=speed,
                                         brightness=brightness, r=r, g=g, b=b)
        except DeviceError:
            pass
