param([string]$Python = "")
$ErrorActionPreference = "Stop"
$root = Split-Path -Parent $MyInvocation.MyCommand.Path
if ([string]::IsNullOrWhiteSpace($Python)) {
    if ($env:CONDA_PREFIX) {
        $candidate = Join-Path $env:CONDA_PREFIX "python.exe"
        if (Test-Path -LiteralPath $candidate) { $Python = $candidate }
    }
    if ([string]::IsNullOrWhiteSpace($Python)) { $Python = "python" }
}
& $Python "$root\verify_package.py" --package $root
if ($LASTEXITCODE -ne 0) { throw "Package verification failed" }
