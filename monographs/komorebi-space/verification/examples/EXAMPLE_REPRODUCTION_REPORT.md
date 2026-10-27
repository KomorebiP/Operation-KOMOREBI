# Documented finite examples: fresh reproduction

**PASS.** The existing finite examples were executed on isolated, byte-identical copies of the accepted Space publication sources. The main publication and its figure assets were not edited.

The four documented entry commands completed successfully. The protected-repair, budgeted-repair and inexact-certificate demonstrations reproduced their preserved reference JSON exactly. The approximation command used the documented depth of 16 and ten steps, with exact reciprocal-difference and fixed-depth checks.

The worked proposal was generated, serialized and independently submitted to the program's verification entry point. Fourteen printed exact fields agreed, including the inherited-kernel normal residual, its squared norm, the primal and dual values, the duality gap and both squared-error bounds. A separate rational calculation of the fixed scalar quadratic confirmed its optimum, the actual squared errors and objective excess.

Both documented invalid cases were rejected with exit code 2 and their intended diagnostic:

- The correction `(1/4, 0)` was rejected because it changes protected data.
- A certificate whose objective was changed to zero was rejected because it differs from exact recomputation.

These are expected rejection outcomes, not failed mathematical experiments or infrastructure failures.

The existing visual wrapper completed both plotting scripts. Its 52 recorded checks passed across sixteen scenes. Eight checks concern the minimum figure text size. The other 44 records concern the specified algebraic or numerical examples, often grouping several explicitly enumerated values. They are not 52 independent theorems. The finite domains include all 64 two-bit phase triples, all sixteen scalar sign functions, fixed Euclidean and rational examples, and diagonal prefixes through 4096. Geometry and most analytic plotting checks use binary64 with the original stated tolerances. Four Gram-metric checks use exact rational arithmetic.

## Provenance and bounds

`runs/check01/manifest.json` is a validated version-2 computation record. Its actual run status is `completed`. It binds all nineteen declared audit inputs before and after execution, including sixteen unchanged files from the accepted publication, the two documented proposal fixtures and the small replay driver. The accepted archive identity is recorded in `EVIDENCE_SUMMARY.json`.

The run used Python 3.12.14, NumPy 2.3.5 and Matplotlib 3.10.8. The outer wall limit was 240 seconds, combined captured output limit 4 MiB, CPU affinity one core and conventional numerical-library thread limit one. No address-space or CPU-time cap was imposed. The outer run completed in approximately 11.8 seconds. Each child command had a 120-second timeout. The original visual wrapper additionally gives each of its two plotting scripts a 60-second timeout. No command timed out.

Nine command contracts and 35 audit checks passed. These counts overlap the preserved numerical and layout checks and must not be added as independent results. Complete argv arrays, actual exit statuses, expected diagnostics, output hashes and exact values are retained in `runs/check01/commands.json`, `runs/check01/summary.json` and the raw stdout/stderr files. `MANIFEST.json` inventories the complete evidence tree.

The original visual wrapper retains its static historical archive label in its version-1 report. The current version-2 record and the explicit source bindings identify the actual copied sources used here. No new revision is inferred from that historical label.

## Limits and a corrected reporting probe

The outcome is **documented results reproduced, with an orthogonal exact check of the worked scalar example**. It is not a universal Python-to-Lean refinement, independent proof of the entire implementation, interval certificate for plotting arithmetic, large-instance performance result, or proof of an infinite limit from finite sums. The mathematical and Lean statements provide their own separate evidence.

One post-run reporting probe failed with `KeyError: 'arithmetic'`. It assumed every visual-check record used that field, whereas eight older foundation records store detailed data under a different schema. The summary extraction was corrected to respect both schemas. The successful scientific run and its output records were not changed or rerun.

## Reproduce

Work in a copy of this evidence tree. The original command interfaces remain in `examples/README.md` and `examples/WORKED_EXAMPLE.md`. `run_suite.py` orchestrates precisely those documented commands and the printed-value checks. Create a new empty output directory under `runs/`, then run:

```sh
python3 -B run_suite.py runs/new_attempt
```

The new attempt must use a fresh directory. The script writes generated visual records and figures under `build/`, `records/` and `source/figures/` in that copy. To generate and validate a new bounded version-2 manifest, use the Mathbox computation-audit runner identified in `TOOLING_PROVENANCE.json`, updating the output/result paths in the retained launch record. Those external provenance helpers are not vendored as project code.
