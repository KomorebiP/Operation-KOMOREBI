param(
    [ValidateSet("auto", "cpu", "cuda")][string]$Device = "auto",
    [string]$Python = "python",
    [string]$OutputRoot = "results",
    [string]$OutputDirectory = ""
)

. (Join-Path $PSScriptRoot "Common.ps1")

$runDirectory = New-LabRunDirectory -OutputRoot $OutputRoot -Prefix "dependency_check" -OutputDirectory $OutputDirectory
$null = Start-LabTranscript -RunDirectory $runDirectory
try {
    Assert-LabPython -Python $Python
    Invoke-LabCli -Python $Python -CliArguments @("doctor", "--require-neural", "--device", $Device, "--output-dir", $runDirectory)
    Write-Host "Dependency check passed. Results: $runDirectory"
}
finally {
    Stop-LabTranscript
}
