# Formalization scope: 52 new kernel-checked theorem constants

| Module | Count | Actual kernel-checked content |
|---|---:|---|
| H12UnitCoinvariants | 21 | Universal integer quotient/preimage identities, conductor carry/order, and full finite sixth-character classification |
| H12MixedGauge | 13 | Integer coefficient identities underlying holomorphic gauge changes and zero Hodge projection |
| H12AnchorObstruction | 9 | Six-point phase-interpolation coefficients, fixed carries, based exponent cancellation and iteration |
| H12SevenClassDetector | 9 | CRT fixed equations, coefficient recovery, and primitive-class selector |

All use the pinned Lean 4.34.0-rc2 and bundled Std, warnings as errors, one worker.
Every exported theorem's transitive axioms are audited. Only propext,
Classical.choice and Quot.sound are permitted where required. There are no
admitted proofs, custom axioms, native_decide calls or unsafe declarations.
A deliberately false integer equality must be rejected.

Not formalized here: analytic line bundles or gerbes, Appell-Humbert theory,
Liouville's theorem, holomorphic exponentiation in the counterexample,
semidirect-product character classification in an arbitrary complex group,
the full analytic compact-line theorem, actual gamma descent, or its
identification with a normalized based fiber multiplier.

Those statements are ordinary mathematical proofs or explicit missing inputs
in PROOF.md. The coefficient witnesses are not mislabeled as a formal analytic
bundle theory. No theorem asserts U_Gamma=U_alg or any bound on its phase group.

The inherited 308 declarations remain byte-for-byte in the predecessor ZIP,
with historical evidence. They were not replayed. 360 is only the cumulative
source inventory; 52 is the fresh theorem count.
