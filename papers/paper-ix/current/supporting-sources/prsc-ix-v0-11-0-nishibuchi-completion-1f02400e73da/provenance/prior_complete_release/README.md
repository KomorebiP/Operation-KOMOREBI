# Paper IX v0.10.0 — all-residue finite-difference completion

**Author: Komorebi P.**

All **24 of 24 named manuscript-proved items** in the status-corrected Paper IX register are now covered under their documented hypotheses. Three classical inputs and two unproved conjectures remain separately tracked. The original 28-page manuscript is preserved; the cumulative supplements and amendments remain part of the reading copy.

## Final theorem

Let `p` be prime, `m > 0`, `m | p-1`, `N=m*p`, `h=(p-1)/m`, and `0 <= j < N`. For the original rational coefficients defined by the triangular recurrence, set `E(n)=j! C_(N,j)(n)`. The final theorem proves integrality of `E(n)` and, for all natural `n,k,u`,

```
Delta_(u*h)^k E(n) = 0 OR v_p(Delta_(u*h)^k E(n)) >= min(k,m*n),
Delta_(u*h)^k C_(N,j)(n) = 0 OR
  v_p(Delta_(u*h)^k C_(N,j)(n)) >= min(k,m*n) - v_p(j!).
```

A separate theorem constructs the actual integral lift and proves divisibility by `p^min(k,m*n)` **in Z_p**, not in Q_p. Zero differences are handled correctly. The result includes the manuscript's odd-prime, positive-step case, and also zero steps and the `p=2,m=1` specialization. It is not a claim about a different external dyadic conjecture.

Principal declaration: `KomorebiPaperIX.Theorem75.global_finite_difference` in `formalization/Theorem75.lean`. The statement has only arithmetic parameter hypotheses. It does not assume flatness, a singular-ratio estimate, or the desired finite-difference bound.

## What closes the remaining proof

The previously saved v0.9.0 singular-ratio Amice estimate is preserved and used. The recovered failed `ThetaWeighted` draft is repaired. Its actual normalized operator preserves the complete weighted power-series ring. The proved exponential/logarithm substitution transfers this to all-order Hurwitz integrality for the actual singular ratios. A coefficientwise Picard argument propagates flatness through nonsingular addresses, and the proved telescoping ratio product identifies the final series with the original `j! C_(N,j)` coefficients.

The current corpus has **70 modules, 753 theorem declarations and 148 explicit definitions**, with **901 transitive-axiom reports**. The thirteen added modules contribute 123 theorems and twenty definitions. Counts include supporting lemmas and examples, not independent discoveries. All 57 v0.9.0 proof files, the original manuscript and previous supplements are byte-identical.

## Evidence and reading order

- `docs/Paper_IX_All_Residue_Completion_Supplement.pdf`: six-page completion proof and scope.
- `docs/Paper_IX_Finite_Completion_Ledger.md`, `coverage.json`: all registered items and exact targets.
- `docs/Paper_IX_Tenth_Block_Amendments.md`: final statement, normalization and trust boundary.
- `verification/tenth_clean/verification.json`: successful fresh cumulative Lean build and axiom audit.
- `verification/tenth_evidence/`: unit-test, regression, targeted-axiom and document-build records.
- `results/tenth_regressions.json`: independent exact-arithmetic mirror results.
- `development/`: 61 compiler records, including twelve failed development drafts and their repaired successors.
- `provenance/v0.9.0/`: frozen prior inventory, coverage, verifier and tests.
- `preserved_checkpoint/`: recovered prior research source, before the repairs.

The accompanying external release audit identifies the delivered ZIP hash and its fresh-extraction replay. Evidence produced by that replay is a separate artifact rather than a circular claim that a ZIP contains its own hash.

## Reproduce

The portable runtime is external and is not included in this source archive. It must provide Lean **4.34.0-rc2**, Mathlib `aeb72f1e9981b6d35b426b16dca7759be3e7ba06`, and the other eight revisions in `provenance/dependency_pins.json`.

```bash
python3 scripts/check_manifest.py
bash Run-Portable.sh /path/to/Komorebi_Portable_Lean_4.34.0-rc2
python3 scripts/check_manifest.py
```

The launcher runs **235 unit/infrastructure tests**, all ten block-level exact regression programs, and a clean cumulative build with **901 axiom reports and 33 negative controls**. It does not overwrite the frozen proof evidence. A timeout, missing import, panic or malformed prelude does not count as a meaningful rejection of a false theorem.

Proof-only run:

```bash
python3 scripts/verify.py --kit /path/to/Komorebi_Portable_Lean_4.34.0-rc2
```

The accepted axiom dependencies are subsets of `propext`, `Classical.choice` and `Quot.sound`. Warnings are errors. Axioms, admitted proofs and prohibited native-evaluation bypasses are rejected by the source and dependency checks.

## Boundaries

Mathlib's pinned compiled cache is reused, not independently rebuilt. Python regressions use exact arithmetic but are finite mirrors, not extracted Lean programs or replacements for the universal proofs. The original historical numerical suite and Papers I–VIII are not rerun. The two native conjectures remain unproved. General classical inputs are reused where documented. No independent historical-priority review, external theorem identification, or third-party proof replay is claimed. The prose-to-Lean correspondence remains mathematical review, not an automated semantic-equivalence theorem.

The primary manuscript has not been rewritten in this release. Read it with the cumulative supplements and amendments. Final manuscript integration and editorial proofreading remain distinct from completing the registered Lean proofs.
