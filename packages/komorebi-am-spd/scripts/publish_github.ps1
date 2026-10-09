param(
    [Parameter(Mandatory = $false)][string]$Repository = "komorebi-am-spd",
    [Parameter(Mandatory = $false)][ValidateSet("private", "public")][string]$Visibility = "private"
)
$ErrorActionPreference = "Stop"
$Root = Split-Path -Parent $PSScriptRoot
Set-Location $Root
if (-not (Get-Command gh -ErrorAction SilentlyContinue)) { throw "GitHub CLI is not installed" }
gh auth status
if ($LASTEXITCODE -ne 0) { throw "GitHub CLI authentication failed" }
if (-not (Test-Path .git)) { git init -b main }
if (-not (git config --get user.name)) { throw "Set a Git author name with: git config --global user.name 'Your Name'" }
if (-not (git config --get user.email)) { throw "Set a Git author email with: git config --global user.email 'you@example.com'" }
git add .
if ($LASTEXITCODE -ne 0) { throw "git add failed" }
$HasHead = $true
git rev-parse --verify HEAD 2>$null | Out-Null
if ($LASTEXITCODE -ne 0) { $HasHead = $false }
$HasChanges = $false
git diff --cached --quiet
if ($LASTEXITCODE -ne 0) { $HasChanges = $true }
if (-not $HasHead -or $HasChanges) {
    git commit -m "Prepare AM-SPD repository release"
    if ($LASTEXITCODE -ne 0) { throw "git commit failed" }
}
$Flag = "--$Visibility"
gh repo create $Repository $Flag --source . --remote origin --push
if ($LASTEXITCODE -ne 0) { throw "GitHub repository creation failed" }
