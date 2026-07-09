# Nikon MV-1 to EXIF v1.0.0

**First public release** — apply exposure, date, and camera metadata from Nikon MV-1 text files to scanned TIFF images.

## Highlights

- **Desktop app** with a dark-themed PyQt6 UI for selecting MV-1 files, scan folders, and output location
- **EXIF writing** for standard tags: date/time, ISO, shutter speed, aperture, focal length, metering, flash, and more
- **XMP preservation** of every MV-1 CSV column in the custom `NMV1` namespace (`http://nikonmv1toexif/1.0/`)
- **Smart frame matching** by frame number in filenames, with alphabetical-order fallback
- **TIFF support** for `.tif` and `.tiff`, preserving original bit depth (8-bit and 16-bit)
- **Metadata viewer** — inspect EXIF and XMP on any TIFF before or after processing
- **Windows standalone build** — self-contained x64 `.exe` with no Python install required

## What's included

### Core workflow

1. Load an MV-1 `.txt` file (e.g. `n00032.txt`)
2. Select a folder of TIFF scans
3. Preview frame-to-file matches
4. Apply metadata in place or to an output folder

### Metadata written

**EXIF:** `DateTime`, `DateTimeOriginal`, `DateTimeDigitized`, `Make`, `Model`, `ISOSpeedRatings`, `ExposureTime`, `FNumber`, `FocalLength`, `MeteringMode`, `ExposureMode`, `Flash`, `UserComment`, and related fields.

**XMP:** One tag per MV-1 column (`Xmp.NMV1.FilmSpeed`, `Xmp.NMV1.FrameNumber`, `Xmp.NMV1.Aperture`, etc.).

### TIFF filename matching

Recognizes patterns like `frame_01.tif`, `001.tif`, `n00032_01.tif`, `scan-01.tiff`, and similar variants. If filenames contain no frame numbers, files are matched in alphabetical order to MV-1 frame order.

## Downloads

| Platform | Package |
|----------|---------|
| Windows x64 | `NikonMV1ToEXIF-win64.zip` — extract fully, then run `NikonMV1ToEXIF.exe` |

Keep `NikonMV1ToEXIF.exe` and the `_internal` folder together in the same directory.

### From source

Requires Python 3.12 (recommended via [uv](https://docs.astral.sh/uv/)):

```bash
uv sync
uv run nikon-mv1-to-exif
```

## Requirements

- **Windows x64** for the standalone build
- **Python 3.10+** (3.12 recommended) for running from source
- TIFF scans in `.tif` or `.tiff` format

## Testing

The release includes synthetic unit tests (no real scan files required) and sample data in `manual_test_data/` — 36 synthetic TIFFs plus a copy of `n00032.txt` for hands-on testing.

## Known limitations

- MV-1 text files and TIFF scans only; no RAW or JPEG output
- Frame matching by alphabetical order requires scan order to match MV-1 frame order
- Windows standalone build is x64 only

## Acknowledgements

Built with PyQt6, pyexiv2, and Pillow. Licensed under GPL-3.0 (see `LICENSE`).
