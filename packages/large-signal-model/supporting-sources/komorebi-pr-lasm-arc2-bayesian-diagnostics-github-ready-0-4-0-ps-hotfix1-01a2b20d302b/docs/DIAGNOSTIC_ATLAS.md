# Diagnostic atlas

PR-LASM ARC2 keeps exact ARC scoring unchanged. A task is solved only when one
attempt has the correct dimensions and every cell is equal to the expected
output. The diagnostic atlas adds partial measurements solely to explain
failures.

## Generated artifacts

A diagnostic run can write:

```text
index.html
summary.json
output_ledger.csv
near_misses.json
problems_and_solutions.jsonl
tasks/<task_id>_<test_index>.html
tasks/<task_id>_<test_index>.svg
tasks/<task_id>_<test_index>.json
```

Each task page contains all demonstrations, the held-out input, the expected
solution, both predictions, mismatch-highlighted grids, residual category maps,
cell agreement, color confusions, mismatch coordinates, the Bayesian posterior,
and the selected program records.

The residual map uses fixed diagnostic colors:

```text
0 black   correct cell
1 blue    extra predicted support
2 red     missing expected support
4 yellow  wrong nonbackground color
8 cyan    shape-only region
```

These colors are not task semantics and do not affect inference or scoring.

## Failure-stage diagnosis

The atlas separates two materially different failures:

1. `operator_or_representation_coverage`

   No candidate reproduces every demonstration exactly. Posterior reranking
   cannot solve this case by itself. The representation or typed operator
   grammar must be expanded.

2. `posterior_selection_or_few_shot_generalization`

   At least one candidate fits every demonstration exactly, but the selected
   test prediction is wrong. The remaining issue is ambiguity, parameter
   transfer, output-posterior aggregation, or ranking.

Severity is reported as `near_miss`, `partial_structure`, or
`representation_failure` from the best cell agreement. These labels are
engineering diagnostics, not ARC scores.

## PowerShell audit

```powershell
& .\powershell\Run_Diagnostic_Audit.ps1 -DataDir "$HOME\Downloads\ARC_AGI_2_OFFLINE_DATA" -Environment komorebi-full -MaxTasks 100 -DiagnosticLimit 100 -TimeLimit 0.05
```

The runner resolves `conda.exe` directly, including under `powershell.exe -NoProfile`. To override discovery:

```powershell
& .\powershell\Run_Diagnostic_Audit.ps1 -DataDir "$HOME\Downloads\ARC_AGI_2_OFFLINE_DATA" -Environment komorebi-full -CondaExecutable "$HOME\miniconda3\Scripts\conda.exe"
```

Set `-DiagnosticLimit 0` to render every selected output rather than the first 100. Rendering the entire 1,000-task training corpus creates a substantially larger atlas.

Open:

```text
results\diagnostic_atlas\index.html
```

## Direct command

```powershell
python -m komorebi_arc2 --input "$Data\arc-agi_training_challenges.json" --solutions "$Data\arc-agi_training_solutions.json" --output "$Repo\results\submission.json" --report "$Repo\results\report.json" --posterior-diagnostics "$Repo\results\posterior.json" --diagnostics-dir "$Repo\results\diagnostic_atlas" --diagnostic-limit 100 --time-limit 0.05 --report-failures 25
```

Add `--include-solved-diagnostics` when a matched problem/solution atlas is
needed for comparison with the failures.
