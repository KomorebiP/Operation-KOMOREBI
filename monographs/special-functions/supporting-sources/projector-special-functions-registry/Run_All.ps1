param(
    [switch]$CompilePdf,
    [switch]$Update
)

$ErrorActionPreference = "Stop"
$Work = Split-Path -Parent $MyInvocation.MyCommand.Path
Set-Location $Work

$Packages = @("numpy", "sympy", "mpmath", "matplotlib", "pytest")
foreach ($Package in $Packages) {
    $Installed = python -c "import importlib.util; raise SystemExit(0 if importlib.util.find_spec('$Package') else 1)" 2>$null
    if ($LASTEXITCODE -ne 0) {
        python -m pip install $Package
    } elseif ($Update) {
        python -m pip install --upgrade --upgrade-strategy only-if-needed $Package
    }
}

python .\run_all.py

if ($CompilePdf) {
    if (Get-Command latexmk -ErrorAction SilentlyContinue) {
        latexmk -pdf -interaction=nonstopmode -halt-on-error .\Projector_Special_Functions_Registry.tex
    } else {
        Write-Host "latexmk was not found; Python outputs and tests are complete."
    }
}
