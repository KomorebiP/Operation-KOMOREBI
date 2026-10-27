# Windows and Conda runbook — 25 supplied environments

## 1. Extract to a new folder

```text
C:\Users\<you>\Downloads\Komorebi_ARC_AGI3_Offline_25_Tests
```

The 25 local environment trees are already inside `environment_files`. Do not import or download games.

## 2. Reuse the existing `arc3-offline` environment

From Anaconda PowerShell Prompt:

```powershell
$Work = "$env:USERPROFILE\Downloads\Komorebi_ARC_AGI3_Offline_25_Tests"
Set-ExecutionPolicy -Scope Process Bypass -Force

& "$Work\Install_or_Repair_Arc3_Offline.ps1" -EnvName "arc3-offline"
```

The repair script reinstalls only the local Komorebi wheel with `--no-deps`. It does not replace the already installed official toolkit.

## 3. Validate every supplied environment

```powershell
& "$Work\1_Validate_25_Tests.ps1" -EnvName "arc3-offline"
& "$Work\2_List_25_Tests.ps1" -EnvName "arc3-offline"
& "$Work\3_Official_Smoke_All_25.ps1" -EnvName "arc3-offline"
```

The first command parses the metadata and source without executing the games. The second uses the official toolkit's local scanner. The third actually loads, resets, and steps each environment once.

## 4. Five-game pilot

```powershell
& "$Work\4_Run_5_Easiest.ps1" `
    -EnvName "arc3-offline" `
    -Profile "quick"
```

## 5. Full run

```powershell
& "$Work\5_Run_All_25_Offline.ps1" `
    -EnvName "arc3-offline" `
    -Profile "balanced" `
    -Order "easy"
```

Profiles:

```text
quick:     short diagnostic run
balanced:  default benchmark run
thorough:  extended run with larger action, probe, reset, and time budgets
```

The suite writes an index after every game. Repeating the same command resumes the suite, skips recorded non-error results, and reruns any game whose previous state was `ERROR`.

To rerun all recorded but unsolved games:

```powershell
& "$Work\5_Run_All_25_Offline.ps1" `
    -EnvName "arc3-offline" `
    -Profile "thorough" `
    -RerunUnsolved
```

## 6. Summary

```powershell
& "$Work\6_Summarize_25_Results.ps1" -EnvName "arc3-offline"
```

Primary files:

```text
results\suite_25\suite_index.json
results\suite_25\suite_index.csv
results\suite_25\<game-id>\result.json
results\suite_25\<game-id>\trace.json
results\suite_25\<game-id>\posterior_trace.json
```

## 7. Optional hardened run

`Run_Offline_Hardened.ps1` adds a temporary Windows Firewall outbound-block rule for the exact Conda Python executable. It requires an elevated PowerShell session.
