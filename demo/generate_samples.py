#!/usr/bin/env python3
"""Generate demo audio samples for testing."""

import subprocess
import sys
from pathlib import Path

DEMO_DIR = Path(__file__).parent


def generate_good_interview():
    """Generate a clean interview audio."""
    output = DEMO_DIR / "good_interview.wav"
    subprocess.run(
        ["ffmpeg", "-f", "lavfi", "-i", "sine=frequency=440:duration=5",
         "-ar", "48000", "-y", str(output)],
        capture_output=True, check=True,
    )
    print(f"Created: {output}")


def generate_empty():
    """Generate an empty/silent file."""
    output = DEMO_DIR / "empty_file.wav"
    subprocess.run(
        ["ffmpeg", "-f", "lavfi", "-i", "anullsrc=r=48000:cl=mono", "-t", "3",
         "-acodec", "pcm_s16le", "-y", str(output)],
        capture_output=True, check=True,
    )
    print(f"Created: {output}")


def generate_corrupted():
    """Generate a corrupted file."""
    output = DEMO_DIR / "corrupted_noise.wav"
    with open(output, "wb") as f:
        f.write(b"RIFF" + b"\x00" * 100)  # Invalid WAV header
    print(f"Created: {output}")


def generate_muffled():
    """Generate a quiet/muffled file."""
    output = DEMO_DIR / "muffled_mic.wav"
    subprocess.run(
        ["ffmpeg", "-f", "lavfi", "-i", "sine=frequency=440:duration=3",
         "-af", "volume=0.05",
         "-ar", "48000", "-y", str(output)],
        capture_output=True, check=True,
    )
    print(f"Created: {output}")


def generate_video():
    """Generate a video with audio."""
    output = DEMO_DIR / "video_bad_audio.mp4"
    subprocess.run(
        ["ffmpeg", "-f", "lavfi", "-i", "sine=frequency=200:duration=2",
         "-f", "lavfi", "-i", "color=c=black:s=320x240:d=2",
         "-shortest", "-y", str(output)],
        capture_output=True, check=True,
    )
    print(f"Created: {output}")


def main():
    DEMO_DIR.mkdir(exist_ok=True)
    print("Generating demo samples...")
    generate_good_interview()
    generate_empty()
    generate_corrupted()
    generate_muffled()
    generate_video()
    print("Done!")


if __name__ == "__main__":
    main()
