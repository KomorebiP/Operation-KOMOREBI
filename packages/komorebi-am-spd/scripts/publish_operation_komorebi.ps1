[CmdletBinding()]
param(
    [string]$Archive,
    [string]$Workspace = (Join-Path $HOME "Documents\GitHub"),
    [string]$Repository = "KomorebiP/Operation-KOMOREBI",
    [string]$PackagePath = "packages\komorebi-am-spd",
    [switch]$DirectToMain,
    [switch]$SkipTests,
    [switch]$RunPaperReplay
)

$ErrorActionPreference = "Stop"

function Invoke-NativeChecked {
    param([string]$Command, [string[]]$Arguments, [string]$Failure)
    & $Command @Arguments
    if ($LASTEXITCODE -ne 0) { throw $Failure }
}

if (-not (Get-Command git -ErrorAction SilentlyContinue)) {
    throw "Git is not installed or is not on PATH. Install Git for Windows, reopen PowerShell, and retry."
}
if (-not (Get-Command gh -ErrorAction SilentlyContinue)) {
    throw "GitHub CLI is not installed or is not on PATH. Install GitHub CLI, reopen PowerShell, and retry."
}
if (-not (Get-Command python -ErrorAction SilentlyContinue)) {
    throw "Python is not installed or is not on PATH."
}

if ([string]::IsNullOrWhiteSpace($Archive)) {
    $Archive = Get-ChildItem -LiteralPath (Join-Path $HOME "Downloads") -Filter "komorebi-am-spd-functional-v1.0.0*.zip" -File |
        Sort-Object LastWriteTime -Descending |
        Select-Object -First 1 -ExpandProperty FullName
}
if ([string]::IsNullOrWhiteSpace($Archive) -or -not (Test-Path -LiteralPath $Archive)) {
    throw "The v1.0.0 archive was not found. Pass -Archive 'C:\path\komorebi-am-spd-functional-v1.0.0.zip'."
}
$Archive = (Resolve-Path -LiteralPath $Archive).Path

& gh auth status --hostname github.com | Out-Host
if ($LASTEXITCODE -ne 0) {
    Invoke-NativeChecked "gh" @("auth", "login", "--hostname", "github.com", "--git-protocol", "https", "--web") "GitHub authentication failed"
}
Invoke-NativeChecked "gh" @("auth", "setup-git") "GitHub could not configure Git authentication"

$ActiveLogin = (& gh api user --jq ".login").Trim()
if ($LASTEXITCODE -ne 0) { throw "Could not identify the authenticated GitHub account" }
if ($ActiveLogin -ne "KomorebiP") {
    & gh auth switch --hostname github.com --user KomorebiP
    if ($LASTEXITCODE -ne 0) {
        throw "Authenticate or switch GitHub CLI to KomorebiP, then retry."
    }
    $ActiveLogin = (& gh api user --jq ".login").Trim()
}
if ($ActiveLogin -ne "KomorebiP") { throw "GitHub CLI is not authenticated as KomorebiP" }

New-Item -ItemType Directory -Force -Path $Workspace | Out-Null
$RepoName = ($Repository -split "/")[-1]
$RepoDir = Join-Path $Workspace $RepoName

if (Test-Path -LiteralPath (Join-Path $RepoDir ".git")) {
    Set-Location $RepoDir
    if (git status --porcelain) {
        throw "The local Operation-KOMOREBI checkout has uncommitted changes. Commit or stash them before running this updater."
    }
    Invoke-NativeChecked "git" @("fetch", "origin", "--prune") "git fetch failed"
    Invoke-NativeChecked "git" @("switch", "main") "Could not switch to main"
    Invoke-NativeChecked "git" @("pull", "--ff-only", "origin", "main") "Could not update main"
} elseif (Test-Path -LiteralPath $RepoDir) {
    throw "$RepoDir exists but is not a Git repository"
} else {
    Invoke-NativeChecked "gh" @("repo", "clone", $Repository, $RepoDir) "Repository clone failed"
    Set-Location $RepoDir
}

$CommitName = "Komorebi P."
$GitHubUserId = (& gh api user --jq ".id").Trim()
if ($LASTEXITCODE -ne 0 -or [string]::IsNullOrWhiteSpace($GitHubUserId)) { throw "Could not resolve the authenticated GitHub user ID" }
$CommitEmail = "$GitHubUserId+$ActiveLogin@users.noreply.github.com"
git config user.name $CommitName
git config user.email $CommitEmail

$Branch = "release-am-spd-v1.0.0"
if (-not $DirectToMain) {
    git show-ref --verify --quiet "refs/heads/$Branch"
    $LocalExists = $LASTEXITCODE -eq 0
    git ls-remote --exit-code --heads origin $Branch *> $null
    $RemoteExists = $LASTEXITCODE -eq 0
    if ($LocalExists -or $RemoteExists) {
        $Branch = "$Branch-$(Get-Date -Format 'yyyyMMdd-HHmmss')"
    }
    Invoke-NativeChecked "git" @("switch", "-c", $Branch) "Could not create branch $Branch"
}

$ExtractDir = Join-Path $env:TEMP ("komorebi-am-spd-v100-" + [guid]::NewGuid().ToString("N"))
New-Item -ItemType Directory -Force -Path $ExtractDir | Out-Null

try {
    Expand-Archive -LiteralPath $Archive -DestinationPath $ExtractDir -Force
    $Source = Join-Path $ExtractDir "komorebi-am-spd"
    if (-not (Test-Path -LiteralPath (Join-Path $Source "pyproject.toml"))) {
        throw "The archive does not contain the expected komorebi-am-spd repository root"
    }

    $Target = Join-Path $RepoDir $PackagePath
    if (Test-Path -LiteralPath $Target) {
        Remove-Item -LiteralPath $Target -Recurse -Force
    }
    New-Item -ItemType Directory -Force -Path $Target | Out-Null
    & robocopy $Source $Target /E /R:2 /W:1 /NFL /NDL /NJH /NJS /NP | Out-Host
    if ($LASTEXITCODE -gt 7) { throw "robocopy failed with exit code $LASTEXITCODE" }

    Remove-Item -LiteralPath (Join-Path $Target ".git") -Recurse -Force -ErrorAction SilentlyContinue

    $WorkflowSource = Join-Path $Source "monorepo\.github\workflows"
    $WorkflowTarget = Join-Path $RepoDir ".github\workflows"
    New-Item -ItemType Directory -Force -Path $WorkflowTarget | Out-Null
    Get-ChildItem -LiteralPath $WorkflowSource -Filter "*.yml" -File | ForEach-Object {
        Copy-Item -LiteralPath $_.FullName -Destination (Join-Path $WorkflowTarget $_.Name) -Force
    }

    $Readme = Join-Path $RepoDir "README.md"
    $ReadmeText = if (Test-Path -LiteralPath $Readme) { Get-Content -LiteralPath $Readme -Raw } else { "# Operation-KOMOREBI`n" }
    if ($ReadmeText -notmatch "packages/komorebi-am-spd") {
        $ReadmeText += @"

## Packages

### Adaptive Multiscale Singular Packet Decomposition

AM-SPD is the image-packet reconstruction component of Operation: Komorebi. Version 1.0.0 adds resumable packet-search checkpoints, overlap-blended tiled reconstruction, automatic finite-grid selection, content-aware batch processing, model comparison, portable single and tiled archives, exact residual closure, benchmarks, and exact paper replay.

- Package: ``packages/komorebi-am-spd``
- Distribution: ``komorebi-am-spd``
- Import namespace: ``am_spd``
- Version: ``1.0.0``
- Manuscript: ``packages/komorebi-am-spd/docs/paper/final/``
- Functionality matrix: ``packages/komorebi-am-spd/FUNCTIONALITY_MATRIX.md``
"@
    } else {
        $ReadmeText = $ReadmeText -replace '- Version: ``0\.[0-9]+\.[0-9]+``', '- Version: ``1.0.0``'
        $ReadmeText = $ReadmeText -replace 'AM-SPD 0\.[0-9]+\.[0-9]+', 'AM-SPD 1.0.0'
    }
    Set-Content -LiteralPath $Readme -Value $ReadmeText -Encoding utf8

    if (-not $SkipTests) {
        Push-Location $Target
        try {
            Invoke-NativeChecked "python" @("-m", "pip", "install", "-e", ".[dev,research]") "AM-SPD installation failed"
            Invoke-NativeChecked "python" @("-m", "pytest", "-m", "not slow") "AM-SPD tests failed"
            Invoke-NativeChecked "python" @("-m", "am_spd", "verify", "--full") "AM-SPD full package verification failed"
            Invoke-NativeChecked "python" @("-m", "am_spd", "reproduce-paper", "--list-cases") "Bundled paper-replay resources are unavailable"
            Invoke-NativeChecked "python" @("-m", "am_spd", "info") "AM-SPD command and schema metadata are unavailable"
            if ($RunPaperReplay) {
                $env:OPENBLAS_NUM_THREADS = "1"
                $env:OMP_NUM_THREADS = "1"
                $env:MKL_NUM_THREADS = "1"
                Invoke-NativeChecked "python" @(
                    "-m", "am_spd", "reproduce-paper",
                    "--cases", "synthetic_geometry",
                    "--output-dir", "artifacts\upload-paper-replay",
                    "--strict-reference"
                ) "Exact paper replay failed"
            }
        } finally {
            Pop-Location
        }
    }
} finally {
    Remove-Item -LiteralPath $ExtractDir -Recurse -Force -ErrorAction SilentlyContinue
}

Set-Location $RepoDir
git add -- $PackagePath README.md ".github/workflows/am-spd-ci.yml" ".github/workflows/am-spd-paper-replay.yml" ".github/workflows/am-spd-full-research-verification.yml" ".github/workflows/am-spd-build.yml"
if ($LASTEXITCODE -ne 0) { throw "git add failed" }

git diff --cached --stat | Out-Host
git diff --cached --quiet
if ($LASTEXITCODE -eq 0) {
    Write-Host "No new changes were found."
    exit 0
}

Invoke-NativeChecked "git" @("commit", "-m", "Expand AM-SPD functionality to v1.0.0") "git commit failed"

if ($DirectToMain) {
    Invoke-NativeChecked "git" @("push", "origin", "main") "Push to main failed"
    & gh repo view $Repository --web
    exit 0
}

Invoke-NativeChecked "git" @("push", "-u", "origin", $Branch) "Branch push failed"

$Title = "Import AM-SPD 1.0.0 with audited reconstruction and model workflows"
$Body = @"
Imports the AM-SPD 1.0.0 image-decomposition package at packages/komorebi-am-spd and adds package-specific root workflows. The maintained release fixes input scaling, downstream parameter caps, malformed-model rejection, checkpoint continuation, finite-grid selection, and batch output/restart behavior while retaining the historical research snapshot.

The package preserves normalized floating-point rasters through unthresholded residual closure, with roundoff explicitly reported. Image previews remain quantized display outputs. Historical paper replay uses frozen, checksummed fixtures and reports archived diagnostic differences separately; it does not rerun the original moving search or certify every current configuration.

Validation from release preparation: 228 package tests passed, alongside full package verification, installed-wheel/source-distribution checks, strict benchmark replay, and preserved-source checksum checks. Root workflows cover Python 3.10 through 3.13 on Linux and 3.12/3.13 on Windows, with independent distribution checks and copied-tree historical verification.

Windows runtime checks and hosted GitHub Actions were not executed in the Linux release-preparation environment. Their results remain separate from the recorded local validation. This import does not create a public release, publish to PyPI, or change the distribution terms of other components.
"@

$BodyFile = Join-Path $env:TEMP ("komorebi-am-spd-pr-" + [guid]::NewGuid().ToString("N") + ".md")
try {
    Set-Content -LiteralPath $BodyFile -Value $Body -Encoding utf8
    & gh pr create --repo $Repository --base main --head $Branch --title $Title --body-file $BodyFile
    $PrCreateExitCode = $LASTEXITCODE
} finally {
    Remove-Item -LiteralPath $BodyFile -Force -ErrorAction SilentlyContinue
}
if ($PrCreateExitCode -eq 0) {
    & gh pr view --repo $Repository --web
} else {
    Write-Warning "GitHub CLI could not create the pull request. The branch was pushed successfully. Opening the browser comparison instead."
    $EncodedTitle = [uri]::EscapeDataString($Title)
    $EncodedBody = [uri]::EscapeDataString($Body)
    $CompareUrl = "https://github.com/${Repository}/compare/main...${Branch}?quick_pull=1&title=${EncodedTitle}&body=${EncodedBody}"
    Write-Host $CompareUrl
    Start-Process $CompareUrl
}
