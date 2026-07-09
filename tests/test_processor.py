"""Tests for frame-to-TIFF matching and end-to-end processing."""

from pathlib import Path
from unittest.mock import patch

import pytest

from nikon_mv1_to_exif.exif_builder import format_exif_datetime
from nikon_mv1_to_exif.matcher import FrameMatch, match_frames_to_tiffs
from nikon_mv1_to_exif.parser import parse_mv1_file
from nikon_mv1_to_exif.processor import (
    apply_exif_to_tiff,
    process_mv1_folder,
    read_exif_from_tiff,
    read_xmp_from_tiff,
)
from nikon_mv1_to_exif.xmp_builder import XMP_PREFIX
from tests.helpers import create_synthetic_tiff


def test_match_frames_by_filename(tiff_folder: Path, sample_mv1_path: Path) -> None:
    data = parse_mv1_file(sample_mv1_path)
    matches = match_frames_to_tiffs(data, tiff_folder)

    assert len(matches) == 3
    assert all(match.tiff_path is not None for match in matches)
    assert matches[0].match_method == "filename"
    assert matches[0].tiff_path.name == "frame_01.tif"


def test_match_frames_by_order_when_unnumbered(tmp_path: Path, sample_mv1_path: Path) -> None:
    folder = tmp_path / "ordered"
    folder.mkdir()
    create_synthetic_tiff(folder / "alpha.tif")
    create_synthetic_tiff(folder / "beta.tif")
    create_synthetic_tiff(folder / "gamma.tif")

    data = parse_mv1_file(sample_mv1_path)
    matches = match_frames_to_tiffs(data, folder)

    assert [match.frame.frame_number for match in matches] == [1, 2, 3]
    assert all(match.match_method == "order" for match in matches)


def test_process_mv1_folder_writes_exif(
    tiff_folder: Path,
    sample_mv1_path: Path,
    tmp_path: Path,
) -> None:
    output_dir = tmp_path / "output"
    data, matches, results = process_mv1_folder(
        sample_mv1_path,
        tiff_folder,
        output_dir=output_dir,
    )

    assert len(results) == 3
    assert all(result.success for result in results)

    first_output = output_dir / "frame_01.tif"
    assert first_output.exists()

    exif = read_exif_from_tiff(first_output)
    frame = data.frames[0]
    expected_datetime = format_exif_datetime(frame.date, frame.time)

    assert exif["Exif.Image.Make"] == "Nikon"
    assert exif["Exif.Photo.ISOSpeedRatings"] == "400"
    assert exif["Exif.Photo.ExposureTime"] == "1/100"
    assert exif["Exif.Photo.FNumber"] == "110/10"
    assert exif["Exif.Photo.DateTimeOriginal"] == expected_datetime


def test_process_mv1_folder_writes_xmp(
    tiff_folder: Path,
    sample_mv1_path: Path,
    tmp_path: Path,
) -> None:
    output_dir = tmp_path / "output"
    data, _, results = process_mv1_folder(
        sample_mv1_path,
        tiff_folder,
        output_dir=output_dir,
    )

    assert all(result.success for result in results)

    xmp = read_xmp_from_tiff(output_dir / "frame_01.tif")
    frame = data.frames[0]

    assert xmp[f"Xmp.{XMP_PREFIX}.FilmSpeed"] == "400"
    assert xmp[f"Xmp.{XMP_PREFIX}.FrameNumber"] == "01"
    assert xmp[f"Xmp.{XMP_PREFIX}.Aperture"] == frame.aperture
    assert xmp[f"Xmp.{XMP_PREFIX}.FlashSyncMode"] == frame.flash_sync_mode
    assert xmp[f"Xmp.{XMP_PREFIX}.VibrationReduction"] == frame.vibration_reduction


def test_apply_exif_moves_file_when_copy_fails_due_to_disk_space(
    sample_mv1_path: Path,
    tmp_path: Path,
) -> None:
    input_dir = tmp_path / "input"
    output_dir = tmp_path / "output"
    input_dir.mkdir()
    output_dir.mkdir()
    source = create_synthetic_tiff(input_dir / "frame_01.tif")

    data = parse_mv1_file(sample_mv1_path)
    match = FrameMatch(
        frame=data.frames[0],
        tiff_path=source,
        match_method="filename",
    )

    def fail_copy(_source: Path, _destination: Path) -> None:
        raise OSError(112, "There is not enough space on the disk")

    with patch("nikon_mv1_to_exif.processor.shutil.copy2", side_effect=fail_copy):
        result = apply_exif_to_tiff(
            source,
            data,
            match,
            output_dir=output_dir,
        )

    assert result.success
    assert "moved to output" in result.message
    assert (output_dir / "frame_01.tif").exists()
    assert not source.exists()
    assert read_exif_from_tiff(output_dir / "frame_01.tif")["Exif.Image.Make"] == "Nikon"


def test_process_reports_unmatched_frames(
    tmp_path: Path,
    sample_mv1_path: Path,
) -> None:
    folder = tmp_path / "single"
    folder.mkdir()
    create_synthetic_tiff(folder / "frame_01.tif")

    _, _, results = process_mv1_folder(sample_mv1_path, folder, output_dir=tmp_path / "out")
    successes = [result.success for result in results]
    assert successes.count(True) == 1
    assert successes.count(False) == 2
