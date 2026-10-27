# Paper IX: exact dyadic displacements and least packet periods

**Author: Komorebi P.** Continuation date: 8 September 2026.

This block proves the least-period classification proposed in the prior brainstorm. It uses the actual generalized Euler coefficients, all natural rows, and every positive shift. The proof goes beyond finding a sufficient power-of-two period: it characterizes all positive periods.

## Main theorem

Let

\[
U_j(n)=E_{4n}^{(4,j)}=j!C_{4,j}(n),\qquad 0\le j<4,
\]

and put \((d_0,d_1,d_2,d_3)=(1,1,5,3)\). For every \(n\ge0\) and \(T>0\),

\[
U_j(n+T)-U_j(n)\ne0,
\qquad
\boxed{v_2\bigl(U_j(n+T)-U_j(n)\bigr)=v_2(T)+d_j.}
\]

For every integer precision exponent \(r\ge0\), a positive packet shift \(T\) is a period modulo \(2^r\) exactly when

\[
\boxed{2^{\max(0,r-d_j)}\mid T.}
\]

The word period means that the congruence holds for **every** row \(n\ge0\). Thus the least positive packet periods are exactly:

| Address | Exact displacement gain | Least positive packet period modulo \(2^r\) |
|---|---:|---|
| \(j=0\) | \(1\) | \(2^{\max(0,r-1)}\) |
| \(j=1\) | \(1\) | \(2^{\max(0,r-1)}\) |
| \(j=2\) | \(5\) | \(2^{\max(0,r-5)}\) |
| \(j=3\) | \(3\) | \(2^{\max(0,r-3)}\) |

In particular, \(U_2(n)\equiv2\pmod{32}\) and \(U_3(n)\equiv6\pmod8\) for every row. At precision \(2^{10}=1024\), the respective least packet periods are \(512,512,32,128\).

For the normalized sequences, the exact gains are \((1,1,4,2)\). The difference is the address factorial. Zero shift is excluded from the nonzero/exact-valuation theorem. Precision zero is permitted by the formal period statements and correctly gives least positive period one.

A packet shift \(T\) corresponds to original degree displacement \(4T\), and this exact degree correspondence is proved. The least-period assertion concerns packet shifts. It does not claim that multiplying by four gives the least period among all shifts of the full degree-indexed sequence, including its off-support zero coefficients.

## How the proof closes the gap

For any rational sequence \(f\), let \(a_k=\Delta_1^k f(0)\). The new generic theorem assumes

\[
a_1\ne0,\quad v_2(a_1)=c,\quad
v_2(a_k)\ge c+1+\lfloor\log_2 k\rfloor\quad(k\ge2),
\]

with zero-safe higher-coefficient bounds. It proves

\[
f(n+T)-f(n)\ne0,\qquad
v_2(f(n+T)-f(n))=v_2(T)+c.
\]

Finite Newton reconstruction first translates the coefficient bounds to each row. The binomial identity

\[
k\binom Tk=T\binom{T-1}{k-1}
\]

then bounds every positive-order displacement coefficient. Every term beyond the leading one has strictly higher valuation, so it cannot cancel the leading contribution. There is no infinite-series convergence premise in this proof.

For the actual normalized packets, the earlier all-row Lean theorem supplies \(v_2(a_{j,k})\ge k\). Uniform logarithmic threshold lemmas reduce the stronger envelope to a finite prefix. Every required coefficient was proved in Lean from the actual binomial triangular recurrence. The supporting computations are not assumed as a table.

| Address | Valuation of \(a_{j,1}\) | Additional prefix valuations used |
|---|---:|---|
|0|1|\(k=2:\ 3\)|
|1|1|\(k=2:\ 3\)|
|2|4|\(k=2,\ldots,6:\ 6,9,13,16,22\)|
|3|2|\(k=2,\ldots,4:\ 8,8,15\)|

Multiplying by \(j!\) produces the original-coefficient gain \(d_j\). A final generic theorem turns exact displacement valuations into divisibility classification and an actual \(\operatorname{IsLeast}\) statement.

## New source modules

All active sources are in strengthening/formalization/.

| Module | Role |
|---|---|
| DyadicLogThresholds.lean | Uniform logarithmic arithmetic thresholds |
| NewtonDominance.lean | Generic translated Newton bounds and exact leading-term dominance |
| DyadicFourPrefix.lean | Actual recurrence coefficients, Mahler coefficients, exact valuations, and full envelope |
| ExactPeriodClassification.lean | Exact valuation law implies all-positive-period classification and least period |
| DyadicFourLeastPeriods.lean | Original \(N=4\) sequence, factorial gain, exact periods, and degree bridge |
| ExactPeriodControls.lean | Precision boundaries, non-power-of-two periods, minimality and nonzero controls |

Main declarations are:

- `KomorebiPaperIX.DyadicFourLeastPeriods.exact_displacement`
- `KomorebiPaperIX.DyadicFourLeastPeriods.period_iff_dvd`
- `KomorebiPaperIX.DyadicFourLeastPeriods.least_packet_period`
- `KomorebiPaperIX.DyadicFourLeastPeriods.original_degree_exact_displacement`

## Validation and reproduction

The final observed result is recorded in RELEASE_AUDIT.json and strengthening/verification/continuation_verification.json. The combined gate builds the previous ten continuation modules plus these six modules, audits every explicit declaration, and runs the old and new statement contracts and invalid-proof controls. No placeholder or custom project axiom is admitted. Permitted axioms are only propext, Classical.choice and Quot.sound.

The six new modules contain 79 named theorems/supporting lemmas and four definitions, including the positive controls. These are not 79 independent mathematical discoveries. Together with the prior ten modules the continuation contains 179 named theorems, 12 definitions and one abbreviation, for 192 explicit axiom-audit targets.

The original 79-module baseline and prior native affine work are preserved. The combined gate checks and reuses the fresh baseline build from this conversation, validating its source inventory and recorded compiled-file hashes. Mathlib compiled dependencies are reused, not rebuilt. To reproduce everything from the source bundle with the existing pinned Linux runtime:

```sh
python3 replay_exact_periods.py --kit /absolute/path/to/Komorebi_Portable_Lean_4.34.0-rc2 --output /absolute/path/to/new_replay
```

The runtime is pinned to Lean 4.34.0-rc2 and Mathlib revision aeb72f1e9981b6d35b426b16dca7759be3e7ba06. No dependencies are downloaded by this command. The full wrapper is supplied for reproduction; the observed current run used the verifier's already-checked-baseline mode to avoid repeating the earlier complete baseline/native builds.

Development logs retain initial proof-script, lint, and module-header/import failures, followed by corrected successful checks. These were implementation issues, not mathematical counterexamples. The independent mathematical reviewer inspected the actual new source, original coefficient definitions, zero conventions, low-precision endpoints, arbitrary positive shifts, and degree normalization.

## Preserved results and remaining questions

The full stated Nishibuchi Conjecture 3.9, the all-row higher-difference bounds, and the optimal classical dyadic Euler tail remain proved. Their previous report is in review/SHARP_DYADIC_README.md; the original source archive remains in baseline/. Prior strengthening verification is retained under strengthening/provenance/.

This block closes the dyadic least-positive-packet-period question. Exact valuations of arbitrary higher-order differences remain open in general. Other prime/parameter families have not acquired a least-period classification here. The general affine Mahler-kernel valuation problem and unrestricted native Conjectures 13.2/13.3 remain unresolved in the scopes documented previously. A continuous isometry/bijection theorem on all of Z2, although suggested by the exact displacement law, is not newly formalized in this block. No external priority claim is made.
