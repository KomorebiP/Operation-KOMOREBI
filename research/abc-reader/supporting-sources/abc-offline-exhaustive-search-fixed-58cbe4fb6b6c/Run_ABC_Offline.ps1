param(
    [ValidateSet('Quick','Deep','Extreme')][string]$Profile='Deep',
    [double]$Hours=24,
    [int]$Workers=0,
    [int]$FactorLimit=2000,
    [string]$WorkDir='',
    [switch]$Plan,
    [switch]$FactorOnly,
    [switch]$ExportOnly
)

$ErrorActionPreference='Stop'
Set-StrictMode -Version Latest

function Convert-ToWslPath {
    param([Parameter(Mandatory=$true)][string]$WindowsPath)

    $FullPath=[System.IO.Path]::GetFullPath($WindowsPath)

    # Standard local-drive paths are converted directly. This avoids wsl.exe
    # passing backslashes through a shell and turning C:\Users\... into C:Users...
    if($FullPath -match '^(?<Drive>[A-Za-z]):[\\/](?<Rest>.*)$'){
        $Drive=$Matches['Drive'].ToLowerInvariant()
        $Rest=$Matches['Rest'] -replace '\\','/'
        return "/mnt/$Drive/$Rest"
    }

    # Fallback for uncommon paths such as UNC locations. -e bypasses the
    # intermediate Linux shell so backslashes are not consumed as escapes.
    $Output=@(& wsl.exe -e wslpath -a -u "$FullPath" 2>&1)
    if($LASTEXITCODE -ne 0 -or $Output.Count -eq 0){
        throw "Could not convert Windows path to a WSL path: $FullPath`n$($Output -join [Environment]::NewLine)"
    }
    return ([string]$Output[-1]).Trim()
}

$Root=[System.IO.Path]::GetFullPath((Split-Path -Parent $PSCommandPath))
if(-not $WorkDir){
    $WorkDir=Join-Path $Root (Join-Path 'runs' $Profile.ToLowerInvariant())
}
$WorkDir=[System.IO.Path]::GetFullPath($WorkDir)

$WslRoot=Convert-ToWslPath $Root
$WslWork=Convert-ToWslPath $WorkDir

$ArgsList=@('--profile',$Profile.ToLowerInvariant(),'--workdir',$WslWork)
if($Hours -gt 0){$ArgsList+=@('--hours',[string]$Hours)}
if($Workers -gt 0){$ArgsList+=@('--workers',[string]$Workers)}
if($FactorLimit -gt 0){$ArgsList+=@('--factor-limit',[string]$FactorLimit)}
if($Plan){$ArgsList+='--plan'}
if($FactorOnly){$ArgsList+='--factor-only'}
if($ExportOnly){$ArgsList+='--export-only'}

$Runner="$WslRoot/run_wsl.sh"
Write-Host "WSL project: $WslRoot"
Write-Host "WSL workdir: $WslWork"

& wsl.exe -e bash "$Runner" @ArgsList
if($LASTEXITCODE -ne 0){
    exit $LASTEXITCODE
}
