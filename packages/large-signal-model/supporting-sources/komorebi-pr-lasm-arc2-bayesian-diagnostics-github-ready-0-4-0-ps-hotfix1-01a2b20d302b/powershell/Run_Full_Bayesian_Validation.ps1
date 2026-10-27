param(
  [string]$Environment="komorebi-full",
  [string]$DataDir="",
  [int]$TrainingTasks=25,
  [double]$TimeLimit=0.05,
  [string]$CondaExecutable=""
)
$ErrorActionPreference="Stop"
. (Join-Path $PSScriptRoot "Conda_Runtime.ps1")
$Conda=Resolve-KomorebiCondaExecutable -ExplicitPath $CondaExecutable
Write-Host "Using Conda executable: $Conda"
$Root=Split-Path -Parent $PSScriptRoot
Invoke-KomorebiConda -CondaExecutable $Conda -Arguments @("run","-n",$Environment,"python","-m","pip","install","--no-deps","--no-build-isolation","-e",$Root)
Invoke-KomorebiConda -CondaExecutable $Conda -Arguments @("run","-n",$Environment,"python","-c","import komorebi_arc2; print('komorebi_arc2',komorebi_arc2.__version__,komorebi_arc2.__file__)")
Invoke-KomorebiConda -CondaExecutable $Conda -Arguments @("run","-n",$Environment,"python","-m","komorebi_arc2","--self-test")
Invoke-KomorebiConda -CondaExecutable $Conda -Arguments @("run","-n",$Environment,"python","-m","pytest",(Join-Path $Root "tests"))
Invoke-KomorebiConda -CondaExecutable $Conda -Arguments @("run","-n",$Environment,"python",(Join-Path $Root "scripts\audit_atlas_reconstruction.py"),"--output",(Join-Path $Root "results\atlas_reconstruction_audit.json"))
if($DataDir){
  & (Join-Path $Root "powershell\Run_Public_Training_Audit.ps1") -DataDir $DataDir -Environment $Environment -TimeLimit $TimeLimit -MaxTasks $TrainingTasks -CondaExecutable $Conda
}
