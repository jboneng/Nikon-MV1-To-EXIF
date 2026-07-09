"""Tests for XMP tag construction and writing."""

from nikon_mv1_to_exif.parser import parse_mv1_text
from nikon_mv1_to_exif.xmp_builder import XMP_PREFIX, build_xmp_tags


def test_build_xmp_tags_has_one_tag_per_mv1_column(sample_mv1_text: str) -> None:
    data = parse_mv1_text(sample_mv1_text)
    frame = data.frames[0]
    tags = build_xmp_tags(data, frame)

    expected_keys = {
        f"Xmp.{XMP_PREFIX}.FilmSpeed",
        f"Xmp.{XMP_PREFIX}.FilmNumber",
        f"Xmp.{XMP_PREFIX}.CameraID",
        f"Xmp.{XMP_PREFIX}.FrameNumber",
        f"Xmp.{XMP_PREFIX}.ShutterSpeed",
        f"Xmp.{XMP_PREFIX}.Aperture",
        f"Xmp.{XMP_PREFIX}.FocalLength",
        f"Xmp.{XMP_PREFIX}.LensMaximumAperture",
        f"Xmp.{XMP_PREFIX}.MeteringSystem",
        f"Xmp.{XMP_PREFIX}.ExposureMode",
        f"Xmp.{XMP_PREFIX}.FlashSyncMode",
        f"Xmp.{XMP_PREFIX}.ExposureCompensationValue",
        f"Xmp.{XMP_PREFIX}.EVDifferenceInManual",
        f"Xmp.{XMP_PREFIX}.FlashExposureCompensationValue",
        f"Xmp.{XMP_PREFIX}.SpeedlightSetting",
        f"Xmp.{XMP_PREFIX}.MultipleExposure",
        f"Xmp.{XMP_PREFIX}.Lock",
        f"Xmp.{XMP_PREFIX}.VibrationReduction",
        f"Xmp.{XMP_PREFIX}.Date",
        f"Xmp.{XMP_PREFIX}.Time",
    }

    assert set(tags) == expected_keys
    assert tags[f"Xmp.{XMP_PREFIX}.FilmSpeed"] == "400"
    assert tags[f"Xmp.{XMP_PREFIX}.FrameNumber"] == "01"
    assert tags[f"Xmp.{XMP_PREFIX}.Aperture"] == "F11"
    assert tags[f"Xmp.{XMP_PREFIX}.Date"] == "2026/06/08"
    assert tags[f"Xmp.{XMP_PREFIX}.Time"] == "07:00"
