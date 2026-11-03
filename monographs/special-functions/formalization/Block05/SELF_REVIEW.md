# Focused self-review: SF-LEAN-B05

Primary verdict: **proved as written**, for the guarded labeled-germ inverse
and coefficient transport stated in `CoupledGermInverse.lean`. This is a
self-review of the source digest bound by `declarations.json`, against base
`ee59ff257a74fc046981e5ca633476148fe2e1a4` and the pinned replay receipt.
It is not an independent audit or a whole-manuscript correctness verdict.

## Claim card

Objects: labeled real tuples s,t, with 0<q,r,a,b<1 for each tuple, and their
canonical complex functions U,V. Hypotheses: both labeled components agree
as germs at zero and s.defect is nonzero. Conclusion: equality of all four
ordered parameters. Intermediate coefficient results cover every natural
index. The separate supplied-Taylor-object theorem assumes actual
`HasFPowerSeriesAt` witnesses for a normalized analytic solution germ.

## Dependency graph

Odd HasSum -> injective dense reindexing -> scalar formal multilinear series
at zero -> coefficient uniqueness under equality of germs -> equality of
real paired coefficients -> Block01 positive-scale guarded inverse.
Block03 entire convergence supplies canonical HasSum. Block04 analytic
solution uniqueness supplies the arbitrary-solution coefficient and shared
solution corollaries. No step depends on the new inverse to prove its own
coefficient comparison.

## Obligation matrix

| Obligation | Result | Evidence |
|---|---|---|
| Domain and quantifiers | passed | Actual complex germs; all coefficient indices; strict positive scales only where canonical existence is used |
| Zero degree and parity | passed | `denseOdd_even`, including n=0; sparse support complement proved zero |
| Degree addresses | passed | `denseOdd_odd`; positive fixture consumes degrees 3,5,7 as indices 1,2,3 |
| Sum transport | passed | Exact `HasSum` reindexing with injective map and zero off-range premise |
| Taylor normalization | passed | `coeff_ofScalars` and `hasFPowerSeriesAt_iff`; ordinary coefficients, no inserted factorial |
| Germ-to-series direction | passed | Equality-of-germs uniqueness theorem applied to two already constructed representations |
| Real/complex comparison | passed | `Complex.ofReal_inj` after equality at odd dense indices |
| Ordered component labels | passed | Separate U and V premises; paired coefficient equality uses `Prod.ext` |
| Exceptional locus | passed | Nonzero-defect premise retained; old finite-jet collision checked in positive fixture |
| Arbitrary supplied Taylor objects | passed | Same-function formal-series uniqueness at all degrees, using actual supplied witnesses |
| Dependency freshness | passed | Nine revision pins, input hashes before and after replay; source/map digests checked |
| Placeholder and extra axioms | passed | Source guard, warnings as errors, exact axiom audit, same-kernel replay |
| Full analytic-germ collision at D=0 | not addressed | The preserved counterexample is only a finite-jet collision |
| Stable inverse, unlabeled classification, growth and rescaling | out of scope | No conclusion claims these |

## Exact-source checks and limits

The relevant Mathlib sources were read at the pinned local revision:
`Topology/Algebra/InfiniteSum/Defs.lean` (`Function.Injective.hasSum_iff`,
generated additively from `hasProd_iff`), `Analysis/Analytic/Basic.lean`
(`hasFPowerSeriesAt_iff`), `Analysis/Analytic/OfScalars.lean`
(`coeff_ofScalars`), and `Analysis/Analytic/Uniqueness.lean`
(`eq_formalMultilinearSeries_of_eventually`). Lean checks their exact types
and the coefficient convention through the real proof terms. No unverified
external mathematical citation or load-bearing computation is used.

The smallest edge cases are explicit: k=0 gives zero, k=1 gives c0, k=2
gives zero, and k=3 gives c1. The two sum representations are centered at
zero, so the translation `0+z=z` introduces no change of center or sign.
Strict contraction is not silently extended to a boundary scale of one.

The four negative controls check rejection mechanisms. Omitting the defect
argument fails the actual API; this alone does not establish necessity of
the guard for full germ equality. The positive boundary fixture preserves
exactly the older finite-jet counterexample, with its original scope.

No missing implication remains in this block's target contract. The strongest
safe conclusion is exact ordered-parameter recovery under the stated guard,
plus all-degree coefficient transport. The next check is an exact contract
for Appendix G.1; no growth conclusion follows from this inverse.
