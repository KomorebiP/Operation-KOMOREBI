param(
    [Parameter(Mandatory = $true)][string]$Repository,
    [ValidateSet("public", "private")][string]$Visibility = "public",
    [switch]$SkipTag
)
$ErrorActionPreference = "Stop"
$Root = Split-Path $PSScriptRoot -Parent
Set-Location $Root
$Version = (Get-Content .\VERSION -Raw).Trim()
if (-not (Get-Command git -ErrorAction SilentlyContinue)) { throw "git is required." }
if (-not (Get-Command gh -ErrorAction SilentlyContinue)) { throw "GitHub CLI (gh) is required." }
python scripts/check_release.py
if ($LASTEXITCODE -ne 0) { throw "Repository verification failed." }
python scripts/package_release.py
if ($LASTEXITCODE -ne 0) { throw "Release packaging failed." }
if (-not (Test-Path .git)) {
    git init
    git branch -M main
    git add .
    git commit -m "Initial release v$Version"
}
if ($Visibility -eq "public") {
    gh repo create $Repository --public --source . --remote origin --push
} else {
    gh repo create $Repository --private --source . --remote origin --push
}
if (-not $SkipTag) {
    git tag -a "v$Version" -m "Universal Lane Transport Theorem v$Version"
    git push origin "v$Version"
}
