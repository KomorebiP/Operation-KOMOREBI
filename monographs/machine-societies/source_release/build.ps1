$ErrorActionPreference = "Stop"
Set-Location $PSScriptRoot
if (-not (Get-Command latexmk -ErrorAction SilentlyContinue)) {
    throw "latexmk is required. Install TeX Live or MiKTeX with the declared packages."
}
New-Item -ItemType Directory -Force -Path "build" | Out-Null
& latexmk -pdf -interaction=nonstopmode -halt-on-error -outdir=build Machine_Societies_v1.0.0.tex
if ($LASTEXITCODE -ne 0) { throw "LaTeX build failed with exit code $LASTEXITCODE." }
Write-Output "Built: $PSScriptRoot\build\Machine_Societies_v1.0.0.pdf"
