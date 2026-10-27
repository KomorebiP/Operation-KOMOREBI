# Proof and computation boundary

## Formalization supplement in version 1.2.0

C01, the NCT specialization of the F3 degree dependency, and the lower-bound component of C02 have maintained Lean proofs in `formalization/lean`. Restoration is a stated premise about an implementation, not an extra axiom. Legal gates, reversal, every circuit cut, the degree invariant with sharing, complete safe coverage, and zero-Toffoli affine-output implementation are proved from the source definitions.

There are **115 theorem declarations: 40 inherited and 75 new**, across eight modules. This is an inventory of lemmas and examples, not 115 independent discoveries. The joint endpoint is `restored_degree_and_cover_bound`. `DegreeLE d f` is a proved polynomial-representation criterion (XOR of monomials of length at most d), not a postulated circuit-cost statistic. A canonical ANF normalization/extraction procedure is not formalized.

**C02 remains partial as a claim group.** Its evaluation-span dual, affine input invariance, and general monotone ideal are still written with their recorded finite checks. C03-C08 and the general exact monomial-cost theorem are not promoted by this block. The two-input AND example is proved separately.

The proof audit permits only `propext`, `Classical.choice`, and `Quot.sound`. No custom axioms, admitted proofs, native-decision oracle, or kernel bypass is used. All eight modules are replayed with the bundled Lean checker. This is not an independent kernel implementation or independent mathematical review.

Historical Block 01 evidence is pinned to v1.1.0. Its old manifest is not a claim about changed Block 02 inventory files. The unchanged v1.1.0 release is preserved in `archive/releases/`; the Block 02 manifest identifies the active source hashes.

## What the release asserts

C01–C08 have written arguments in `docs/FOUNDATIONS.md` and `docs/THEORY.md`. Specified finite checks have been rerun against frozen results. A finite pass validates only the tested assertions and ranges. It does not convert an informal proof into kernel-checked mathematics.

The basis is classical NOT/CNOT/Toffoli, with distinct wires in each gate and positive controls. The oracle restores logical inputs and zero-initialized ancillas and works for both initial target values. Borrowed logical bits may be included as additional inputs. There are no measurements, quantum phases, or discarded work registers.

`T` counts Toffoli gates; NOT and CNOT are free only in that count. Ordinary total gate count is a different resource. All degree claims use unique multilinear Boolean polynomials over F2. GF16 checks use the stated irreducible polynomial. Actual instance-encoding length, not witness length or a convenient auxiliary parameter, controls asymptotic circuit claims.

## What the release does not assert

No resolution of P versus NP. No superpolynomial lower bound for unrestricted Boolean decision circuits. No polynomial-time evaluator of the weighted trace. No independence or optimality conclusion extrapolated from a sampled computation. No quantum-circuit lower bound. No Lean verification of the unlisted parts of C02 or of C03-C08. No independent review. No comprehensive literature or novelty audit. No claim that an exponential algebra dimension forces exponential circuit length.

A lower bound for a restricted model stays a restricted-model result. A conditional randomized SAT implication stays conditional and randomized. Exact small optimum counts rely on the displayed lower bounds and matching constructed circuits, not on enumerating all circuits.

## Evidence labels

- **LEAN:** the exact listed declaration was built, audited, and kernel-replayed with the pinned toolchain; its stated hypotheses remain part of the result.
- **WRITTEN:** an argument is supplied with hypotheses; it is not kernel checked.
- **FINITE:** a stated finite assertion was executed with exact arithmetic.
- **COUNTEREXAMPLE:** the displayed inference fails in the specified model.
- **CONDITIONAL:** the conclusion follows from an assumption not implemented here.
- **ARCHIVED:** preserved historical material, not automatically included among current claims.

The active claim register is authoritative over conversational phrasing and historical continuation notes. Public-facing descriptions must preserve these qualifications.
