param(
    [ValidateSet("check", "generate", "smoke", "standard", "confirmatory", "full", "verify")]
    [string]$Mode = "smoke",
    [ValidateSet("smoke", "standard", "confirmatory", "full")][string]$Preset = "standard",
    [ValidateSet("auto", "cpu", "cuda")][string]$Device = "auto",
    [string]$Python = "python",
    [string]$OutputRoot = "results",
    [int]$Seed = 1729,
    [switch]$Force
)

$ErrorActionPreference = "Stop"
$root = $PSScriptRoot
$scripts = Join-Path $root "PowerShell"

switch ($Mode) {
    "check" {
        & (Join-Path $scripts "Check_Dependencies.ps1") -Device $Device -Python $Python -OutputRoot $OutputRoot
    }
    "generate" {
        & (Join-Path $scripts "Generate_Only.ps1") -Preset $Preset -Python $Python -OutputRoot $OutputRoot -Seed $Seed -Force:$Force
    }
    "smoke" {
        & (Join-Path $scripts "Run_Smoke.ps1") -Device $Device -Python $Python -OutputRoot $OutputRoot -Seed $Seed -Force:$Force
    }
    "standard" {
        & (Join-Path $scripts "Run_Standard.ps1") -Device $Device -Python $Python -OutputRoot $OutputRoot -Seed $Seed -Force:$Force
    }
    "confirmatory" {
        & (Join-Path $scripts "Run_Confirmatory.ps1") -Device $Device -Python $Python -OutputRoot $OutputRoot -Force:$Force
    }
    "full" {
        & (Join-Path $scripts "Run_Full.ps1") -Device $Device -Python $Python -OutputRoot $OutputRoot -Seed $Seed -Force:$Force
    }
    "verify" {
        & (Join-Path $scripts "Verify.ps1") -Preset $Preset -Device $Device -Python $Python -OutputRoot $OutputRoot -Seed $Seed
    }
}

if ($LASTEXITCODE -ne 0) {
    exit $LASTEXITCODE
}
