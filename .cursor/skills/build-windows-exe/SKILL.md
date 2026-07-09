---
name: build-windows-exe
description: Build and verify the self-contained Windows x64 PyInstaller distribution for Nikon MV-1 to EXIF. Use when the user asks to build, package, test, or fix the Windows exe, frozen build, PyInstaller bundle, or QtCore DLL errors.
---

# Build and Test Windows EXE

## Quick start

From the project root on Windows:

```powershell
powershell -ExecutionPolicy Bypass -File scripts/build_windows.ps1
```

This is the canonical pipeline. Do not hand-roll PyInstaller flags unless debugging.

**Outputs:**
- `dist/NikonMV1ToEXIF-win64/NikonMV1ToEXIF.exe` (with `_internal/`)
- `dist/NikonMV1ToEXIF-win64.zip`

## Prerequisites

- `uv` installed
- Python 3.12 (pinned via `.python-version`)
- Build deps: `uv sync --extra build` (the script runs this)

Dev/test before building:

```powershell
uv run pytest -q
uv run python -m nikon_mv1_to_exif --smoke-test   # dev only; frozen exe uses same flag
```

## Build pipeline (what the script does)

```
Task Progress:
- [ ] Step 1: Console build (`BUILD_CONSOLE=1`) for visible errors
- [ ] Step 2: Frozen smoke test (`NikonMV1ToEXIF.exe --smoke-test` → must print `SMOKE_TEST_OK`)
- [ ] Step 3: Windowed build (`BUILD_CONSOLE=0`) for distribution
- [ ] Step 4: GUI launch smoke test (process alive after 4s)
- [ ] Step 5: Create `dist/NikonMV1ToEXIF-win64.zip`
```

## Manual verification

After any build change, run these checks:

```powershell
# 1. Frozen import smoke test
& dist\NikonMV1ToEXIF-win64\NikonMV1ToEXIF.exe --smoke-test

# 2. ICU DLLs must NOT be in bundle root (they break Qt)
Test-Path dist\NikonMV1ToEXIF-win64\_internal\icuuc.dll   # expect False

# 3. GUI launches (or use the build script's GUI step)
Start-Process dist\NikonMV1ToEXIF-win64\NikonMV1ToEXIF.exe
```

Expected smoke output:

```
PyQt6 6.11.0
pyexiv2 2.15.5
SMOKE_TEST_OK
```

## Key files

| File | Role |
|------|------|
| `scripts/build_windows.ps1` | Full build + verify pipeline |
| `build/nikon_mv1_to_exif.spec` | PyInstaller spec; excludes ICU DLLs |
| `build/pyi_rth_qt_dll_path.py` | Runtime hook: Qt DLL dirs only |
| `src/nikon_mv1_to_exif/runtime_bootstrap.py` | Frozen PATH fixup; `--smoke-test` |
| `src/nikon_mv1_to_exif/__main__.py` | Calls bootstrap before PyQt import |

## Critical domain knowledge

### QtCore DLL failure (`The specified procedure could not be found`)

**Root cause:** Anaconda `icuuc.dll` / `icudt73.dll` get collected into `_internal/`. PyInstaller's `pyi_rth_pyqt6.py` prepends `_MEIPASS` to `PATH`, so Qt loads the wrong ICU and fails.

**Fixes already in repo (do not regress):**
1. `build/nikon_mv1_to_exif.spec` — `EXCLUDED_BINARY_NAMES` filters `icuuc.dll`, `icudt73.dll`
2. `scripts/build_windows.ps1` — strips `anaconda3` from `PATH` before PyInstaller runs
3. `runtime_bootstrap.py` — only adds `PyQt6/Qt6/bin` and `PyQt6` to PATH; removes `_MEIPASS` from PATH after PyInstaller hooks; loads pyexiv2 DLLs separately via `prepare_pyexiv2_runtime()`
4. pyexiv2 binaries collected under `pyexiv2/lib`, not bundle root

**If smoke test still fails:** check whether `dist/.../internal/icuuc.dll` exists. If yes, the spec filter or build PATH sanitization was bypassed.

### PowerShell smoke-test check

When validating output in PowerShell, coerce to string before `-match`:

```powershell
$SmokeText = ($SmokeOutput | Out-String)
if ($SmokeExitCode -ne 0 -or ($SmokeText -notmatch "SMOKE_TEST_OK")) { throw "Smoke test failed." }
```

Arrays break `-match` (non-matching lines are truthy).

### Anaconda vs uv Python

Dev and build must use uv's Python 3.12 (`.venv`), not Anaconda. Anaconda on PATH during build pollutes the bundle.

## Debugging a failed build

1. **Console build first** — set `$env:BUILD_CONSOLE = "1"` and run PyInstaller directly to see tracebacks
2. **Compare dev vs frozen** — `uv run python -m nikon_mv1_to_exif --smoke-test` should pass before debugging frozen
3. **Isolate ICU** — temporarily delete `_internal/icuuc.dll` and re-run `--smoke-test`; if it passes, fix spec/PATH collection
4. **Stop running exe** — build script kills `NikonMV1ToEXIF` processes; do the same if rebuild fails with file locks

```powershell
Get-Process NikonMV1ToEXIF -ErrorAction SilentlyContinue | Stop-Process -Force
```

## Distribution notes for users

- Extract the zip fully before running
- Keep `NikonMV1ToEXIF.exe` and `_internal/` together
- No Python install required on target machine

## When changing dependencies

If adding native DLL packages (especially anything shipping ICU/OpenSSL):

1. Rebuild and run `--smoke-test`
2. Confirm no conflicting DLLs land in `_internal/` root
3. Add module-level `prepare_pyexiv2_runtime()` (or equivalent) **before** importing the native package if it needs its own DLL subdirectory
