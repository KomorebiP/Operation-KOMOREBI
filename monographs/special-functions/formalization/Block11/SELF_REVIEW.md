# Focused self-review: SF-LEAN-B11

Verdict: **proved as written** for the canonical F.2 type/limit contract.
Provenance: self-review. Base: `1c7814ef551709f44547561fe9b04ff7f9faa505`.
Audited source: `lean/CoupledGrowthTypes.lean`, SHA256
`1363c216cfd64706fce14bc8fece963f3313ecc3b4e393a7486c89b09b313c7a`. Kernel replay is separate
execution evidence and supplies no independent-review claim.

Claim card: for each 0<q,r,a,b<1 and each canonical component, the real
atTop liminf/limsup of log(M_i(R))/R^rho lie between the explicit positive
lower and finite upper coefficients from Blocks09-10, in the stated order.
M_i is the actual spherical supremum of the complex norm. Its double-log
radial profile tends to the unique positive characteristic rho, so its
limsup order is exactly rho. This is not a claim that either type ratio
has an ordinary limit or that angular growth is uniform.

Dependency graph: Block10 canonical two-sided ratio bounds -> explicit
eventual bounds -> bounded/cobounded real filter sandwich -> positive types.
The same pointwise bounds -> positive log(F), positive R^rho and log(R)
on R>1 -> logarithmic squeeze -> vanishing constant/log(R) errors -> radial
limit -> limsup order. Block08 attained spherical maximum -> real supremum
equality on R>=0 -> eventual equality -> maximum-modulus type/limit transport.
No edge uses F.3 or a type-ratio convergence assumption. Leaves are internal
Lean proofs or the exact pinned Mathlib order/topology/power/log APIs.

| Obligation | Result | Evidence |
| --- | --- | --- |
| Actual canonical functions | passed | Real indexed components and independent positivity lemma |
| Real liminf/limsup conventions | passed | Explicit definitions atTop and both eventual bounds |
| Bounded/cobounded direction | passed | Upper bound -> cobounded GE; lower bound -> cobounded LE |
| liminf<=limsup and filter | passed | Both boundedness witnesses and nontrivial real atTop |
| Positive finite types | passed | Positive lower coefficient, type ordering and real upper coefficient |
| Double logarithm domains | passed | Positive comparison base -> log(F)>0; canonical F>0 separately |
| Denominator and powers | passed | R>1 implies R>0, R^rho>0 and log(R)>0 |
| Limit range and exponent | passed | Eventual squeeze; any real rho in the general helper, including 1/2 fixture |
| Actual maximum and R=0 | passed | IsGreatest witness proves nonempty real supremum equality |
| Eventual transport and order | passed | Equality for R>=0 and Tendsto.limsup_eq |
| Ordinary type convergence/F.3 | out of scope | Radial exponent is a different profile; no convergence claim |
| Whole monograph audit | out of scope | Remaining-work inventory is explicitly correspondence-only |

Pinned API checks: Filter.le_liminf_of_le, limsup_le_of_le and
liminf_le_limsup in Mathlib/Order/LiminfLimsup.lean:141-185 have their
boundedness/coboundedness premises supplied explicitly. Real.log_rpow is
used only at R>0; Real.log_le_log is applied to positive comparison values.
Filter.Tendsto.const_div_atTop and Real.tendsto_log_atTop justify the errors.
The eventual squeeze theorem is used after restricting to R>1. IsLUB.csSup_eq
receives a nonempty sphere-image witness; no value for a negative-radius
empty sphere is used in a limit argument.

Decisive evidence: 48 replay steps pass, 234 coupled names are freshly
audited, eleven modules are kernel-replayed, four controls are rejected and
the positive fixture passes. The zero-lower-coefficient control would permit
the false lower squeeze 1<=0. The wrong-profile control has a type mismatch.
The exp(2R) fixture has radial exponent one while its normalized type ratio
is two; the rho=1/2 fixture tests a fractional exponent.

The first replay's allocation failure is not a mathematical counterexample
or an admitted theorem; the accepted run executes every required step from
a new directory with fixed source inputs.

The strongest safe conclusion is the full registered canonical F.2 growth
contract. Next missing implication for the Perron growth chapter is F.3's
scaled type-vector transport and proportions. Ancillary identities and
the wider manuscript remain separately mapped. No mathematical restriction
or theorem correction was required in this review.
