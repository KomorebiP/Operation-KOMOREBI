# Paper IX — first checked Lean block

**Komorebi P.** · Release 0.1.0 · 6 September 2026

## Result

Seven of the corrected manuscript's 24 named theorem, lemma, corollary and proposition items have checked formal coverage in this release. Seventeen remain pending. Three classical inputs and two conjectures are counted separately. The formalization contains **89 explicit theorem declarations and 22 definitions across eight modules**, all freshly compiled and audited.

Read `docs/Paper_IX_First_Lean_Block_Supplement.pdf` for the mathematical work and `docs/Paper_IX_First_Block_Ledger.md` for exact coverage. The authoritative first-block evidence is `verification/Paper_IX_First_Block_Verification.json`; the raw successful compiler logs are under `verification/first_final`.

The original 28-page status-corrected manuscript is unchanged in `paper/`. The release is a formalization companion, not a rewritten or completed Paper IX.

## Run the checks

Requirements: Linux x86-64 (or a compatible WSL environment), Python 3.10+, and the separately extracted Komorebi portable Lean kit. The large runtime is not included in this ZIP. The pinned runtime is Lean **4.34.0-rc2**, with Mathlib **aeb72f1e9981b6d35b426b16dca7759be3e7ba06**. All nine dependency revision pins are in `provenance/dependency_pins.json`.

From this extracted release:

```bash
bash Run-Portable.sh /path/to/Komorebi_Portable_Lean_4.34.0-rc2
```

This command runs the Python unit tests, the independent exact-rational regressions, and then a clean cumulative Lean build. Results go into a new time-stamped directory. It changes neither global environment settings nor the kit. No network access is needed once the exact kit is present. Native Windows behavior has not been tested.

The same stages can be run separately:

```bash
python -m unittest discover -s tests -v
python scripts/regressions.py
python scripts/verify.py --kit /path/to/Komorebi_Portable_Lean_4.34.0-rc2
```

The verifier refuses to reuse an existing run directory and checks source hashes against `inventory.json`. It builds in dependency order with warnings treated as errors, audits all explicit project theorems and definitions, and rejects three negative proof controls. The allowed transitive axioms are `propext`, `Classical.choice` and `Quot.sound`. A `sorry` control is rejected by warnings-as-errors policy, and `sorryAx` is independently excluded from the audit.

## What is proved

Items **1.2, 2.1, 2.2, 3.2, 3.3, 8.2 and 13.1** are covered: residue reconstruction/refinement, actual unit-EGF coordinate equivalence, coefficientwise filtered truncation (including actual p-adic integer specialization), the unique congruential Euler inverse, universal denominator clearing, Lucas standard-window reduction, and the sharp normalization counterexample.

For the normalized coefficients the checked counterexample is

\[
C_{6,3}(1)=-1/84,\quad C_{6,3}(2)=703/5460,\quad
C_{6,3}(2)-C_{6,3}(1)=64/455.
\]

Its 3-adic valuation is zero. Multiplying by `3!` gives `384/455`, whose valuation is one. These values are proved from the same recursive coefficient definition as the general inverse theorem. The general corrected finite-difference theorem (7.5) is **not** proved by this example and remains pending.

## Boundaries and failures

Formal series and coefficient identities do not certify analytic convergence. The generic two-powers-per-level tail lemma is not a proof of the Euler reconstruction formulas. Lucas' theorem is reused from the pinned Mathlib dependency. The original historical numerical program, full global finite-difference supplement, and original TeX were not recovered in this block.

The exact-rational Python checks are independent finite mirrors, not executions extracted from Lean. Mathlib's precompiled cache was reused, not independently rebuilt. The check covers explicit project declarations, not every automatically generated declaration or every imported Mathlib theorem.

All 29 captured development checks are retained: 15 passed and 14 failed before repair. A malformed generic-field draft triggered a release-candidate compiler panic after proof errors. The corrected source passed the clean final build. One earlier cumulative invocation was interrupted and is kept separately as incomplete. An initial test fixture had an incorrect whitespace expectation and was repaired. None of these failures is relabelled as success.

No Lean build products are distributed. The shipped hashes record the products of the observed run; future recompilation need not produce byte-identical binaries. Proof-source and document correspondence remains a mathematical review, not an automated proof that every manuscript sentence equals its Lean type.
