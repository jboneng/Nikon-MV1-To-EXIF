"""Build EXIF metadata from MV-1 records."""

from __future__ import annotations

import math
import re
from datetime import datetime

from nikon_mv1_to_exif.parser import FrameRecord, MV1Data


def parse_aperture(value: str) -> float:
    """Convert values like 'F11' or 'F2.5' to an f-number."""
    cleaned = value.strip().upper()
    if cleaned.startswith("F"):
        cleaned = cleaned[1:]
    return float(cleaned)


def shutter_speed_to_exposure_time(shutter_speed: int) -> str:
    """MV-1 shutter speed is the denominator of the exposure fraction."""
    if shutter_speed <= 0:
        raise ValueError(f"Invalid shutter speed: {shutter_speed}")
    return f"1/{shutter_speed}"


def rational_to_string(numerator: int, denominator: int) -> str:
    return f"{numerator}/{denominator}"


def focal_length_to_string(focal_length: int) -> str:
    return rational_to_string(focal_length, 1)


def aperture_to_string(f_number: float) -> str:
    scaled = round(f_number * 10)
    return rational_to_string(scaled, 10)


def exposure_bias_to_string(ev: float) -> str:
    scaled = round(ev * 100)
    return rational_to_string(scaled, 100)


def max_aperture_to_string(f_number: float) -> str:
    apex = round(2.0 * math.log2(f_number) * 100)
    return rational_to_string(apex, 100)


def format_exif_datetime(date: str, time: str) -> str:
    """Convert MV-1 date/time to EXIF DateTime format."""
    parsed_date = datetime.strptime(date, "%Y/%m/%d")
    parsed_time = datetime.strptime(time, "%H:%M")
    combined = datetime.combine(parsed_date.date(), parsed_time.time())
    return combined.strftime("%Y:%m:%d %H:%M:%S")


def build_image_description(frame: FrameRecord, header_film_number: int) -> str:
    return (
        f"Nikon MV-1 frame {frame.frame_number:02d}, "
        f"film {header_film_number}, "
        f"1/{frame.shutter_speed} @ {frame.aperture}, "
        f"{frame.focal_length}mm"
    )


def build_exif_tags(data: MV1Data, frame: FrameRecord) -> dict[str, str]:
    """Create EXIF key/value pairs for pyexiv2."""
    f_number = parse_aperture(frame.aperture)
    max_f = parse_aperture(frame.lens_max_aperture)
    exif_datetime = format_exif_datetime(frame.date, frame.time)
    description = build_image_description(frame, data.header.film_number)

    tags = {
        "Exif.Image.Make": "Nikon",
        "Exif.Image.Model": f"MV-1 Camera {data.header.camera_id}",
        "Exif.Image.Software": "Nikon MV-1 to EXIF",
        "Exif.Image.DateTime": exif_datetime,
        "Exif.Image.ImageDescription": description,
        "Exif.Photo.DateTimeOriginal": exif_datetime,
        "Exif.Photo.DateTimeDigitized": exif_datetime,
        "Exif.Photo.ExposureTime": shutter_speed_to_exposure_time(frame.shutter_speed),
        "Exif.Photo.FNumber": aperture_to_string(f_number),
        "Exif.Photo.FocalLength": focal_length_to_string(frame.focal_length),
        "Exif.Photo.ISOSpeedRatings": str(data.header.film_speed),
        "Exif.Photo.ExposureBiasValue": exposure_bias_to_string(
            frame.exposure_compensation
        ),
        "Exif.Photo.MaxApertureValue": max_aperture_to_string(max_f),
        "Exif.Photo.MeteringMode": str(_metering_mode_value(frame.metering_system)),
        "Exif.Photo.ExposureMode": str(_exposure_mode_value(frame.exposure_mode)),
        "Exif.Photo.Flash": str(_flash_value(frame.flash_sync_mode, frame.speedlight_setting)),
        "Exif.Photo.UserComment": _build_user_comment(data, frame),
    }
    return tags


def _metering_mode_value(metering_system: str) -> int:
    normalized = metering_system.strip().lower()
    if "matrix" in normalized:
        return 5
    if "center" in normalized:
        return 2
    if "spot" in normalized:
        return 3
    return 0


def _exposure_mode_value(exposure_mode: str) -> int:
    mode = exposure_mode.strip().upper()
    if mode == "M":
        return 1
    if mode == "A":
        return 3
    if mode == "S":
        return 4
    if mode == "P":
        return 2
    return 0


def _flash_value(flash_sync_mode: str, speedlight_setting: str) -> int:
    del flash_sync_mode
    setting = speedlight_setting.strip().lower()
    if "no flash" in setting or setting == "none":
        return 32
    if "ttl" in setting:
        return 24
    return 16


def _build_user_comment(data: MV1Data, frame: FrameRecord) -> str:
    fields = [
        f"FilmSpeed={data.header.film_speed}",
        f"FilmNumber={data.header.film_number}",
        f"CameraID={data.header.camera_id}",
        f"Frame={frame.frame_number}",
        f"Metering={frame.metering_system}",
        f"ExposureMode={frame.exposure_mode}",
        f"FlashSync={frame.flash_sync_mode}",
        f"FlashComp={frame.flash_exposure_compensation}",
        f"EVDiff={frame.ev_difference}",
        f"Speedlight={frame.speedlight_setting}",
        f"MultipleExposure={frame.multiple_exposure}",
        f"Lock={frame.lock}",
        f"VR={frame.vibration_reduction}",
    ]
    return "; ".join(fields)


def extract_frame_number_from_filename(filename: str) -> int | None:
    """Try to extract a frame number from common TIFF naming patterns."""
    stem = filename.rsplit(".", 1)[0]
    patterns = [
        r"(?:^|[_\-])(\d{1,4})$",
        r"(?:frame|frm|img|scan)[_\-]?(\d{1,4})",
        r"^(\d{1,4})(?:[_\-]|$)",
    ]
    for pattern in patterns:
        match = re.search(pattern, stem, re.IGNORECASE)
        if match:
            return int(match.group(1))
    return None
