param(
  [Parameter(Mandatory=$true)][string]$ProjectLinuxPath,
  [Parameter(Mandatory=$true)][string]$KitLinuxPath
)
$ErrorActionPreference = 'Stop'
& wsl --cd $ProjectLinuxPath -- python3 scripts/verify.py --kit $KitLinuxPath
if ($LASTEXITCODE -ne 0) { throw "Lean verification failed with exit code $LASTEXITCODE" }
