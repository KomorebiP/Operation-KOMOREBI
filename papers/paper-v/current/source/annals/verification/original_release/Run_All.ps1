param(
    [string]$Work = $PSScriptRoot,
    [switch]$Update,
    [switch]$SkipPdf
)

$ErrorActionPreference = "Stop"
Set-Location $Work

function Test-PythonModule {
    param([string]$Name)
    & python -c "import importlib.util,sys; sys.exit(0 if importlib.util.find_spec('$Name') else 1)"
    return ($LASTEXITCODE -eq 0)
}

$Required = @(
    @{Module="numpy"; Package="numpy>=1.26"},
    @{Module="scipy"; Package="scipy>=1.11"},
    @{Module="matplotlib"; Package="matplotlib>=3.8"},
    @{Module="pytest"; Package="pytest>=8"}
)

if ($Update) {
    & python -m pip install --upgrade --upgrade-strategy only-if-needed @($Required.Package)
} else {
    $Missing = @()
    foreach ($Item in $Required) {
        if (-not (Test-PythonModule $Item.Module)) {
            $Missing += $Item.Package
        }
    }
    if ($Missing.Count -gt 0) {
        & python -m pip install --upgrade-strategy only-if-needed @Missing
    } else {
        Write-Host "Python dependencies already available; no installation performed."
    }
}

& python .\scripts\generate_all.py
& python -m pytest -q

if (-not $SkipPdf) {
    $Latexmk = Get-Command latexmk -ErrorAction SilentlyContinue
    if ($null -ne $Latexmk) {
        & latexmk -pdf -interaction=nonstopmode -halt-on-error .\Projector_Resolved_Seed_Calculus_V.tex
    } else {
        Write-Warning "latexmk was not found. Python results and tests completed; PDF compilation was skipped."
    }
}
