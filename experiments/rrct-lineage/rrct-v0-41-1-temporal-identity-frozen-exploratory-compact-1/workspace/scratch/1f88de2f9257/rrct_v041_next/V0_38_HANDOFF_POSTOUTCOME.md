# RRCT v0.38 Post Outcome Handoff

## Completed block

v0.37 introduced action tails after hidden structural changes. The fresh D1 pilot passed 9 of 10 endpoints and failed only the remap public access threshold at 387/480.

v0.38 replaced the single centroid access decoder with a bounded FIFO one nearest exemplar memory. Four fresh seeds then passed all v0.38 endpoints and all inherited v0.37 endpoints.

## Primary result

| Quantity | Result |
|---|---:|
| Fresh seeds passing all endpoints | 4/4 |
| Median remap exact actions | 476/480 |
| Median restoration exact actions | 477/480 |
| Disconnection correct null actions | 480/480 on every seed |
| Complete sealed rows | 24,960 |
| Collectible tests | 398 passed, 2 skipped, 89 subtests passed |

## Critical files

- `validation/V0_38_ACCESS_GENERALIZATION_PROTOCOL.md`
- `validation/V0_38_PREOUTCOME_FREEZE.json`
- `validation/V0_38_COHORT_SUMMARY.json`
- `validation/V0_38_COHORT_REPORT_POSTOUTCOME.md`
- `validation/V0_38_POSTOUTCOME_AUDIT.json`
- `validation/V0_38_COHORT_ENDPOINTS_POSTOUTCOME.csv`
- `Verify_V038_Evidence.ps1`

## Windows verification

From the extracted repository root:

```powershell
powershell.exe -NoProfile -ExecutionPolicy Bypass -File .\Verify_V038_Evidence.ps1 -Python "$env:CONDA_PREFIX\python.exe"
```

The verifier runs the focused causal boundary suite, verifies the immutable pre outcome source archive, reparses the four row streams, recomputes the cohort endpoints, and exits nonzero if the cohort target is not reproduced.

## Next major block

The strongest next experiment is complete structural certificate access under repeated change. The public path should independently recover `(active, handle, source, rank)` and then survive multiple remap, contraction, disconnection, and restoration cycles without reset. That would test whether the system maintains a revisable structural identity rather than only a pair label.

The present result remains a bounded functional architecture result. It is not evidence of phenomenal consciousness.
