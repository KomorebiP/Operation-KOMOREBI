# Komorebi Physics — Lean Formalization
## Full edition, checked Blocks 01–06 · v0.6.0

**PASS: 483 theorem declarations, 579 named declarations, 29 mathematical modules, and 41 negative controls.** The completed verification result is in `verification/final/report.json`; a count alone is not a pass certificate. Block 06 adds **81 theorem declarations and eight definitions**, preserving all 25 previous mathematical source modules byte-for-byte. The cumulative total contains 444 full-edition theorem declarations and 39 recovered Paper VII theorems, not 483 independently discovered physical laws.

The included manuscript is the **550-page Projector-Refinement Physics: Complete Unified Theory**. Its recovered identity and page count were separately checked in `verification/block06_source_identity.json`, and its bytes are covered by the package manifest. Read `docs/BLOCK_06_PROOF_GUIDE.md`, `STATUS.md`, `docs/SOURCE_MAP.md`, and `docs/CLAIM_LEDGER.json` for exact assumptions and equation coverage. `CONTINUE_HERE.md` specifies the next block.

## Block 06

| Module | New theorems | Main result |
|---|---:|---|
| RefinementCancellation | 25 | Actual recursive tower and arbitrary-depth polynomial cancellation |
| RefinementAsymptotics | 17 | Genuine remainder propagation, positive-step limit and sharpness |
| RefinementBounds | 10 | Quantified truncation and sample-error bounds |
| RefinementExamples | 29 | Source formulas, nonzero cubic witness and invalid alternatives |

The recursion is `T_0 f(h)=f(h)` and `T_(m+1) f(h)=(b^(m+1) T_m f(h/b)-T_m f(h))/(b^(m+1)-1)`, with fixed b>1. Exact cancellation of degrees 1 through m is proved first. An explicit finite-order expansion of the original f then gives the genuine bound `T_m f(h)-F=O(h^(m+1))`, including a positive-step-only version.

The degree m+1 term is proved not generally to satisfy an extra order. Quantified error control keeps sample perturbations separate: refinement can amplify bounded sample noise, with a sharp first-level witness. No formal infinite series is assumed to converge, and no later physical discretization automatically inherits the input expansion.

## Run the cumulative verifier

```bash
python3 scripts/verify.py --kit /path/to/Komorebi_Portable_Lean_4.34.0-rc2 --out verification/recheck
```

The verifier checks the exact runtime/dependency pins, verifies the mathematical source-preservation hashes, removes local compiled outputs, recompiles all local modules with one worker and warnings as errors, audits all named declarations, and requires every negative control to fail for its designated proof diagnostic. Control bodies are unchanged and separately namespaced in one batch; a line-range map checks each diagnostic independently, rather than treating any nonzero exit as sufficient. Import errors and timeouts are not proofs or successful controls.

Lean is **4.34.0-rc2**, Mathlib **aeb72f1e9981b6d35b426b16dca7759be3e7ba06**. Nine dependency revisions and clean tracked trees are checked. Permitted axiom dependencies are only `propext`, `Classical.choice`, and `Quot.sound`. The imported dependency cache is reused, not independently rebuilt wholesale. No admitted active proofs or custom axioms are used.

Runtime assembler and checksums are included in `runtime_restore_support/`; the multi-gigabyte runtime and seven archive parts are not duplicated. `verification/block05_baseline/` contains the freshly reverified 402-theorem baseline. All earlier evidence and the successful/failed Block 06 development snapshots are retained. See `docs/BLOCK_06_FAILURES.md`.

## Recheck the packaged ZIP

```bash
python3 scripts/recheck_archive.py --archive /path/to/Komorebi_Physics_Lean_v0.6.0_Checked_Block_06.zip --kit /path/to/Komorebi_Portable_Lean_4.34.0-rc2 --destination /path/to/new-empty-parent --out /path/to/recheck-evidence
```

The destination must not exist. The script safely extracts, verifies checksums, invokes the extracted cumulative verifier, then compares proof inputs, theorem/declaration counts, dependency pins, and axiom inventories. It verifies checksums again afterward. This rebuilds all local proofs using the pinned imported cache; it is not an independent reconstruction of every foundational library.

## Boundaries and next target

This is a fixed-depth finite-expansion theorem, not a theorem about arbitrary h-dependent depths, an infinite refinement tower, automatic convergence of a formal series, or certified floating-point arithmetic. The sample-noise term remains explicit.

Earlier limits on ODE existence, positivity preservation, entropy boundary points, general-graph convergence, coarse Markov closure, unbounded/countable extensions, gravity, cosmology, and empirical adequacy remain in force. Chapter 3 still needs complete inventory. Keep the source's corrected dark-sector branch distinct from superseded additive branches.

**Next: Chapter 5.1–5.3, positive and overlapping operator atlases.** Derive the actual probability derivative, moving source term, and coarse current law without assuming idempotence or orthogonality. Chapter 5.4's Parseval-channel dilation is a subsequent target.
