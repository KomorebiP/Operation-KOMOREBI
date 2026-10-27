# Verified checkpoint

Status: PASS

Lean version: 4.34.0-rc2
Mathlib revision: aeb72f1e9981b6d35b426b16dca7759be3e7ba06

All 22 theorem statements in the 0.1.0 draft have compiled unchanged. The active
mathematical development contains 59 named theorem declarations in four modules.
Four additional test theorems formally refute deliberately false mutations.
There are therefore 63 checked named theorem declarations including controls.

The final verification run:

* rebuilt the four mathematical modules from fresh source with warnings as errors,
* audited all 59 mathematical theorem dependencies,
* replayed all four mathematical modules through the Lean kernel,
* compiled, audited, and replayed four explicit refutations of false test claims,
* rejected all four corresponding mutations of the original source,
* reran the independent exact Python arithmetic verifier.

The axiom audit found only propext, Classical.choice, and Quot.sound. No proof
placeholder, project-specific axiom, native decision proof, or Lean.ofReduceBool
appears in the checked dependency closure.

The only authoritative result receipt is
`verification/final_run/VERIFICATION.json`. The theorem index and proof boundary
specify exactly what has been checked. This status does not extend to arbitrary
modulus, a quantum circuit implementation, or the whole philosophical essay.

The current PDF has not been edited during this Lean run. A carefully scoped
publication note is provided in `PUBLICATION_STATUS_TEXT.md`.
