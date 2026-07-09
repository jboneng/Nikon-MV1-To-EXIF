"""Tests for EXIF tag construction."""

from nikon_mv1_to_exif.exif_builder import (
    build_exif_tags,
    extract_frame_number_from_filename,
    format_exif_datetime,
    parse_aperture,
    shutter_speed_to_exposure_time,
)
from nikon_mv1_to_exif.parser import parse_mv1_text


def test_aperture_and_shutter_helpers() -> None:
    assert parse_aperture("F11") == 11.0
    assert parse_aperture("F2.5") == 2.5
    assert shutter_speed_to_exposure_time(100) == "1/100"


def test_format_exif_datetime() -> None:
    assert format_exif_datetime("2026/06/08", "07:00") == "2026:06:08 07:00:00"


def test_extract_frame_number_from_filename() -> None:
    assert extract_frame_number_from_filename("frame_02.tif") == 2
    assert extract_frame_number_from_filename("001.tiff") == 1
    assert extract_frame_number_from_filename("scan-24.tif") == 24
    assert extract_frame_number_from_filename("photo.tif") is None


def test_build_exif_tags(sample_mv1_text: str) -> None:
    data = parse_mv1_text(sample_mv1_text)
    frame = data.frames[0]
    tags = build_exif_tags(data, frame)

    assert tags["Exif.Image.Make"] == "Nikon"
    assert tags["Exif.Photo.ExposureTime"] == "1/100"
    assert tags["Exif.Photo.FNumber"] == "110/10"
    assert tags["Exif.Photo.FocalLength"] == "35/1"
    assert tags["Exif.Photo.ISOSpeedRatings"] == "400"
    assert tags["Exif.Photo.DateTimeOriginal"] == "2026:06:08 07:00:00"
