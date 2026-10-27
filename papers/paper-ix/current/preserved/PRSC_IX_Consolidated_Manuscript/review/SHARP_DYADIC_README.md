# Paper IX: sharp dyadic towers and all-row Nishibuchi strengthening

**Author: Komorebi P.** Continuation date: 8 September 2026.

The later Paper IX manuscript did contain sharper edge towers and an optimal dyadic Euler tower. This continuation recovers those statements, closes the missing sharp dyadic formalization, and proves an all-row theorem for the four generalized N=4 packets. The classical tower and generalized packets have separate complete proofs.

## Checked advances

Write C_(4,j)(n) for the normalized packet coefficient and U_j(n)=j! C_(4,j)(n)=E^(4,j)_(4n) for Nishibuchi's original coefficient. Differences use packet step u. Every valuation lower bound is zero-safe: a zero difference satisfies every requested precision.

1. **All rows and all four addresses.** For j<4 and all nonnegative u,k,n,

   `v2(Delta_u^k C_(4,j)(n)) >= k(1+v2(u))`,

   `v2(Delta_u^k U_j(n)) >= k(1+v2(u)) + v2(j!)`.

   The old minimum with n is gone. These are genuine Z2 divisibility theorems with explicit rational-coefficient bridges. At u=0, positive-order differences vanish; Lean's natural valuation convention v2(0)=0 does not affect validity.

2. **Periods from row zero.** For r>=1, n>=0 and j<4,

   `U_j(n+2^(r-1)) = U_j(n) (mod 2^r)`.

   The original degree displacement is 2^(r+1). For j=2,3 and r>=2 the sufficient packet period halves to 2^(r-2), or degree displacement 2^r, again at every row. At precision one these two addresses vanish modulo two everywhere. Least periods are not claimed.

3. **Recovered optimal classical dyadic tower.** For the signed Euler coefficients E_(2n) of sech(z) and the existing truncation T_M(n),

   `E_(2n) - T_M(n) belongs to 2^(4M+3) Z2`.

   This upgrades the earlier formalized exponent 2M+2. At packet row n=M+1, equivalently Euler degree 2M+2, the error has valuation exactly 4M+3. Hence the uniform exponent is optimal. For 1<=m<=n the m-th summand has exact valuation

   `4m-1 + v2(binomial(2n,2m))`.

   Any lower bound on the omitted term weights gives a tail bound. Cancellation can raise the tail valuation, so the minimum need not be exact. Empty tails are zero. The recovered manuscript gives the binary-carry interpretation; Lean states the binomial valuation directly.

4. **Divisor-branch step amplification.** For any prime p, m>0 dividing p-1, j<mp and natural u,k,n,

   `v_p(Delta_[u(p-1)/m]^k (j! C_(mp,j))(n)) >= min(k(1+v_p(u)),m*n)`.

   The normalized statement subtracts v_p(j!). This separate branch retains its row cap. The generic Newton argument is independently available.

## Proof mechanisms

The all-row proof uses the charged operator A_c=(D^4-c)/2 on Hurwitz integral series. Its product formula adds charges, with integral middle coefficients 2,3,2. Reciprocal closure changes charge 1 to -1; shifting it back by two costs no denominator. The actual N=4 sources satisfy the required all-order bounds. Applying closure to their actual reciprocals and extracting coefficients yields the full exponent without shifting the row. The earlier (D^8-D^4)/2 route introduced the cap.

The classical tower separately derives the actual coefficient identity

`kappa_m = -2^(4m)(2m-1) B_(2m)` for m>0,

then uses the pinned Mathlib theorem v2(B_(2m))=-1. The exact kernel valuation 4m-1 is proved, not introduced as a hypothesis.

## Main files

All new active Lean sources are in strengthening/formalization/.

| File | Purpose |
| --- | --- |
| ChargedDworkClosure.lean | Product, reciprocal, and charge-shift closure |
| DyadicFourAllRows.lean | Actual source-to-reciprocal all-row bridge |
| DyadicFourFinalStrengthening.lean | Final uncapped bounds and periods in the original degree convention |
| DyadicSharpTower.lean | Exact kernel valuation, sharp tail, optimality, and row weights |
| StepAmplification.lean | Generic gain from displacement valuation |
| AllResidueStepAmplification.lean | Actual divisor-branch specialization |
| DyadicStepAmplification.lean; DyadicFourSharpening.lean | Checked intermediate bounds and factorial gain |
| StepAmplificationExamples.lean; AllRowsControls.lean | Boundary examples and universal statement controls |

The original v0.11.0 source ZIP remains in baseline/. Its full Conjecture 3.9 completion and the prior native continuation are retained unchanged. The all-row statements above supersede the weaker dyadic bounds in that historical baseline's README.

## Verification and reproduction

**Observed combined result: PASS.** Ten fresh new module builds, 109/109 explicit declaration axiom audits, six correctly rejected invalid-proof controls, and a compiler-checked final statement contract. The ten modules contain 100 named theorems, eight definitions and one abbreviation. Counts include supporting lemmas and controls, not independent mathematical discoveries.

The combined run reused the fresh 79-module baseline replay from this conversation, first checking its source inventory and every recorded compiled-file hash. Mathlib was not rebuilt. All new declaration audits contain only propext, Classical.choice and Quot.sound. No project axiom, proof placeholder or native proof-evaluation shortcut is admitted. The exact record and logs are in strengthening/verification/.

Use the existing Linux runtime pinned to Lean 4.34.0-rc2 and Mathlib revision aeb72f1e9981b6d35b426b16dca7759be3e7ba06:

```sh
python3 replay_sharpened.py --kit /absolute/path/to/Komorebi_Portable_Lean_4.34.0-rc2 --output /absolute/path/to/new_replay
```

This invokes the original complete baseline replay, the prior native affine continuation, and the new dyadic continuation. It downloads no dependencies. For a previously checked baseline, strengthening/scripts/verify_strengthening.py accepts --baseline-root and --baseline-build. The full wrapper is provided for reproduction; this continuation's observed run used the latter mode and did not unnecessarily repeat the already successful baseline/native builds.

## Recovery and scope

strengthening/recovery/RECOVERED_EDGE_TOWERS.md maps the historical odd edge formulas, literal dyadic inversion, and later sharpening to their user-owned source files. Full text reads succeeded where byte downloads returned HTTP 502. The included Annals TeX is a retrieved textual copy, without a byte-identity claim.

The historical odd edge tower is recovered and documented; this continuation does not claim to freshly formalize every older odd-edge formula. A uniform additional dyadic digit is false in general: the normalized N=4,j=0 first difference at row one equals 70 and has valuation exactly one.

The unrestricted native Conjectures 13.2 and 13.3 remain separate and unproved in their original generality. Their prior checked finite affine obstruction theorem and scoped progress notes remain in native/. No publication-priority claim is made. Independent agent mathematical review was performed; human peer review and an independent proof-checking implementation were not.
