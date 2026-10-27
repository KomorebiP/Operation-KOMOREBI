param([string]$Root = "/mnt/data/lean_compact_runtime/extracted/Komorebi_Portable_Lean_4.34.0-rc2")
if (-not (Test-Path "$Root/run.sh")) { throw "Set -Root to the extracted portable Lean runtime." }
bash "$Root/run.sh" attach (Get-Location).Path
$env:PATH = "$Root/toolchain/bin:" + $env:PATH
lake build -KwarningAsError=true
