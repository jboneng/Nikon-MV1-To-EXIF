"""Shared pytest fixtures."""

from __future__ import annotations

from pathlib import Path

import pytest

from tests.helpers import create_synthetic_tiff


@pytest.fixture
def sample_mv1_text() -> str:
    return (FIXTURES_DIR / "sample_mv1.txt").read_text(encoding="utf-8")


@pytest.fixture
def sample_mv1_path() -> Path:
    return FIXTURES_DIR / "sample_mv1.txt"


FIXTURES_DIR = Path(__file__).parent / "fixtures"


@pytest.fixture
def tiff_folder(tmp_path: Path) -> Path:
    """Folder with three synthetic TIFFs named by frame number."""
    folder = tmp_path / "tiffs"
    folder.mkdir()
    colors = [(255, 0, 0), (0, 255, 0), (0, 0, 255)]
    for frame_number, color in enumerate(colors, start=1):
        create_synthetic_tiff(folder / f"frame_{frame_number:02d}.tif", color=color)
    return folder
