param([string]$OutputDirectory = "artifacts\recomputed-research")
$ErrorActionPreference = "Stop"
$Root = Split-Path -Parent $PSScriptRoot
$Source = Join-Path $Root "research\original"
$Destination = if ([IO.Path]::IsPathRooted($OutputDirectory)) {
    [IO.Path]::GetFullPath($OutputDirectory)
} else {
    [IO.Path]::GetFullPath((Join-Path $Root $OutputDirectory))
}
if (-not (Test-Path -LiteralPath (Join-Path $Source "adaptive_multiscale_spd_final.py"))) {
    throw "Research regeneration requires the full source bundle containing research/original."
}
if (Test-Path -LiteralPath $Destination) {
    throw "The output directory already exists: $Destination. Choose a new directory to preserve earlier evidence."
}
$SourcePath = [IO.Path]::GetFullPath($Source).TrimEnd([IO.Path]::DirectorySeparatorChar)
if ($Destination.StartsWith($SourcePath + [IO.Path]::DirectorySeparatorChar, [StringComparison]::OrdinalIgnoreCase)) {
    throw "The output directory must be outside research/original."
}
New-Item -ItemType Directory -Path $Destination -Force | Out-Null
Get-ChildItem -LiteralPath $Source -Force | Copy-Item -Destination $Destination -Recurse -Force
function Invoke-NativeChecked {
    param([string]$Command, [string[]]$Arguments)
    & $Command @Arguments
    if ($LASTEXITCODE -ne 0) { throw "Command failed: $Command $($Arguments -join ' ')" }
}
Push-Location $Destination
try {
    Invoke-NativeChecked "python" @("adaptive_multiscale_spd_final.py", "--base", ".")
    Invoke-NativeChecked "python" @("aggregate_am_spd_final_results.py")
    Invoke-NativeChecked "python" @("am_spd_final_stress.py", "--base", ".", "--size", "32", "--budget", "720")
    Invoke-NativeChecked "python" @("am_spd_noise_stress_small.py")
    Invoke-NativeChecked "python" @("verify_am_spd_final.py")
    Invoke-NativeChecked "python" @("generate_am_spd_final_tables.py")
    Invoke-NativeChecked "python" @("generate_am_spd_final_figures.py")
    Invoke-NativeChecked "pdflatex" @("-interaction=nonstopmode", "-halt-on-error", "Projector_Resolved_Adaptive_Multiscale_Singular_Packet_Decomposition_Final.tex")
    Invoke-NativeChecked "pdflatex" @("-interaction=nonstopmode", "-halt-on-error", "Projector_Resolved_Adaptive_Multiscale_Singular_Packet_Decomposition_Final.tex")
    Invoke-NativeChecked "pdflatex" @("-interaction=nonstopmode", "-halt-on-error", "Projector_Resolved_Adaptive_Multiscale_Singular_Packet_Decomposition_Final.tex")
} finally {
    Pop-Location
}
