param(
    [string]$Work = $PSScriptRoot,
    [switch]$Update,
    [switch]$SkipPdf
)

$ErrorActionPreference = "Stop"
Set-Location $Work

$Modules = [ordered]@{
    "numpy" = "numpy"
    "scipy" = "scipy"
    "matplotlib" = "matplotlib"
    "pytest" = "pytest"
}

$Missing = @()
foreach ($Entry in $Modules.GetEnumerator()) {
    python -c "import $($Entry.Key)" 2>$null
    if ($LASTEXITCODE -ne 0) {
        $Missing += $Entry.Value
    }
}

if ($Update) {
    $Packages = @($Modules.Values)
    python -m pip install --upgrade --upgrade-strategy only-if-needed $Packages
} elseif ($Missing.Count -gt 0) {
    python -m pip install --upgrade-strategy only-if-needed $Missing
} else {
    Write-Host "All required Python packages are already available."
}

python .\run_all.py
python -m pytest -q

if (-not $SkipPdf) {
    if (Get-Command latexmk -ErrorAction SilentlyContinue) {
        latexmk -pdf -interaction=nonstopmode -halt-on-error .\Projector_Resolved_Seed_Calculus_VI.tex
    } else {
        Write-Host "latexmk was not found; Python results and tests completed, but the PDF was not rebuilt."
    }
}
