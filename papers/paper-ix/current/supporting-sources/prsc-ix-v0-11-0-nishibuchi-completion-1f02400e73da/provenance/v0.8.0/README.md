# Paper IX v0.8.0 — checked eighth block

**Author: Komorebi P.**

This source-and-evidence release continues the unchanged 28-page status-corrected Paper IX and the v0.7.0 checked sources. The main new result is the **full higher-power finite-difference bound for the actual Euler packets in every standard-window residue `0 <= j < p`**, not merely a period modulo `p`.

## Scope

**23 of 24 named manuscript-proved items are fully covered. Theorem 7.5 remains pending as an all-residue theorem.** The cumulative inventory contains **526 explicit theorem declarations and 107 explicit definitions across 47 modules**. The nine new modules add 87 theorem declarations and 13 definitions. Supporting lemmas, examples and earlier conditional implications are included; these are not counts of independent discoveries.

For prime `p`, positive `m | p-1`, `h=(p-1)/m`, and `j<p`, the actual original normalized and unnormalized rational Euler coefficients satisfy

    v_p(Delta_(u*h)^k C_(m*p,j)(n)) >= min(k,m*n),

with a separate zero case and genuine ideal divisibility in `Z_p`. This holds for every natural row, order and step multiplier. For `m=1` it includes all permissible residue labels. For `m>1`, the interval `p <= j < m*p` is still pending. The three classical inputs and two conjectures remain separately tracked.

The closure proofs derive the characteristic-zero product correction for `(D^(p^2)-D^p)/p`, then establish product and reciprocal closure to every order in the actual integral Hurwitz lattice. The source flatness proof uses the actual Euler-operator commutator and proved unit pivots, not an assumed flatness certificate. The reciprocal is identified with the original generating-function family before extracting differences.

## Read first

- `docs/Paper_IX_Eighth_Lean_Block_Supplement.pdf`: six-page mathematical development.
- `docs/Paper_IX_Eighth_Block_Amendments.md`: the new standard-window theorem and precise singular-residue boundary.
- `docs/Paper_IX_Eighth_Block_Ledger.md` and `coverage.json`: full register, with item 7.5 still pending and partial targets separate.
- `verification/eighth_final_corrected/verification.json`: clean cumulative Lean build and all axiom reports after the negative-control prelude repair.
- `verification/eighth_final/verification.json`: earlier unsuccessful release gate, preserved as failed; its new control had an invalid rewrite prelude.
- `verification/eighth_baseline/verification.json`: successful unchanged 38-module baseline replay.
- `verification/eighth_infrastructure/`: unit-test logs.
- `verification/eighth_regressions/`: deterministic exact finite mirrors.
- `verification/eighth_development/`: failed and successful development source snapshots and diagnostics.
- `provenance/global_argument_source/`: preserved 18-page supporting prose proof. The word "formal" in that document's title does not mean kernel-checked Lean.

All 38 upstream active proof files, the original manuscript and the seven earlier supplements remain byte-identical. Historical metadata snapshots and earlier run statuses are retained. The active verifier and tests extend the inventory without changing earlier mathematical proof bodies.

## Repeat the checks

The portable runtime is separate. Use its extracted kit root, not a part ZIP. Required Lean version: **4.34.0-rc2**; package revisions are in `provenance/dependency_pins.json`.

```bash
python3 scripts/check_manifest.py
bash Run-Portable.sh /path/to/Komorebi_Portable_Lean_4.34.0-rc2
```

The launcher runs all **189 unit tests**, all eight cumulative independent regression programs, and a clean cumulative Lean build. It audits all **633 explicit declarations** and executes **27 invalid-proof controls** with warnings treated as errors. Missing imports, timeouts, compiler panics, and failed rewrite preludes are not accepted as meaningful negative-control successes. New runs create their own outputs under `verification/` instead of replacing frozen evidence.

For the proof build alone:

```bash
python3 scripts/verify.py --kit /path/to/Komorebi_Portable_Lean_4.34.0-rc2
```

To rebuild the latest supplement, with pdflatex installed:

```bash
python3 scripts/build_eighth_supplement.py
```

## Trust and limitations

The allowed transitive axioms are `propext`, `Classical.choice`, and `Quot.sound`. The bundle contains sources and evidence, not the runtime or prebuilt local `.olean` files. Mathlib's pinned compiled cache is reused, not independently rebuilt. No original historical numerical suite, hardware benchmark, or complete earlier paper is rerun. Independent Python mirrors are finite checks, not extracted Lean programs.

The higher-residue singular estimates required by all-residue Theorem 7.5 are still missing. The new window theorem is an infinite family, not a finite sample, but does not prove the remaining interval. No all-residue completion, conjecture resolution, or proportion of research effort completed is claimed. Manuscript-to-Lean correspondence remains mathematical review rather than an automatically checked equivalence.

The accompanying external release audit records archive CRC/hash checks and the fresh-extraction launcher replay of that exact ZIP. See `DEVELOPMENT_NOTES.md` for failures and repairs.
