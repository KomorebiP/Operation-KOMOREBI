$ErrorActionPreference = "Stop"
$ReleaseRoot = Split-Path -Parent $MyInvocation.MyCommand.Path
$PreviousPythonPath = $env:PYTHONPATH
$PreviousBytecodeSetting = $env:PYTHONDONTWRITEBYTECODE
$PythonCommand = if ($env:PYTHON) { $env:PYTHON } else { "python" }

function Invoke-Core05Python {
    param(
        [Parameter(Mandatory = $true)][string]$Script,
        [Parameter(Mandatory = $true)][string]$FailureMessage,
        [switch]$Quiet
    )
    if ($Quiet) {
        & $PythonCommand $Script | Out-Null
    } else {
        & $PythonCommand $Script
    }
    if ($LASTEXITCODE -ne 0) {
        throw $FailureMessage
    }
}

Push-Location $ReleaseRoot
try {
    $env:PYTHONDONTWRITEBYTECODE = "1"
    $ReferencePath = Join-Path $ReleaseRoot "reference"
    if ($PreviousPythonPath) {
        $env:PYTHONPATH = $ReferencePath + [IO.Path]::PathSeparator + $PreviousPythonPath
    } else {
        $env:PYTHONPATH = $ReferencePath
    }

    Invoke-Core05Python "reference/verify_core05_package.py" "Package integrity verification failed."
    Invoke-Core05Python "reference/generate_core05_evidence.py" "Core 0.5 conformance evidence regeneration failed." -Quiet
    Invoke-Core05Python "reference/generate_core05_bridge_report.py" "Core 0.5 Discovery Bridge verification failed." -Quiet
    Invoke-Core05Python "reference/generate_core05_focused_report.py" "Core 0.5 focused semantic gate failed." -Quiet
    Invoke-Core05Python "reference/generate_test_report.py" "Full test verification failed." -Quiet
    Invoke-Core05Python "reference/verify_core05_package.py" "Regenerated evidence differs from the manifest." -Quiet

    Write-Output "OSL-Core 0.5 offline verification passed."
} finally {
    if ($null -eq $PreviousPythonPath) {
        Remove-Item Env:PYTHONPATH -ErrorAction SilentlyContinue
    } else {
        $env:PYTHONPATH = $PreviousPythonPath
    }
    if ($null -eq $PreviousBytecodeSetting) {
        Remove-Item Env:PYTHONDONTWRITEBYTECODE -ErrorAction SilentlyContinue
    } else {
        $env:PYTHONDONTWRITEBYTECODE = $PreviousBytecodeSetting
    }
    Pop-Location
}
