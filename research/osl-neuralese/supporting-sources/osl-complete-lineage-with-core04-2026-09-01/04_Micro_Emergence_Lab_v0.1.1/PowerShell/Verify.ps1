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
if ($DataDirectory) {
    $data = Resolve-LabPath -Path $DataDirectory
}
else {
    $data = $sourceRun
}
if (-not (Test-Path -LiteralPath $data -PathType Container)) {
    throw "Data directory not found: $data"
}
$verificationDirectory = New-LabRunDirectory -OutputRoot $OutputRoot -Prefix ("verify_{0}" -f $Preset) -OutputDirectory $OutputDirectory
$null = Start-LabTranscript -RunDirectory $verificationDirectory
try {
    Assert-LabPython -Python $Python
    $arguments = @("verify", "--config", $config, "--data-dir", $data, "--output-dir", $verificationDirectory, "--device", $Device, "--seed", $Seed)
    if ($Checkpoint) {
        $arguments += @("--checkpoint", (Resolve-LabPath -Path $Checkpoint))
    }
    else {
        try {
            $arguments += @("--checkpoint", (Find-LabCheckpoint -RunDirectory $sourceRun))
        }
        catch {
        }
    }
    Invoke-LabCli -Python $Python -CliArguments $arguments
    Write-Host "Verification completed. Results: $verificationDirectory"
}
finally {
    Stop-LabTranscript
}
