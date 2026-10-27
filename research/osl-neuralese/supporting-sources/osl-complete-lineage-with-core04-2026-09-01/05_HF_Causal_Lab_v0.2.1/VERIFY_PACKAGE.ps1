param([string]$Python = "python")

$ErrorActionPreference = "Stop"
$root = Split-Path -Parent $MyInvocation.MyCommand.Path
Set-Location $root

Get-Content PACKAGE_SHA256SUMS.txt | ForEach-Object {
    if ($_ -match '^([0-9a-f]{64})  (.+)$') {
        $expected = $Matches[1]
        $relative = $Matches[2]
        $actual = (Get-FileHash -Algorithm SHA256 -LiteralPath (Join-Path $root $relative)).Hash.ToLowerInvariant()
        if ($actual -ne $expected) { throw "Checksum mismatch: $relative" }
    }
}

& $Python -m py_compile run_experiment.py smoke_tests.py verify_results.py
if ($LASTEXITCODE -ne 0) { throw "Python compilation failed" }

& $Python smoke_tests.py
if ($LASTEXITCODE -ne 0) { throw "Source smoke tests failed" }

Write-Host "Package verification passed"

