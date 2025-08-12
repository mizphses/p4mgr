"""Font management for OTF and other font formats."""

from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

from .constants import DisplayConstants
from .utils import hex_to_rgb


class FontManager:
    """Manages font loading and caching for display."""

    def __init__(self, font_dir: str | Path = "fonts"):
        """Initialize font manager.

        Args:
            font_dir: Directory containing font files.
        """
        self.font_dir = Path(font_dir)
        self.font_cache: dict[tuple[str, int], ImageFont.FreeTypeFont] = {}
        self.default_font = "ipag.ttf"
        self._default_font_loaded = False
        self._temp_image_cache: dict[int, Image.Image] = {}

    def get_font(
        self,
        font_name: str | None = None,
        size: int = DisplayConstants.DEFAULT_FONT_SIZE,
    ) -> ImageFont.FreeTypeFont:
        """Get font object with caching.

        Args:
            font_name: Font filename. Uses default if None.
            size: Font size in points.

        Returns:
            PIL ImageFont object.
        """
        if font_name is None:
            font_name = self.default_font

        cache_key = (font_name, size)
        if cache_key in self.font_cache:
            return self.font_cache[cache_key]

        font_path = self.font_dir / font_name
        if not font_path.exists():
            # Try system font directories
            system_font_paths = [
                Path("/usr/share/fonts/opentype/noto") / font_name,
                Path("/usr/share/fonts/truetype/noto") / font_name,
                Path("/usr/share/fonts/truetype/liberation")
                / "LiberationSans-Regular.ttf",
            ]

            for sys_path in system_font_paths:
                if sys_path.exists():
                    font_path = sys_path
                    break
            else:
                # Load default font only once
                if not self._default_font_loaded:
                    print(f"Font {font_name} not found in any location")
                    print(f"Searched paths: {self.font_dir / font_name}")
                    for sys_path in system_font_paths:
                        print(f"  - {sys_path}")
                    print("Using default font (limited character support)")
                    self._default_font_loaded = True

                font = ImageFont.load_default()
                self.font_cache[cache_key] = font
                return font

        # Load the font
        try:
            font = ImageFont.truetype(str(font_path), size, encoding="unicode")
            self.font_cache[cache_key] = font
            return font
        except Exception as e:
            print(f"Failed to load font {font_path}: {e}")
            font = ImageFont.load_default()
            self.font_cache[cache_key] = font
            return font

    def draw_text(
        self,
        image: Image.Image,
        text: str,
        position: tuple[int, int],
        font_name: str | None = None,
        size: int = DisplayConstants.DEFAULT_FONT_SIZE,
        color: str | tuple[int, int, int] = "#FFFFFF",
    ) -> None:
        """Draw text on image with specified font.

        Args:
            image: PIL Image to draw on.
            text: Text to draw.
            position: (x, y) position for text.
            font_name: Font filename.
            size: Font size.
            color: Text color (hex string or RGB tuple).
        """
        draw = ImageDraw.Draw(image)
        font = self.get_font(font_name, size)

        # Convert hex color to RGB if needed
        if isinstance(color, str):
            color = hex_to_rgb(color)

        # Disable font smoothing for sharper edges
        draw.fontmode = "1"  # Binary mode (no anti-aliasing)
        draw.text(position, text, font=font, fill=color)

    def get_text_size(
        self,
        text: str,
        font_name: str | None = None,
        size: int = DisplayConstants.DEFAULT_FONT_SIZE,
    ) -> tuple[int, int]:
        """Get the size of text when rendered.

        Args:
            text: Text to measure.
            font_name: Font filename.
            size: Font size.

        Returns:
            (width, height) of text bounding box.
        """
        font = self.get_font(font_name, size)
        # Use cached temporary image for measuring
        cache_key = size
        if cache_key not in self._temp_image_cache:
            self._temp_image_cache[cache_key] = Image.new("RGB", (1, 1))

        temp_img = self._temp_image_cache[cache_key]
        draw = ImageDraw.Draw(temp_img)

        try:
            bbox = draw.textbbox((0, 0), text, font=font)
            return bbox[2] - bbox[0], bbox[3] - bbox[1]
        except Exception:
            # Fallback for older PIL versions or edge cases
            return len(text) * int(size * 0.6), size
