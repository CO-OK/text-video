#!/usr/bin/env python3
"""Terminal ASCII Video Player - Main Entry Point."""

import argparse
import sys

from video_to_ascii import VideoFrameExtractor, AsciiConverter, TerminalPlayer


def parse_args():
    """Parse command line arguments.

    Returns:
        Parsed arguments.
    """
    parser = argparse.ArgumentParser(
        description='Play MP4 video as ASCII art in terminal'
    )
    parser.add_argument(
        'video',
        help='Path to the MP4 video file'
    )
    parser.add_argument(
        '--fps', '-f',
        type=float,
        default=30.0,
        help='Playback frames per second (default: 30)'
    )
    parser.add_argument(
        '--width', '-w',
        type=int,
        default=None,
        help='Width of ASCII output in characters (default: auto-detect)'
    )
    parser.add_argument(
        '--charset', '-c',
        default=' .:-=+*#%@',
        help='Character set for ASCII mapping (default: " .:-=+*#%@")'
    )
    parser.add_argument(
        '--contrast',
        type=float,
        default=1.0,
        help='Contrast multiplier (default: 1.0)'
    )
    parser.add_argument(
        '--loop', '-l',
        action='store_true',
        help='Loop video playback'
    )
    parser.add_argument(
        '--progress', '-p',
        action='store_true',
        help='Show frame progress indicator'
    )

    return parser.parse_args()


def main():
    """Main entry point."""
    args = parse_args()

    # Open video file
    print(f"Opening video: {args.video}")
    extractor = VideoFrameExtractor(args.video)

    if not extractor.open():
        print(f"Error: Could not open video file: {args.video}", file=sys.stderr)
        sys.exit(1)

    print(f"Video info:")
    print(f"  Resolution: {extractor.width}x{extractor.height}")
    print(f"  FPS: {extractor.fps}")
    print(f"  Total frames: {extractor.frame_count}")

    # Get terminal size info
    player = TerminalPlayer(fps=args.fps)
    term_width, term_height = player.get_terminal_size()
    print(f"Terminal size: {term_width}x{term_height}")

    # Extract frames
    print("Extracting frames...")
    frames = extractor.extract_all_frames()
    extractor.release()

    if not frames:
        print("Error: No frames extracted from video", file=sys.stderr)
        sys.exit(1)

    print(f"Extracted {len(frames)} frames")

    # Initialize converter
    converter = AsciiConverter(charset=args.charset, contrast=args.contrast)

    # Calculate frame size
    if args.width:
        target_width = args.width
    else:
        target_width, target_height = player.calculate_frame_size(extractor.width, extractor.height)
        print(f"ASCII frame size: {target_width}x{target_height}")

    print(f"Converting to ASCII with width {target_width} characters...")

    # Convert frames to ASCII
    ascii_frames = []
    for i, frame in enumerate(frames):
        ascii_frame = converter.convert_frame(frame, target_width)
        ascii_frames.append(ascii_frame)

        # Show progress
        if (i + 1) % 100 == 0 or i + 1 == len(frames):
            print(f"  Converted {i + 1}/{len(frames)} frames")

    # Reinitialize player (to get latest terminal size)
    player = TerminalPlayer(fps=args.fps)

    print(f"\nPlaying at {args.fps} FPS...")
    print("Press Ctrl+C to stop")

    # Play frames
    if args.progress:
        player.play_with_progress(ascii_frames)
    else:
        player.play(ascii_frames, loop=args.loop)

    print("\nPlayback finished")


if __name__ == '__main__':
    main()
