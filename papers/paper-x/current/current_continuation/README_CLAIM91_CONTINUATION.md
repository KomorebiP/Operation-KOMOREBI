# Paper X — Claim 9.1 Scalar/Mellin + Arithmetic Separator Continuation

This cumulative source release advances the arithmetic dependency of Paper X Claim 9.1 without changing the full-paper ledger: **17 checked / 3 partial**. Claim 9.1 remains partial.

## What is newly checked

- Nonzero simultaneous finite-prime avoidance by CRT.
- Automatic inverse-class integral representatives with norm coprime to every prescribed nonzero integer modulus.
- Actual norm-character power saving with the representative constructed internally.
- A convenient scalar-unit criterion: nontrivial scalar restriction plus `gcd([K:Q], phi(m)) = 1`.
- A weaker exact scalar criterion: `exists a, chi(a^[K:Q]) != 1`.
- Exact characterization of the scalar exceptional case by triviality of the degree-th power of the restricted character.
- Measurability and first-order Mellin endpoint control for the actual norm-character summatory function.
- Pole-rigidity assembly conditional only on the genuine arithmetic product/residue inputs.
- Direct composition from choice-free prescribed-Frobenius arithmetic coverage to the full nonsingular finite compatible-system trace separator.

## Remaining boundary

General prescribed-conjugacy Frobenius occurrence (`ExistentialArithmeticCoverage`) is **not proved**. This is the weak-Chebotarev bottleneck. The alternative analytic route also still requires its arithmetic Euler-product/residue identity and prescribed-prime reciprocal-series divergence. Characters in the exact scalar exceptional class require a non-scalar norm witness or a justified descent.

## Verification

All final compile checks in `verification/final_logs` returned exit code 0 under Lean 4.34.0-rc2 with Mathlib revision `aeb72f1e9981b6d35b426b16dca7759be3e7ba06`, with warnings treated as errors. The final declaration-level axiom audit reports only `propext`, `Classical.choice`, and `Quot.sound`. Retained failed development attempts are kept separately and are not counted as proof passes.

See `CURRENT_STATUS.md` and `verification/CLAIM91_CONTINUATION_VERIFICATION.json`.
