# Proof and computation boundary

## What the release asserts

C01–C08 have written arguments in `docs/FOUNDATIONS.md` and `docs/THEORY.md`. Specified finite checks have been rerun against frozen results. A finite pass validates only the tested assertions and ranges. It does not convert an informal proof into kernel-checked mathematics.

The basis is classical NOT/CNOT/Toffoli, with distinct wires in each gate and positive controls. The oracle restores logical inputs and zero-initialized ancillas and works for both initial target values. Borrowed logical bits may be included as additional inputs. There are no measurements, quantum phases, or discarded work registers.

`T` counts Toffoli gates; NOT and CNOT are free only in that count. Ordinary total gate count is a different resource. All degree claims use unique multilinear Boolean polynomials over F2. GF16 checks use the stated irreducible polynomial. Actual instance-encoding length, not witness length or a convenient auxiliary parameter, controls asymptotic circuit claims.

## What the release does not assert

No resolution of P versus NP. No superpolynomial lower bound for unrestricted Boolean decision circuits. No polynomial-time evaluator of the weighted trace. No independence or optimality conclusion extrapolated from a sampled computation. No quantum-circuit lower bound. No Lean build or independent review. No comprehensive literature or novelty audit. No claim that an exponential algebra dimension forces exponential circuit length.

A lower bound for a restricted model stays a restricted-model result. A conditional randomized SAT implication stays conditional and randomized. Exact small optimum counts rely on the displayed lower bounds and matching constructed circuits, not on enumerating all circuits.

## Evidence labels

- **WRITTEN:** an argument is supplied with hypotheses; it is not kernel checked.
- **FINITE:** a stated finite assertion was executed with exact arithmetic.
- **COUNTEREXAMPLE:** the displayed inference fails in the specified model.
- **CONDITIONAL:** the conclusion follows from an assumption not implemented here.
- **ARCHIVED:** preserved historical material, not automatically included among current claims.

The active claim register is authoritative over conversational phrasing and historical continuation notes. Public-facing descriptions must preserve these qualifications.
