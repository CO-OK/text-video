# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

TextVideo is a Python-based terminal ASCII video player. It converts video files (MP4, MOV, AVI, etc.) into ASCII character art and plays them directly in the terminal.

## Running the Project

```bash
# Install dependencies
pip install -r requirements.txt

# Run with a video file
python main.py <video_file>

# Common options
python main.py video.mov --fps 24 --width 120    # specify fps and width
python main.py video.mov --contrast 1.5          # increase contrast
python main.py video.mov --loop                   # loop playback
python main.py video.mov --progress               # show frame progress
```

## CLI Arguments

| Argument | Short | Description | Default |
|----------|-------|-------------|---------|
| `video` | - | Video file path (required) | - |
| `--fps` | `-f` | Playback frames per second | 30 |
| `--width` | `-w` | ASCII width in characters | Auto-detect |
| `--charset` | `-c` | Character set (dark to light) | ` .:-=+*#%@` |
| `--contrast` | - | Contrast multiplier | 1.0 |
| `--loop` | `-l` | Loop playback | Off |
| `--progress` | `-p` | Show frame progress | Off |

## Architecture

The project uses a three-stage pipeline:

1. **VideoFrameExtractor** (`video_to_ascii/core.py`): Uses OpenCV to extract frames from video files
2. **AsciiConverter** (`video_to_ascii/converter.py`): Resizes frames, converts to grayscale, maps to charset characters
3. **TerminalPlayer** (`video_to_ascii/player.py`): Renders frames to terminal using ANSI escape sequences

Key details:
- Terminal character aspect ratio is ~0.5, so vertical dimension is scaled accordingly
- Contrast formula: `((pixels - 128) * contrast + 128)` with clipping to 0-255
- ANSI clear sequence: `\033[H\033[J` clears screen and moves cursor to home position
