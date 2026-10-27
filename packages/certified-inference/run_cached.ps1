param(
  [string]$InputFile = "examples/adaptive_coordinate.json",
  [string]$OutputFile = "results/local_cached.json",
  [string]$LeanFile = "Komorebi/LocalCached.lean"
)
$ErrorActionPreference = "Stop"
Set-Location $PSScriptRoot
python checks/cached_posterior.py $InputFile --output $OutputFile --emit-lean $LeanFile --namespace LocalCached --try-precisions 4 12
if ($LASTEXITCODE -ne 0) { throw "The requested cached run did not complete. Read its result and error output." }
Write-Host "Provisional result produced. Compile the exported Lean instance with the pinned portable runtime to certify it."
