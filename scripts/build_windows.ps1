# Build and verify a self-contained Windows x64 distribution with PyInstaller.
$ErrorActionPreference = "Stop"

$ProjectRoot = Resolve-Path (Join-Path $PSScriptRoot "..")
Set-Location $ProjectRoot

$DistDir = Join-Path $ProjectRoot "dist\NikonMV1ToEXIF-win64"
$ArchivePath = Join-Path $ProjectRoot "dist\NikonMV1ToEXIF-win64.zip"
$ExePath = Join-Path $DistDir "NikonMV1ToEXIF.exe"

function Stop-RunningApp {
    Get-Process NikonMV1ToEXIF -ErrorAction SilentlyContinue | Stop-Process -Force
    Start-Sleep -Seconds 1
}

function Invoke-Build([bool]$Console) {
    Stop-RunningApp
    if (Test-Path $DistDir) {
        Remove-Item $DistDir -Recurse -Force
    }

    if ($Console) {
        $env:BUILD_CONSOLE = "1"
    } else {
        $env:BUILD_CONSOLE = "0"
    }

    Write-Host "Building (console=$Console)..."
    uv run pyinstaller --noconfirm --clean "build\nikon_mv1_to_exif.spec"

    if (-not (Test-Path $ExePath)) {
        throw "Build failed: executable not found at $ExePath"
    }
}

Write-Host "Installing build dependencies..."
uv sync --extra build

# Anaconda DLLs on PATH (especially ICU) are collected into the bundle and break PyQt6.
$env:PATH = ($env:PATH -split ';' | Where-Object { $_ -and ($_ -notmatch 'anaconda3') }) -join ';'

Write-Host "Step 1/3: Console build for smoke test..."
Invoke-Build -Console $true

Write-Host "Step 2/3: Running smoke test..."
$SmokeOutput = & $ExePath --smoke-test 2>&1
$SmokeExitCode = $LASTEXITCODE
$SmokeText = ($SmokeOutput | Out-String)
$SmokeOutput | ForEach-Object { Write-Host $_ }
if ($SmokeExitCode -ne 0 -or ($SmokeText -notmatch "SMOKE_TEST_OK")) {
    throw "Smoke test failed."
}
Write-Host "Smoke test passed."

Write-Host "Step 3/3: Final windowed build..."
Invoke-Build -Console $false

Write-Host "Launching GUI smoke test..."
$GuiProcess = Start-Process -FilePath $ExePath -PassThru
Start-Sleep -Seconds 4
if ($GuiProcess.HasExited) {
    throw "GUI launch failed with exit code $($GuiProcess.ExitCode)."
}
Stop-Process -Id $GuiProcess.Id -Force
Write-Host "GUI launch passed."

Write-Host "Creating zip archive..."
if (Test-Path $ArchivePath) {
    Remove-Item $ArchivePath -Force
}
Compress-Archive -Path $DistDir -DestinationPath $ArchivePath

Write-Host ""
Write-Host "Build complete and verified."
Write-Host "Folder: $DistDir"
Write-Host "Zip:    $ArchivePath"
Write-Host "Run:    $ExePath"
