# Komorebi Space: infinite diagonal Lean completion

Komorebi P.

This source and verification package completes the three Chapter 30 Lean translations that remained outside the formal coverage of the v1.13.0 publication. All three statements concern the actual infinite real Hilbert space. The previous publication remains an identifiable, unchanged parent of this continuation.

| Monograph result | Completed content | Main Lean declaration |
| --- | --- | --- |
| Proposition 30.1 | Actual square-summable optimizer and residual, four global bounds, and two certified omitted-tail bounds | `KomorebiSpace.DiagonalRegularization.proposition_30_1` and `a_unique_minimizer` |
| Theorem 30.2 | Both scalar limits with constant π/4, the exact budget limit over all real budgets, and the actual hard-prefix comparator with constant 1 | `KomorebiSpace.DiagonalRegularization.sharp_diagonal_budget_asymptotic` |
| Corollary 30.3 | Literal ceiling schedule and both deterministic noisy-error inequalities for the actual attainable datum | `KomorebiSpace.DiagonalRegularization.corollary_30_3` |

The mathematical model uses `lp (fun _ : ℕ => ℝ) 2`. Lean index `j` denotes printed coordinate `n = j + 1`; prefix length `K` is exactly the first `K` positive coordinates. The noise theorem constructs its bias estimate from the model and its proved series bounds. The budget theorem quantifies over `M : ℝ` tending to infinity.

## Verification

The seven new production modules and their import entrypoint compile with warnings rejected and automatic implicit binders disabled. A module-provenance inventory checks all 273 new exported declarations, including generated helpers. Their recursive axiom dependencies are contained in `propext`, `Classical.choice`, and `Quot.sound`; none is an unsafe or project-axiom declaration. Independent reviews match every conclusion of the three printed statements to the formal source.

The targeted control suite has two expected successes, five expected elaboration rejections, and one expected axiom-policy rejection. Deliberately invalid control files are stored outside the production source tree. The initial axiom-name matching bug in the control harness, its correction, and its rejected first run are retained. The parent publication's separate 44-control audit was not replayed in this continuation.

See `records/COMPLETION.json` for the final status and evidence links, `records/DIAGONAL_DECLARATIONS.json` for the full declaration inventory, `records/FINAL_REPLAY.json` for strict source-check commands, and `records/DIAGONAL_CONTROLS.json` for the control outcomes. `records/PROGRESS_LEDGER.jsonl` retains the chronological milestones. Failed source attempts and compiler logs are retained under `records/`, `logs/`, and `audit/`.

## Use and reproduce

Read `REPRODUCIBILITY.md` for the pinned environment and the host-specific compatibility disclosure. On an ordinary matching Lean installation:

```sh
cd lean
lake exe cache get
lake build KomorebiSpaceDiagonal
cd ..
python3 scripts/verify_diagonal.py --native
```

Import the completed diagonal development with:

```lean
import KomorebiSpaceDiagonal
```

The package contains the parent's complete Lean source tree plus these additions. The existing theorem sources and three original import entrypoints are preserved byte-for-byte. The configuration and usage documentation have been updated to expose the new import target. Compiler binaries, dependency caches, private transfer helpers, and machine-specific build symlinks are excluded from the archive.

## Scope

These results close the three recorded Chapter 30 formalization gaps. This statement does not assert that every sentence, illustration, or auxiliary discussion in the monograph is a Lean theorem. The printed proofs already existed; this continuation supplies their checked formal counterparts. Its asymptotic proof uses an equivalent monotone integral-comparison route, with `g = h - f`, in place of the monograph's compact-interval Riemann-sum presentation.

The v1.13.0 monograph, visual guide, publication PDF, and publication archive have not been regenerated. Their historical coverage labels should be updated when this source continuation is incorporated into a new publication edition.
