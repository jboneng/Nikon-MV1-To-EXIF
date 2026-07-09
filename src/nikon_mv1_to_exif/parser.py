"""Parse Nikon MV-1 CSV-like metadata files."""

from __future__ import annotations

import csv
from dataclasses import dataclass
from io import StringIO
from pathlib import Path


@dataclass(frozen=True)
class MV1Header:
    film_speed: int
    film_number: int
    camera_id: str


@dataclass(frozen=True)
class FrameRecord:
    frame_number: int
    shutter_speed: int
    aperture: str
    focal_length: int
    lens_max_aperture: str
    metering_system: str
    exposure_mode: str
    flash_sync_mode: str
    exposure_compensation: float
    ev_difference: float
    flash_exposure_compensation: float
    speedlight_setting: str
    multiple_exposure: str
    lock: str
    vibration_reduction: str
    date: str
    time: str


@dataclass(frozen=True)
class MV1Data:
    header: MV1Header
    frames: tuple[FrameRecord, ...]


def _parse_float(value: str) -> float:
    return float(value.strip())


def _parse_int(value: str) -> int:
    return int(value.strip())


def parse_mv1_text(text: str) -> MV1Data:
    """Parse MV-1 file contents into structured metadata."""
    lines = [line.strip() for line in text.splitlines() if line.strip()]
    if len(lines) < 4:
        raise ValueError("MV-1 file must contain a header and at least one frame row")

    header_reader = csv.reader(StringIO("\n".join(lines[:2])))
    header_fields = next(header_reader)
    header_values = next(header_reader)
    if len(header_fields) != len(header_values):
        raise ValueError("MV-1 header row and value row have mismatched columns")

    header_map = dict(zip(header_fields, header_values))
    try:
        header = MV1Header(
            film_speed=_parse_int(header_map["Film speed"]),
            film_number=_parse_int(header_map["Film number"]),
            camera_id=header_map["Camera ID"].strip(),
        )
    except KeyError as exc:
        raise ValueError(f"Missing MV-1 header field: {exc.args[0]}") from exc

    frame_reader = csv.DictReader(StringIO("\n".join(lines[2:])))
    if frame_reader.fieldnames is None or "Frame number" not in frame_reader.fieldnames:
        raise ValueError("MV-1 frame section is missing required columns")

    frames: list[FrameRecord] = []
    for row in frame_reader:
        frames.append(
            FrameRecord(
                frame_number=_parse_int(row["Frame number"]),
                shutter_speed=_parse_int(row["Shutter speed"]),
                aperture=row["Aperture"].strip(),
                focal_length=_parse_int(row["Focal length"]),
                lens_max_aperture=row["Lens maximum aperture"].strip(),
                metering_system=row["Metering system"].strip(),
                exposure_mode=row["Exposure mode"].strip(),
                flash_sync_mode=row["Flash sync mode"].strip(),
                exposure_compensation=_parse_float(row["Exposure compensation value"]),
                ev_difference=_parse_float(row["EV difference in Manual"]),
                flash_exposure_compensation=_parse_float(
                    row["Flash exposure compensation value"]
                ),
                speedlight_setting=row["Speedlight setting"].strip(),
                multiple_exposure=row["Multiple exposure"].strip(),
                lock=row["Lock"].strip(),
                vibration_reduction=row["Vibration Reduction"].strip(),
                date=row["Date(yy/mm/dd)"].strip(),
                time=row["Time"].strip(),
            )
        )

    if not frames:
        raise ValueError("MV-1 file contains no frame records")

    return MV1Data(header=header, frames=tuple(frames))


def parse_mv1_file(path: Path | str) -> MV1Data:
    """Load and parse an MV-1 file from disk."""
    file_path = Path(path)
    text = file_path.read_text(encoding="utf-8-sig")
    return parse_mv1_text(text)
