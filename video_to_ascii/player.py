"""Terminal player module for ASCII video playback."""

import os
import sys
import time
import shutil
import fcntl
import termios
import tty
from typing import List, Optional, Tuple


class TerminalPlayer:
    """Plays ASCII art video in terminal."""

    def __init__(self, fps: float = 30.0):
        """Initialize the terminal player.

        Args:
            fps: Target frames per second. Default: 30.0
        """
        self.fps = fps
        self.frame_duration = 1.0 / fps
        self.terminal_width = 80
        self.terminal_height = 24
        self._update_terminal_size()

    def _update_terminal_size(self):
        """Update terminal size by querying the actual terminal."""
        # First try shutil
        try:
            size = shutil.get_terminal_size(fallback=(80, 24))
            self.terminal_width = size.columns
            self.terminal_height = size.lines
        except (AttributeError, OSError):
            pass

        # Try to get more accurate size using ioctl
        try:
            import io
            from os import environ

            def get_size():
                from os import popen
                try:
                    # Try using stty
                    output = popen('stty size', 'r').read().split()
                    if len(output) == 2:
                        return int(output[0]), int(output[1])
                except:
                    pass

                # Try using tput
                try:
                    output = popen('tput lines && tput cols', 'r').read().split()
                    if len(output) == 2:
                        return int(output[0]), int(output[1])
                except:
                    pass

                return None

            result = get_size()
            if result:
                self.terminal_height, self.terminal_width = result
        except:
            pass

    def _get_terminal_width(self) -> int:
        """Get terminal width in characters."""
        return self.terminal_width

    def _get_terminal_height(self) -> int:
        """Get terminal height in lines."""
        return self.terminal_height

    def get_terminal_size(self) -> Tuple[int, int]:
        """Get current terminal size.

        Returns:
            Tuple of (width, height) in characters.
        """
        self._update_terminal_size()
        return self.terminal_width, self.terminal_height

    def calculate_frame_size(self, video_width: int, video_height: int) -> tuple:
        """Calculate appropriate frame size for terminal.

        Args:
            video_width: Original video width in pixels.
            video_height: Original video height in pixels.

        Returns:
            Tuple of (width, height) in characters.
        """
        # Update terminal size first
        self._update_terminal_size()

        # Use 70% of terminal width to leave margin
        width = int(self.terminal_width * 0.7)

        # Calculate height to maintain aspect ratio
        # Characters are typically ~2x taller than wide
        aspect_ratio = video_height / video_width
        height = int(width * aspect_ratio * 0.5)

        # Ensure height fits in terminal (use 90% to leave room for cursor)
        max_height = int(self.terminal_height * 0.9)
        if height > max_height:
            height = max_height
            # Recalculate width based on height limit
            width = int(height / (aspect_ratio * 0.5))

        # Ensure minimum size
        width = max(width, 20)
        height = max(height, 10)

        return width, height

    def clear_screen(self):
        """Clear the terminal screen."""
        sys.stdout.write('\033[2J')
        sys.stdout.flush()

    def clear_line(self):
        """Clear the current line."""
        sys.stdout.write('\r\033[K')
        sys.stdout.flush()

    def move_to_top(self):
        """Move cursor to top of screen."""
        sys.stdout.write('\033[H')
        sys.stdout.flush()

    def render_frame(self, frame: str, max_lines: int = None):
        """Render a single ASCII frame.

        Args:
            frame: ASCII art string to display.
            max_lines: Maximum number of lines to display.
        """
        # Update terminal size
        self._update_terminal_size()

        # Limit lines if needed
        if max_lines is None:
            max_lines = self.terminal_height - 1

        lines = frame.split('\n')
        if len(lines) > max_lines:
            lines = lines[:max_lines]

        # Move to top and clear screen
        sys.stdout.write('\033[H\033[J')
        sys.stdout.write('\n'.join(lines))
        sys.stdout.flush()

    def play(self, frames: List[str], loop: bool = False):
        """Play ASCII frames in sequence.

        Args:
            frames: List of ASCII art strings.
            loop: Whether to loop playback indefinitely.
        """
        total_frames = len(frames)
        if total_frames == 0:
            print("No frames to play")
            return

        # Update terminal size and calculate max lines
        self._update_terminal_size()
        max_lines = self.terminal_height - 1

        frame_index = 0
        try:
            while True:
                self.render_frame(frames[frame_index], max_lines=max_lines)

                # Wait for next frame
                time.sleep(self.frame_duration)

                # Move to next frame
                frame_index += 1
                if frame_index >= total_frames:
                    if loop:
                        frame_index = 0
                    else:
                        break

        except KeyboardInterrupt:
            print("\nPlayback stopped by user")

    def play_with_progress(self, frames: List[str]):
        """Play ASCII frames with progress indicator.

        Args:
            frames: List of ASCII art strings.
        """
        total_frames = len(frames)
        if total_frames == 0:
            print("No frames to play")
            return

        # Update terminal size
        self._update_terminal_size()
        # Reserve 2 lines for progress info
        max_lines = self.terminal_height - 2

        try:
            for i, frame in enumerate(frames):
                # Add progress info to top
                progress = f"Frame {i + 1}/{total_frames} | Terminal: {self.terminal_width}x{self.terminal_height}"

                # Limit frame lines
                lines = frame.split('\n')
                if len(lines) > max_lines:
                    lines = lines[:max_lines]

                sys.stdout.write('\033[H\033[J')
                sys.stdout.write(progress + '\n')
                sys.stdout.write('\n'.join(lines))
                sys.stdout.flush()

                time.sleep(self.frame_duration)

        except KeyboardInterrupt:
            print("\nPlayback stopped by user")

    def set_fps(self, fps: float):
        """Set the playback frame rate.

        Args:
            fps: Frames per second.
        """
        self.fps = max(1.0, min(fps, 60.0))
        self.frame_duration = 1.0 / self.fps
