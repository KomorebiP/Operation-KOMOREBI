$ErrorActionPreference = "Stop"
Set-StrictMode -Version Latest

$RootDir = $PSScriptRoot
$BuildDir = Join-Path $RootDir "build"
$Main = "Projector_Refinement_Physics_Covariant_Backreaction_Bridge"
$PythonBin = if ($env:PYTHON_BIN) { $env:PYTHON_BIN } else { "python" }

Set-Location $RootDir
$env:PYTHONDONTWRITEBYTECODE = "1"
if (-not $env:SOURCE_DATE_EPOCH) {
    $env:SOURCE_DATE_EPOCH = "1787097600"
}

if (-not (Get-Command $PythonBin -ErrorAction SilentlyContinue)) {
    throw "Python interpreter not found: $PythonBin"
}
if (-not (Get-Command "latexmk" -ErrorAction SilentlyContinue)) {
    throw "latexmk is required to build the manuscript."
}

New-Item -ItemType Directory -Force -Path $BuildDir | Out-Null
& $PythonBin ".\code\validate_release.py"
if ($LASTEXITCODE -ne 0) {
    throw "Pre-build release validation failed with exit code $LASTEXITCODE."
}

& latexmk `
    -pdf `
    -interaction=nonstopmode `
    -halt-on-error `
    -file-line-error `
    "-outdir=$BuildDir" `
    "$Main.tex"
if ($LASTEXITCODE -ne 0) {
    throw "LaTeX build failed with exit code $LASTEXITCODE."
}

& $PythonBin ".\code\validate_release.py" `
    --pdf (Join-Path $BuildDir "$Main.pdf") `
    --log (Join-Path $BuildDir "$Main.log")
if ($LASTEXITCODE -ne 0) {
    throw "Post-build release validation failed with exit code $LASTEXITCODE."
}
