# Formalization scope: 140 compiled theorem constants

The 109 inherited theorem declarations and proof bodies are unchanged. Their files are hash-checked against the predecessor.

The 31 new theorems comprise eight in H12FifthIsogeny, nine in H12TateMarking, and fourteen in H12FifthModuli. They prove explicit polynomial/field identities, a rational map's curve equation under a nonzero denominator hypothesis, generator changes, and moduli relations. The derivative numerator is defined explicitly; Lean does not here identify it with an analytic derivative.

Not formalized: elliptic uniformization, the geometric isogeny degree or group-morphism theorem, meromorphic divisor theory, analytic differentiation of theta/gamma, the eta ratio identification, the normalized uniqueness statement, or the outstanding arithmetic limit evaluation. These remain ordinary proofs/inputs where stated in PROOF.md.

All 140 theorem constants are compiled with warnings as errors and all transitive axiom dependencies audited. Allowed standard logical dependencies: propext, Classical.choice, Quot.sound. No project-specific axiom, admitted proof, unsafe declaration or native_decide is permitted. A deliberately false integer equality must be rejected.

No theorem has the unproved gamma-arithmetic identity hidden as an axiom. The inherited conditional comparison lemmas retain both required limit identifications as visible hypotheses.
