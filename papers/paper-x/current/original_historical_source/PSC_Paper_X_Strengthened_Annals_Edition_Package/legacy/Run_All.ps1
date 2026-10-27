param(
    [string]$Work = $PSScriptRoot,
    [switch]$Update,
    [switch]$SkipPdf
)

$ErrorActionPreference = "Stop"
Set-Location $Work

$Packages = @(
    @{Name="numpy"; Import="numpy"},
    @{Name="sympy"; Import="sympy"},
    @{Name="matplotlib"; Import="matplotlib"},
    @{Name="pytest"; Import="pytest"},
    @{Name="setuptools"; Import="setuptools"},
    @{Name="wheel"; Import="wheel"},
    @{Name="pypdf"; Import="pypdf"},
    @{Name="Pillow"; Import="PIL"}
)

foreach ($Package in $Packages) {
    python -c "import importlib.util,sys;sys.exit(0 if importlib.util.find_spec('$($Package.Import)') else 1)"
    if ($LASTEXITCODE -ne 0) {
        python -m pip install $Package.Name
    } elseif ($Update) {
        python -m pip install --upgrade --upgrade-strategy only-if-needed $Package.Name
    }
}

python -m pytest -q
python .\scripts\generate_all.py
python .\scripts\scrub_assets.py
python .\scripts\make_contact_sheets.py .\figures .\Figure_Contact_Sheet.png --columns 4 --width 520
python -m pip wheel . --no-deps --no-build-isolation -w .\dist

if (-not $SkipPdf) {
    $Latex = Get-Command latexmk -ErrorAction SilentlyContinue
    if ($null -ne $Latex) {
        latexmk -pdf -interaction=nonstopmode -halt-on-error .\Projector_Resolved_Seed_Calculus_X.tex
        python .\scripts\scrub_pdf_metadata.py .\Projector_Resolved_Seed_Calculus_X.pdf `
            --title "Projector-Resolved Seed Calculus X" `
            --subject "Universal residual seeds, deformation forests, directed transport, seed zeta functions, companion completion, compatible carriers, and finite occupancy"
    } else {
        Write-Host "latexmk was not found; tests, results, figures, and wheel were generated."
    }
}
