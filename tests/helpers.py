"""Test helpers."""

from __future__ import annotations

from pathlib import Path

from PIL import Image


def create_synthetic_tiff(path: Path, *, color: tuple[int, int, int] = (128, 64, 32)) -> Path:
    """Create a minimal uncompressed TIFF for testing."""
    image = Image.new("RGB", (32, 24), color=color)
    path.parent.mkdir(parents=True, exist_ok=True)
    image.save(path, format="TIFF", compression="tiff_deflate")
    return path
