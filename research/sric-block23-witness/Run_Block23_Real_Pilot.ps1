param(
  [string]$RepoDir = ".\external\are-lrms-easily-interpretable",
  [string]$Checkpoint = ".\external\checkpoint\checkpoint_37",
  [string]$Tasks = ".\external\are-lrms-easily-interpretable\data\prontoqa_test.json",
  [int]$Limit = 32,
  [string]$Device = "cuda"
)
$env:OMP_NUM_THREADS='1'
$env:OPENBLAS_NUM_THREADS='1'
$env:MKL_NUM_THREADS='1'
$env:NUMEXPR_NUM_THREADS='1'
$env:PYTHONHASHSEED='0'
$ErrorActionPreference = "Stop"
Set-Location $PSScriptRoot
python .\external_preflight.py --repo-dir $RepoDir --checkpoint $Checkpoint
python .\real_pilot.py --repo-dir $RepoDir --checkpoint $Checkpoint --tasks $Tasks --limit $Limit --device $Device
