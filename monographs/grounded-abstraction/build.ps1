$ErrorActionPreference = 'Stop'
Set-Location $PSScriptRoot
New-Item -ItemType Directory -Force -Path build | Out-Null
1..3 | ForEach-Object {
    & pdflatex -halt-on-error -interaction=nonstopmode -output-directory=build Grounded_Abstraction_v1.0.0.tex
    if ($LASTEXITCODE -ne 0) { throw 'LaTeX build failed.' }
}
Copy-Item build/Grounded_Abstraction_v1.0.0.pdf . -Force
