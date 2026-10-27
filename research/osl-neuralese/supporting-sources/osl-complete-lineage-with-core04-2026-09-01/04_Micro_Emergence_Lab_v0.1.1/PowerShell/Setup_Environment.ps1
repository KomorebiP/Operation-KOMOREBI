param(
    [ValidateSet("Current", "Conda", "Venv")][string]$Environment = "Current",
    [ValidateSet("Minimal", "Full")][string]$Profile = "Full",
    [string]$CondaEnv = "komorebi-full",
    [string]$VenvPath = ".venv",
    [string]$Python = "python",
    [string]$Wheelhouse = "",
    [string]$OutputRoot = "results"
)

. (Join-Path $PSScriptRoot "Common.ps1")

if ($Environment -ne "Conda") {
    $Python = Resolve-LabPython -Python $Python
}

$runDirectory = New-LabRunDirectory -OutputRoot $OutputRoot -Prefix "setup"
$null = Start-LabTranscript -RunDirectory $runDirectory
try {
    $requirementsName = "requirements.txt"
    if ($Profile -eq "Minimal") {
        $requirementsName = "requirements-minimal.txt"
    }
    $requirements = Join-Path (Get-LabRoot) $requirementsName
    $pipArguments = @("-m", "pip", "install", "--disable-pip-version-check", "--no-input")
    if ($Wheelhouse) {
        $wheelhousePath = Resolve-LabPath -Path $Wheelhouse
        $pipArguments += @("--no-index", "--find-links", $wheelhousePath)
    }
    $pipArguments += @("-r", $requirements)
    $doctorArguments = @("doctor", "--device", "auto", "--output-dir", $runDirectory)
    if ($Profile -eq "Full") {
        $doctorArguments += "--require-neural"
    }

    if ($Environment -eq "Conda") {
        if ($null -eq (Get-Command conda -ErrorAction SilentlyContinue)) {
            throw "Conda was not found. Open Anaconda Prompt or initialize conda for PowerShell."
        }
        & conda run --no-capture-output -n $CondaEnv python @pipArguments
        if ($LASTEXITCODE -ne 0) {
            throw "Dependency installation failed in conda environment '$CondaEnv'."
        }
        & conda run --no-capture-output -n $CondaEnv python -m pip install --disable-pip-version-check --no-input --no-build-isolation --no-deps -e (Get-LabRoot)
        if ($LASTEXITCODE -ne 0) {
            throw "Editable project installation failed in conda environment '$CondaEnv'."
        }
        & conda run --no-capture-output -n $CondaEnv python -m osl_lab.cli @doctorArguments
        if ($LASTEXITCODE -ne 0) {
            throw "The post-install dependency check failed in conda environment '$CondaEnv'."
        }
    }
    elseif ($Environment -eq "Venv") {
        $venv = Resolve-LabPath -Path $VenvPath
        $venvPython = Join-Path $venv "Scripts\python.exe"
        if (-not (Test-Path -LiteralPath $venvPython -PathType Leaf)) {
            Assert-LabPython -Python $Python
            & $Python -m venv $venv
            if ($LASTEXITCODE -ne 0) {
                throw "Virtual environment creation failed: $venv"
            }
        }
        & $venvPython @pipArguments
        if ($LASTEXITCODE -ne 0) {
            throw "Dependency installation failed in virtual environment '$venv'."
        }
        & $venvPython -m pip install --disable-pip-version-check --no-input --no-build-isolation --no-deps -e (Get-LabRoot)
        if ($LASTEXITCODE -ne 0) {
            throw "Editable project installation failed in virtual environment '$venv'."
        }
        & $venvPython -m osl_lab.cli @doctorArguments
        if ($LASTEXITCODE -ne 0) {
            throw "The post-install dependency check failed in virtual environment '$venv'."
        }
    }
    else {
        Assert-LabPython -Python $Python
        & $Python @pipArguments
        if ($LASTEXITCODE -ne 0) {
            throw "Dependency installation failed for '$Python'."
        }
        & $Python -m pip install --disable-pip-version-check --no-input --no-build-isolation --no-deps -e (Get-LabRoot)
        if ($LASTEXITCODE -ne 0) {
            throw "Editable project installation failed for '$Python'."
        }
        Invoke-LabCli -Python $Python -CliArguments $doctorArguments
    }
    Write-Host "Setup completed. Results: $runDirectory"
}
finally {
    Stop-LabTranscript
}
