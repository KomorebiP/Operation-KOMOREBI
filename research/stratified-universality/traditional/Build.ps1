param([switch]$FullRegression, [switch]$AuditOnly)
$ErrorActionPreference = "Stop"
Set-Location $PSScriptRoot

function Invoke-PythonChecked {
    param([Parameter(Mandatory = $true)][string]$Script, [string]$FailureMessage = "")
    & python $Script
    if ($LASTEXITCODE -ne 0) {
        if ([string]::IsNullOrWhiteSpace($FailureMessage)) { $FailureMessage = "Python step failed: $Script" }
        throw "$FailureMessage Exit code: $LASTEXITCODE"
    }
}

function Invoke-LatexChecked {
    param([Parameter(Mandatory = $true)][string[]]$Arguments, [string]$FailureMessage)
    & latexmk @Arguments
    if ($LASTEXITCODE -ne 0) { throw "$FailureMessage Exit code: $LASTEXITCODE" }
}

if ($FullRegression -and $AuditOnly) { throw "Choose either -FullRegression or -AuditOnly, not both." }

if ($FullRegression) {
    Invoke-PythonChecked ".\verify_block03_periodic_atlas.py"
    Invoke-PythonChecked ".\verify_block04_rational_mask_atlas.py"
    Invoke-PythonChecked ".\verify_block05_regular_atlas.py"
    Invoke-PythonChecked ".\verify_block06_integral_tower.py"
    Invoke-PythonChecked ".\verify_block07_product_multiplicative.py"
    Invoke-PythonChecked ".\verify_block08_local_polyphase.py"
    Invoke-PythonChecked ".\verify_block09_holonomic.py"
    Invoke-PythonChecked ".\verify_block10_algebraic.py"
    Invoke-PythonChecked ".\generate_figures.py"
    Invoke-PythonChecked ".\generate_block06_integral_figures.py"
    Invoke-PythonChecked ".\generate_block07_product_figures.py"
    Invoke-PythonChecked ".\generate_block08_local_figures.py"
    Invoke-PythonChecked ".\generate_block09_holonomic_figures.py"
    Invoke-PythonChecked ".\generate_block10_algebraic_figures.py"
} elseif ($AuditOnly) {
    Invoke-PythonChecked ".\verify_prior_regression_records.py"
    Invoke-PythonChecked ".\verify_recent_regression_records.py"
} else {
    Invoke-PythonChecked ".\verify_prior_regression_records.py"
}

if (-not $AuditOnly) {
    Invoke-PythonChecked ".\verify_block11_nonlinear_tree.py"
    Invoke-PythonChecked ".\verify_block12_galois_tannakian.py"
    Invoke-PythonChecked ".\verify_block13_bridge_synthesis.py"
    Invoke-PythonChecked ".\verify_block13_global_invariants.py"
    Invoke-PythonChecked ".\assemble_block13_outputs.py"
    Invoke-PythonChecked ".\generate_block11_nonlinear_figures.py"
    Invoke-PythonChecked ".\generate_block12_galois_figures.py"
    Invoke-PythonChecked ".\generate_block13_global_figures.py"
}

Invoke-PythonChecked ".\verify_block15_lane_transport.py" "Block 15 lane verifier failed."
Invoke-PythonChecked ".\verify_block16_holonomy_lane_transport.py" "Block 16 holonomy verifier failed."
Invoke-PythonChecked ".\generate_latex_components.py"
Invoke-PythonChecked ".\prepare_block14_publication.py"
Invoke-PythonChecked ".\generate_block14_publication_figure.py"

$Main = ".\Komorebi_Stratified_Universality_Foundations_v1.16.0_Block16.tex"
& latexmk -C $Main | Out-Null
Invoke-LatexChecked @("-silent", "-pdf", "-interaction=nonstopmode", "-halt-on-error", "-file-line-error", $Main) "Integrated manuscript build failed."
Invoke-PythonChecked ".\verify_block16_publication_audit.py" "Block 16 publication audit failed."
Invoke-LatexChecked @("-silent", "-pdf", "-interaction=nonstopmode", "-halt-on-error", "-file-line-error", $Main) "Integrated manuscript rebuild failed."
Invoke-PythonChecked ".\verify_block16_publication_audit.py" "Final Block 16 publication audit failed."

Push-Location "..\standalone"
try {
    $Standalone = ".\Holonomy_Twisted_Lane_Transport_and_Orbit_Descent.tex"
    & latexmk -C $Standalone | Out-Null
    Invoke-LatexChecked @("-silent", "-pdf", "-interaction=nonstopmode", "-halt-on-error", "-file-line-error", $Standalone) "Standalone theorem-note build failed."
} finally {
    Pop-Location
}
