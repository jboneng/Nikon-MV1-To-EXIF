"""Apply MV-1 metadata as EXIF tags to TIFF images."""

from __future__ import annotations

import errno
import shutil
from dataclasses import dataclass
from pathlib import Path

from nikon_mv1_to_exif.runtime_bootstrap import prepare_pyexiv2_runtime

prepare_pyexiv2_runtime()
import pyexiv2

from nikon_mv1_to_exif.exif_builder import build_exif_tags
from nikon_mv1_to_exif.matcher import FrameMatch, match_frames_to_tiffs
from nikon_mv1_to_exif.parser import MV1Data, parse_mv1_file
from nikon_mv1_to_exif.xmp_builder import build_xmp_tags


@dataclass(frozen=True)
class ProcessResult:
    source_path: Path
    output_path: Path
    frame_number: int
    success: bool
    message: str


def _is_no_space_error(exc: OSError) -> bool:
    return exc.errno in {errno.ENOSPC, 112}


def _prepare_output_file(source_path: Path, output_path: Path) -> str:
    """Copy source to output, moving instead when disk space is insufficient."""
    if source_path.resolve() == output_path.resolve():
        return "updated in place"

    try:
        shutil.copy2(source_path, output_path)
        return "copied to output"
    except OSError as exc:
        if not _is_no_space_error(exc):
            raise
        shutil.move(source_path, output_path)
        return "moved to output (insufficient disk space to copy)"


def _resolve_output_path(
    source_path: Path,
    output_dir: Path | None,
    *,
    overwrite: bool,
) -> Path:
    if output_dir is None:
        return source_path
    output_dir.mkdir(parents=True, exist_ok=True)
    destination = output_dir / source_path.name
    if destination.exists() and not overwrite:
        raise FileExistsError(f"Output file already exists: {destination}")
    return destination


def apply_exif_to_tiff(
    tiff_path: Path,
    data: MV1Data,
    frame_match: FrameMatch,
    *,
    output_dir: Path | None = None,
    overwrite: bool = True,
) -> ProcessResult:
    """Write EXIF metadata from one MV-1 frame into a TIFF file."""
    if frame_match.tiff_path is None:
        return ProcessResult(
            source_path=tiff_path,
            output_path=tiff_path,
            frame_number=frame_match.frame.frame_number,
            success=False,
            message="No TIFF file matched to this frame",
        )

    try:
        output_path = _resolve_output_path(
            tiff_path, output_dir, overwrite=overwrite
        )
        transfer_message = "updated in place"
        if output_dir is not None and output_path != tiff_path:
            transfer_message = _prepare_output_file(tiff_path, output_path)

        tags = build_exif_tags(data, frame_match.frame)
        xmp_tags = build_xmp_tags(data, frame_match.frame)
        image = pyexiv2.Image(str(output_path))
        image.modify_exif(tags)
        image.modify_xmp(xmp_tags)
        image.close()

        return ProcessResult(
            source_path=tiff_path,
            output_path=output_path,
            frame_number=frame_match.frame.frame_number,
            success=True,
            message=f"EXIF and XMP metadata applied ({transfer_message})",
        )
    except Exception as exc:
        return ProcessResult(
            source_path=tiff_path,
            output_path=tiff_path,
            frame_number=frame_match.frame.frame_number,
            success=False,
            message=str(exc),
        )


def process_mv1_folder(
    mv1_path: Path,
    tiff_folder: Path,
    *,
    output_dir: Path | None = None,
    overwrite: bool = True,
) -> tuple[MV1Data, list[FrameMatch], list[ProcessResult]]:
    """Parse MV-1 data, match TIFFs, and apply EXIF to each matched pair."""
    data = parse_mv1_file(mv1_path)
    matches = match_frames_to_tiffs(data, tiff_folder)
    results: list[ProcessResult] = []

    for match in matches:
        if match.tiff_path is None:
            results.append(
                ProcessResult(
                    source_path=tiff_folder,
                    output_path=tiff_folder,
                    frame_number=match.frame.frame_number,
                    success=False,
                    message="No matching TIFF file found",
                )
            )
            continue
        results.append(
            apply_exif_to_tiff(
                match.tiff_path,
                data,
                match,
                output_dir=output_dir,
                overwrite=overwrite,
            )
        )

    return data, matches, results


def read_exif_from_tiff(tiff_path: Path) -> dict[str, str]:
    """Load EXIF from a TIFF file for verification in tests."""
    image = pyexiv2.Image(str(tiff_path))
    tags = image.read_exif()
    image.close()
    return tags


def read_xmp_from_tiff(tiff_path: Path) -> dict[str, str]:
    """Load XMP from a TIFF file for verification in tests."""
    image = pyexiv2.Image(str(tiff_path))
    tags = image.read_xmp()
    image.close()
    return tags
