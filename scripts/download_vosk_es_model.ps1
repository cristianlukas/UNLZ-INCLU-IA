param(
    [string]$OutputDir = "assets/models/vosk",
    [string]$Version = "vosk-model-small-es-0.42"
)

$ErrorActionPreference = "Stop"

if (-not (Test-Path $OutputDir)) {
    New-Item -ItemType Directory -Path $OutputDir -Force | Out-Null
}

$zipPath = Join-Path $OutputDir "$Version.zip"
$modelDir = Join-Path $OutputDir $Version

if (-not (Test-Path $zipPath)) {
    & curl.exe `
        -L `
        --retry 5 `
        --retry-delay 2 `
        --user-agent "UNLZ-INCLU-IA-vosk-fetch/1.0" `
        --output $zipPath `
        "https://alphacephei.com/vosk/models/$Version.zip"
}

if (-not (Test-Path $modelDir)) {
    Expand-Archive -Path $zipPath -DestinationPath $OutputDir -Force
}

Write-Host "[ok] modelo listo en $modelDir"
