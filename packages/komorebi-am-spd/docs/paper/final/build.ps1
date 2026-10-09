$ErrorActionPreference = "Stop"
Set-Location $PSScriptRoot
latexmk -pdf -interaction=nonstopmode -halt-on-error Adaptive_Multiscale_Singular_Packet_Decomposition_Final.tex
if ($LASTEXITCODE -ne 0) { throw "LaTeX build failed with exit code $LASTEXITCODE" }
