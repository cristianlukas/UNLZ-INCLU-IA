param(
  [switch]$SkipFfmpeg,
  [switch]$SkipWhisperCpp,
  [switch]$SkipBuildTools,
  [string]$WhisperCppModel = "base",
  [string]$WhisperCppDir = ""
)

$ErrorActionPreference = "Stop"

$RepoDir = Split-Path -Parent $PSScriptRoot
$SoftwareDir = Join-Path $RepoDir "software"
$VenvPython = Join-Path $SoftwareDir ".venv\Scripts\python.exe"
$EnvPath = Join-Path $SoftwareDir ".env"
$EnvExamplePath = Join-Path $SoftwareDir ".env.example"

if (-not $WhisperCppDir) {
  $WhisperCppDir = Join-Path $RepoDir "whisper.cpp"
}

function Require-Winget {
  if (-not (Get-Command winget -ErrorAction SilentlyContinue)) {
    throw "No se encontro winget. Instala winget o instala manualmente las dependencias faltantes."
  }
}

function Install-CommandIfMissing {
  param(
    [string]$Command,
    [string]$PackageId,
    [string]$DisplayName
  )

  if (Get-Command $Command -ErrorAction SilentlyContinue) {
    return
  }

  Require-Winget
  Write-Host "Instalando $DisplayName..."
  winget install --id $PackageId --exact
}

function Has-CppBuildTools {
  if (Get-Command cl -ErrorAction SilentlyContinue) {
    return $true
  }

  $VsWhere = "${env:ProgramFiles(x86)}\Microsoft Visual Studio\Installer\vswhere.exe"
  if (-not (Test-Path $VsWhere)) {
    return $false
  }

  $InstallPath = & $VsWhere -products * -requires Microsoft.VisualStudio.Component.VC.Tools.x86.x64 -property installationPath -latest
  return -not [string]::IsNullOrWhiteSpace($InstallPath)
}

function Install-CppBuildToolsIfMissing {
  if ($SkipBuildTools -or (Has-CppBuildTools)) {
    return
  }

  Require-Winget
  Write-Host "Instalando Visual Studio Build Tools para compilar whisper.cpp..."
  winget install --id Microsoft.VisualStudio.2022.BuildTools --exact --override "--quiet --wait --add Microsoft.VisualStudio.Workload.VCTools --includeRecommended"

  if (-not (Has-CppBuildTools)) {
    throw "No se detectaron herramientas C++ despues de instalar Build Tools. Cerrar y abrir PowerShell, o instalar Visual Studio Build Tools manualmente."
  }
}

function Set-DotEnvValue {
  param(
    [string]$Path,
    [string]$Key,
    [string]$Value
  )

  if (-not (Test-Path $Path)) {
    if (Test-Path $EnvExamplePath) {
      Copy-Item $EnvExamplePath $Path
    } else {
      New-Item -ItemType File -Path $Path | Out-Null
    }
  }

  $EscapedValue = $Value.Replace("\", "/")
  $Lines = Get-Content $Path
  $Pattern = "^$([regex]::Escape($Key))="
  $Replacement = "$Key=$EscapedValue"
  $Updated = $false

  $NewLines = foreach ($Line in $Lines) {
    if ($Line -match $Pattern) {
      $Updated = $true
      $Replacement
    } else {
      $Line
    }
  }

  if (-not $Updated) {
    $NewLines += $Replacement
  }

  Set-Content -Path $Path -Value $NewLines
}

function Find-WhisperStreamBinary {
  param([string]$BuildDir)

  $Candidates = @(
    (Join-Path $BuildDir "bin\Release\whisper-stream.exe"),
    (Join-Path $BuildDir "bin\whisper-stream.exe")
  )

  foreach ($Candidate in $Candidates) {
    if (Test-Path $Candidate) {
      return (Resolve-Path $Candidate).Path
    }
  }

  $Found = Get-ChildItem -Path $BuildDir -Recurse -Filter "whisper-stream.exe" -ErrorAction SilentlyContinue | Select-Object -First 1
  if ($Found) {
    return $Found.FullName
  }

  return $null
}

function Install-WhisperCpp {
  Install-CommandIfMissing -Command "git" -PackageId "Git.Git" -DisplayName "Git"
  Install-CommandIfMissing -Command "cmake" -PackageId "Kitware.CMake" -DisplayName "CMake"
  Install-CppBuildToolsIfMissing

  if (-not (Test-Path $WhisperCppDir)) {
    git clone https://github.com/ggml-org/whisper.cpp $WhisperCppDir
  } elseif (Test-Path (Join-Path $WhisperCppDir ".git")) {
    git -C $WhisperCppDir pull --ff-only
  }

  $BuildDir = Join-Path $WhisperCppDir "build"
  cmake -S $WhisperCppDir -B $BuildDir -DWHISPER_SDL2=ON
  cmake --build $BuildDir --config Release --target whisper-stream

  $WhisperBin = Find-WhisperStreamBinary -BuildDir $BuildDir
  if (-not $WhisperBin) {
    throw "No se encontro whisper-stream.exe despues de compilar whisper.cpp."
  }

  $ModelsDir = Join-Path $WhisperCppDir "models"
  New-Item -ItemType Directory -Force -Path $ModelsDir | Out-Null

  $ModelFile = "ggml-$WhisperCppModel.bin"
  $ModelPath = Join-Path $ModelsDir $ModelFile
  if (-not (Test-Path $ModelPath)) {
    $ModelUrl = "https://huggingface.co/ggerganov/whisper.cpp/resolve/main/$ModelFile"
    Write-Host "Descargando modelo $ModelFile..."
    Invoke-WebRequest -Uri $ModelUrl -OutFile $ModelPath
  }

  Set-DotEnvValue -Path $EnvPath -Key "INCLUIA_WCPP_BIN" -Value $WhisperBin
  Set-DotEnvValue -Path $EnvPath -Key "INCLUIA_WCPP_MODEL" -Value (Resolve-Path $ModelPath).Path

  return @{
    Bin = $WhisperBin
    Model = (Resolve-Path $ModelPath).Path
  }
}

if (-not $SkipFfmpeg) {
  Install-CommandIfMissing -Command "ffmpeg" -PackageId "Gyan.FFmpeg" -DisplayName "ffmpeg"
}

Set-Location $SoftwareDir

if (-not (Test-Path $VenvPython)) {
  python -m venv .venv
}

& $VenvPython -m pip install --upgrade pip
& $VenvPython -m pip install -r requirements.txt

if (-not $SkipWhisperCpp) {
  $WhisperCppInstall = Install-WhisperCpp
  Write-Host "whisper.cpp listo:"
  Write-Host "  Binario: $($WhisperCppInstall.Bin)"
  Write-Host "  Modelo: $($WhisperCppInstall.Model)"
}

$env:INCLUIA_FALLBACK_SIM = "0"

$env:INCLUIA_DRIVER = "faster_whisper"
& $VenvPython .\tools\check_stt_setup.py --json

if (-not $SkipWhisperCpp) {
  $env:INCLUIA_DRIVER = "whisper_cpp"
  & $VenvPython .\tools\check_stt_setup.py --json
}
