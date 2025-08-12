"""
定数定義モジュール
ラズベリーパイの性能を考慮し、頻繁に参照される値は定数として事前定義
"""

class DisplayConstants:
    TYPE_BOX_DEFAULT_WIDTH = 40
    TYPE_BOX_TEXT_Y_OFFSET = 3
    TYPE_BOX_TEXT_SPACING = 15
    SCROLL_Y_OFFSET = 13
    SCROLL_SPEED = 2
    STATIC_TEXT_MAX_LENGTH = 7
    
    RENDER_FPS = 20
    FRAME_DURATION = 1.0 / RENDER_FPS
    
    DEFAULT_FONT_SIZE = 16
    
    DEFAULT_WHITE = (255, 255, 255)
    DEFAULT_BLACK = (0, 0, 0)
    DEFAULT_BACKGROUND = "#000000"


class MatrixConfig:
    DEFAULT_ROWS = 32
    DEFAULT_COLS = 64
    DEFAULT_CHAIN_LENGTH = 2
    DEFAULT_BRIGHTNESS = 80
    DEFAULT_HARDWARE_MAPPING = "adafruit-hat"
    
    GPIO_SLOWDOWN = 4


class InputConfig:
    DEVICE_RECONNECT_DELAY = 1.0
    KEYPAD_VENDOR_ID = 0x04d9
    KEYPAD_PRODUCT_ID = 0x1203
    
    KEY_MAPPINGS = {
        79: "1", 80: "2", 81: "3",
        75: "4", 76: "5", 77: "6", 
        71: "7", 72: "8", 73: "9",
        98: "0"
    }


COLOR_CACHE = {}