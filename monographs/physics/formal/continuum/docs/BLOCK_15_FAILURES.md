# Block 15 failures, repairs and boundary counterexample

## Mathematical boundary found

The source's compact reconstruction statement cannot be read as a theorem about arbitrary strongly convergent approximations without further cutoff control. A constructed uniformly bounded (norm<=2) non-self-adjoint family S_n=I+|e0><e_(n+1)| converges strongly but has compact sandwich error exactly one. This is a proved counterexample to the overly broad reading, not a failed implementation. The actual strong-atlas cutoffs satisfy the stronger self-adjoint contractive hypotheses used by the checked positive theorem.

## Development compilations

There were **15 failed mathematical development compilations** among 25 retained compilation receipts. Ten receipts have exit code zero, including the final versions of all eight new modules. The failures are retained byte-for-byte with source snapshot, command, exit code, duration and raw diagnostics under `verification/development/block15/`. A failed attempt is not included as a checked proof.

Repairs addressed deprecated/mismatched APIs, an inner-product/norm instance mismatch, actual lp-column membership construction, namespace/section-scoping and warnings-as-errors checks, partial-operator coercions, and exact basis/series normalization. The first column construction and the first geometric-symbol constructor caused cascading kernel/metavariable diagnostics in dependent declarations; repairing the constructors removed the cascades. Overly broad simp on an adjoint identity looped, and over-general shift inference hit the default elaboration heartbeat limit. Specializing the rewrites and supplying the explicit shifted function fixed those errors. No admission, custom axiom, weakened mathematical conclusion or kernel-bypass setting was used.

| Snapshot | Module | Exit | First diagnostic |
|---|---|---:|---|
| `20260914T100335905224Z` | `KomorebiPhysics.StrongReconstruction` | 1 | KomorebiPhysics/StrongReconstruction.lean:3:0: warning:  |
| `20260914T100634130843Z` | `KomorebiPhysics.CompactReconstruction` | 1 | KomorebiPhysics/CompactReconstruction.lean:57:19: error: try 'simp' instead of 'simpa' |
| `20260914T100725326189Z` | `KomorebiPhysics.CompactReconstruction` | 1 | KomorebiPhysics/CompactReconstruction.lean:80:4: error: Type mismatch: After simplification, term |
| `20260914T101155208718Z` | `KomorebiPhysics.HilbertSchmidtCore` | 1 | KomorebiPhysics/HilbertSchmidtCore.lean:29:8: error: Tactic `rewrite` failed: Did not find an occurrence of the pattern |
| `20260914T101336690092Z` | `KomorebiPhysics.HilbertSchmidtCore` | 1 | KomorebiPhysics/HilbertSchmidtCore.lean:65:73: error: unexpected token 'omit'; expected 'lemma' |
| `20260914T101651489082Z` | `KomorebiPhysics.HilbertSchmidtReconstruction` | 1 | KomorebiPhysics/HilbertSchmidtReconstruction.lean:18:0: error: automatically included section variable(s) unused in theorem `KomorebiPhysics.HilbertSchmidtReconstruction.left_energy_tendsto`: |
| `20260914T102108368589Z` | `KomorebiPhysics.AtlasReconstruction` | 1 | KomorebiPhysics/AtlasReconstruction.lean:22:21: error: `ContinuousLinearMap.sum_apply` has been deprecated: Use `sum_apply` instead |
| `20260914T102225569559Z` | `KomorebiPhysics.GraphReconstruction` | 1 | KomorebiPhysics/GraphReconstruction.lean:43:2: error: Type mismatch: After simplification, term |
| `20260914T102253477260Z` | `KomorebiPhysics.GraphReconstruction` | 1 | KomorebiPhysics/GraphReconstruction.lean:45:2: error: Type mismatch: After simplification, term |
| `20260914T102518677014Z` | `KomorebiPhysics.HilbertSchmidtExamples` | 1 | KomorebiPhysics/HilbertSchmidtExamples.lean:20:0: error: Not a definitional equality: the left-hand side |
| `20260914T102607682200Z` | `KomorebiPhysics.HilbertSchmidtExamples` | 1 | KomorebiPhysics/HilbertSchmidtExamples.lean:20:65: error: unsolved goals |
| `20260914T102729443766Z` | `KomorebiPhysics.HilbertSchmidtExamples` | 1 | KomorebiPhysics/HilbertSchmidtExamples.lean:22:20: error: This simp argument is unused: |
| `20260914T102826730159Z` | `KomorebiPhysics.HilbertSchmidtExamples` | 1 | KomorebiPhysics/HilbertSchmidtExamples.lean:85:16: error(lean.unknownIdentifier): Unknown constant `Nat.not_add_lt_right` |
| `20260914T103032574143Z` | `KomorebiPhysics.ReconstructionExamples` | 1 | KomorebiPhysics/ReconstructionExamples.lean:107:58: error: unsolved goals |
| `20260914T103103322854Z` | `KomorebiPhysics.ReconstructionExamples` | 1 | KomorebiPhysics/ReconstructionExamples.lean:108:15: error: Tactic `rewrite` failed: Did not find an occurrence of the pattern |

## Baseline, runtime and release audit

The unchanged Block 14 project was restored and freshly passed its full 78-module/1,260-theorem/1,502-name/101-control audit before the cumulative inventory was extended. Its fresh records are preserved at `verification/block14_baseline_fresh/`.

Runtime assembly verified all seven part hashes and the combined archive hash before extraction. Its restoration log is retained in `verification/environment/block15_runtime_restore.log`. The imported Lean/Mathlib cache was reused, not independently rebuilt wholesale. Runtime bytes are not bundled.

The complete Block 15 production audit passed on its first cumulative run. Its completed `verification/final/report.json` is authoritative. No cumulative mathematical or negative-control failure was suppressed. Seven new invalid controls are deliberately expected to fail for their designated proof diagnostic; each requires its own mapped diagnostic. A timeout, syntax error, import error or a nonzero batch exit without all designated diagnostics is an audit failure. The separate fresh-extraction report is delivered outside the unchanged final ZIP.

An exploratory shell inspection initially requested a nonexistent restoration-script pathname. It did not run a restoration or verify anything. The actual `runtime_restore_support/assemble.py` was then located and used successfully. No runtime or baseline success is inferred from that failed inspection.

## Metadata reconciliation before the final archive

The inherited `reference/source_manifest.json` still named Chapter 5 as its next target from Block 06. This stale metadata was preserved in the Block 14 documentation snapshot and updated to Chapter 7, with the new Section 6.8 scope recorded separately. The preliminary ZIP candidate was superseded before any extraction recheck. Mathematical sources, the source PDF and the completed proof audit were unchanged.
