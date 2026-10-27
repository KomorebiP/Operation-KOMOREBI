param(
    [ValidateSet("smoke", "standard", "confirmatory", "full")][string]$Preset = "standard",
    [ValidateSet("answer_only", "role_bind_augmented", "role_bind_scrambled", "state_supervised", "equivalence_regularized", "operator_regularized", "combined")][string]$Arm = "answer_only",
    [ValidateSet("auto", "cpu", "cuda")][string]$Device = "auto",
    [string]$RunDirectory = "",
    [string]$Checkpoint = "",
    [string]$DataDirectory = "",
    [string]$Python = "python",
    [string]$OutputRoot = "results",
    [string]$OutputDirectory = "",
    [int]$Seed = 1729,
    [switch]$Force
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
    $checkpointPath = Find-LabCheckpoint -RunDirectory $sourceRun -Preference "last" -Arm $Arm
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
$resumeDirectory = New-LabRunDirectory -OutputRoot $OutputRoot -Prefix ("resume_{0}_{1}" -f $Preset, $Arm) -OutputDirectory $OutputDirectory
$null = Start-LabTranscript -RunDirectory $resumeDirectory
try {
    Assert-LabPython -Python $Python
    Invoke-LabCli -Python $Python -CliArguments @("validate", "--config", $config, "--data-dir", $data, "--output-dir", $resumeDirectory)
    $arguments = @("train", "--config", $config, "--data-dir", $data, "--output-dir", $resumeDirectory, "--device", $Device, "--seed", $Seed, "--arm", $Arm, "--resume", $checkpointPath)
    if ($Force) { $arguments += "--force" }
    Invoke-LabCli -Python $Python -CliArguments $arguments
    Write-Host "Resumed training completed. Results: $resumeDirectory"
}
finally {
    Stop-LabTranscript
}
