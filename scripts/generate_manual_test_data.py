"""Generate synthetic TIFFs for manual testing against n00032.txt."""

from __future__ import annotations

import shutil
from pathlib import Path

from PIL import Image, ImageDraw

PROJECT_ROOT = Path(__file__).resolve().parents[1]
OUTPUT_ROOT = PROJECT_ROOT / "manual_test_data"
TIFF_DIR = OUTPUT_ROOT / "tiffs"
SOURCE_MV1 = Path(r"c:\Users\jbone\Desktop\n00032.txt")
FRAME_COUNT = 36


def frame_color(frame_number: int) -> tuple[int, int, int]:
    hue = int(255 * (frame_number - 1) / FRAME_COUNT)
    return (
        max(40, hue),
        max(40, 180 - hue),
        max(40, (hue + 90) % 255),
    )


def create_frame_image(frame_number: int) -> Image.Image:
    image = Image.new("RGB", (640, 480), color=frame_color(frame_number))
    draw = ImageDraw.Draw(image)
    draw.rectangle([20, 20, 620, 460], outline="white", width=4)
    draw.text((240, 220), f"Frame {frame_number:02d}", fill="white")
    draw.text((180, 260), "Synthetic test scan", fill="white")
    return image


def generate_manual_test_data(
    *,
    output_root: Path = OUTPUT_ROOT,
    source_mv1: Path = SOURCE_MV1,
    frame_count: int = FRAME_COUNT,
) -> None:
    tiff_dir = output_root / "tiffs"
    tiff_dir.mkdir(parents=True, exist_ok=True)

    if source_mv1.is_file():
        shutil.copy2(source_mv1, output_root / source_mv1.name)
    else:
        fallback = PROJECT_ROOT / "tests" / "fixtures" / "sample_mv1.txt"
        if not fallback.is_file():
            raise FileNotFoundError(f"MV-1 source file not found: {source_mv1}")
        shutil.copy2(fallback, output_root / "n00032.txt")

    for frame_number in range(1, frame_count + 1):
        output_path = tiff_dir / f"frame_{frame_number:02d}.tif"
        create_frame_image(frame_number).save(
            output_path,
            format="TIFF",
            compression="tiff_deflate",
        )

    print(f"Wrote {frame_count} TIFFs to {tiff_dir}")
    print(f"MV-1 file at {output_root / 'n00032.txt'}")


if __name__ == "__main__":
    generate_manual_test_data()
