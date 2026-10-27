param(
    [ValidateSet("smoke", "standard", "confirmatory", "full")][string]$Preset = "standard",
    [ValidateSet("auto", "cpu", "cuda")][string]$Device = "auto",
    [string]$RunDirectory = "",
    [string]$Checkpoint = "",
    [string]$DataDirectory = "",
    [string]$Python = "python",
    [string]$OutputRoot = "results",
    [string]$OutputDirectory = "",
    [int]$Seed = 1729
)

. (Join-Path $PSScriptRoot "Common.ps1")
$config = Resolve-LabConfig -Preset $Preset
if ($RunDirectory) {
    $sourceRun = Resolve-LabPath -Path $RunDirectory
}
elseif ($DataDirectory) {
    $sourceRun = Resolve-LabPath -Path $DataDirectory
}
elseif ($Checkpoint) {
    $sourceRun = Split-Path -Parent (Resolve-LabPath -Path $Checkpoint)
}
else {
    $sourceRun = Find-LatestLabRunWithCheckpoint -OutputRoot $OutputRoot
}
if ($Checkpoint) {
    $checkpointPath = Resolve-LabPath -Path $Checkpoint
}
else {
    $checkpointPath = Find-LabCheckpoint -RunDirectory $sourceRun
}
if ($DataDirectory) {
    $data = Resolve-LabPath -Path $DataDirectory
}
else {
    $data = $sourceRun
}
if (-not (Test-Path -LiteralPath $checkpointPath -PathType Leaf)) {
    throw "Checkpoint not found: $checkpointPath"
}
if (-not (Test-Path -LiteralPath $data -PathType Container)) {
    throw "Data directory not found: $data"
}
$evaluationDirectory = New-LabRunDirectory -OutputRoot $OutputRoot -Prefix ("evaluate_{0}" -f $Preset) -OutputDirectory $OutputDirectory
$null = Start-LabTranscript -RunDirectory $evaluationDirectory
try {
    Assert-LabPython -Python $Python
    Invoke-LabCli -Python $Python -CliArguments @("evaluate", "--config", $config, "--data-dir", $data, "--checkpoint", $checkpointPath, "--output-dir", $evaluationDirectory, "--device", $Device, "--seed", $Seed)
    Invoke-LabCli -Python $Python -CliArguments @("quotient", "--config", $config, "--data-dir", $data, "--checkpoint", $checkpointPath, "--output-dir", $evaluationDirectory, "--device", $Device, "--seed", $Seed)
    Invoke-LabCli -Python $Python -CliArguments @("report", "--config", $config, "--data-dir", $data, "--checkpoint", $checkpointPath, "--output-dir", $evaluationDirectory, "--device", $Device, "--seed", $Seed)
    Write-Host "Evaluation, quotient analysis, and report completed. Results: $evaluationDirectory"
}
finally {
    Stop-LabTranscript
}
