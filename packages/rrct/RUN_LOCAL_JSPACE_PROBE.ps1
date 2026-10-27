param(
    [Parameter(Mandatory=$true)][string]$Model,
    [Parameter(Mandatory=$true)][string]$Prompts,
    [Parameter(Mandatory=$true)][string]$Output,
    [int]$Layer=-1,
    [int]$ResidualToken=-1,
    [int]$PredictionToken=-1,
    [int[]]$TargetTokenId=@(),
    [string]$Device="cpu",
    [string]$DType="",
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
$ArgsList = @(
    ".\scripts\run_local_jspace_probe.py",
    "--model",$Model,"--prompts",$Prompts,"--output",$Output,
    "--layer",$Layer,"--residual-token",$ResidualToken,
    "--prediction-token",$PredictionToken,"--device",$Device
)
foreach($TokenId in $TargetTokenId){ $ArgsList += @("--target-token-id",$TokenId) }
if (-not [string]::IsNullOrWhiteSpace($DType)){ $ArgsList += @("--dtype",$DType) }
& $Python @ArgsList
if ($LASTEXITCODE -ne 0) { throw "Local J-space probe failed" }
