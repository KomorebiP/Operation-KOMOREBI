# Continuous square-zero obstruction and a finite-image vanishing theorem

Base: Strong_Artin_Lean_v0.26.0_Representation_H2_Obstruction_Checked.zip, SHA-256 6ab67721841940b82a621642dcb78a0e67e6012c1df20a9bb519ac01c8ee8bbd.

Builds on: continuous-obstruction-route.md.

## Target and success criterion

Construct an actual continuous-cochain obstruction for discrete square-zero coefficient extensions, prove the continuous lifting criterion including strict subgroup prescriptions, and prove a substantive vanishing theorem from an order condition rather than assume the distinguished class is zero.

## Outcome

Proved at the stated scope. The continuous inhomogeneous class is constructed; continuous liftability is equivalent to its zero value. A compatible provisional section is constructed for clopen subgroup prescriptions. Finite-group averaging constructs H2 primitives, then H1 averaging adjusts them to respect a prescribed subgroup. A continuous representation of a compact group into discrete coefficients lifts through its same residual image when that image order is a unit upstairs. Its exact kernel is preserved.

## Decisive derivation

Sum the two-cocycle equation over the last group variable. The sum is the coboundary of the cochain g -> sum_t c(g,t), and equals |G| c. Invertibility of |G| on the actual coefficient kernel produces a primitive. The square-zero correction (1-b(g))r(g) is a representation. When this construction is carried out on the finite residual image, composing with the original continuous quotient map preserves continuity. Reduction proves the reverse kernel inclusion; factoring through the same quotient proves the forward inclusion.

## Falsification and scope controls

- The C3 mod-9 character with nonzero obstruction mod 27 remains nonliftable continuously.
- The C4 subgroup example retains zero absolute obstruction and nonzero relative obstruction.
- The positive product_(N) C2 example is proved compact and nondiscrete, preventing a false success obtained by discretizing the source.
- The order-invertible hypothesis excludes the defining-characteristic image cases. No universal vanishing is asserted.

## Self-review

The section construction is based on residual values, not a source-singleton modification. Every correction used in the continuous criterion has a proved continuity witness. The finite-group vanishing input is unit invertibility on the actual ring kernel, not a relabeled H2-vanishing assumption. The strict-relative theorem states literal subgroup agreement; no gauge or local-Selmer comparison is silently used. This is a self-review, not independent referee review.

## Durable evidence

Source files, MODULES.json, DECLARATIONS.json, audit/AxiomAudit.lean, verifier, RESULT.json, logs, proof/failure ledgers, and boundary files. See the external extracted-archive replay report for the second fresh replay after packaging.

## First unresolved arithmetic implication

Define and prove vanishing of the distinguished continuous locally constrained relative obstruction for a specified arithmetic case outside the already solved order-invertible sector. Local Tate duality, Selmer comparison, auxiliary descent, and automorphic carrier occurrence are not supplied here.
