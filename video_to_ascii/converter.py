"""ASCII conversion module."""

import numpy as np
from PIL import Image
from typing import List


class AsciiConverter:
    """Converts images to ASCII art."""

    DEFAULT_CHARSET = " .:-=+*#%@"

    def __init__(self, charset: str = None, contrast: float = 1.0):
        """Initialize the ASCII converter.

        Args:
            charset: Characters from dark to light. Default: " .:-=+*#%@"
            contrast: Contrast multiplier. Default: 1.0
        """
        self.charset = charset or self.DEFAULT_CHARSET
        self.contrast = contrast

    def convert_frame(self, frame: np.ndarray, width: int) -> str:
        """Convert a video frame to ASCII art.

        Args:
            frame: Video frame in BGR format (numpy array).
            width: Target width in characters.

        Returns:
            ASCII art string representation of the frame.
        """
        # Convert BGR to RGB
        rgb_frame = frame[:, :, ::-1]

        # Create PIL Image
        img = Image.fromarray(rgb_frame)

        # Calculate height to maintain aspect ratio
        # Characters are typically ~2x taller than wide
        aspect_ratio = img.height / img.width
        height = int(width * aspect_ratio * 0.5)

        # Resize image
        img = img.resize((width, height), Image.Resampling.LANCZOS)

        # Convert to grayscale
        gray_img = img.convert('L')

        # Convert to numpy array
        pixels = np.array(gray_img)

        # Apply contrast adjustment
        if self.contrast != 1.0:
            pixels = ((pixels - 128) * self.contrast + 128)
            pixels = np.clip(pixels, 0, 255)

        # Map pixels to ASCII characters
        ascii_lines = []
        for row in pixels:
            line = ''.join(self._pixel_to_char(pixel) for pixel in row)
            ascii_lines.append(line)

        return '\n'.join(ascii_lines)

    def _pixel_to_char(self, gray_value: int) -> str:
        """Map a gray value (0-255) to an ASCII character.

        Args:
            gray_value: Gray value from 0 to 255.

        Returns:
            Corresponding ASCII character.
        """
        char_index = int(gray_value / 256 * len(self.charset))
        char_index = min(char_index, len(self.charset) - 1)
        return self.charset[char_index]

    def convert_image(self, image_path: str, width: int) -> str:
        """Convert an image file to ASCII art.

        Args:
            image_path: Path to the image file.
            width: Target width in characters.

        Returns:
            ASCII art string representation.
        """
        img = Image.open(image_path)
        img = img.convert('RGB')

        # Calculate height
        aspect_ratio = img.height / img.width
        height = int(width * aspect_ratio * 0.5)

        # Resize
        img = img.resize((width, height), Image.Resampling.LANCZOS)

        # Convert to grayscale
        gray_img = img.convert('L')
        pixels = np.array(gray_img)

        # Apply contrast
        if self.contrast != 1.0:
            pixels = ((pixels - 128) * self.contrast + 128)
            pixels = np.clip(pixels, 0, 255)

        # Map to ASCII
        ascii_lines = []
        for row in pixels:
            line = ''.join(self._pixel_to_char(pixel) for pixel in row)
            ascii_lines.append(line)

        return '\n'.join(ascii_lines)
