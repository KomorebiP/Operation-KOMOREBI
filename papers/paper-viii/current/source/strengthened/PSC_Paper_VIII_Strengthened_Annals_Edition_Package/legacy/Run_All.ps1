param(
    [string]$Work = $PSScriptRoot,
    [switch]$Update,
    [switch]$SkipPdf
)

$ErrorActionPreference = "Stop"
Set-Location $Work

$Packages = @("numpy", "scipy", "matplotlib", "pandas", "pytest", "setuptools", "wheel")
foreach ($Package in $Packages) {
    $ImportName = $Package
    python -c "import importlib.util,sys;sys.exit(0 if importlib.util.find_spec('$ImportName') else 1)"
    if ($LASTEXITCODE -ne 0) {
        python -m pip install $Package
    } elseif ($Update) {
        python -m pip install --upgrade --upgrade-strategy only-if-needed $Package
    }
}

python -m pytest -q
python .\scripts\generate_all.py --benchmark .\data\benchmark_results_sanitized.json --root $Work
python -m pip wheel . --no-deps --no-build-isolation -w .\dist

if (-not $SkipPdf) {
    $Latex = Get-Command latexmk -ErrorAction SilentlyContinue
    if ($null -ne $Latex) {
        latexmk -pdf -interaction=nonstopmode -halt-on-error .\Projector_Resolved_Seed_Calculus_VIII.tex
    } else {
        Write-Host "latexmk was not found; tests, results, figures, and wheel were generated."
    }
}
