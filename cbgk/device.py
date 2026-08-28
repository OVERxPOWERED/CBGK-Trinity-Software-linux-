"""
Low-level USB HID Communication & Device Discovery for Cosmic Byte Trinity.
"""

import os
import glob
import fcntl
from typing import Optional, List, Tuple

# Constants for Sonix MCU Feature Reports (65 bytes)
# Report ID (0x00) + 64 data bytes
HIDIOCSFEATURE_65 = 0xC0414806 # _IOC(_IOC_WRITE|_IOC_READ, 'H', 0x06, 65)
HIDIOCGFEATURE_65 = 0xC0414807 # _IOC(_IOC_WRITE|_IOC_READ, 'H', 0x07, 65)

TARGET_VID = 0x0C45 # Sonix / Microdia
TARGET_PID = 0x8006 # Trinity / K870T Keyboard Controller

class DeviceError(Exception):
    """Custom exception for device communication errors."""
    pass

class Device:
    """Manages the raw HID interface to the Cosmic Byte Trinity Keyboard."""

    def __init__(self, path: Optional[str] = None):
        self.path = path or self.find_device()
        self.fd: Optional[int] = None

    @staticmethod
    def find_device() -> str:
        """
        Scans /sys/class/hidraw to automatically locate the keyboard's
        configuration endpoint supporting 64-byte unnumbered feature reports.
        """
        candidates: List[str] = []
        for uevent_path in glob.glob("/sys/class/hidraw/hidraw*/device/uevent"):
            try:
                with open(uevent_path, "r") as f:
                    content = f.read()
                # Parse HID_ID=0003:00000C45:00008006
                for line in content.splitlines():
                    if line.startswith("HID_ID="):
                        parts = line.split("=")[1].split(":")
                        if len(parts) == 3:
                            vid = int(parts[1], 16)
                            pid = int(parts[2], 16)
                            if vid == TARGET_VID and pid == TARGET_PID:
                                hidraw_name = uevent_path.split("/")[4]
                                dev_path = f"/dev/{hidraw_name}"
                                candidates.append(dev_path)
            except Exception:
                continue

        if not candidates:
            # Fallback to known hidraw devices if sysfs check failed
            for fallback in ["/dev/hidraw2", "/dev/hidraw3", "/dev/hidraw1", "/dev/hidraw0"]:
                if os.path.exists(fallback):
                    candidates.append(fallback)

        if not candidates:
            raise DeviceError(
                "Cosmic Byte Trinity keyboard not detected in wired mode.\n"
                "Please ensure the keyboard is connected via USB-C cable."
            )

        # Test candidate nodes to find the active feature report endpoint
        for cand in candidates:
            try:
                fd = os.open(cand, os.O_RDWR)
                test_buf = bytearray(65)
                # Try a safe read of RAM block 0
                test_buf[1] = 0x04
                test_buf[2] = 0xF5
                test_buf[3] = 0x01
                fcntl.ioctl(fd, HIDIOCSFEATURE_65, test_buf)
                resp = bytearray(65)
                fcntl.ioctl(fd, HIDIOCGFEATURE_65, resp)
                os.close(fd)
                if resp[1] != 0 or resp[2] != 0 or resp[3] != 0:
                    return cand
            except (PermissionError, OSError):
                continue

        # If probe was inconclusive, return first candidate
        return candidates[0]

    def open(self) -> "Device":
        """Opens the hidraw interface."""
        if not self.path or not os.path.exists(self.path):
            raise DeviceError(f"Device node '{self.path}' does not exist.")

        try:
            self.fd = os.open(self.path, os.O_RDWR)
            return self
        except PermissionError:
            raise DeviceError(
                f"Permission denied accessing '{self.path}'.\n"
                "Please ensure udev rules are installed: 'sudo cbgk setup-udev'"
            )
        except OSError as e:
            raise DeviceError(f"Failed to open '{self.path}': {e}")

    def close(self):
        """Closes the hidraw file descriptor."""
        if self.fd is not None:
            try:
                os.close(self.fd)
            except OSError:
                pass
            self.fd = None

    def send_feature(self, data: bytes):
        """
        Sends a 64-byte payload using an unnumbered Feature Report (Report ID 0x00).
        """
        if self.fd is None:
            raise DeviceError("Device is not open.")

        buf = bytearray(65)
        buf[0] = 0x00 # Report ID
        for i, b in enumerate(data):
            if i + 1 < 65:
                buf[i + 1] = b

        try:
            fcntl.ioctl(self.fd, HIDIOCSFEATURE_65, buf)
        except OSError as e:
            raise DeviceError(f"Feature Report transmission failed on {self.path}: {e}")

    def get_feature(self) -> bytes:
        """
        Reads a 64-byte payload from the keyboard via Feature Report.
        """
        if self.fd is None:
            raise DeviceError("Device is not open.")

        buf = bytearray(65)
        buf[0] = 0x00 # Report ID

        try:
            fcntl.ioctl(self.fd, HIDIOCGFEATURE_65, buf)
            return bytes(buf[1:65])
        except OSError as e:
            raise DeviceError(f"Feature Report read failed on {self.path}: {e}")

    def __enter__(self) -> "Device":
        return self.open()

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close()
