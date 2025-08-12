__version__ = "0.0.1"
__author__ = "Christoph Friedrich <christoph.friedrich@vonaffenfels.de>"

try:
    # Try to import compiled Cython module (for Raspberry Pi)
    from .core import FrameCanvas as FrameCanvas
    from .core import RGBMatrix as RGBMatrix
    from .core import RGBMatrixOptions as RGBMatrixOptions
except ImportError:
    # Fall back to Python mock implementation (for development)
    from .core import FrameCanvas as FrameCanvas
    from .core import RGBMatrix as RGBMatrix
    from .core import RGBMatrixOptions as RGBMatrixOptions
