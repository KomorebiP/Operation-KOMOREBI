# Development and evidence boundary

The three new mathematical modules are `PolynomialPadicUnique`, `PolynomialCoefficientPerturbation`, and `PolynomialRootStability`.

- The uniqueness module was developed against the prior checked tower/count sources. Early elaboration and warning-as-error failures were repaired. The final module compares arbitrary roots via actual residue lifts, with no uniqueness assumption. Canonical integer truncation and reduction/evaluation identities are public support lemmas.
- The coefficient module's first compile failed while simplifying its final p-adic evaluation identity. Explicit evaluation-homomorphism rewrites resolved that issue; the subsequent compile passed. The perturbation is the actual polynomial list `F i + C c * H i`.
- The parent root-stability module compiled cleanly at both its initial nearby-existence stage and its completed square comparison stage. The final proof first constructs a nearby perturbed root in a rectangular system, then uses square uniqueness to identify any chosen perturbed root in the original ball.
- Development controls had elaboration failures before their successful build. These are distinct from the deliberate negative controls, whose rejection is a required result of the final gate.

Raw development logs are retained. Compiled development files and symlinks to previous builds are omitted from the release. The authoritative proof evidence is the fresh gate, which compiles every required active project source into a new build directory, followed by explicit declaration-axiom audits and independent proof review. Early partial or failed builds are not used to assert completed results.

The written weighted perturbation note is preserved separately. This release formalizes its unit-Jacobian uniqueness and coefficient-stability portion. It does not add Lean proofs of nonunit-Jacobian contraction, the first-order root-motion remainder, or the full parameter graph.
