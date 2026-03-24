#!/usr/bin/env python3
"""Compress JPEG images in diary and gallery folders.

Strips EXIF data, resizes to max 1600px wide, and saves at 85% quality.
Skips images already under 200KB.
"""

import os
import sys
from PIL import Image

QUALITY = 85
MAX_WIDTH = 1600
SIZE_THRESHOLD = 200 * 1024  # skip files already under 200KB

DIRS = [
    "assets/images/diary",
    "assets/images/gallery",
]


def optimize_image(filepath):
    original_size = os.path.getsize(filepath)
    if original_size < SIZE_THRESHOLD:
        return 0  # already small enough

    try:
        img = Image.open(filepath)
    except Exception as e:
        print(f"  SKIP (cannot open): {filepath} — {e}")
        return 0

    # Convert RGBA to RGB for JPEG
    if img.mode in ("RGBA", "P"):
        img = img.convert("RGB")

    # Resize if wider than MAX_WIDTH
    w, h = img.size
    if w > MAX_WIDTH:
        ratio = MAX_WIDTH / w
        img = img.resize((MAX_WIDTH, int(h * ratio)), Image.LANCZOS)

    # Save without EXIF, at reduced quality
    img.save(filepath, "JPEG", quality=QUALITY, optimize=True)

    new_size = os.path.getsize(filepath)
    saved = original_size - new_size
    pct = (saved / original_size) * 100
    print(f"  {os.path.basename(filepath)}: {original_size // 1024}KB -> {new_size // 1024}KB ({pct:.0f}% saved)")
    return saved


def main():
    root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    total_saved = 0
    total_files = 0

    for d in DIRS:
        dirpath = os.path.join(root, d)
        if not os.path.isdir(dirpath):
            print(f"Directory not found: {dirpath}")
            continue

        print(f"\nOptimizing {d}/")
        for fname in sorted(os.listdir(dirpath)):
            fpath = os.path.join(dirpath, fname)
            if not os.path.isfile(fpath):
                continue
            ext = fname.lower().rsplit(".", 1)[-1] if "." in fname else ""
            if ext not in ("jpg", "jpeg", "png"):
                continue
            saved = optimize_image(fpath)
            total_saved += saved
            total_files += 1

    print(f"\n--- Done: {total_files} files processed, {total_saved // (1024 * 1024)}MB saved ---")


if __name__ == "__main__":
    main()
