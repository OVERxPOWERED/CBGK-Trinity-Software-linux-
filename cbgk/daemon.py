"""
Continuous Background Lighting & IPC Service for CBGK.
"""

import os
import sys
import time
import socket
import select
import signal
import json
import threading
from typing import Dict, Any, Optional

from .device import Device, DeviceError
from .protocol import Protocol
from .matrix import hex_to_rgb, rgb_to_hex, LIGHTING_MODES, KEYS_87
from .profiles import ProfileManager

SOCKET_PATH = "/tmp/cbgk.sock"
PID_FILE = "/tmp/cbgk.pid"

class Daemon:
    """Background service ensuring persistent lighting state & IPC control."""

    def __init__(self):
        self.running = False
        self.profile_mgr = ProfileManager()
        self.current_profile_name = self.profile_mgr.get_active_profile_name()
        self.current_profile = self.profile_mgr.get_profile(self.current_profile_name) or self.profile_mgr.get_profile("Lavender Bliss")
        self.lock = threading.RLock()
        self.device: Optional[Device] = None
        self.active_buffer: Optional[bytearray] = None
        self.preset_mode_info: Optional[Dict[str, Any]] = None

    def _setup_signals(self):
        signal.signal(signal.SIGINT, self._handle_signal)
        signal.signal(signal.SIGTERM, self._handle_signal)

    def _handle_signal(self, sig, frame):
        print(f"\n[*] Received signal {sig}. Terminating daemon cleanly...")
        self.running = False

    def load_active_profile(self):
        """Loads profile data into memory buffer."""
        with self.lock:
            if not self.current_profile:
                return

            mode = self.current_profile.get("mode", "custom")
            if mode == "custom":
                self.preset_mode_info = None
                per_key = self.current_profile.get("per_key", {})
                global_color = self.current_profile.get("color", "#CB94F7")
                def_r, def_g, def_b = hex_to_rgb(global_color)

                # Initialize full 576-byte buffer with 144 key entries
                buf = bytearray(576)
                for slot in range(144):
                    buf[slot * 4] = slot
                for k in KEYS_87:
                    off = k.matrix_idx * 4
                    if off + 4 <= len(buf):
                        hex_col = per_key.get(k.name, global_color)
                        r, g, b = hex_to_rgb(hex_col)
                        buf[off + 1] = r
                        buf[off + 2] = g
                        buf[off + 3] = b
                self.active_buffer = buf
            else:
                self.active_buffer = None
                mode_id = LIGHTING_MODES.get(mode, 1)
                r, g, b = hex_to_rgb(self.current_profile.get("color", "#CB94F7"))
                self.preset_mode_info = {
                    "mode_id": mode_id,
                    "speed": self.current_profile.get("speed", 3),
                    "brightness": self.current_profile.get("brightness", 4),
                    "direction": self.current_profile.get("direction", 0),
                    "r": r,
                    "g": g,
                    "b": b
                }

    def _ensure_device(self) -> bool:
        """Ensures active connection to the keyboard."""
        if self.device is not None and self.device.fd is not None:
            return True

        try:
            self.device = Device()
            self.device.open()
            print(f"[+] Connected to Cosmic Byte Trinity on {self.device.path}")
            return True
        except Exception as e:
            self.device = None
            return False

    def start(self):
        """Starts the daemon main event loop."""
        self._setup_signals()
        self.running = True

        # Write PID file
        with open(PID_FILE, "w") as f:
            f.write(str(os.getpid()))

        # Remove old socket if exists
        if os.path.exists(SOCKET_PATH):
            os.remove(SOCKET_PATH)

        server_sock = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
        server_sock.bind(SOCKET_PATH)
        server_sock.listen(5)
        server_sock.setblocking(False)
        os.chmod(SOCKET_PATH, 0o777)

        print("[*] CBGK Background Daemon started.")
        print(f"[*] IPC Socket active at {SOCKET_PATH}")

        self.load_active_profile()
        self._sync_hardware()

        try:
            while self.running:
                # Check for incoming IPC client requests
                readable, _, _ = select.select([server_sock], [], [], 0.5)
                if readable:
                    try:
                        client_sock, _ = server_sock.accept()
                        client_thread = threading.Thread(target=self._handle_client, args=(client_sock,), daemon=True)
                        client_thread.start()
                    except Exception:
                        pass
        finally:
            if self.device:
                self.device.close()
            server_sock.close()
            if os.path.exists(SOCKET_PATH):
                os.remove(SOCKET_PATH)
            if os.path.exists(PID_FILE):
                os.remove(PID_FILE)
            print("[*] CBGK Daemon terminated cleanly.")

    def _sync_hardware(self):
        """Transmits current active lighting state to physical hardware once."""
        if not self._ensure_device():
            return
        try:
            with self.lock:
                if self.active_buffer:
                    Protocol.upload_matrix_buffer(self.device, self.active_buffer)
                elif self.preset_mode_info:
                    p = self.preset_mode_info
                    Protocol.set_preset_mode(
                        self.device,
                        mode_id=p["mode_id"],
                        speed=p["speed"],
                        brightness=p["brightness"],
                        direction=p["direction"],
                        r=p["r"],
                        g=p["g"],
                        b=p["b"]
                    )
        except Exception as e:
            if self.device:
                self.device.close()
            self.device = None
        finally:
            if self.device:
                self.device.close()
            server_sock.close()
            if os.path.exists(SOCKET_PATH):
                os.remove(SOCKET_PATH)
            if os.path.exists(PID_FILE):
                os.remove(PID_FILE)
            print("[*] CBGK Daemon terminated cleanly.")

    def _handle_client(self, client_sock: socket.socket):
        """Processes IPC JSON commands from CLI or GUI."""
        try:
            client_sock.settimeout(2.0)
            raw = client_sock.recv(65536).decode("utf-8")
            if not raw:
                return

            req = json.loads(raw.strip())
            cmd = req.get("cmd", "")

            response = {"status": "ok"}

            if cmd == "ping":
                response["data"] = "pong"

            elif cmd == "status":
                with self.lock:
                    response["data"] = {
                        "connected": self.device is not None and self.device.fd is not None,
                        "device_path": self.device.path if self.device else None,
                        "active_profile": self.current_profile_name,
                        "profile_data": self.current_profile
                    }

            elif cmd == "set_color":
                hex_color = req.get("color", "#CB94F7")
                with self.lock:
                    self.current_profile = {
                        "name": "Custom Solid",
                        "mode": "custom",
                        "color": hex_color,
                        "brightness": 4,
                        "speed": 3,
                        "per_key": {k.name: hex_color for k in KEYS_87}
                    }
                    self.load_active_profile()
                self._sync_hardware()
                response["message"] = f"Applied color {hex_color}"

            elif cmd == "set_custom_matrix":
                per_key = req.get("per_key", {})
                global_color = req.get("color", "#FFFFFF")
                with self.lock:
                    self.current_profile = {
                        "name": "Custom Matrix",
                        "mode": "custom",
                        "color": global_color,
                        "brightness": 4,
                        "speed": 3,
                        "per_key": dict(per_key)
                    }
                    self.load_active_profile()
                self._sync_hardware()
                response["message"] = "Applied custom per-key matrix"

            elif cmd == "set_mode":
                mode_name = req.get("mode", "static")
                color = req.get("color", "#CB94F7")
                speed = req.get("speed", 3)
                brightness = req.get("brightness", 4)
                with self.lock:
                    self.current_profile = {
                        "name": f"Preset {mode_name.capitalize()}",
                        "mode": mode_name,
                        "color": color,
                        "speed": speed,
                        "brightness": brightness,
                        "per_key": {}
                    }
                    self.load_active_profile()
                self._sync_hardware()
                response["message"] = f"Applied preset {mode_name}"

            elif cmd == "apply_profile":
                p_name = req.get("profile")
                prof = self.profile_mgr.get_profile(p_name)
                if prof:
                    with self.lock:
                        self.current_profile_name = p_name
                        self.current_profile = prof
                        self.profile_mgr.set_active_profile_name(p_name)
                        self.load_active_profile()
                    self._sync_hardware()
                    response["message"] = f"Switched to profile {p_name}"
                else:
                    response["status"] = "error"
                    response["message"] = f"Profile '{p_name}' not found"

            elif cmd == "stop":
                self.running = False
                response["message"] = "Daemon shutting down"

            resp_bytes = json.dumps(response).encode("utf-8")
            client_sock.sendall(resp_bytes)
        except Exception as e:
            try:
                client_sock.sendall(json.dumps({"status": "error", "message": str(e)}).encode("utf-8"))
            except Exception:
                pass
        finally:
            try:
                client_sock.close()
            except Exception:
                pass

def send_ipc_command(cmd: str, **kwargs) -> Dict[str, Any]:
    """Client utility to send IPC commands to the running daemon."""
    if not os.path.exists(SOCKET_PATH):
        raise ConnectionError("CBGK daemon is not running.")

    sock = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
    sock.settimeout(2.5)
    try:
        sock.connect(SOCKET_PATH)
        payload = json.dumps({"cmd": cmd, **kwargs})
        sock.sendall(payload.encode("utf-8"))
        resp = sock.recv(65536).decode("utf-8")
        if not resp:
            raise ConnectionError("Empty response from daemon.")
        return json.loads(resp.strip())
    except (socket.timeout, ConnectionRefusedError, OSError) as e:
        if os.path.exists(SOCKET_PATH):
            try: os.remove(SOCKET_PATH)
            except OSError: pass
        if os.path.exists(PID_FILE):
            try: os.remove(PID_FILE)
            except OSError: pass
        raise ConnectionError(f"Failed to communicate with daemon: {e}")
    finally:
        sock.close()

if __name__ == "__main__":
    daemon = Daemon()
    daemon.start()
