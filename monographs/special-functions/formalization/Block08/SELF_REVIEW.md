# Focused self-review: SF-LEAN-B08

Primary verdict: **proved as written**, for the real-axis, maximum-modulus
and lower-recurrence contracts in CoupledPositiveReal.lean, at the source
digest bound by declarations.json and the pinned replay receipt. This is
self-review at base `13e65505a1ce2de3ece418b22b93b38811573207`, not independent
review or a proof of the complete F.2 type/growth theorem.

## Claim card and dependency graph

Objects: real labeled scales in (0,1), the canonical complex entire functions,
and their real-valued restrictions UReal,VReal. Conclusions: actual real
series and complex embeddings at every real argument; nonnegativity and
values >=R on R>=0; actual real derivative equations; strict monotonicity;
attained maximum moduli at R>=0; final-unit product recurrence at R>=1 and
its log form at R>1; child radii >=2 at R>=B=1+2/minScale.

Canonical absolute convergence -> real-part HasSum -> real series -> ofReal
HasSum and uniqueness -> complex real-axis identification. Positive terms
and c0=1 -> nonnegativity and linear lower bound. Complex HasDerivAt plus
real restriction and real-valued products -> real equations -> derivatives
>=1 -> monotonicity. Termwise norm domination and actual sums -> closed-ball
norm bound -> equality at the positive point -> IsGreatest on the sphere.
Monotone positive products on [R-1,R] -> mean-value derivative comparison
-> unit recurrence -> logarithmic recurrence. Positive minimum and R>=B
-> child-radius bounds. No growth/type estimate is used circularly.

## Obligation matrix

| Obligation | Result | Evidence |
|---|---|---|
| Ordered codomain | passed | All inequalities are in the real field; no order on complex values is introduced |
| Actual convergent series | passed | HasSum transport of the globally absolutely convergent canonical series |
| Embedding direction | passed | Real series mapped back by ofReal, then uniqueness of complex sums |
| Negative real arguments | passed | Embedding/series identity holds for all real x; nonnegativity is restricted to x>=0 |
| Degree-one term | passed | Canonical c0=1 and the ordinary degree 2*0+1=1; a single-term HasSum bound |
| Real derivatives | passed | HasDerivAt.real_of_complex and real-axis identification before simplifying products |
| Monotonicity hypotheses | passed | Differentiability/continuity and derivative >=1 on the nonnegative axis |
| Maximum existence and attainment | passed | IsGreatest of the actual norm image of the sphere, attained at z=R; includes R=0 |
| Mean-value interval | passed | Closed [R-1,R], R>=1, differentiability and nonnegative child arguments |
| Product order | passed | Both factors monotone and nonnegative; no unsupported product comparison |
| Equation-row alignment | passed | First output UReal uses q,r; second output VReal uses a,b; inputs retain UReal,VReal labels |
| Logarithm domain | passed | R>1 gives positive child radii and function values before log monotonicity/product law |
| Threshold and endpoints | passed | minScale positive, B>1, and R>=B includes equality; worked B=11 tested |
| Dependency and I/O freshness | passed | Revision pins, source/input hashes before and after replay, sealed logs and output inventory |
| Additional axioms/placeholders | passed | Production source guard, exact axiom audits and kernel replay; placeholder confined to rejection fixture |
| Explicit lower power/type bound, upper bound and asymptotic limit | out of scope | No claim marks these complete |

The norm comparison uses coefficients' nonnegativity and a bound on norm(z),
not an assertion that complex values themselves are ordered. At negative
real arguments the embedding is still correct, but norm equality with the
signed real value is not provided. The negative-radius control checks the
actual API guard rather than being reported as an analytic counterexample.

The mean-value argument supplies the same required inequality as integrating
over the final unit interval. It does not add an unproved formal integral
identity. The parent lower recurrence is valid for R>=1, while child radii
>=2 require the separate stronger threshold. The logarithmic recurrence
requires R>1; it does not rely on log(0) or imply that all child logarithms
are positive at every such R.

Pinned Mathlib leaves are HasSum real/ofReal maps, ordered sums, actual real
restriction of complex derivatives, norm-of-sum comparison, derivative-based
monotonicity and the convex mean-value comparison, and the real logarithm
laws. Their exact types are consumed by checked proof terms. Cached imports
are reused, with no new package revision or load-bearing numerical run.

No implication remains missing in this block's target. The strongest safe
statement is the real-axis and lower-recurrence foundation. The next check is
the shifted-radius inequality and seed/descent induction yielding the
explicit lower power comparison; the full analytic growth theorem remains open.
