"""Video frame extraction module."""

import cv2
import numpy as np
from typing import List, Optional


class VideoFrameExtractor:
    """Extracts frames from video files."""

    def __init__(self, video_path: str):
        """Initialize with video file path.

        Args:
            video_path: Path to the MP4 video file.
        """
        self.video_path = video_path
        self.cap: Optional[cv2.VideoCapture] = None
        self.fps: float = 0.0
        self.frame_count: int = 0
        self.width: int = 0
        self.height: int = 0

    def open(self) -> bool:
        """Open the video file.

        Returns:
            True if successful, False otherwise.
        """
        self.cap = cv2.VideoCapture(self.video_path)
        if not self.cap.isOpened():
            return False

        self.fps = self.cap.get(cv2.CAP_PROP_FPS)
        self.frame_count = int(self.cap.get(cv2.CAP_PROP_FRAME_COUNT))
        self.width = int(self.cap.get(cv2.CAP_PROP_FRAME_WIDTH))
        self.height = int(self.cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
        return True

    def extract_frame(self) -> Optional[np.ndarray]:
        """Extract a single frame from the video.

        Returns:
            Frame as numpy array (BGR format), or None if no more frames.
        """
        if self.cap is None or not self.cap.isOpened():
            return None

        ret, frame = self.cap.read()
        if not ret:
            return None

        return frame

    def extract_all_frames(self) -> List[np.ndarray]:
        """Extract all frames from the video.

        Returns:
            List of frames as numpy arrays.
        """
        frames = []
        while True:
            frame = self.extract_frame()
            if frame is None:
                break
            frames.append(frame)
        return frames

    def reset(self):
        """Reset video to the beginning."""
        if self.cap is not None:
            self.cap.set(cv2.CAP_PROP_POS_FRAMES, 0)

    def release(self):
        """Release video resources."""
        if self.cap is not None:
            self.cap.release()
            self.cap = None

    def __enter__(self):
        """Context manager entry."""
        self.open()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit."""
        self.release()
