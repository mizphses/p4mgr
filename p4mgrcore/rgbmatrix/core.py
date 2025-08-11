"""
Mock implementation of RGBMatrix for development/testing
This should be replaced with actual compiled Cython module on Raspberry Pi
"""


class RGBMatrixOptions:
    def __init__(self):
        self.rows = 32
        self.cols = 64
        self.chain_length = 1
        self.parallel = 1
        self.pwm_bits = 11
        self.pwm_lsb_nanoseconds = 130
        self.pwm_dither_bits = 0
        self.brightness = 100
        self.scan_mode = 0
        self.row_address_type = 0
        self.multiplexing = 0
        self.led_rgb_sequence = "RGB"
        self.pixel_mapper_config = ""
        self.panel_type = ""
        self.gpio_slowdown = 1
        self.disable_hardware_pulsing = False
        self.show_refresh_rate = False
        self.inverse_colors = False
        self.hardware_mapping = "adafruit-hat"
        self.limit_refresh_rate_hz = 0
        self.drop_privileges = True


class FrameCanvas:
    def __init__(self, matrix):
        self.matrix = matrix
        self.width = matrix.width
        self.height = matrix.height

    def SetPixel(self, x, y, red, green, blue):
        """Set a pixel at (x, y) with RGB values"""
        pass

    def Clear(self):
        """Clear the canvas"""
        pass

    def Fill(self, red, green, blue):
        """Fill the entire canvas with a color"""
        pass

    def SetImage(self, image, offset_x=0, offset_y=0, unsafe=True):
        """Set image on canvas (mock implementation)"""
        # In real implementation, this would copy the PIL image to the LED matrix
        print(
            f"Mock: Setting image with size {image.size} at offset ({offset_x}, {offset_y})"
        )
        pass


class RGBMatrix:
    def __init__(self, options=None):
        if options is None:
            options = RGBMatrixOptions()
        self.options = options
        self.width = options.cols * options.chain_length
        self.height = options.rows * options.parallel
        self.brightness = options.brightness

    def CreateFrameCanvas(self):
        """Create a new frame canvas"""
        return FrameCanvas(self)

    def SwapOnVSync(self, canvas, framerate_fraction=1):
        """Swap the canvas (mock implementation)"""
        return canvas

    def Clear(self):
        """Clear the matrix"""
        pass

    @property
    def luminanceCorrect(self):
        return True

    @luminanceCorrect.setter
    def luminanceCorrect(self, value):
        pass
