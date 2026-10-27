param(
  [ValidateSet("build", "test", "verify", "package", "clean")]
  [string]$Task = "verify",
  [switch]$Strict
)
$ArgsList = @($PSScriptRoot + "\repo.py", $Task)
if ($Strict) { $ArgsList += "--strict" }
python @ArgsList
exit $LASTEXITCODE
