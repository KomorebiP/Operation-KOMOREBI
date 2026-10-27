param(
    [string]$EnvName = "arc3-offline",
    [switch]$IncludeTorch
)

$ErrorActionPreference = "Stop"
$Work = (Resolve-Path (Join-Path $PSScriptRoot '..\..\..')).Path
$Wheelhouse = Join-Path $Work "wheelhouse"
New-Item -ItemType Directory -Path $Wheelhouse -Force | Out-Null

$Packages = @(
    "arc-agi==0.9.9",
    "arcengine==0.9.3",
    "numpy>=1.26,<3",
    "scipy>=1.11,<2",
    "pillow>=12.1.1,<13",
    "pydantic>=2,<3",
    "requests>=2.31,<3",
    "flask>=3.1,<4",
    "python-dotenv>=1,<2",
    "matplotlib>=3.7,<4",
    "pytest>=8,<10"
)

& conda run -n $EnvName python -m pip download --dest $Wheelhouse @Packages
if ($LASTEXITCODE -ne 0) {
    throw "Wheelhouse dependency download failed."
}

if ($IncludeTorch) {
    & conda run -n $EnvName python -m pip download `
        --dest $Wheelhouse `
        "torch==2.11.0+cu128" `
        --index-url "https://download.pytorch.org/whl/cu128"
    if ($LASTEXITCODE -ne 0) {
        throw "PyTorch wheel download failed."
    }
}

Get-ChildItem -Path (Join-Path $Work "dist") -Filter "*.whl" | Copy-Item -Destination $Wheelhouse -Force
Get-ChildItem -Path $Wheelhouse -File | ForEach-Object {
    $Hash = Get-FileHash -Algorithm SHA256 $_.FullName
    "$($Hash.Hash.ToLower())  $($_.Name)"
} | Set-Content -Encoding UTF8 (Join-Path $Wheelhouse "SHA256SUMS.txt")

Write-Host "Offline wheelhouse prepared at $Wheelhouse" -ForegroundColor Green
