"""Match MV-1 frame records to TIFF files in a folder."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

from nikon_mv1_to_exif.exif_builder import extract_frame_number_from_filename
from nikon_mv1_to_exif.parser import FrameRecord, MV1Data


TIFF_EXTENSIONS = {".tif", ".tiff"}


@dataclass(frozen=True)
class FrameMatch:
    frame: FrameRecord
    tiff_path: Path | None
    match_method: str


def list_tiff_files(folder: Path) -> list[Path]:
    files = [
        path
        for path in folder.iterdir()
        if path.is_file() and path.suffix.lower() in TIFF_EXTENSIONS
    ]
    return sorted(files, key=lambda p: p.name.lower())


def match_frames_to_tiffs(
    data: MV1Data,
    tiff_folder: Path,
    *,
    match_by_filename: bool = True,
    match_by_order: bool = True,
) -> list[FrameMatch]:
    """Match MV-1 frames to TIFF files using filename hints, then order."""
    tiff_files = list_tiff_files(tiff_folder)
    frame_by_number = {frame.frame_number: frame for frame in data.frames}
    used_files: set[Path] = set()
    matches: list[FrameMatch] = []

    if match_by_filename:
        for tiff_path in tiff_files:
            frame_number = extract_frame_number_from_filename(tiff_path.name)
            if frame_number is None or frame_number not in frame_by_number:
                continue
            if tiff_path in used_files:
                continue
            matches.append(
                FrameMatch(
                    frame=frame_by_number[frame_number],
                    tiff_path=tiff_path,
                    match_method="filename",
                )
            )
            used_files.add(tiff_path)

    matched_frame_numbers = {match.frame.frame_number for match in matches}
    remaining_frames = [
        frame for frame in data.frames if frame.frame_number not in matched_frame_numbers
    ]
    remaining_files = [path for path in tiff_files if path not in used_files]

    if match_by_order and remaining_frames and remaining_files:
        pair_count = min(len(remaining_frames), len(remaining_files))
        for index in range(pair_count):
            matches.append(
                FrameMatch(
                    frame=remaining_frames[index],
                    tiff_path=remaining_files[index],
                    match_method="order",
                )
            )

    matches.sort(key=lambda item: item.frame.frame_number)

    unmatched_frames = [
        frame
        for frame in data.frames
        if frame.frame_number not in {match.frame.frame_number for match in matches}
    ]
    for frame in unmatched_frames:
        matches.append(FrameMatch(frame=frame, tiff_path=None, match_method="unmatched"))

    return matches
