param(
  [switch]$SkipFfmpeg
)

$ErrorActionPreference = "Stop"

$RepoDir = Split-Path -Parent $PSScriptRoot
$SoftwareDir = Join-Path $RepoDir "software"
$VenvPython = Join-Path $SoftwareDir ".venv\Scripts\python.exe"

if (-not $SkipFfmpeg) {
  if (-not (Get-Command ffmpeg -ErrorAction SilentlyContinue)) {
    if (-not (Get-Command winget -ErrorAction SilentlyContinue)) {
      throw "No se encontro ffmpeg ni winget. Instala ffmpeg manualmente y volve a correr este script."
    }
    winget install Gyan.FFmpeg
    Write-Host "Si ffmpeg se instalo recien, cerra y abri PowerShell antes de validar."
  }
}

Set-Location $SoftwareDir

if (-not (Test-Path $VenvPython)) {
  python -m venv .venv
}

& $VenvPython -m pip install --upgrade pip
& $VenvPython -m pip install -r requirements.txt

$env:INCLUIA_DRIVER = "faster_whisper"
$env:INCLUIA_FALLBACK_SIM = "0"
& $VenvPython .\tools\check_stt_setup.py --json
