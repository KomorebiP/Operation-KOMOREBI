$ErrorActionPreference="Stop"
Set-Location (Split-Path -Parent $MyInvocation.MyCommand.Path)
latexmk -pdf -interaction=nonstopmode -halt-on-error -file-line-error Projector_Refinement_Physics_Volume_II.tex
