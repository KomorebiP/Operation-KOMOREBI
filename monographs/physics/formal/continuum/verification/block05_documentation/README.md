# Komorebi Physics — Lean Formalization
## Full edition, checked Blocks 01–05 · v0.5.0

**PASS: 402 theorem declarations, 490 named declarations, 25 mathematical modules and 34 negative controls.** Consult `verification/final/report.json` for the completed verification status. Block 05 adds **98 theorems and 20 definitions**, with all 20 Block 04 mathematical source files preserved byte-for-byte. The cumulative total contains 363 declarations authored in this full-edition program plus 39 recovered Paper VII theorems. Counts are not independent discoveries or a full-edition completion percentage.

The included source is the **550-page Projector-Refinement Physics: Complete Unified Theory**, not the short physics guide. Read `docs/BLOCK_05_PROOF_GUIDE.md`, `docs/SOURCE_MAP.md`, `STATUS.md` and `CONTINUE_HERE.md` for assumptions, equation coverage and remaining obligations.

## Block 05

| Module | New theorems | Content |
|---|---:|---|
| LindbladJumps | 26 | Actual square-root jump matrices, full generator, actual diagonal derivatives and trace/boundary balance |
| DetailedBalance | 28 | Relative-entropy derivative and monotonicity, explicit zero-rate domain treatment, equality conditions and original-matrix bridge |
| LindbladDynamics | 14 | Constructed coordinate atlas, coherent-plus-jump evolution, exact coarsening and information derivatives |
| LindbladCoherence | 5 | Exact off-diagonal generator and actual coherence derivative |
| LindbladExamples | 25 | Exact nonzero mixed-state rates and counterexamples to invalid simplifications |

The literal targets are Chapter 4.7 (4.45–4.52) and 4.8 (4.53–4.58). The population and entropy derivatives start from the actual matrix derivative; no separate scalar gain–loss law is inserted into the matrix theorem. Coherent inputs are allowed. Detailed-balance dissipation includes zero-rate edges through an explicit inactive-edge convention, with positivity of every active logarithm argument proved. It concerns classical population relative entropy, not quantum relative entropy.

## Verify locally

Use Linux x86-64 or WSL with the restored exact-pin kit:

```bash
bash run_checks.sh /path/to/Komorebi_Portable_Lean_4.34.0-rc2
```

Or choose a separate evidence directory:

```bash
python3 scripts/verify.py --kit /path/to/Komorebi_Portable_Lean_4.34.0-rc2 --out verification/local_run
```

Lean is **4.34.0-rc2**, Mathlib **aeb72f1e9981b6d35b426b16dca7759be3e7ba06**. The verifier checks all nine exact dependency revisions and clean tracked trees, deletes local compiled outputs, rebuilds every mathematical module plus the aggregate with one worker and warnings as errors, audits all named declarations, and tests every negative control for its intended proof diagnostic. Import errors and timeouts are not proofs or successful controls.

Allowed axiom dependencies are restricted to `propext`, `Classical.choice` and `Quot.sound`. There are no admitted active proofs, custom axioms or native-evaluation escapes. The imported dependency cache is used, not rebuilt wholesale. Runtime assembler/checksums are included under `runtime_restore_support/`; the multi-gigabyte runtime and seven archive parts are not bundled.

`verification/block04_baseline/` holds the freshly rerun 304-theorem starting point. Previous final reports, original documentation snapshots, and both failed and successful development attempts are retained. `docs/BLOCK_05_FAILURES.md` records this block's actual failures and repairs.

## Recheck the ZIP

```bash
python3 scripts/recheck_archive.py --archive /path/to/Komorebi_Physics_Lean_v0.5.0_Checked_Block_05.zip --kit /path/to/Komorebi_Portable_Lean_4.34.0-rc2 --destination /path/to/new-empty-parent --out /path/to/recheck-evidence
```

The destination must not exist. The script safely extracts, verifies checksums, invokes the extracted cumulative verifier, then rechecks hashes and compares proof inputs, counts, dependency pins and axiom inventories. It is a fresh local-proof compilation using the same pinned imported cache, not an independent rebuild of all foundational libraries.

## Boundaries and next target

No ODE existence/uniqueness, positivity-preserving dynamical semigroup, positivity from initial data, zero-probability or q=1 entropy limit, universal entropy monotonicity, general-graph convergence, closed coarse rate model without lumpability, unbounded/countable extension, or gravity/cosmology/empirical verification is claimed. The affine matrix examples satisfy the original derivative at zero only.

**Next: Chapter 4.9 (4.59–4.67), general refinement-cancellation towers.** Prove exact coefficient cancellation separately from asymptotic remainder control, then read the next source pages. Chapter 3 remains incompletely inventoried. The source's later corrected dark-sector branch must remain distinguished from superseded additive branches.
