# Build ZaloBot.exe (one file, windowed) with PyInstaller.
#   powershell -ExecutionPolicy Bypass -File src\pylos\gate\side_gate\desktop\packaging\build-exe.ps1
#   -NoCopy : do not copy the exe to the project root (next to userdata\)
# (ASCII only on purpose: Windows PowerShell 5.1 reads BOM-less files as ANSI.)
param([switch]$NoCopy)

$ErrorActionPreference = "Stop"
$root = $PSScriptRoot
while ($root -and -not (Test-Path (Join-Path $root "pyproject.toml"))) { $root = Split-Path -Parent $root }
if (-not $root) { throw "pyproject.toml not found above $PSScriptRoot" }
$python = Join-Path $root ".venv\Scripts\python.exe"
if (-not (Test-Path $python)) { throw "Missing .venv. See README.md, section 'Cai dat'." }

Write-Host "== Installing build dependencies"
& $python -m pip install --quiet -e "$root[desktop,build,personal]"
if ($LASTEXITCODE -ne 0) { throw "pip install failed" }

Write-Host "== Running PyInstaller (takes a few minutes)"
& $python -m PyInstaller --noconfirm --clean --log-level WARN `
    --distpath "$root\dist" --workpath "$root\build\pyinstaller" "$root\src\pylos\gate\side_gate\desktop\packaging\ZaloBot.spec"
if ($LASTEXITCODE -ne 0) { throw "PyInstaller failed" }

Write-Host "== Checking the build for secrets"
& $python "$root\src\pylos\gate\side_gate\desktop\packaging\check_secrets.py" "$root\dist\ZaloBot.exe" "$root\build"
if ($LASTEXITCODE -ne 0) { throw "Secret found in build output. Do NOT use or share this exe." }

if (-not $NoCopy) {
    # In the project root, next to userdata\, so the exe uses your current settings and data.
    try {
        Copy-Item "$root\dist\ZaloBot.exe" "$root\ZaloBot.exe" -Force
        Write-Host "== Done: $root\ZaloBot.exe"
    } catch {
        Write-Warning "Could not replace $root\ZaloBot.exe (is it running? Quit it from the tray first). New build: $root\dist\ZaloBot.exe"
    }
} else {
    Write-Host "== Done: $root\dist\ZaloBot.exe"
}
