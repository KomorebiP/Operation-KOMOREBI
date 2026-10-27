# Development record

- PolynomialSurjectiveStep compiled cleanly on its first development run.
- PolynomialIntegerTower compiled cleanly on its first development run. Its construction is dependent recursion from the actual one-step theorem.
- PadicTowerLimit initially failed on two elementary telescoping rewrites. Explicit ring identities repaired those steps. Scalar and vector convergence, retained precision, vanishing and unique sequence limit then compiled and passed local contracts/audits.
- PolynomialSmoothCounts initially failed on a finrank_top namespace reference and deprecated if_pos usage under warnings-as-errors. Both were corrected with no change to the mathematical statements.
- PolynomialPadicLift initially failed to match the continuity theorem with the named actual-evaluation definition. Explicitly unfolding padicEval in the simplification closed the mismatch. The second compile passed.
- Controls and contract development logs are preserved under development/controls_dev where available. The final fresh replay is recorded separately.

The main theorem requires a prime p, positive polynomial depth, an actual lower polynomial root and surjectivity of the initial actual reduced Jacobian. It does not assume an infinite tower, convergence, vanishing at the limit, later-level surjectivity or uniqueness among all polynomial roots.
