param(
    [string]$Work = $PSScriptRoot,
    [switch]$Update
)

$ErrorActionPreference = "Stop"
Set-Location $Work

if ($Update) {
    python -m pip install --upgrade --upgrade-strategy only-if-needed -r .\requirements.txt
}
else {
    $Missing = python -c "import importlib.util; mods=['numpy','scipy','matplotlib','pytest']; print('1' if any(importlib.util.find_spec(m) is None for m in mods) else '0')"
    if ($Missing.Trim() -eq "1") {
        python -m pip install -r .\requirements.txt
    }
}

python .\run_all.py
python -m pytest -q

if (Get-Command latexmk -ErrorAction SilentlyContinue) {
    latexmk -pdf -interaction=nonstopmode -halt-on-error .\Projector_Resolved_Seed_Calculus_VII.tex
}
