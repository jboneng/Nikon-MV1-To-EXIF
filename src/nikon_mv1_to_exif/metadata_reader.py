"""Read and format TIFF metadata for display."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

from nikon_mv1_to_exif.runtime_bootstrap import prepare_pyexiv2_runtime

prepare_pyexiv2_runtime()
import pyexiv2


@dataclass(frozen=True)
class TiffMetadata:
    path: Path
    exif: dict[str, str]
    xmp: dict[str, str]


def format_metadata_value(value: object) -> str:
    """Convert EXIF/XMP values to a readable string."""
    if value is None:
        return ""
    if isinstance(value, dict):
        parts = [f"{key}: {inner}" for key, inner in value.items()]
        return "; ".join(parts)
    return str(value)


def normalize_metadata_tags(tags: dict[str, object]) -> dict[str, str]:
    """Sort and stringify metadata tag dictionaries."""
    return {
        key: format_metadata_value(value)
        for key, value in sorted(tags.items(), key=lambda item: item[0].lower())
    }


def read_metadata_from_tiff(tiff_path: Path) -> TiffMetadata:
    """Load EXIF and XMP metadata from a TIFF file."""
    image = pyexiv2.Image(str(tiff_path))
    try:
        exif = normalize_metadata_tags(image.read_exif())
        xmp = normalize_metadata_tags(image.read_xmp())
    finally:
        image.close()

    return TiffMetadata(path=tiff_path, exif=exif, xmp=xmp)
