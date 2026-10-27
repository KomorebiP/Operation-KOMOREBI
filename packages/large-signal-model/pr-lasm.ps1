[CmdletBinding()]
param(
    [Parameter(Position = 0)]
    [ValidateSet("help", "setup", "test", "test-all", "benchmark", "smoke", "build", "suite-list", "suite-audit", "suite-run", "suite-summary")]
    [string]$Command = "help",
    [string]$Python = "python",
    [string]$EnvName = "",
    [string]$EnvironmentsDir = "",
    [string]$OutputDir = "",
    [ValidateSet("quick", "balanced", "thorough")]
    [string]$Profile = "balanced",
    [ValidateSet("easy", "hard", "id")]
    [string]$Order = "easy",
    [int]$Limit = 0
)

$ErrorActionPreference = "Stop"
$RepoRoot = $PSScriptRoot
if (-not $EnvironmentsDir) { $EnvironmentsDir = Join-Path $RepoRoot "environment_files" }
if (-not $OutputDir) { $OutputDir = Join-Path $RepoRoot "results" }

$env:OPERATION_MODE = "OFFLINE"
$env:ARC_API_KEY = ""
$env:KOMOREBI_ARC3_OFFLINE_ONLY = "1"

function Invoke-ProjectPython {
    param([string[]]$Arguments)
    if ($EnvName) {
        & conda run --no-capture-output -n $EnvName python @Arguments
    } else {
        & $Python @Arguments
    }
    if ($LASTEXITCODE -ne 0) {
        throw "Python command failed with exit code $LASTEXITCODE."
    }
}

Set-Location $RepoRoot

switch ($Command) {
    "help" {
        @"
PR-LASM repository command

  .\pr-lasm.ps1 setup                  Install editable development dependencies
  .\pr-lasm.ps1 test                   Run clean-repository core tests
  .\pr-lasm.ps1 test-all               Run all tests, including optional local-suite tests
  .\pr-lasm.ps1 benchmark              Run exactness, operator, and synthetic-agent benchmarks
  .\pr-lasm.ps1 smoke                  Run the four deterministic interactive smoke systems
  .\pr-lasm.ps1 build                  Build a wheel into dist\
  .\pr-lasm.ps1 suite-list             List locally installed ARC environments
  .\pr-lasm.ps1 suite-audit            Statically audit local ARC environments
  .\pr-lasm.ps1 suite-run              Run the checkpointed local ARC suite
  .\pr-lasm.ps1 suite-summary          Summarize the latest local ARC suite

Add -EnvName <conda-environment> to execute through conda run.
"@
    }
    "setup" {
        Invoke-ProjectPython @("-m", "pip", "install", "-e", ".[dev]")
    }
    "test" {
        Invoke-ProjectPython @("-m", "pytest", "-q", "-m", "not local_suite")
    }
    "test-all" {
        Invoke-ProjectPython @("-m", "pytest", "-q")
    }
    "benchmark" {
        Invoke-ProjectPython @("-m", "komorebi_pr_lasm", "benchmark", "--output", (Join-Path $OutputDir "pr_lasm_benchmark"))
    }
    "smoke" {
        Invoke-ProjectPython @("-m", "komorebi_pr_lasm", "smoke", "--output", (Join-Path $OutputDir "pr_lasm_smoke"))
    }
    "build" {
        if (Test-Path (Join-Path $RepoRoot "dist")) { Remove-Item -Recurse -Force (Join-Path $RepoRoot "dist") }
        Invoke-ProjectPython @("-m", "pip", "wheel", ".", "--no-deps", "--no-build-isolation", "--wheel-dir", "dist")
    }
    "suite-list" {
        Invoke-ProjectPython @("-m", "komorebi_arc3_offline.cli", "suite-list", "--environments-dir", $EnvironmentsDir)
    }
    "suite-audit" {
        Invoke-ProjectPython @("-m", "komorebi_arc3_offline.cli", "suite-audit", "--environments-dir", $EnvironmentsDir, "--output", (Join-Path $OutputDir "suite_static_audit.json"))
    }
    "suite-run" {
        $Arguments = @("-m", "komorebi_arc3_offline.cli", "suite-run", "--environments-dir", $EnvironmentsDir, "--output", (Join-Path $OutputDir "suite"), "--profile", $Profile, "--order", $Order)
        if ($Limit -gt 0) { $Arguments += @("--limit", $Limit.ToString()) }
        Invoke-ProjectPython $Arguments
    }
    "suite-summary" {
        Invoke-ProjectPython @("-m", "komorebi_arc3_offline.cli", "suite-summary", "--output", (Join-Path $OutputDir "suite"))
    }
}
