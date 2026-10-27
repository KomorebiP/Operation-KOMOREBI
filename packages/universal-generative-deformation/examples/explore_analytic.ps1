$ErrorActionPreference = "Stop"
$Root = Split-Path -Parent (Split-Path -Parent $MyInvocation.MyCommand.Path)
Push-Location $Root
try {
    python -m generative_deformation explore --example analytic --depth 3 --max-paths 1800 --out .\examples\analytic_cli_output
}
finally {
    Pop-Location
}
