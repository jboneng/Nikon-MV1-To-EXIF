"""Prepare the frozen runtime before importing PyQt or pyexiv2."""

from __future__ import annotations

import os
import sys

_qt_prepared = False
_pyexiv2_prepared = False


def _frozen_base_dir() -> str:
    return getattr(sys, "_MEIPASS", "")


def _add_dll_dirs(dll_dirs: list[str]) -> None:
    if sys.platform != "win32":
        return

    path_parts = [dll_dir for dll_dir in dll_dirs if os.path.isdir(dll_dir)]
    if not path_parts:
        return

    existing_path = os.environ.get("PATH", "")
    os.environ["PATH"] = os.pathsep.join(path_parts + ([existing_path] if existing_path else []))

    if hasattr(os, "add_dll_directory"):
        for dll_dir in path_parts:
            os.add_dll_directory(dll_dir)


def _fix_path_after_pyinstaller_hooks(base_dir: str, qt_bin: str, pyqt_dir: str) -> None:
    """PyInstaller's Qt hook prepends _MEIPASS, which can load conflicting ICU DLLs."""
    if sys.platform != "win32":
        return

    preferred = [qt_bin, pyqt_dir]
    existing = os.environ.get("PATH", "").split(os.pathsep)
    base_norm = os.path.normcase(os.path.normpath(base_dir))
    filtered: list[str] = []

    for entry in existing:
        if not entry:
            continue
        entry_norm = os.path.normcase(os.path.normpath(entry))
        if entry_norm == base_norm or entry in preferred:
            continue
        filtered.append(entry)

    os.environ["PATH"] = os.pathsep.join(preferred + filtered)


def prepare_frozen_runtime() -> None:
    """Ensure bundled Qt DLLs are discovered without loading pyexiv2 ICU copies."""
    global _qt_prepared

    if _qt_prepared or not getattr(sys, "frozen", False):
        return

    base_dir = _frozen_base_dir()
    if not base_dir:
        return

    qt_bin = os.path.join(base_dir, "PyQt6", "Qt6", "bin")
    pyqt_dir = os.path.join(base_dir, "PyQt6")
    _add_dll_dirs([qt_bin, pyqt_dir])
    _fix_path_after_pyinstaller_hooks(base_dir, qt_bin, pyqt_dir)

    plugins_dir = os.path.join(base_dir, "PyQt6", "Qt6", "plugins")
    if os.path.isdir(plugins_dir):
        os.environ.setdefault("QT_PLUGIN_PATH", plugins_dir)

    _qt_prepared = True


def prepare_pyexiv2_runtime() -> None:
    """Add pyexiv2's bundled DLL directory after Qt has been initialized."""
    global _pyexiv2_prepared

    if _pyexiv2_prepared or not getattr(sys, "frozen", False):
        return

    base_dir = _frozen_base_dir()
    if not base_dir:
        return

    pyexiv2_lib = os.path.join(base_dir, "pyexiv2", "lib")
    _add_dll_dirs([pyexiv2_lib])
    _pyexiv2_prepared = True


def run_smoke_test() -> int:
    """Verify bundled Qt and pyexiv2 can be imported in a frozen build."""
    prepare_frozen_runtime()

    from PyQt6.QtCore import QT_VERSION_STR

    prepare_pyexiv2_runtime()
    import pyexiv2

    print(f"PyQt6 {QT_VERSION_STR}")
    print(f"pyexiv2 {pyexiv2.__version__}")
    print("SMOKE_TEST_OK")
    return 0
