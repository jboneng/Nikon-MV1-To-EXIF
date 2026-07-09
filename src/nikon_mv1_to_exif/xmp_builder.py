"""Build XMP metadata from MV-1 records."""

from __future__ import annotations

import pyexiv2

from nikon_mv1_to_exif.parser import FrameRecord, MV1Data

XMP_NAMESPACE = "http://nikonmv1toexif/1.0/"
XMP_PREFIX = "NMV1"
_NAMESPACE_REGISTERED = False


def ensure_xmp_namespace_registered() -> None:
    global _NAMESPACE_REGISTERED
    if not _NAMESPACE_REGISTERED:
        pyexiv2.registerNs(XMP_NAMESPACE, XMP_PREFIX)
        _NAMESPACE_REGISTERED = True


def _xmp_key(name: str) -> str:
    return f"Xmp.{XMP_PREFIX}.{name}"


def build_xmp_tags(data: MV1Data, frame: FrameRecord) -> dict[str, str]:
    """Create one XMP tag for each MV-1 CSV column."""
    ensure_xmp_namespace_registered()

    return {
        _xmp_key("FilmSpeed"): str(data.header.film_speed),
        _xmp_key("FilmNumber"): str(data.header.film_number),
        _xmp_key("CameraID"): data.header.camera_id,
        _xmp_key("FrameNumber"): f"{frame.frame_number:02d}",
        _xmp_key("ShutterSpeed"): str(frame.shutter_speed),
        _xmp_key("Aperture"): frame.aperture,
        _xmp_key("FocalLength"): str(frame.focal_length),
        _xmp_key("LensMaximumAperture"): frame.lens_max_aperture,
        _xmp_key("MeteringSystem"): frame.metering_system,
        _xmp_key("ExposureMode"): frame.exposure_mode,
        _xmp_key("FlashSyncMode"): frame.flash_sync_mode,
        _xmp_key("ExposureCompensationValue"): str(frame.exposure_compensation),
        _xmp_key("EVDifferenceInManual"): str(frame.ev_difference),
        _xmp_key("FlashExposureCompensationValue"): str(
            frame.flash_exposure_compensation
        ),
        _xmp_key("SpeedlightSetting"): frame.speedlight_setting,
        _xmp_key("MultipleExposure"): frame.multiple_exposure,
        _xmp_key("Lock"): frame.lock,
        _xmp_key("VibrationReduction"): frame.vibration_reduction,
        _xmp_key("Date"): frame.date,
        _xmp_key("Time"): frame.time,
    }
