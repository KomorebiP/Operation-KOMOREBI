# Formalization scope: 83 kernel-checked theorem constants

## Included

The inherited six modules contain 50 theorems; their statements and proofs are unchanged.

The 33 new theorems are:

- **H12SignedGeometry (18):** eight-character transport and reconstruction, affine and low-degree moment spectra, exact one/three-step normalization gains, and the finite phase-gauge calculation.
- **H12SignedAlgebra (11):** multiplicative signed identities over an arbitrary commutative group, carried transport, eighth-power inversion, ninth-power reconstruction conditional on the explicit conductor norm, and preservation/detection of the phase gauge.
- **H12ThreeStepTransport (4):** the actual integral unit cube, the rational half-grid carry, and induction proving that every iterate has integral affine carries.

All 83 are recompiled and their transitive axiom dependencies audited. Allowed standard dependencies are propext, Classical.choice, and Quot.sound. There are no project axioms, admitted proofs, native_decide calls, or unsafe declarations. Warnings are errors. A false arithmetic control must fail.

## Not formalized or proved here

The complex analytic definitions and convergence of theta/gamma, the inherited analytic covariance and multiplication theorems, the meromorphic/divisor correspondence, the Taylor-limit estimates as complex analytic statements, and the identification with the arithmetic ray-field candidate are not formalized in this release.

The ordinary proof in PROOF.md applies the formal algebraic core to the explicitly stated inherited analytic inputs. No gamma equality is supplied as an axiom. The new conductor_ninth_power theorem assumes the displayed full-norm equation; it does not prove gamma algebraicity. The old pointwise_phase_comparison theorem retains both limit identifications as explicit hypotheses.

The phase deformation is only a counterexample to sufficiency of selected finite packet data. It is not claimed to produce another gamma function respecting every functional equation and the normalized limit at zero.
