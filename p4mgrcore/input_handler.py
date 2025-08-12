"""Handle USB numpad input for display control."""

import select
import threading
import time
from collections.abc import Callable

from evdev import InputDevice, categorize, ecodes, list_devices


class InputHandler:
    """Handles USB numpad input events."""

    def __init__(self, callback: Callable[[str], None], device_path: str | None = None):
        """Initialize input handler.

        Args:
            callback: Function to call with input string when Enter is pressed.
            device_path: Optional specific device path to use.
        """
        self.callback = callback
        self.device_path = device_path
        self.device: InputDevice | None = None
        self.current_input = ""
        self.running = False
        self._thread: threading.Thread | None = None
        self._direct_number_callback: Callable[[str], None] | None = None
        self._clear_callback: Callable[[], None] | None = None
        self._last_key = None
        self._last_key_time = 0
        self._key_repeat_count = 0
        self._repeat_threshold = 3  # Number of repeats to trigger clear

    def find_numpad(self) -> InputDevice | None:
        """Find USB numpad device.

        Returns:
            InputDevice instance or None if not found.
        """
        # If specific device path provided, use it
        if self.device_path:
            try:
                device = InputDevice(self.device_path)
                print(f"Using specified device: {device.name} at {self.device_path}")
                return device
            except Exception as e:
                print(f"Failed to open specified device {self.device_path}: {e}")

        try:
            # Try both standard list_devices and manual search
            device_paths = list_devices()
            if not device_paths:
                # Manually check common device paths
                import glob

                device_paths = glob.glob("/dev/input/event*")
                print(f"Manually found {len(device_paths)} devices in /dev/input/")
            else:
                print(f"Found {len(device_paths)} input devices")

            devices = []
            for path in device_paths:
                try:
                    device = InputDevice(path)
                    devices.append(device)
                    print(f"Device: {device.name} at {path}")
                except Exception as e:
                    print(f"Failed to access device at {path}: {e}")

            for device in devices:
                # Look for devices with numpad-like names or keyboards with numpad keys
                if any(
                    keyword in device.name.lower()
                    for keyword in [
                        "numpad",
                        "keypad",
                        "numeric",
                        "number",
                        "keyboard",
                        "touchpad",
                    ]
                ):
                    # Check if device has numpad keys
                    caps = device.capabilities()
                    if ecodes.EV_KEY in caps and ecodes.KEY_KP0 in caps[ecodes.EV_KEY]:
                        print(f"Found numpad device: {device.name}")
                        return device
                    else:
                        print(f"Device {device.name} has no numpad keys")

            # If no device with numpad keys found, show available devices
            print("No devices with numpad keys found.")
            print("Available input devices:")
            for device in devices:
                print(f"  - {device.name} ({device.path})")

        except Exception as e:
            print(f"Error finding devices: {e}")

        return None

    def start(self) -> bool:
        """Start listening for input.

        Returns:
            True if started successfully, False otherwise.
        """
        self.device = self.find_numpad()
        if not self.device:
            print("USB numpad not found. Please connect a USB numpad.")
            return False

        self.running = True
        self._thread = threading.Thread(target=self._input_loop)
        self._thread.daemon = True
        self._thread.start()
        return True

    def stop(self) -> None:
        """Stop listening for input."""
        self.running = False
        if self._thread and self._thread.is_alive():
            self._thread.join(timeout=1.0)
            if self._thread.is_alive():
                print("Warning: Input thread did not stop gracefully")
        if self.device:
            try:
                self.device.close()
            except Exception:
                pass

    def _input_loop(self) -> None:
        """Main input loop running in separate thread."""
        try:
            # Grab exclusive access to the device
            self.device.grab()

            while self.running:
                # Use select to check if data is available with timeout
                r, w, x = select.select([self.device.fd], [], [], 0.1)

                if not r:
                    continue

                for event in self.device.read():
                    if event.type == ecodes.EV_KEY:
                        key_event = categorize(event)
                        if key_event.keystate == key_event.key_down:
                            self._handle_key_press(key_event.keycode)
        except Exception as e:
            print(f"Input loop error: {e}")
        finally:
            try:
                self.device.ungrab()
            except Exception:
                pass

    def _handle_key_press(self, keycode: str) -> None:
        """Handle individual key press.

        Args:
            keycode: Key code string from evdev.
        """
        current_time = time.time()

        # Check for key repeat
        if self._last_key == keycode:
            if current_time - self._last_key_time < 0.3:  # 300ms threshold
                self._key_repeat_count += 1
            else:
                self._key_repeat_count = 1
        else:
            self._key_repeat_count = 1

        self._last_key = keycode
        self._last_key_time = current_time

        # Map numpad keys
        numpad_map = {
            "KEY_KP0": "0",
            "KEY_KP1": "1",
            "KEY_KP2": "2",
            "KEY_KP3": "3",
            "KEY_KP4": "4",
            "KEY_KP5": "5",
            "KEY_KP6": "6",
            "KEY_KP7": "7",
            "KEY_KP8": "8",
            "KEY_KP9": "9",
            "KEY_KPENTER": "ENTER",
            "KEY_KPDOT": ".",
            "KEY_KPPLUS": "+",
            "KEY_KPMINUS": "-",
            "KEY_KPASTERISK": "*",
            "KEY_KPSLASH": "/",
            "KEY_BACKSPACE": "BS",
        }

        if keycode in numpad_map:
            key = numpad_map[keycode]

            # Handle BS or Enter repeat for clear
            if (
                key == "BS" or key == "ENTER"
            ) and self._key_repeat_count >= self._repeat_threshold:
                if self._clear_callback:
                    print("Clearing display...")
                    self._clear_callback()
                self._key_repeat_count = 0
                return

            if key == "ENTER":
                if self.current_input:
                    # If input is a single digit, prepend 0
                    if len(self.current_input) == 1 and self.current_input.isdigit():
                        self.current_input = "0" + self.current_input
                    self.callback(self.current_input)
                    self.current_input = ""
            elif key == "BS":
                if self.current_input:
                    self.current_input = self.current_input[:-1]
                    print(f"Current input: {self.current_input}")
            elif key not in ["ENTER", "BS"]:
                self.current_input += key
                print(f"Current input: {self.current_input}")

    def clear_input(self) -> None:
        """Clear current input buffer."""
        self.current_input = ""

    def set_direct_number_callback(self, callback: Callable[[str], None]) -> None:
        """Set callback for direct number key switching.

        Args:
            callback: Function to call with number code (e.g., "01", "02").
        """
        self._direct_number_callback = callback

    def set_clear_callback(self, callback: Callable[[], None]) -> None:
        """Set callback for clearing display.

        Args:
            callback: Function to call when clear is triggered.
        """
        self._clear_callback = callback
