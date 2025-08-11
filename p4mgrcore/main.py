"""Main entry point for P4Mgr LED Matrix Display Manager."""

import signal
import sys
import time
from pathlib import Path

from .rgbmatrix import RGBMatrix, RGBMatrixOptions

from .config import Config
from .display_templates import create_display_template
from .font_manager import FontManager
from .input_handler import InputHandler


class P4MgrApp:
    """Main application class for P4Mgr."""

    def __init__(self, config_file: str = "config.json", font_dir: str = "fonts", use_local: bool = False):
        """Initialize P4Mgr application.

        Args:
            config_file: Path to configuration JSON file.
            font_dir: Directory containing font files.
            use_local: Force use of local config file.
        """
        self.config = Config(config_file, use_local=use_local)
        self.font_manager = FontManager(font_dir)
        self.matrix = self._setup_matrix()
        self.input_handler = InputHandler(self.handle_input)
        self.input_handler.set_clear_callback(self.clear_display)
        self.current_display: str | None = None
        self.current_display_instance = None
        self._setup_signal_handlers()

    def _setup_matrix(self) -> RGBMatrix:
        """Configure and create RGB matrix.

        Returns:
            Configured RGBMatrix instance.
        """
        options = RGBMatrixOptions()

        # Configuration for 2x P4 32x64 panels
        options.rows = 32
        options.cols = 64
        options.chain_length = 2  # 2 panels chained
        options.parallel = 1
        options.hardware_mapping = "adafruit-hat"
        options.gpio_slowdown = 4
        options.brightness = 80
        options.show_refresh_rate = False
        options.disable_hardware_pulsing = True  # Avoid sound module conflict
        options.led_rgb_sequence = "RGB"  # Try different values: "RGB", "RBG", "GRB", "GBR", "BGR", "BRG"
        
        # P4 panel specific settings
        options.multiplexing = 0  # Try 0-8 if display is garbled
        options.row_address_type = 0  # Try 0-4 for different addressing
        options.panel_type = ""  # Try "FM6126A" or "FM6127" for some panels

        return RGBMatrix(options=options)

    def _setup_signal_handlers(self) -> None:
        """Set up signal handlers for graceful shutdown."""
        signal.signal(signal.SIGINT, self._signal_handler)
        signal.signal(signal.SIGTERM, self._signal_handler)

    def _signal_handler(self, sig: int, frame: object) -> None:
        """Handle shutdown signals."""
        print("\nShutting down...")
        self.cleanup()
        sys.exit(0)

    def handle_input(self, input_code: str) -> None:
        """Handle input from USB numpad.

        Args:
            input_code: Input code string (e.g., "01", "02").
        """
        print(f"Received input: {input_code}")

        # Reload configuration every time
        self.config.reload()

        # Get display configuration
        display_config = self.config.get_display_config(input_code)
        if not display_config:
            print(f"No configuration found for code: {input_code}")
            return

        # Stop current display if running
        if self.current_display_instance:
            self.current_display_instance.stop()
            self.current_display_instance = None

        # Clear current display
        self.matrix.Clear()

        # Create and render new display
        display = create_display_template(
            self.matrix, self.font_manager, display_config
        )
        if display:
            self.current_display = input_code
            self.current_display_instance = display
            try:
                display.render()
            except KeyboardInterrupt:
                # Allow interrupting long-running displays (like scrolling)
                display.stop()
        else:
            print(f"Unknown display type: {display_config.get('type')}")
    
    def clear_display(self) -> None:
        """Clear the current display."""
        # Stop current display if running
        if self.current_display_instance:
            self.current_display_instance.stop()
            self.current_display_instance = None
        
        # Clear display
        self.matrix.Clear()
        self.current_display = None
        print("Display cleared")

    def run(self) -> None:
        """Run the main application loop."""
        print("P4Mgr - LED Matrix Display Manager")
        print("==================================")

        # Create fonts directory if it doesn't exist
        Path(self.font_manager.font_dir).mkdir(exist_ok=True)

        # Start input handler
        if not self.input_handler.start():
            print("Failed to start input handler.")
            return

        print("Ready. Enter display codes on USB numpad.")
        print("Press Ctrl+C to exit.")

        try:
            # Keep main thread alive
            while True:
                time.sleep(1)
        except KeyboardInterrupt:
            pass

    def cleanup(self) -> None:
        """Clean up resources."""
        if self.current_display_instance:
            self.current_display_instance.stop()
        self.input_handler.stop()
        self.matrix.Clear()


def main():
    """Main entry point."""
    import argparse

    parser = argparse.ArgumentParser(description="P4Mgr - LED Matrix Display Manager")
    parser.add_argument(
        "-c",
        "--config",
        default="config.json",
        help="Path to configuration file (default: config.json)",
    )
    parser.add_argument(
        "-f",
        "--fonts",
        default="fonts",
        help="Path to fonts directory (default: fonts)",
    )
    parser.add_argument(
        "--local",
        action="store_true",
        help="Use local config file instead of remote API",
    )

    args = parser.parse_args()

    app = P4MgrApp(config_file=args.config, font_dir=args.fonts, use_local=args.local)
    app.run()
    app.cleanup()


if __name__ == "__main__":
    main()
