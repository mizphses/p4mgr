"""Main entry point for P4Mgr LED Matrix Display Manager."""

import signal
import sys
import time
from pathlib import Path

from .config import Config
from .constants import InputConfig, MatrixConfig
from .display_templates import create_display_template
from .exceptions import MatrixError
from .font_manager import FontManager
from .input_handler import InputHandler
from .rgbmatrix import RGBMatrix, RGBMatrixOptions
from .validators import quick_validate_config


class P4MgrApp:
    """Main application class for P4Mgr."""

    def __init__(
        self,
        config_file: str = "config.json",
        font_dir: str = "fonts",
        use_local: bool = False,
    ):
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

        # Check for custom matrix configuration
        matrix_config = self.config.config_data.get("matrix", {})

        # Apply configuration with defaults
        options.rows = matrix_config.get("rows", MatrixConfig.DEFAULT_ROWS)
        options.cols = matrix_config.get("cols", MatrixConfig.DEFAULT_COLS)
        options.chain_length = matrix_config.get(
            "chain_length", MatrixConfig.DEFAULT_CHAIN_LENGTH
        )
        options.parallel = matrix_config.get("parallel", 1)
        options.hardware_mapping = matrix_config.get(
            "hardware_mapping", MatrixConfig.DEFAULT_HARDWARE_MAPPING
        )
        options.gpio_slowdown = matrix_config.get(
            "gpio_slowdown", MatrixConfig.GPIO_SLOWDOWN
        )
        options.brightness = matrix_config.get(
            "brightness", MatrixConfig.DEFAULT_BRIGHTNESS
        )
        options.show_refresh_rate = False
        options.disable_hardware_pulsing = True  # Avoid sound module conflict
        options.led_rgb_sequence = matrix_config.get("led_rgb_sequence", "RGB")

        # P4 panel specific settings
        options.multiplexing = matrix_config.get("multiplexing", 0)
        options.row_address_type = matrix_config.get("row_address_type", 0)
        options.panel_type = matrix_config.get("panel_type", "")

        try:
            return RGBMatrix(options=options)
        except Exception as e:
            raise MatrixError(f"RGBMatrixの初期化に失敗しました: {e}") from e

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

        # Validate configuration
        errors = quick_validate_config({"displays": {input_code: display_config}})
        if errors:
            print(f"設定エラー: {', '.join(errors)}")
            return

        # Stop current display if running
        if self.current_display_instance:
            self.current_display_instance.stop()
            self.current_display_instance = None

        # Clear current display
        self.matrix.Clear()

        # Create and render new display
        try:
            display = create_display_template(
                self.matrix, self.font_manager, display_config
            )
            if display:
                self.current_display = input_code
                self.current_display_instance = display
                display.render()
            else:
                print(f"Unknown display type: {display_config.get('type')}")
        except Exception as e:
            print(f"表示エラー: {e}")
            self.clear_display()

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

        # Validate initial configuration
        errors = quick_validate_config(self.config.config_data)
        if errors:
            print("\n設定ファイルにエラーがあります:")
            for error in errors:
                print(f"  - {error}")
            print("\n設定を修正してください。")
            return

        # Create fonts directory if it doesn't exist
        Path(self.font_manager.font_dir).mkdir(exist_ok=True)

        # Start input handler
        if not self.input_handler.start():
            print("Failed to start input handler.")
            return

        print(f"\nMatrix: {self.matrix.width}x{self.matrix.height}")
        print(f"Config: {self.config.config_path}")
        print("\nReady. Enter display codes on USB numpad.")
        print("Press Ctrl+C to exit.")

        try:
            # Keep main thread alive with less frequent checks
            while True:
                time.sleep(InputConfig.DEVICE_RECONNECT_DELAY)
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
