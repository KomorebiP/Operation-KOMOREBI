param(
    [ValidateSet("smoke", "standard", "confirmatory", "full")][string]$Preset = "standard",
    [string]$Python = "python",
    [string]$OutputRoot = "results",
    [string]$OutputDirectory = "",
    [int]$Seed = 1729,
    [switch]$Force
)

. (Join-Path $PSScriptRoot "Common.ps1")
$config = Resolve-LabConfig -Preset $Preset
$runDirectory = New-LabRunDirectory -OutputRoot $OutputRoot -Prefix ("generate_{0}" -f $Preset) -OutputDirectory $OutputDirectory
$null = Start-LabTranscript -RunDirectory $runDirectory
try {
    Assert-LabPython -Python $Python
    $arguments = @("generate", "--config", $config, "--seed", $Seed, "--output-dir", $runDirectory)
    if ($Force) { $arguments += "--force" }
    Invoke-LabCli -Python $Python -CliArguments $arguments
    Invoke-LabCli -Python $Python -CliArguments @("validate", "--config", $config, "--data-dir", $runDirectory, "--output-dir", $runDirectory)
    Write-Host "Dataset generation and validation completed. Data: $runDirectory"
}
finally {
    Stop-LabTranscript
}
