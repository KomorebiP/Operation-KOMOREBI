param(
    [ValidateSet("smoke", "standard", "confirmatory", "full")][string]$Preset = "standard",
    [ValidateSet("answer_only", "role_bind_augmented", "role_bind_scrambled", "state_supervised", "equivalence_regularized", "operator_regularized", "combined")][string]$Arm = "answer_only",
    [ValidateSet("auto", "cpu", "cuda")][string]$Device = "auto",
    [string]$DataDirectory = "",
    [string]$Python = "python",
    [string]$OutputRoot = "results",
    [string]$OutputDirectory = "",
    [int]$Seed = 1729,
    [switch]$Force
)

. (Join-Path $PSScriptRoot "Common.ps1")
$config = Resolve-LabConfig -Preset $Preset
$runDirectory = New-LabRunDirectory -OutputRoot $OutputRoot -Prefix ("train_{0}_{1}" -f $Preset, $Arm) -OutputDirectory $OutputDirectory
$null = Start-LabTranscript -RunDirectory $runDirectory
try {
    Assert-LabPython -Python $Python
    if ($DataDirectory) {
        $data = Resolve-LabPath -Path $DataDirectory
        if (-not (Test-Path -LiteralPath $data -PathType Container)) {
            throw "Data directory not found: $data"
        }
    }
    else {
        $data = $runDirectory
        $generateArguments = @("generate", "--config", $config, "--seed", $Seed, "--output-dir", $data)
        if ($Force) { $generateArguments += "--force" }
        Invoke-LabCli -Python $Python -CliArguments $generateArguments
    }
    Invoke-LabCli -Python $Python -CliArguments @("validate", "--config", $config, "--data-dir", $data, "--output-dir", $runDirectory)
    $trainArguments = @("train", "--config", $config, "--data-dir", $data, "--output-dir", $runDirectory, "--device", $Device, "--seed", $Seed, "--arm", $Arm)
    if ($Force) { $trainArguments += "--force" }
    Invoke-LabCli -Python $Python -CliArguments $trainArguments
    Write-Host "Training completed. Results: $runDirectory"
}
finally {
    Stop-LabTranscript
}
