param(
    [ValidateSet("auto", "cpu", "cuda")][string]$Device = "auto",
    [string]$Python = "python",
    [string]$OutputRoot = "results",
    [string]$OutputDirectory = "",
    [int]$Seed = 1729,
    [switch]$Force
)

. (Join-Path $PSScriptRoot "Common.ps1")
$config = Resolve-LabConfig -Preset "smoke"
$runDirectory = New-LabRunDirectory -OutputRoot $OutputRoot -Prefix "smoke" -OutputDirectory $OutputDirectory
$null = Start-LabTranscript -RunDirectory $runDirectory
try {
    Assert-LabPython -Python $Python
    $arguments = @("run-all", "--preset", "smoke", "--config", $config, "--device", $Device, "--seed", $Seed, "--output-dir", $runDirectory)
    if ($Force) { $arguments += "--force" }
    Invoke-LabCli -Python $Python -CliArguments $arguments
    $verifyArguments = @("verify", "--config", $config, "--data-dir", $runDirectory, "--output-dir", $runDirectory, "--device", $Device, "--seed", $Seed)
    try { $verifyArguments += @("--checkpoint", (Find-LabCheckpoint -RunDirectory $runDirectory)) } catch { }
    Invoke-LabCli -Python $Python -CliArguments $verifyArguments
    Invoke-LabCli -Python $Python -CliArguments @("report", "--config", $config, "--data-dir", $runDirectory, "--output-dir", $runDirectory, "--device", $Device, "--seed", $Seed)
    Write-Host "Smoke run completed. Results: $runDirectory"
}
finally {
    Stop-LabTranscript
}
