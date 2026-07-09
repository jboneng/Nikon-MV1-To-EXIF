"""Tests for metadata reading and formatting."""

from pathlib import Path

from nikon_mv1_to_exif.metadata_reader import (
    format_metadata_value,
    normalize_metadata_tags,
    read_metadata_from_tiff,
)
from nikon_mv1_to_exif.processor import process_mv1_folder


def test_format_metadata_value_handles_nested_xmp_dict() -> None:
    value = {'lang="x-default"': "frame 1"}
    assert format_metadata_value(value) == 'lang="x-default": frame 1'


def test_read_metadata_from_processed_tiff(
    tiff_folder: Path,
    sample_mv1_path: Path,
    tmp_path: Path,
) -> None:
    output_dir = tmp_path / "output"
    process_mv1_folder(sample_mv1_path, tiff_folder, output_dir=output_dir)

    metadata = read_metadata_from_tiff(output_dir / "frame_01.tif")

    assert metadata.path.name == "frame_01.tif"
    assert metadata.exif["Exif.Image.Make"] == "Nikon"
    assert metadata.xmp["Xmp.NMV1.Aperture"] == "F11"
    assert metadata.xmp["Xmp.NMV1.FrameNumber"] == "01"


def test_normalize_metadata_tags_sorts_keys() -> None:
    normalized = normalize_metadata_tags(
        {"Zebra": "z", "Alpha": {"lang": "test"}, "Middle": "m"}
    )
    assert list(normalized.keys()) == ["Alpha", "Middle", "Zebra"]
    assert normalized["Alpha"] == "lang: test"
