function Resolve-KomorebiCondaExecutable {
  [CmdletBinding()]
  param([string]$ExplicitPath="")

  $Candidates = New-Object System.Collections.Generic.List[string]
  if($ExplicitPath){$Candidates.Add($ExplicitPath)}
  if($env:CONDA_EXE){$Candidates.Add($env:CONDA_EXE)}
  if($env:_CONDA_EXE){$Candidates.Add($env:_CONDA_EXE)}

  foreach($Name in @("conda.exe","conda.bat","conda")){
    $Command = Get-Command $Name -CommandType Application -ErrorAction SilentlyContinue | Select-Object -First 1
    if($Command){$Candidates.Add($Command.Source)}
  }

  $Roots = @(
    (Join-Path $HOME "miniconda3"),
    (Join-Path $HOME "anaconda3"),
    (Join-Path $HOME "miniforge3"),
    (Join-Path $HOME "mambaforge"),
    (Join-Path $env:LOCALAPPDATA "miniconda3"),
    (Join-Path $env:LOCALAPPDATA "anaconda3"),
    (Join-Path $env:LOCALAPPDATA "miniforge3"),
    (Join-Path $env:LOCALAPPDATA "mambaforge")
  )
  foreach($Root in $Roots){
    if(-not $Root){continue}
    $Candidates.Add((Join-Path $Root "Scripts\conda.exe"))
    $Candidates.Add((Join-Path $Root "condabin\conda.bat"))
    $Candidates.Add((Join-Path $Root "_conda.exe"))
  }

  foreach($Candidate in ($Candidates | Where-Object {$_} | Select-Object -Unique)){
    if(Test-Path -LiteralPath $Candidate -PathType Leaf){
      return (Resolve-Path -LiteralPath $Candidate).Path
    }
  }

  throw "Conda executable was not found. Set CONDA_EXE, pass -CondaExecutable, or install Miniconda/Anaconda under the user profile."
}

function Invoke-KomorebiConda {
  [CmdletBinding()]
  param(
    [Parameter(Mandatory=$true)][string]$CondaExecutable,
    [Parameter(Mandatory=$true)][string[]]$Arguments
  )

  & $CondaExecutable @Arguments
  $Code = $LASTEXITCODE
  if($null -eq $Code){$Code=1}
  if($Code -ne 0){
    throw "Conda command failed with exit code $Code: $CondaExecutable $($Arguments -join ' ')"
  }
}
