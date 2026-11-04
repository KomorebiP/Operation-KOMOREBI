# Lean verification for the reading examples

**Recorded 4 November 2026 · Komorebi P.**

These companions connect selected formulas in the reading site to explicit Lean statements. The source files, claim maps, compiler diagnostics, and replay commands identify exactly what was checked. The mathematical scope belongs to the individual theorems.

The current batch contains **58 named theorem declarations and 13 definitions** across four modules. These totals include helper lemmas and three finite data checks. Reused K-COS prerequisites and positive controls are excluded from the new theorem total.

| Module | Theorem declarations | Definitions |
|---|---:|---:|
| Factorial lanes and binomial normalization | 13 | 3 |
| Residue packets and additive transport | 19 | 3 |
| Stirling polynomial recovery and obstruction | 11 | 4 |
| K-COS logarithmic certification | 15 | 3 |

## Factorial lanes and coefficient packets

The [reader example project](../formal/reader-examples/README.md) covers the following parts of the public examples. Its [claim map](../formal/reader-examples/CLAIM_MAP.json) identifies theorem names and assumptions. The [recorded replay](../formal/reader-examples/verification/2026-11-04/run.json) binds the checked sources and verification program by SHA-256.

| Reading claim | Formal coverage |
|---|---|
| [Factorial lane reconstruction](demonstrations/FACTORIAL_LANES.md#2-disassemble-a-factorial-into-ten-lanes) | Every natural offset, lane count, and step count, including empty products. The displayed ten-lane calculation is a specialization. |
| [Rational Pochhammer coordinates](demonstrations/FACTORIAL_LANES.md#3-transport-the-product-to-hypergeometric-coordinates) | Exact scaling of each lane for a positive step, reconstruction of the factorial product, and the unit-parameter factorial identity. |
| [Factorial normalization](demonstrations/FACTORIAL_LANES.md#4-factor-out-the-leading-monomial) | The normalized coefficient equals the reciprocal binomial coefficient over the rational numbers. |
| [Reciprocal coefficient bridge](demonstrations/FACTORIAL_LANES.md#the-same-reciprocal-recurrence-before-normalization) | The general binomial quotient identity relating the original and normalized rows, with the coefficient degree in range. |
| Residue projection and refinement | Idempotence, orthogonality, complete reconstruction for a positive modulus, and refinement to a positive divisible modulus. These hold for arbitrary coefficient sequences over an additive commutative monoid. |
| [Coordinate transport](demonstrations/ROOTS_UNITY_FALLING_FACTORIAL.md#4-transport-the-projector-into-falling-factorial-coordinates) | Conjugation, projector laws, reconstruction, and complete input/output block reconstruction under a supplied additive equivalence and the stated projector hypotheses. |
| [Recovery from a complete parameter polynomial](demonstrations/STIRLING_BELL_FUBINI.md#the-sharp-recovery-distinction) | The exact factorial-weighted polynomial retains every rational coordinate. Its coefficients give an inverse, whereas the two scalar summaries have an explicit noninjectivity witness. |

The coordinate-transport theorems work on arbitrary additive carriers. The sequence specialization concerns full coefficient sequences. The falling-factorial reading example concerns polynomials and finite coefficient support. These are distinct domains. This companion proves the conditional transport algebra and does not construct the concrete Stirling basis equivalence or establish the complex roots-of-unity formula.

The factorial results establish finite-product and rational-coefficient identities. Analytic convergence of hypergeometric series, the full formal-series reciprocal construction, prime-adic estimates, and the other sections of the extended demonstrations keep their separate written and computational evidence.

### Inspect the actual Lean files

- [FactorialLanes.lean](../formal/reader-examples/KomorebiReader/FactorialLanes.lean)
- [ResiduePackets.lean](../formal/reader-examples/KomorebiReader/ResiduePackets.lean)
- [StirlingRecovery.lean](../formal/reader-examples/KomorebiReader/StirlingRecovery.lean)

## K-COS positive logarithm certificates

The [K-COS certification companion](../formal/kcos-certification/README.md) supplies exact-real consequences needed when reporting a positive enclosed tail on a logarithmic scale. Its [claim map](../formal/kcos-certification/CLAIM_MAP.json) and [recorded replay](../formal/kcos-certification/verification/2026-11-04/run.json) specify the formal statements and checked sources.

The input is an already valid positive enclosure. The new results do not establish numerical endpoint construction, the COS remainder bound, the correctness of Decimal or mpmath, or a complete verified Python implementation. The [numerical certification audit](KCOS_NUMERICAL_CERTIFICATION_AUDIT.md) retains its own dated scope. The existing K-COS acceptance development also remains separately available.

## What a recorded pass means

The replay uses Lean **4.34.0-rc2**, compiler commit `6a10ac8c22beadecabdbb0919c2b50214762f91d`, and Mathlib revision `aeb72f1e9981b6d35b426b16dca7759be3e7ba06`. It checks all dependency revisions, builds the project in a fresh temporary directory with warnings treated as errors, audits the explicit declaration inventory, and replays project modules in the Lean kernel. Positive examples must pass and deliberately invalid controls must fail for the intended mathematical reason.

The permitted foundational axioms are `propext`, `Classical.choice`, and `Quot.sound`. An unfinished proof, custom axiom, or native-decision axiom is not accepted. The receipt lists the actual dependencies for each audited declaration.

Project replay uses the same Lean kernel against pinned imported environments. It is not an independent kernel or a fresh rebuild of all Mathlib. Statement correspondence has also been reviewed against the linked reading claims. Neither that review nor compilation extends a theorem beyond its actual hypotheses.

## Reproduce the checks

With the pinned portable runtime already extracted, run from the repository root:

```text
python -B tools/verify_lean_companion.py --project formal/reader-examples --runtime /absolute/path/Komorebi_Portable_Lean_4.34.0-rc2 --output /tmp/reader-examples-replay
python -B tools/verify_lean_companion.py --project formal/kcos-certification --runtime /absolute/path/Komorebi_Portable_Lean_4.34.0-rc2 --output /tmp/kcos-certification-replay
```

Each output directory must be new or empty. The runner uses the existing dependency cache and does not update it. On a standard Lean installation, prepare the dependencies for the pinned project and omit `--runtime`.

The [Reader Lean companions workflow](https://github.com/KomorebiP/Operation-KOMOREBI/actions/workflows/reader-lean-companions.yml) rebuilds both companions on relevant pull requests and changes to `main`. Its artifacts keep fresh compiler diagnostics and rejection results for the recorded revision.

[Demonstrations](DEMONSTRATIONS.md) · [Run and verify](VERIFICATION.md) · [Formal source finder](browse/LEAN.md)
