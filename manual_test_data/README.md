# Manual test data

Synthetic TIFF scans for testing the app against the example MV-1 file.

## Contents
- `n00032.txt` — copy of the example MV-1 metadata file (36 frames, film 32, ISO 400)
- `tiffs/frame_01.tif` … `frame_36.tif` — dummy 8-bit TIFF scans labeled by frame number

## Try it in the app

1. Launch the app: `uv run nikon-mv1-to-exif`
2. MV-1 file: select `manual_test_data/n00032.txt`
3. TIFF folder: select `manual_test_data/tiffs`
4. Output folder: choose a separate folder (for example `manual_test_data/output`) so originals stay untouched
5. Click **Preview Matches** — you should see all 36 frames matched by filename
6. Click **Apply EXIF**, then inspect a file with ExifTool or your image viewer

## Regenerate

```powershell
uv run python scripts/generate_manual_test_data.py
```
