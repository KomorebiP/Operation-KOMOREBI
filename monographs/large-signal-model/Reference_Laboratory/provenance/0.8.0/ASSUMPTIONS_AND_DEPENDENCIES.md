# Assumptions and dependencies — new block

## Two examples, not one extrapolated guarantee

The reduced-repair example starts with the perturbed operators of 0.7.0 and reuses its proposed geometry. Its uncertainty family is deterministic. The dependent-data example starts with a different, fixed observable model. Its conditional statistical confidence does not attach itself to the old repaired operators.

| Proposition | Required inputs | Supplies | Does not supply |
|---|---|---|---|
| 80 | Fixed geometry, reset path, requested margin, exact operators | Convex feasibility interval and separating lower bound | Optimal geometry or optimal repair mechanism |
| 81 | Predictable regressors, fixed true linear conditional mean, positive sub-Gaussian noise scale, parameter bound | Time-uniform regression confidence | Correctness of an estimated hidden-state regressor |
| 82 | Accessible exact predictive state, correct finite observation basis, invertible known moment matrix | Conditional operator confidence sets | Representation discovery or misspecification control |
| 83 | Moment curve and known reference moments, parameter family | Curved-domain validity and accessible posterior | Universality of the chosen family |
| 84 | Saved path, exact measure, prior bounds and confidence budget | Rational outer intervals | Data authentication or empirical coverage frequency |
| 85 | Parameters in certified set, common reference measure | Conditional and finite-record TV bounds | Equivalence of densities with different measures |
| 86 | Markov property, common minorization and one-step discrepancy | Uniform one-time marginal bound and rolling windows | Uniform full-record TV bound |
| 87 | All listed process and observation assumptions, entire returned rectangle | Conditional coverage plus deterministic domain certificate | Unknown model-class correctness |

## Information that is supplied rather than learned

The scalar example supplies the feature dictionary (1,u,u^2), the reference measure, the two-parameter family, the prior parameter bound, the observation protocol and exact accessibility of the last observation. It learns a and b. The geometry is specified and then verified for the whole uncertainty rectangle.

## Certificate and statistical quantifiers

A witness covers all operators/states in its declared deterministic set. A statistical event covers the true process only under a correct observation and model protocol. The exact checker verifies arithmetic and identities; it does not prove those upstream assumptions from one path. Examining additional times is legitimate here because the confidence event is simultaneous over time. Post-response feature selection would invalidate predictability.

## What 1.0 should audit

Freeze the declared finite sectors. Review proof dependencies, exactness versus approximation, types and domains, input accessibility, model-class assumptions, confidence events, and source-to-code correspondence. Treat general hidden-state or dictionary discovery as explicitly separate research rather than either a completed result or an unstated release prerequisite.
