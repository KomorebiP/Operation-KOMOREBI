# Paper IX — dyadic completion and Nishibuchi Conjecture 3.9

**Author: Komorebi P.**  Release `v0.11.0`.

## Mathematical scope

For each prime p, positive m with m | p-1 or m=2, and 0<=j<mp, the actual original unnormalized Euler coefficients are p-adically integral. Set q=lcm(2,p-1). For every r>=1 and n>=r,

    E_(mp*n + q*p^r)^(mp,j) = E_(mp*n)^(mp,j) mod p^r.

The capstone `KomorebiPaperIX.NishibuchiCompletion.conjecture_3_9` supplies both integrality and a positive threshold n0<=r, taking n0=r. It uses the literal degree-indexed coefficient convention of arXiv:2605.10677v2, Definition 2.1 and Conjecture 3.9. The new N=4 dyadic proof includes all four addresses. The N=4,j=0 special case already appears in the external paper; no priority for that case is claimed.

The 70 original v0.10.0 proof modules remain byte-identical. Nine additional modules prove the Newton-period implication, the enlarged differential closure, the four dyadic kernel identifications, and the exact external parameter/degree bridge. The combined inventory contains 836 named theorems, 162 definitions, and two abbreviations. Counts include supporting lemmas and specializations, not independent mathematical discoveries.

## Main files

- `docs/Nishibuchi_Conjecture_Completion.pdf` — five-page proof and verification supplement.
- `formalization/NishibuchiCompletion.lean` — complete external statement and assembly.
- `formalization/DyadicFourCongruences.lean` — new normalized/unnormalized N=4 higher differences and period.
- `formalization/DyadicFourDwork.lean` — actual (D^8-D^4)/2, source identification and reciprocal argument.
- `formalization/DyadicFourKernel.lean` and `KummerSequences.lean` — the four explicit source formulas and discrete closure.
- `formalization/PeriodFromDifferences.lean` — finite Newton expansion and prime-power period theorem.
- `conjecture_contract.json`, `contracts/ExternalStatement.lean.txt` — precise source comparison and compiler-checked statement contract.
- `verification/eleventh_clean/verification.json` — successful cumulative source build and audit when finalized.
- `provenance/prior_complete_release/fresh_baseline_verification.json` — separately rerun 70-module baseline, before extension.
- `development/eleventh_block/` — successful and failed development checks, separate from the release gate.

## Reproduce

The archive does not contain Lean or Mathlib. It uses the previously released offline Linux x86-64 runtime, pinned to Lean 4.34.0-rc2 and Mathlib revision aeb72f1e9981b6d35b426b16dca7759be3e7ba06. Extract that kit, then execute:

    bash Run-Portable.sh /path/to/Komorebi_Portable_Lean_4.34.0-rc2

The launcher checks manifest hashes, runs 25 extension tests and independent exact-rational regressions, builds all 79 active proof modules in a fresh directory, audits all 1,000 explicit theorem/definition/abbreviation targets, checks the capstone's exact type, and runs all 37 deliberate invalid-proof controls. It then checks the manifest again. The legacy `tests/` and earlier regression scripts are retained as history and are not silently counted as freshly rerun extension tests.

## Interpretation

The strengthened dyadic result is v2(Delta_u^k C_(4,j)(n))>=min(k,n), with zero differences handled explicitly. Its statement uses actual divisibility in Z2 and a separate correspondence with the rational sequence. It is not field divisibility. The theorem does not claim the dyadic exponent min(k,2n), the least period, the earliest starting index, or a pointwise optimal exponent. On the divisor branch, the existing stronger sufficient condition r<=m*n is retained by `divisor_period`.

The fixed original external source is Yuta Nishibuchi, *p-adic Congruences of Generalized Euler Numbers and Relations to Even Zeta Values*, arXiv:2605.10677v2, revised 1 June 2026. Conjecture 3.9 is a different target from Paper IX's two native Conjectures 13.2 and 13.3. Those two remain unproved. Paper IX's own 24-item proved register remains 24/24; it is not enlarged or renumbered here.

Axiom audits allow only propext, Classical.choice and Quot.sound. No project axiom, proof placeholder or native proof-evaluation shortcut is admitted in active source. Pinned Mathlib compiled dependencies are reused rather than rebuilt. No third-party proof checker or independent peer review was performed. Matching the external prose with the Lean types remains a mathematical review. No historical-priority claim is made relative to other unpublished work.

Original manuscripts, figures, historical numerical suites and Papers I–VIII were not regenerated. The new exact-rational checks are independent finite mirrors, not extracted Lean implementations and not substitutes for universal proofs.
