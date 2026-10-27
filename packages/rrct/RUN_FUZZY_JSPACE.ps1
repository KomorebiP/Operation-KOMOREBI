param(
    [string]$Config=".\configs\14_persistent_fuzzy_j_workspace.toml",
    [string[]]$Set=@(),
    [string]$Python=""
)
$ErrorActionPreference = "Stop"
$Root = Split-Path -Parent $MyInvocation.MyCommand.Path
Set-Location $Root
if ([string]::IsNullOrWhiteSpace($Python)) {
    if ($env:CONDA_PREFIX -and (Test-Path (Join-Path $env:CONDA_PREFIX "python.exe"))) { $Python = Join-Path $env:CONDA_PREFIX "python.exe" }
    elseif (Get-Command python -ErrorAction SilentlyContinue) { $Python = (Get-Command python).Source }
    else { throw "Python was not found" }
}
$env:PYTHONPATH = Join-Path $Root "src"
$ArgsList = @("-m","rrct_lab","run",$Config)
foreach($Item in $Set){ $ArgsList += @("--set",$Item) }
& $Python @ArgsList
if ($LASTEXITCODE -ne 0) { throw "RRCT fuzzy-to-J bridge run failed" }
