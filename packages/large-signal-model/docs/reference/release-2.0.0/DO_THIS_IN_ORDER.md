# Start here: the supplied 25 local ARC-AGI-3 tests

The complete environment trees from `tests.zip` are already bundled under
`environment_files/`. You do not need to import or download game files.

Open **Anaconda PowerShell Prompt**, then set the release path:

```powershell
$Work = "$env:USERPROFILE\Downloads\Komorebi_ARC_AGI3_Offline_25_Tests"
Set-ExecutionPolicy -Scope Process Bypass -Force
```

## 1. Repair, check, test, validate, and list

You already installed `arc-agi 0.9.9` and `arcengine 0.9.3` in the Conda
environment `arc3-offline`. This command reinstalls only the small local runner
wheel, checks the environment, runs its tests, statically validates all 25 game
trees, and lists the versioned game IDs:

```powershell
& "$Work\0_Preflight_25_Tests.ps1" -EnvName "arc3-offline"
```

## 2. Exercise the official local wrapper on all 25

This loads each supplied environment through the official offline wrapper,
resets it, and performs one public action. It does not attempt to solve the
games.

```powershell
& "$Work\3_Official_Smoke_All_25.ps1" -EnvName "arc3-offline"
```

The report is written to:

```text
validation\official_smoke_25.json
```

## 3. Run a five-game pilot

```powershell
& "$Work\4_Run_5_Easiest.ps1" `
    -EnvName "arc3-offline" `
    -Profile "quick"
```

The pilot uses the five smallest supplied baseline-action totals. It is the
right place to inspect traces, replay behavior, time limits, and action-budget
scaling before committing to the full suite.

## 4. Run all 25 offline

```powershell
& "$Work\5_Run_All_25_Offline.ps1" `
    -EnvName "arc3-offline" `
    -Profile "balanced" `
    -Order "easy"
```

The suite checkpoints after every game. Running the same command again resumes
and skips completed non-error results. Prior runtime errors are automatically
retried. Add `-RerunUnsolved` to rerun recorded games that completed without a
win.

For a shorter first pass use `-Profile quick`. For a larger budget use
`-Profile thorough`.

## 5. Summarize the current run

```powershell
& "$Work\6_Summarize_25_Results.ps1" -EnvName "arc3-offline"
```

The principal files are:

```text
results\suite_25\suite_plan.json
results\suite_25\suite_plan.csv
results\suite_25\suite_index.json
results\suite_25\suite_index.csv
results\suite_25\<game-id>\result.json
results\suite_25\<game-id>\trace.json
results\suite_25\<game-id>\posterior_trace.json
```

A per-game exception produces `failure.json` and `failure_traceback.txt` and
does not stop the rest of the suite.

## Run one specific game

```powershell
& "$Work\Run_One_Of_25.ps1" `
    -Game "ls20-9607627b" `
    -EnvName "arc3-offline" `
    -Profile "balanced"
```

## Offline contract

Every launcher sets:

```text
OPERATION_MODE=OFFLINE
ARC_API_KEY=
ARC_BASE_URL=http://127.0.0.1:9
KOMOREBI_ARC3_OFFLINE_ONLY=1
```

The Python runtime also blocks socket creation, DNS lookup, `urllib`, Requests,
and common HTTP clients before the official local wrapper is created.
