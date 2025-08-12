"""Display template implementations for LED matrix."""

import threading
import time
from abc import ABC, abstractmethod
from typing import Any

from PIL import Image, ImageDraw

from .constants import DisplayConstants
from .font_manager import FontManager
from .rgbmatrix import RGBMatrix
from .utils import calculate_scroll_positions, hex_to_rgb


class DisplayTemplate(ABC):
    """Base class for display templates."""

    def __init__(
        self, matrix: RGBMatrix, font_manager: FontManager, config: dict[str, Any]
    ):
        """Initialize display template.

        Args:
            matrix: RGB matrix instance.
            font_manager: Font manager instance.
            config: Display configuration dict.
        """
        self.matrix = matrix
        self.canvas = matrix.CreateFrameCanvas()
        self.font_manager = font_manager
        self.config = config
        self.canvas_width = matrix.width
        self.canvas_height = matrix.height
        self._stop_event = threading.Event()
        self._render_thread = None

    @abstractmethod
    def render(self) -> None:
        """Render the display template."""
        pass

    def clear(self) -> None:
        """Clear the display."""
        self.canvas.Clear()
        self.canvas = self.matrix.SwapOnVSync(self.canvas)

    def stop(self) -> None:
        """Stop the display rendering."""
        self._stop_event.set()
        if self._render_thread and self._render_thread.is_alive():
            self._render_thread.join(timeout=1.0)

    def _create_image(self) -> Image.Image:
        """Create a reusable image buffer."""
        return Image.new("RGB", (self.canvas_width, self.canvas_height))


class DestinationDisplay(DisplayTemplate):
    """Train destination display template."""
    
    def _get_type_text_size(self, text_length: int) -> int:
        """Calculate appropriate font size based on text length."""
        if text_length > 4:
            return 7
        elif text_length > 3:
            return 10
        return 14
    
    def _create_static_base_image(
        self, type_texts: list, type_text_font: str, type_text_color: str,
        type_box_width: int, dst_bg_color_rgb: tuple[int, int, int],
        dest_text: str, dest_font: str, dest_size: int, dest_color: str
    ) -> Image.Image:
        """Pre-render static elements for performance."""
        image = self._create_image()
        draw = ImageDraw.Draw(image)
        
        # Draw type box
        draw.rectangle(
            [(0, 0), (type_box_width, self.canvas_height)],
            fill=dst_bg_color_rgb,
        )
        
        # Draw type text
        y_offset = DisplayConstants.TYPE_BOX_TEXT_Y_OFFSET
        for text in type_texts:
            text_size = self._get_type_text_size(len(text))
            self.font_manager.draw_text(
                image,
                text,
                (4, y_offset),
                font_name=type_text_font,
                size=text_size,
                color=type_text_color,
            )
            y_offset += DisplayConstants.TYPE_BOX_TEXT_SPACING
        
        # Draw destination text
        dest_x = type_box_width + 4
        dest_y = 0
        self.font_manager.draw_text(
            image,
            dest_text,
            (dest_x, dest_y),
            font_name=dest_font,
            size=dest_size,
            color=dest_color,
        )
        
        return image

    def render(self) -> None:
        """Start rendering destination display in a separate thread."""
        self._stop_event.clear()
        self._render_thread = threading.Thread(target=self._render_loop)
        self._render_thread.daemon = True
        self._render_thread.start()

    def _render_loop(self) -> None:
        """Actual render loop running in separate thread."""
        # Extract configuration
        destination = self.config.get("destination", {})
        dest_text = destination.get("text", "")
        dest_color = destination.get("color", "#FFFFFF")
        dest_size = destination.get("size", 20)
        dest_font = destination.get("font", None)
        dst_bg_color = self.config.get("dstBgColor", "#FF0000")
        scroll_data = self.config.get("scroll", {})
        scroll_text = scroll_data.get("text", "")
        scroll_color = scroll_data.get("color", "#FFFFFF")
        scroll_size = scroll_data.get("size", 12)
        scroll_font = scroll_data.get("font", None)

        # Extract type box configuration
        type_box_config = self.config.get("typeBox", {})
        type_texts = type_box_config.get("texts", ["特急", "LTD.EXP"])
        type_text_color = type_box_config.get("color", "#FFFFFF")
        type_text_font = type_box_config.get("font", None)
        type_box_width = type_box_config.get("width", DisplayConstants.TYPE_BOX_DEFAULT_WIDTH)
        
        # Pre-convert colors to RGB for performance
        dst_bg_color_rgb = hex_to_rgb(dst_bg_color)

        # Create reusable image buffer
        image = self._create_image()
        draw = ImageDraw.Draw(image)
        
        # Set up scrolling text
        if scroll_text:
            scroll_y = self.canvas_height - DisplayConstants.SCROLL_Y_OFFSET
            scroll_width, _ = self.font_manager.get_text_size(
                scroll_text, font_name=scroll_font, size=scroll_size
            )

            # Check if text should be static
            if len(scroll_text) <= DisplayConstants.STATIC_TEXT_MAX_LENGTH:
                # Static display for short text

                # Draw type box (left side)
                draw.rectangle(
                    [(0, 0), (type_box_width, self.canvas_height)],
                    fill=dst_bg_color_rgb,
                )

                # Draw type text
                y_offset = DisplayConstants.TYPE_BOX_TEXT_Y_OFFSET
                for text in type_texts:
                    text_size = self._get_type_text_size(len(text))
                    self.font_manager.draw_text(
                        image,
                        text,
                        (4, y_offset),
                        font_name=type_text_font,
                        size=text_size,
                        color=type_text_color,
                    )
                    y_offset += DisplayConstants.TYPE_BOX_TEXT_SPACING

                # Draw destination text
                dest_x = type_box_width + 4
                dest_y = 0
                self.font_manager.draw_text(
                    image,
                    dest_text,
                    (dest_x, dest_y),
                    font_name=dest_font,
                    size=dest_size,
                    color=dest_color,
                )

                # Draw static scroll text
                static_x = type_box_width + 4
                self.font_manager.draw_text(
                    image,
                    scroll_text,
                    (static_x, scroll_y),
                    font_name=scroll_font,
                    size=scroll_size,
                    color=scroll_color,
                )

                # Update canvas once
                self.canvas.SetImage(image.convert("RGB"))
                self.canvas = self.matrix.SwapOnVSync(self.canvas)
                return

            # Pre-calculate scroll positions for performance
            scroll_positions = calculate_scroll_positions(
                scroll_width, self.canvas_width, DisplayConstants.SCROLL_SPEED
            )
            position_index = 0
            
            # Pre-render static elements
            static_base = self._create_static_base_image(
                type_texts, type_text_font, type_text_color,
                type_box_width, dst_bg_color_rgb,
                dest_text, dest_font, dest_size, dest_color
            )
            
            while not self._stop_event.is_set():
                # Copy pre-rendered static elements
                image = static_base.copy()
                draw = ImageDraw.Draw(image)

                # Get current scroll position
                scroll_x = scroll_positions[position_index]

                # Draw scrolling text with clipping to avoid type box area
                if (
                    scroll_x + scroll_width > type_box_width
                    or scroll_x > type_box_width
                ):
                    # Create a temporary image for scrolling text
                    temp_img = Image.new("RGB", (self.canvas_width, self.canvas_height))
                    self.font_manager.draw_text(
                        temp_img,
                        scroll_text,
                        (scroll_x, scroll_y),
                        font_name=scroll_font,
                        size=scroll_size,
                        color=scroll_color,
                    )
                    # Copy only pixels outside the type box area
                    for x in range(type_box_width, self.canvas_width):
                        for y in range(self.canvas_height):
                            pixel = temp_img.getpixel((x, y))
                            if pixel != (0, 0, 0):
                                image.putpixel((x, y), pixel)

                # Update canvas
                self.canvas.SetImage(image.convert("RGB"))
                self.canvas = self.matrix.SwapOnVSync(self.canvas)

                # Update position index
                position_index = (position_index + 1) % len(scroll_positions)

                time.sleep(DisplayConstants.FRAME_DURATION)
        else:
            # No scrolling text - just display static content
            image = Image.new("RGB", (self.canvas_width, self.canvas_height))
            draw = ImageDraw.Draw(image)

            # Draw type box (left side)
            draw.rectangle(
                [(0, 0), (type_box_width, self.canvas_height)],
                fill=self._hex_to_rgb(dst_bg_color),
            )

            # Draw type text (adjusted for 32px height)
            y_offset = 3
            text_size = 10 if len(type_texts) > 1 else 12
            for text in type_texts:
                self.font_manager.draw_text(
                    image,
                    text,
                    (4, y_offset),
                    font_name=type_text_font,
                    size=text_size,
                    color=type_text_color,
                )
                y_offset += 13

            # Draw destination text (large)
            dest_x = type_box_width + 4
            self.font_manager.draw_text(
                image,
                dest_text,
                (dest_x, 4),
                font_name=dest_font,
                size=24,
                color=dest_color,
            )

            self.canvas.SetImage(image.convert("RGB"))
            self.canvas = self.matrix.SwapOnVSync(self.canvas)


class TextDisplay(DisplayTemplate):
    """Static text display template."""

    def render(self) -> None:
        """Render centered static text."""
        # Create PIL image
        image = Image.new("RGB", (self.canvas_width, self.canvas_height))

        # Extract text configuration
        txt_config = self.config.get("txt", {})
        text = txt_config.get("text", "")
        color = txt_config.get("color", "#FFFFFF")
        size = txt_config.get("size", 16)
        font = txt_config.get("font", None)

        # Calculate text position for centering
        text_width, text_height = self.font_manager.get_text_size(
            text, font_name=font, size=size
        )
        x = (self.canvas_width - text_width) // 2
        y = (self.canvas_height - text_height) // 2 - 8

        # Draw text
        self.font_manager.draw_text(
            image, text, (x, y), font_name=font, size=size, color=color
        )

        # Update matrix
        self.canvas.SetImage(image.convert("RGB"))
        self.canvas = self.matrix.SwapOnVSync(self.canvas)


class ScrollingTextDisplay(DisplayTemplate):
    """Scrolling text display template."""

    def render(self) -> None:
        """Start rendering infinitely scrolling text in a separate thread."""
        self._stop_event.clear()
        self._render_thread = threading.Thread(target=self._render_loop)
        self._render_thread.daemon = True
        self._render_thread.start()

    def _render_loop(self) -> None:
        """Actual render loop running in separate thread."""
        # Create PIL image
        image = Image.new("RGB", (self.canvas_width, self.canvas_height))
        draw = ImageDraw.Draw(image)

        # Extract text configuration
        txt_config = self.config.get("txt", {})
        text = txt_config.get("text", "")
        color = txt_config.get("color", "#FFFFFF")
        size = txt_config.get("size", 16)
        font = txt_config.get("font", None)

        # Get text dimensions
        text_width, text_height = self.font_manager.get_text_size(
            text, font_name=font, size=size
        )
        y = (self.canvas_height - text_height) // 2

        # Add padding between repeats
        padding = 50
        full_width = text_width + padding

        # Scrolling animation
        x = self.canvas_width
        while not self._stop_event.is_set():
            # Clear image
            draw.rectangle(
                [(0, 0), (self.canvas_width, self.canvas_height)], fill=(0, 0, 0)
            )

            # Draw text (potentially multiple times for seamless loop)
            current_x = x
            while current_x < self.canvas_width:
                self.font_manager.draw_text(
                    image, text, (current_x, y), font_name=font, size=size, color=color
                )
                current_x += full_width

            # Update matrix
            self.canvas.SetImage(image.convert("RGB"))
            self.canvas = self.matrix.SwapOnVSync(self.canvas)

            # Update position
            x -= 2
            if x < -full_width:
                x = 0

            time.sleep(DisplayConstants.FRAME_DURATION)


def create_display_template(
    matrix: RGBMatrix, font_manager: FontManager, config: dict[str, Any]
) -> DisplayTemplate | None:
    """Factory function to create appropriate display template.

    Args:
        matrix: RGB matrix instance.
        font_manager: Font manager instance.
        config: Display configuration dict.

    Returns:
        Display template instance or None if type not recognized.
    """
    display_type = config.get("type")

    if display_type == "dest":
        return DestinationDisplay(matrix, font_manager, config)
    elif display_type == "textNsc":
        return TextDisplay(matrix, font_manager, config)
    elif display_type == "textScr":
        return ScrollingTextDisplay(matrix, font_manager, config)

    return None
