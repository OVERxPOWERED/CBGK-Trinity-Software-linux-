"""
Non-blocking asynchronous hardware & IPC worker queue for 120 FPS UI performance.
"""

import threading
import queue
import time
from typing import Dict, Any, Callable, Optional
from ..device import Device
from ..protocol import Protocol
from ..matrix import hex_to_rgb, LIGHTING_MODES, KEYS_87
from ..daemon import send_ipc_command

class AsyncHardwareWorker(threading.Thread):
    """Background worker thread processing hardware updates without lagging the GUI."""

    def __init__(self):
        super().__init__(daemon=True)
        self.queue = queue.Queue(maxsize=10)
        self.running = True
        self.last_update_time = 0.0

    def submit_color(self, hex_color: str, key_colors: Optional[Dict[str, str]] = None):
        """Debounced submission of lighting change."""
        # Drain old pending lighting tasks to prevent backlog
        while not self.queue.empty():
            try:
                self.queue.get_nowait()
            except queue.Empty:
                break

        task = {
            "type": "color",
            "color": hex_color,
            "key_colors": dict(key_colors) if key_colors else None
        }
        try:
            self.queue.put_nowait(task)
        except queue.Full:
            pass

    def submit_mode(self, mode_name: str, color: str, speed: int, brightness: int):
        while not self.queue.empty():
            try:
                self.queue.get_nowait()
            except queue.Empty:
                break

        task = {
            "type": "mode",
            "mode": mode_name,
            "color": color,
            "speed": speed,
            "brightness": brightness
        }
        try:
            self.queue.put_nowait(task)
        except queue.Full:
            pass

    def run(self):
        while self.running:
            try:
                task = self.queue.get(timeout=0.5)
            except queue.Empty:
                continue

            try:
                task_type = task.get("type")
                if task_type == "color":
                    hex_color = task.get("color", "#CB94F7")
                    key_colors = task.get("key_colors")
                    # Try Daemon IPC first
                    try:
                        send_ipc_command("set_color", color=hex_color)
                    except Exception:
                        # Fallback direct hardware
                        r, g, b = hex_to_rgb(hex_color)
                        try:
                            with Device() as dev:
                                if key_colors:
                                    buf = bytearray(576)
                                    for k in KEYS_87:
                                        off = (k.matrix_idx - 1) * 4
                                        if off + 4 <= len(buf):
                                            col = key_colors.get(k.name, hex_color)
                                            kr, kg, kb = hex_to_rgb(col)
                                            buf[off] = k.matrix_idx
                                            buf[off + 1] = kr
                                            buf[off + 2] = kg
                                            buf[off + 3] = kb
                                    Protocol.upload_matrix_buffer(dev, buf)
                                else:
                                    Protocol.set_solid_color(dev, r, g, b)
                        except Exception:
                            pass

                elif task_type == "mode":
                    mode_name = task.get("mode", "static")
                    color = task.get("color", "#CB94F7")
                    speed = task.get("speed", 3)
                    brightness = task.get("brightness", 4)
                    try:
                        send_ipc_command("set_mode", mode=mode_name, color=color, speed=speed, brightness=brightness)
                    except Exception:
                        mode_id = LIGHTING_MODES.get(mode_name, 1)
                        r, g, b = hex_to_rgb(color)
                        try:
                            with Device() as dev:
                                Protocol.set_preset_mode(dev, mode_id=mode_id, speed=speed, brightness=brightness, r=r, g=g, b=b)
                        except Exception:
                            pass
            except Exception:
                pass
            finally:
                self.queue.task_done()
                time.sleep(0.02)
