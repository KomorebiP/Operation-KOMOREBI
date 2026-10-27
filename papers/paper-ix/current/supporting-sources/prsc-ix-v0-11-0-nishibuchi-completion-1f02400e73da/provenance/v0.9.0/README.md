# Paper IX v0.9.0 — checked singular Amice estimate

**Author: Komorebi P.**

The weighted Amice coefficient estimate is now proved for the actual singular ratios `R_(a*p)`, for every permitted singular index `1 <= a < m`, with prime `p`, positive `m | p-1`, and `N=m*p`.

If `R_(a*p)(log(1+T)) = sum_d alpha_d T^d`, then every `p^floor(d/p) alpha_d` belongs to the actual completed ring `Z_p`. The rational statement uses `alpha_d = 0 OR v_p(alpha_d) >= -floor(d/p)`; it does not assign a finite valuation to zero as the meaning of unlimited precision.

## Exact status

**23 of 24 manuscript-proved items are fully covered. Theorem 7.5 remains pending as a full all-residue finite-difference theorem.** The new weighted ratio estimate still needs the dual Mahler polynomial filtration and integral pairing, followed by singular flatness, nonsingular ratio propagation and assembly of the entire Euler family. Neither of the two conjectures is resolved.

The cumulative corpus contains **630 explicit theorem declarations and 128 explicit definitions across 57 modules**. This block adds 104 theorems and 21 definitions across ten modules. Four modules contain previously compiled but unaudited research work; those four files are byte-identical to the preserved singular-residue attempt. Six modules are new in this continuation. Counts include supporting lemmas and examples, not independent discoveries.

All 47 active proof files from v0.8.0 are byte-identical. The original manuscript and earlier mathematical supplements are unchanged.

## What makes the result specific to the actual family

The integral cyclic-ring ideal bound is transferred to actual logarithmic section coefficients by a proved differential recurrence. The section is identified with the original `ExponentialSection.originalSection` used in the Euler project. The normalized denominator `U=c! T^(-c) H_(N,c)(log(1+T))` is constructed without inverting `T`; its factorization, constant term and weighted membership are proved. Inverse and differential closure of the weighted class are also proved. The ratio is independently defined from the original kernels before proving its cleared product identity and logarithmic decomposition. No weighted ratio estimate or flatness property is assumed.

## Read first

- `docs/Paper_IX_Singular_Amice_Supplement.pdf`: six-page mathematical development.
- `docs/Paper_IX_Ninth_Block_Amendments.md`: the exact new scope and remaining obligations.
- `docs/Paper_IX_Ninth_Block_Ledger.md` and `coverage.json`: full register, with item 7.5 still pending.
- `verification/ninth_clean/verification.json`: fresh cumulative compiler and axiom report.
- `verification/ninth_regressions/results.json`: independent finite exact-arithmetic checks.
- `verification/ninth_tests.log`: infrastructure and release tests.
- `verification/ninth_development/`: all new attempted Lean checks, including failed drafts and probes.
- `provenance/Paper_IX_Singular_Residue_Attempt.zip`: the original research checkpoint.

## Reproduce

The portable runtime is external. It must have Lean **4.34.0-rc2** and the dependency revisions recorded in `provenance/dependency_pins.json`, including Mathlib `aeb72f1e9981b6d35b426b16dca7759be3e7ba06`. No local precompiled proof modules are shipped.

```bash
python3 scripts/check_manifest.py
bash Run-Portable.sh /path/to/Komorebi_Portable_Lean_4.34.0-rc2
```

The launcher runs all **209 unit tests**, the eight prior independent finite regression programs, the new singular-Amice regressions, then a clean cumulative Lean build and all **758 requested axiom audits**. It also runs **29 invalid-proof controls**. New outputs do not replace the frozen evidence.

To run only the proof build:

```bash
python3 scripts/verify.py --kit /path/to/Komorebi_Portable_Lean_4.34.0-rc2
```

To rebuild the new supplement with `pdflatex` installed:

```bash
python3 scripts/build_ninth_supplement.py
```

The expected axiom set is contained in `propext`, `Classical.choice` and `Quot.sound`. Warnings are errors. A timeout, missing import, panic or invalid rewrite prelude is not accepted as a meaningful negative-control success.

## Boundaries

Mathlib's pinned compiled cache is reused, not rebuilt from source. Independent Python checks are finite mirrors, not Lean extraction or proofs of a universal statement. No historical numerical experiment suite, hardware benchmark, complete earlier paper, or conjecture is newly certified. The supporting prose proof's title uses the word “formal”; that title alone is not a claim that every step is already checked by Lean.

The external release audit records the exact archive hash and fresh-extraction replay. It is not an independent third-party verification. Manuscript-to-Lean correspondence remains mathematical review, not an automatically proved equivalence.
