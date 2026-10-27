$ErrorActionPreference = "Stop"
$Root = Split-Path -Parent (Split-Path -Parent $MyInvocation.MyCommand.Path)
Push-Location $Root
try {
    python -m generative_deformation explore --example walk --depth 12 --max-paths 9000 --out .\examples\walk_cli_output
}
finally {
    Pop-Location
}
