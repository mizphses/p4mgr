# -*- coding: utf-8 -*-
from __future__ import absolute_import

__version__ = "0.0.1"
__author__ = "Christoph Friedrich <christoph.friedrich@vonaffenfels.de>"

try:
    # Try to import compiled Cython module (for Raspberry Pi)
    from .core import RGBMatrix, FrameCanvas, RGBMatrixOptions
except ImportError:
    # Fall back to Python mock implementation (for development)
    from .core import RGBMatrix, FrameCanvas, RGBMatrixOptions
