# Windows PowerShell commands

## Extract and smoke test

```powershell
$z=Get-ChildItem "$env:USERPROFILE\Downloads\OSL_HuggingFace_Operand_Slot_Lab_v0.3.1*.zip" | Sort-Object LastWriteTime -Descending | Select-Object -First 1; if (-not $z) { throw "v0.3.1 ZIP not found in Downloads" }; $d=Join-Path "$env:USERPROFILE\Downloads" ("OSL_HF_v031_" + (Get-Date -Format "yyyyMMdd_HHmmss")); Expand-Archive -LiteralPath $z.FullName -DestinationPath $d -Force; & "$d\osl_hf_slot_causal_v0_3\Run_OSL_HF_Test.ps1" -Profile smoke -Python "$env:CONDA_PREFIX\python.exe" -Device cuda
```

## Full run after smoke succeeds

Run this in the same PowerShell window; `$d` was set by the extraction command.

```powershell
& "$d\osl_hf_slot_causal_v0_3\Run_OSL_HF_Test.ps1" -Profile full -Python "$env:CONDA_PREFIX\python.exe" -Device cuda -SkipInstall
```

## Full run with a smaller CUDA batch

```powershell
& "$d\osl_hf_slot_causal_v0_3\Run_OSL_HF_Test.ps1" -Profile full -Python "$env:CONDA_PREFIX\python.exe" -Device cuda -SkipInstall -BatchSize 32
```

## Resume

```powershell
& "$d\osl_hf_slot_causal_v0_3\Run_OSL_HF_Test.ps1" -Profile full -Python "$env:CONDA_PREFIX\python.exe" -Device cuda -SkipInstall -Resume -Output "C:\path\to\the\interrupted\results_full_timestamp"
```

## Verify the extracted package only

```powershell
& "$d\osl_hf_slot_causal_v0_3\VERIFY_PACKAGE.ps1" -Python "$env:CONDA_PREFIX\python.exe"
```

## Output

Return `RETURN_THIS_OSL_HF_RESULTS.zip` from the newly created results directory. On failure, return `FAILED_OSL_HF_V03_*.zip` from the package directory.
