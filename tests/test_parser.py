"""Tests for MV-1 file parsing."""

import pytest

from nikon_mv1_to_exif.parser import parse_mv1_text


def test_parse_mv1_header_and_frames(sample_mv1_text: str) -> None:
    data = parse_mv1_text(sample_mv1_text)

    assert data.header.film_speed == 400
    assert data.header.film_number == 32
    assert data.header.camera_id == "000"
    assert len(data.frames) == 3

    first = data.frames[0]
    assert first.frame_number == 1
    assert first.shutter_speed == 100
    assert first.aperture == "F11"
    assert first.focal_length == 35
    assert first.date == "2026/06/08"
    assert first.time == "07:00"


def test_parse_mv1_rejects_empty_file() -> None:
    with pytest.raises(ValueError, match="at least one frame"):
        parse_mv1_text("Film speed,Film number,Camera ID\n400,32,000\n")
