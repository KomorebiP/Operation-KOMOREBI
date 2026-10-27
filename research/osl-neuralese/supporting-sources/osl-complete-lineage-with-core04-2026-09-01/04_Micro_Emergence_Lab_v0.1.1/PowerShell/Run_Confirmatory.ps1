param(
    [ValidateSet("auto", "cpu", "cuda")][string]$Device = "auto",
    [string]$Python = "",
    [string]$OutputRoot = "results",
    [string]$OutputDirectory = "",
    [string]$Config = "configs\confirmatory.json",
    [int[]]$DataSeeds = @(1729, 2718),
    [int[]]$ModelSeeds = @(1729, 2718, 31415),
    [int]$SmokeSeed = 1729,
    [switch]$Force,
    [switch]$SkipSmoke,
    [switch]$StopOnFailure
)

. (Join-Path $PSScriptRoot "Common.ps1")

function Write-RunnerMessage {
    param(
        [Parameter(Mandatory = $true)][string]$Message,
        [Parameter(Mandatory = $true)][string]$LogPath
    )
    $line = "{0} {1}" -f ([DateTime]::UtcNow.ToString("yyyy-MM-ddTHH:mm:ssZ")), $Message
    Write-Host $line
    Add-Content -LiteralPath $LogPath -Value $line -Encoding UTF8
}

function Test-CompletedLabRun {
    param(
        [Parameter(Mandatory = $true)][string]$RunDirectory,
        [string]$ExpectedConfigSha256 = "",
        [string]$ExpectedPackageManifestSha256 = ""
    )
    $metadataPath = Join-Path $RunDirectory "run_metadata.json"
    if (-not (Test-Path -LiteralPath $metadataPath -PathType Leaf)) {
        return $false
    }
    try {
        $metadata = Get-Content -LiteralPath $metadataPath -Raw | ConvertFrom-Json
        if ($metadata.completed -ne $true) {
            return $false
        }
        if ($ExpectedConfigSha256 -and ([string]($metadata.config_sha256) -ne $ExpectedConfigSha256)) {
            throw "Completed run '$RunDirectory' was created from a different configuration. Choose a new -OutputDirectory, or use -Force to regenerate every affected cell."
        }
        if ($ExpectedPackageManifestSha256 -and ([string]($metadata.package_manifest_sha256) -ne $ExpectedPackageManifestSha256)) {
            throw "Completed run '$RunDirectory' was created from a different package manifest. Choose a new -OutputDirectory, or use -Force to regenerate every affected cell."
        }
        return $true
    }
    catch {
        throw "Could not safely reuse run '$RunDirectory'. Choose a new -OutputDirectory, or use -Force to regenerate it. Details: $($_.Exception.Message)"
    }
}

if ($DataSeeds.Count -eq 0) {
    throw "At least one data seed is required."
}
if ($ModelSeeds.Count -eq 0) {
    throw "At least one model seed is required."
}
if (($DataSeeds | Select-Object -Unique).Count -ne $DataSeeds.Count) {
    throw "DataSeeds contains a duplicate value."
}
if (($ModelSeeds | Select-Object -Unique).Count -ne $ModelSeeds.Count) {
    throw "ModelSeeds contains a duplicate value."
}

$activePython = Resolve-ActiveLabPython -Python $Python
$configPath = Resolve-LabPath -Path $Config
if (-not (Test-Path -LiteralPath $configPath -PathType Leaf)) {
    throw "Confirmatory configuration file not found: $configPath"
}
$configSha256 = (Get-FileHash -LiteralPath $configPath -Algorithm SHA256).Hash.ToLowerInvariant()
$packageManifestPath = Join-Path (Get-LabRoot) "MANIFEST.json"
if (-not (Test-Path -LiteralPath $packageManifestPath -PathType Leaf)) {
    throw "Package manifest not found: $packageManifestPath"
}
$packageManifestSha256 = (Get-FileHash -LiteralPath $packageManifestPath -Algorithm SHA256).Hash.ToLowerInvariant()
$smokeConfigPath = Resolve-LabConfig -Preset "smoke"
$smokeConfigSha256 = (Get-FileHash -LiteralPath $smokeConfigPath -Algorithm SHA256).Hash.ToLowerInvariant()

if (-not $OutputDirectory) {
    $OutputDirectory = Join-Path $OutputRoot "confirmatory_v0_1_1"
}
$sessionDirectory = New-LabRunDirectory -OutputRoot $OutputRoot -Prefix "confirmatory" -OutputDirectory $OutputDirectory
$runnerLog = Join-Path $sessionDirectory "RUNNER_LOG.txt"
$checksDirectory = Join-Path $sessionDirectory "checks"
$smokeDirectory = Join-Path $sessionDirectory "smoke"
$matrixDirectory = Join-Path $sessionDirectory "matrix"
$aggregateDirectory = Join-Path $sessionDirectory "aggregate"
New-Item -ItemType Directory -Path $checksDirectory, $matrixDirectory -Force | Out-Null

Write-RunnerMessage -Message "Confirmatory runner started in strict offline mode." -LogPath $runnerLog
Assert-LabPython -Python $activePython

Write-RunnerMessage -Message "Checking active-environment dependencies." -LogPath $runnerLog
Invoke-LabCli -Python $activePython -CliArguments @(
    "doctor", "--require-neural", "--device", $Device,
    "--output-dir", (Join-Path $checksDirectory "dependencies")
)

Write-RunnerMessage -Message "Verifying package sources, JSON, and frozen manifest." -LogPath $runnerLog
Invoke-LabCli -Python $activePython -CliArguments @(
    "verify", "--config", $configPath, "--device", $Device,
    "--output-dir", (Join-Path $checksDirectory "package")
)

if (-not $SkipSmoke) {
    if (-not $Force -and (Test-CompletedLabRun -RunDirectory $smokeDirectory -ExpectedConfigSha256 $smokeConfigSha256 -ExpectedPackageManifestSha256 $packageManifestSha256)) {
        Write-RunnerMessage -Message "Smoke run already complete. Skipping it." -LogPath $runnerLog
    }
    else {
        Write-RunnerMessage -Message "Running one engineering smoke test." -LogPath $runnerLog
        $smokeArguments = @(
            "run-all", "--preset", "smoke", "--device", $Device,
            "--data-seed", $SmokeSeed.ToString(),
            "--model-seed", $SmokeSeed.ToString(),
            "--output-dir", $smokeDirectory
        )
        if ($Force) { $smokeArguments += "--force" }
        Invoke-LabCli -Python $activePython -CliArguments $smokeArguments
    }
}

$failures = @()
foreach ($dataSeed in $DataSeeds) {
    foreach ($modelSeed in $ModelSeeds) {
        $dataDirectory = Join-Path $matrixDirectory ("data_seed_{0}" -f $dataSeed)
        $runDirectory = Join-Path $dataDirectory ("model_seed_{0}" -f $modelSeed)
        if (-not $Force -and (Test-CompletedLabRun -RunDirectory $runDirectory -ExpectedConfigSha256 $configSha256 -ExpectedPackageManifestSha256 $packageManifestSha256)) {
            Write-RunnerMessage -Message ("Skipping completed cell data_seed={0} model_seed={1}." -f $dataSeed, $modelSeed) -LogPath $runnerLog
            continue
        }
        if ((Test-Path -LiteralPath $runDirectory -PathType Container) -and -not $Force) {
            $failure = [ordered]@{
                data_seed = $dataSeed
                model_seed = $modelSeed
                status = "INCOMPLETE_DIRECTORY_REQUIRES_FORCE"
            }
            $failures += $failure
            Write-RunnerMessage -Message ("Incomplete cell requires -Force: data_seed={0} model_seed={1}." -f $dataSeed, $modelSeed) -LogPath $runnerLog
            if ($StopOnFailure) { break }
            continue
        }
        New-Item -ItemType Directory -Path $dataDirectory -Force | Out-Null
        Write-RunnerMessage -Message ("Starting data_seed={0} model_seed={1}." -f $dataSeed, $modelSeed) -LogPath $runnerLog
        $arguments = @(
            "run-all", "--config", $configPath, "--device", $Device,
            "--data-seed", $dataSeed.ToString(),
            "--model-seed", $modelSeed.ToString(),
            "--output-dir", $runDirectory
        )
        if ($Force) { $arguments += "--force" }
        try {
            Invoke-LabCli -Python $activePython -CliArguments $arguments
            Write-RunnerMessage -Message ("Completed data_seed={0} model_seed={1}." -f $dataSeed, $modelSeed) -LogPath $runnerLog
        }
        catch {
            $failure = [ordered]@{
                data_seed = $dataSeed
                model_seed = $modelSeed
                status = "RUN_FAILED"
            }
            $failures += $failure
            Write-RunnerMessage -Message ("Run failed for data_seed={0} model_seed={1}. Continuing so all cells are accounted for." -f $dataSeed, $modelSeed) -LogPath $runnerLog
            if ($StopOnFailure) { break }
        }
    }
    if ($StopOnFailure -and $failures.Count -gt 0) { break }
}

$failurePath = Join-Path $sessionDirectory "FAILED_RUNS.json"
$failureJson = @{
    schema = "osl.micro-emergence.failed-runs.v1"
    failures = $failures
} | ConvertTo-Json -Depth 5
$utf8NoBom = New-Object System.Text.UTF8Encoding($false)
[System.IO.File]::WriteAllText($failurePath, $failureJson + [Environment]::NewLine, $utf8NoBom)

Write-RunnerMessage -Message "Aggregating every completed crossed-seed cell." -LogPath $runnerLog
$aggregateArguments = @(
    "aggregate", "--runs-root", $matrixDirectory,
    "--output-dir", $aggregateDirectory,
    "--config", $configPath
)
foreach ($dataSeed in $DataSeeds) {
    $aggregateArguments += @("--expected-data-seed", $dataSeed.ToString())
}
foreach ($modelSeed in $ModelSeeds) {
    $aggregateArguments += @("--expected-model-seed", $modelSeed.ToString())
}
Invoke-LabModule -Python $activePython -Module "osl_lab.replication" -ModuleArguments $aggregateArguments

$aggregatePath = Join-Path $aggregateDirectory "REPLICATION_SUMMARY.json"
$aggregatePayload = Get-Content -LiteralPath $aggregatePath -Raw | ConvertFrom-Json
$aggregateProblemCount = @($aggregatePayload.errors).Count +
    @($aggregatePayload.duplicate_evaluation_cells).Count +
    @($aggregatePayload.role_binding_contrast_issues).Count
if (($aggregatePayload.matrix_completeness.complete -ne $true) -or $aggregateProblemCount -gt 0) {
    throw "Replication aggregate is incomplete or invalid. The partial aggregate report was preserved."
}

Write-RunnerMessage -Message "Confirmatory aggregation complete." -LogPath $runnerLog
Write-Host "Results: $sessionDirectory"
if ($failures.Count -gt 0) {
    throw ("{0} confirmatory cell(s) failed or were incomplete. Completed cells and aggregate reports were preserved." -f $failures.Count)
}
