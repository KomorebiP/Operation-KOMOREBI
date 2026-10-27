# Local analytic regularity: independent proof audit

**Normalized claim.** Let p be any prime, let e and k be nonnegative integers,
and let F be an actual polynomial system over Q_p in appended coordinates
(Y,T), with e equations and e solved coordinates. Suppose F(a)=0 at
 a=(y0,t0), and let J=D_Y F(a) and K=D_T F(a) be its actual evaluated partial
Jacobian matrices. Assume J is invertible over Q_p. There exist a total
function psi:Q_p^k -> Q_p^e and open neighborhoods U of t0 and V of y0 with

    psi(t0)=y0,  psi(U) contained in V,
    psi analytic at every point of U,
    for every t in U and y in V: F(y,t)=0 if and only if y=psi(t),
    HasStrictFDerivAt psi (v |-> -J^(-1) K v) t0.

An explicit specialization starts with the original integral p-adic coefficients
and center, includes them into Q_p, and concludes the same ambient analytic
root graph using evaluation of the original integral polynomials in Q_p.
The only nonsingularity hypothesis is on the original actual solved Jacobian
included in Q_p. No analytic map or derivative formula is assumed.

**Verdict: proved as written.** This is the independent mathematical raw-source
verdict for the final named constructions. The entire local differentiability
and analyticity target is reached. Fresh Lean compilation and exact source
revision reconciliation are separate evidence, recorded after the fresh gate
finishes. This verdict is not a novelty claim or an independent implementation
of the Lean kernel.

## Dependency graph and decisive implications

1. `PolynomialAnalyticEvaluation.evalSystem` is coordinatewise evaluation of
   the supplied MvPolynomial system. `polynomialDeriv` is the finite sum of
   actual evaluated partial derivatives times coordinate projections. Its
   strict derivative theorem is proved by induction on constants, addition,
   and multiplication by a variable. The product step is P*dX_j + X_j*dP,
   with both factors actually evaluated at the center. The pi rule gives the
   system derivative. `matrixCLM` acts by `Matrix.mulVec`, so rows are
   equations and columns are coordinates.
2. Actual polynomial evaluation is analytic through Mathlib's polynomial
   analyticity theorem and finite pi construction. That source proves
   analyticity by polynomial induction. It is not a supplied property of an
   unrelated function.
3. The actual augmented polynomial is `PolynomialJointSystem.augmented F 0`.
   Its evaluation is exactly f(Y,T)=(F(Y,T),T). The inherited evaluated
   partial-derivative theorem gives

       Df(a) = B = [[J,K],[0,I]].

   `PolynomialAnalyticBlocks.upperEquiv` constructs its continuous linear
   equivalence with inverse C=[[J^(-1),-J^(-1)K],[0,I]]. Both BC=I and CB=I
   are derived by matrix multiplication using both inverse identities of J.
   The conversion from a finite linear equivalence to a continuous one is
   legitimate over the complete normed field and its finite-dimensional
   coordinate spaces. No inverse of a singular matrix is silently used.
4. `PolynomialAnalyticInverse.analyticAt_inverse` constructs the actual local
   inverse g of f from its invertible strict derivative and proves g analytic
   using the analytic inverse theorem for that open partial homeomorphism.
   The latter constructs the inverse power series with positive convergence
   radius. Analyticity is not inferred merely from differentiability.
5. `PolynomialAnalyticImplicit.exists_analytic_graph` defines

       psi(t) = solvedPart(g(join 0 t)).

   The inverse identity at f(a)=(0,t0) proves psi(t0)=y0. The chain rule gives
   its strict derivative as solvedProjection composed with B^(-1) composed
   with parameterInjection. The separately proved block computation reduces
   this map to -J^(-1)K, with the negative sign and matrix order explicit.
6. The inverse source is open. Pulling it back by the continuous join map
   yields an open set in the product of solved and parameter coordinates.
   `isOpen_prod_iff` gives a product rectangle V times U0 containing the
   center and lying in that source. The final U intersects U0 with the inverse
   target preimage, the open locus where the same psi is analytic, and the
   interior of psi^(-1)(V). Continuity of psi at t0 proves the last set
   contains t0. Thus U and V are genuinely open neighborhoods, not arbitrary
   sets containing the center or a conditional root graph.
7. For t in U and y in V, a root makes f(y,t)=(0,t), so the inverse's left
   identity on the source forces y=psi(t). Conversely its right identity at
   (0,t) shows both F(g(0,t))=0 and freePart(g(0,t))=t. Rejoining its solved
   and parameter coordinates proves F(psi(t),t)=0. Every quantified point in
   V times U is covered; a selected witness is not substituted for all roots.
8. `exists_analytic_implicit` supplies the actual augmented polynomial
   analyticity and actual strict derivative to that helper, then substitutes
   the explicit inverse block. The public theorem assumes only actual
   polynomial data, an exact root and actual solved-matrix invertibility.
   `differentiableOn_of_analytic_graph` derives differentiability on all U
   from the already established analyticity.
9. `PolynomialRegularityIntegral.exists_analytic_integral_implicit` maps each
   original coefficient and point coordinate into Q_p. The evaluation and
   formal partial derivative maps commute with these inclusions, so both
   Jacobian blocks are the inclusions of their original integral versions.
   The public graph is stated using eval2(algebraMap Z_p Q_p) on the original
   polynomials. It does not replace them by unrelated rational polynomials or
   assume the analytic conclusion. Its neighborhoods and output map are in
   Q_p. A separate integral-valued branch or a uniform radius is not claimed.
10. `PolynomialAnalyticSelection` adds independence of the local branch for
    continuous selections. Continuity places any supplied selection through
    the same point inside V near t0. Its eventual actual root equation and
    the graph equivalence force equality of germs. Both analyticity and the
    strict derivative transfer by eventual equality. On an open set, the
    pointwise application gives analyticity and the actual derivative at
    every point where that selection's solved Jacobian is invertible.

The graph is acyclic: polynomial evaluation and block algebra feed the generic
inverse and implicit theorem, followed by integral specialization and root
selection transfer. None of those concluding results supplies one of its own
hypotheses through a circular status assertion.

## Obligation matrix

| Obligation | Status | Decisive evidence |
|---|---|---|
| Actual polynomial domain and actual partial derivatives | Passed | Evaluation induction and matrix bridge |
| Analyticity, not just a first-order remainder estimate | Passed | Actual analytic inverse power series theorem |
| Invertibility of actual augmented derivative | Passed | Both block inverse products and actual pderiv comparison |
| Actual constructed root map | Passed | solvedPart of constructed inverse at (0,t) |
| Open parameter and solved neighborhoods | Passed | Product rectangle and open intersections |
| Both graph directions for every point in V times U | Passed | Exact left and right inverse identities |
| Correct strict derivative -J^(-1)K | Passed | Explicit inverse restriction and chain rule |
| Differentiability at every point in U | Passed | AnalyticOnNhd implies DifferentiableOn |
| Original integral coefficients and center | Passed | eval2 and pderiv inclusion bridges |
| Continuous existing root selections | Passed | Equality of germs without an analytic hypothesis |
| All primes, including two | Passed | Generic normed field proof and actual Q_p specialization |
| Zero finite dimensions | Passed | No positive-dimension assumptions; generic inverse admits subsingletons |
| Expanded statement contracts | Separately checked in final frozen record | Must retain actual derivatives and both analytic/root graph conclusions |
| Fresh source and axiom reconciliation | Separate release check | audit/reconciliation.json after fresh gate |
| General rationally rank-deficient persistence | Out of scope | Square solved Jacobian invertibility is explicit |
| Global analytic solution on all Q_p^k | Out of scope | Map is total but regularity/graph conclusions are local |
| Uniform explicit neighborhood radius | Out of scope | Prior quantitative bounds are unchanged |
| Native presentation invariance and descent | Out of scope | No such conclusions occur in this target |

## Boundary and control checks

- For F(Y,T)=Y+T, the exact branch is psi(T)=-T, J=K=1 and
  Dpsi=-1. This checks the matrix order and negative sign. The positive
  derivative is refuted over characteristic-zero fields by uniqueness of
  the derivative evaluated at the unit vector. This remains decisive at p=2
  because computations occur in Q_2, not in the residue field F_2.
- The nonlinear F(Y,T)=Y+Y^2+T has a root at (0,0), with J=K=1.
  The positive control actually invokes the complete implicit theorem for
  this nonlinear polynomial and concludes an analytic local root graph with
  strict derivative -I. It does not postulate the branch.
- At k=0, the parameter space is the singleton empty vector and the theorem
  becomes isolation of a nonsingular root with the unique empty-domain
  parameter map. At e=0, there are no equations or solved coordinates, J is
  the empty invertible matrix, and the unique empty solved vector is the
  graph. No nonempty Fin index is required in the universal proofs.
- The proof uses no factorial denominator or division by two. The generic
  normed-field argument and Q_p specialization include the dyadic prime.
- Continuous-selection regularity is explicitly conditional on an actual
  continuous root selection, but the principal existence theorem constructs
  a root map without this assumption. It is therefore an additional
  identification theorem, not a weakened substitute for construction.

## External sources and search scope

All external mathematical leaves were checked in the pinned local Mathlib
revision `aeb72f1e9981b6d35b426b16dca7759be3e7ba06`:

- `Analysis/Analytic/Polynomial.lean`: polynomial evaluation analyticity by
  induction and its finite-coordinate specialization.
- `Analysis/Calculus/FDeriv/Analytic.lean`:
  `OpenPartialHomeomorph.analyticAt_symm'` is over arbitrary
  `NontriviallyNormedField`, not only real or complex scalars.
- `Analysis/Calculus/InverseFunctionTheorem/FDeriv.lean`: the local inverse
  construction requires completeness of the original domain. Its proof
  handles the subsingleton alternative explicitly.
- `Analysis/Analytic/Inverse.lean`: the inverse has the formally inverted
  power series, with a positive radius proof.
- `NumberTheory/Padics/PadicNumbers.lean`: the actual Q_p nontrivially normed
  field and complete-space instances apply for every prime p.

The exact source paths, read portions and hashes are in
`audit/LOCAL_SOURCE_CHECK.json`. These are authorized local primary sources.
No uncached external paper theorem, internet-derived inference or literature
novelty claim is required. The result is a formal specialization of the
analytic implicit-function theorem to the project's actual polynomial and
coordinate interfaces.

The six new mathematical modules, final new controls and final statement
contracts are raw-reviewed. Inherited block algebra and actual joint-system
coordinate/Jacobian definitions were read in full; only the relevant finite
coordinate split and evaluated-Jacobian definitions were rechecked in other
inherited modules. Earlier Paper IX arithmetic proofs and all transitive
Mathlib proofs are not independently re-audited here.

Development elaboration failures are distinct from mathematical counterexamples.
They must be reported from actual retained records, not reconstructed as
invented raw logs. The observed fixes concerned simplification, coercions,
finite indices and dependency order. The target was not weakened to obtain a
passing proof. Fresh compiler acceptance, standard axiom closure inspection,
source hashes and archived report linkage are separately reconciled.
