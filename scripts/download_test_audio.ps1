param(
    [string]$Manifest = "assets/test_audio/es/manifest.json",
    [string]$OutputDir = "assets/test_audio/es"
)

$ErrorActionPreference = "Stop"

if (-not (Test-Path $Manifest)) {
    throw "No existe el manifiesto: $Manifest"
}

if (-not (Test-Path $OutputDir)) {
    New-Item -ItemType Directory -Path $OutputDir -Force | Out-Null
}

$items = Get-Content $Manifest | ConvertFrom-Json

foreach ($item in $items) {
    $target = Join-Path $OutputDir $item.filename
    if (Test-Path $target) {
        Write-Host "[skip] $($item.filename)"
        continue
    }

    Write-Host "[down] $($item.filename)"
    & curl.exe `
        -L `
        --retry 5 `
        --retry-delay 2 `
        --user-agent "UNLZ-INCLU-IA-audio-fetch/1.0" `
        --output $target `
        $item.url

    Start-Sleep -Seconds 2
}

Write-Host "[ok] audios listos en $OutputDir"
