# Independent audit: first-order motion of weighted p-adic roots

Author: Komorebi P.  
Audit role: independent source-reading subagent, separate from proof builders.  
Target: `TARGET_CONTRACT.json`, checkpoint `paper9-motion-from-weighted-dd99a705`.

## Normalized claim and verdict

**Verdict: proved as written.** The raw final declarations construct the root,
establish uniqueness on the entire stated ball, retain the displacement depth,
and prove the fraction-field formula with an integral error witness. A conditional
error estimate alone would not discharge this target; the main theorem supplies
the missing existence and uniqueness conclusions explicitly. Exact source
hashes are recorded in `motion_source_audit.json`.

Let p be prime, R = Z_p, K = Q_p, d finite, F,H in R[X_1,...,X_d]^d,
a in R^d, and F(a)=0. Let J = DF(a) be the actual polynomial Jacobian.
Suppose J is invertible over K and p^s J^(-1) has integral entries, with
s,M natural and M>2s. For G=F+p^M H there is exactly one root b in
a+p^(s+1)R^d. It satisfies b-a in p^(M-s)R^d and

    b-a = -p^M J^(-1) H(a) + epsilon,
    epsilon in p^(2M-3s)R^d.

The matrix in the correction term is the original DF(a), not DG(a).
The inverse bound uses the stated s, not a substituted determinant valuation.
The fraction-field equation has an integral epsilon witness. No topology or
analyticity claim beyond these conclusions is implicit.

## Dependency graph

1. Integral polynomial Taylor identity at a:
   F(a+h)=Jh+Q(h), with Q containing no constant or linear terms.
2. Integrality gives v(Q(h))>=2v(h) and, on p^(s+1)R^d,
   v(Q(h)-Q(k))>=v(h-k)+s+1. Integral H is nonexpanding.
3. The original inverse defines the self-map
   Psi(h)=-J^(-1)(Q(h)+p^M H(a+h)). It preserves p^(s+1)R^d,
   and gains at least one digit on differences because M>2s.
4. Completeness/contraction supplies existence and uniqueness on that entire
   ball. Preservation of p^(M-s)R^d yields the stronger displacement bound.
5. Subtract the linear response at a:
   epsilon=-J^(-1)Q(b-a)-p^M J^(-1)(H(b)-H(a)).
6. The two terms have respective depth at least 2M-3s and 2M-2s.
   Their sum therefore has depth at least 2M-3s.
7. The integral certificate A=p^s J^(-1) yields the equivalent expression
   epsilon=b-a+p^(M-s) A H(a); inclusion into K preserves the equation.

The Lean implementation may express steps 2--4 by polynomial normalization and
the already checked contraction theorem rather than by explicit valuation
functions. That is equivalent only if it constructs the actual perturbed
polynomial and proves equivalence for every point of the full root ball.

## Obligation matrix

| Obligation | Mathematical status | Decisive check |
|---|---|---|
| Actual square polynomial system, arbitrary integral p-adic coefficients | Passed | Translation and polynomial substitution preserve integrality. |
| Actual base-point derivative J=DF(a) | Passed | Required explicitly in Taylor and correction formula. |
| Same inverse exponent s throughout | Passed | Each inverse application loses at most s; no determinant bound needed. |
| Root existence | Passed | Actual polynomial normalization followed by complete-space contraction. |
| Uniqueness on a+p^(s+1)R^d | Passed | Every point of the full ball is a shifted integral vector; root/fixed-point equivalence and contraction uniqueness apply. |
| Displacement depth M-s | Passed | The smaller ball is preserved, or normalized contraction retains constant-term precision. |
| First-order error depth 2M-3s | Passed | Quadratic term depth 2(M-s), followed by one inverse loss s. |
| Perturbation variation term | Passed | Depth M+(M-s)-s=2M-2s, at least claimed error depth. |
| Sign and inverse order | Passed | Move Q+p^MH to the right of Jh=-(Q+p^MH). |
| Natural subtraction | Passed | M>2s implies s<=M and 3s<2M; no truncation hides a negative depth. |
| p=2, s=0, M=1 | Passed | Error depth 2, displacement depth 1; explicit sharpness example below. |
| d=0 | Passed | Empty vector space has exactly one vector; all coordinate conditions vacuous. |
| H=0 or H(a)=0 | Passed | a itself is the unique selected root; no finite valuation of zero is required. |
| Strict threshold M>2s | Passed and necessary uniformly | Existing X^2+3 dyadic counterexample at M=2s. |
| Rationally singular Jacobian | Out of scope | The required invertibility fails. |
| Analytic root dependence and native descent | Out of scope | Neither follows solely from this theorem. |

## Sharpness and boundary checks

The displacement exponent is attained by F(X)=p^s X, a=0, H=1:
b=-p^(M-s). The earlier release formally verifies this example.

For the first-order exponent, choose F(X)=p^s X+X^2, a=0, H=1.
The root in the selected ball satisfies

    b(p^s+b)=-p^M.

Since b has depth at least s+1, p^s+b has exact depth s. Consequently
b has exact depth M-s, and

    b+p^(M-s)=-p^(-s)b^2

has exact depth 2M-3s. This proves that no uniformly larger error exponent
can replace the stated one. It is a written sharpness proof for all allowed
p,s,M; the control module gives an actual Lean-checked dyadic specialization.

The dyadic specialization F=X+X^2, H=1, s=0, M=1 has an even selected root.
Every such root has b+2 divisible by 4 and not 8. Reduction modulo 8 forces
b=2 modulo 8. The finite calculation in `sharp_mod_eight` is a kernel-checked
enumeration of ZMod 8, not a numerical approximation to a p-adic root.
`exists_sharp_motion_root` connects actual existence to the main root theorem,
and `no_uniform_extra_error_digit` therefore gives an unconditional formal
counterexample to a uniform exponent improvement.

At the excluded boundary p=2, F=X^2-1, a=1, s=1, M=2, H=1,
G=X^2+3 has no Z_2 root. This rules out the uniform relaxation M>=2s.
The inherited `PolynomialWeightedControls` verifies its failure modulo 8 and
passes that obstruction to actual p-adic roots.

## Source scope

Read in full: historical
`research/perturbation/Paper_IX_Perturbation_Deformation_Bridge.md`, especially
sections 2--4, from the prior parameter-charts release. Its historical statements
that these results were not yet formalized are dated status, not current status.
The proof above is self-contained except for completeness of Z_p and the
standard contraction theorem, which the implementation inherits through pinned
Mathlib. No novelty claim or new external literature attribution is made.

Raw-source checks: `PolynomialTaylorDisplacement.lean`,
`PolynomialMotionEstimate.lean`, and `PolynomialMotionRational.lean` implement
steps 1, 5--7 with the correct actual derivative, signs, exponents and field map.
The estimate is correctly conditional on an already constructed root with its
displacement bound. It is not by itself the full target theorem.

## Final formal audit

`PolynomialMotionNormalization.exists_motion_normalization` applies Taylor to
AF and a polynomial difference identity to AH. With t=p^(s+1), it proves the
actual identity

    A G(a+t u) = p^(2s+1) (C + u + p Q(u)),
    C = p^(M-(2s+1)) A H(a),   Q(0)=0.

The perturbation contribution to Q is p^(M-(s+1)) times its normalized
polynomial difference. All exponent equalities use M>2s. The normalization has
no assumption about the new Jacobian DG(a).

`PolynomialRootMotion.exists_root_from_original_preconditioner` proves a
root/fixed-point equivalence for every integral u. Its matrix certificate
JA=p^s I makes A injective by applying J and cancelling the nonzero scalar.
This injectivity does not depend on which polynomial system is preconditioned.
That fact justifies using the original certificate on the perturbed G.
Every competitor z in the entire stated ball has z=a+p^(s+1)w for some
integral vector w, so the proof does not restrict uniqueness to the smaller
precision ball. The constant-term depth and Q(0)=0 give the claimed M-s
displacement without assuming an approximate or pre-existing root.

`exists_root_motion` assumes the actual J=DF(a), its fraction-field
invertibility, and exactly the specified bound p^sJ^(-1) integral. It obtains
both integral certificate identities from the prior inverse bridge, constructs
b, and applies the independent Taylor estimate. `exists_rational_error` then
chooses epsilon as the integral difference from the linear response and proves
the formula by the entrywise integral-to-rational inclusion. Its scaling identity
uses p^(M-s) p^s=p^M; the original inverse J^(-1) remains in the final equation.

`exists_unique_root_motion` cleanly states unique existence for roots in the
full ball and separately quantifies the stronger estimates for every such root.
Thus the stronger estimates are not accidentally part of a weakened uniqueness
predicate. No unverified root, Lipschitz estimate, or updated-Jacobian inverse is
assumed at the public theorem boundary.

The inherited polynomial contraction source was reread. It proves polynomial
evaluation is nonexpanding, obtains strict contraction from ||p||<1, and calls
the pinned Mathlib complete-space fixed-point theorem. The exact local Mathlib
source for `ContractingWith.fixedPoint`, `fixedPoint_isFixedPt`, and
`fixedPoint_unique` was inspected, including its Nonempty and CompleteSpace
hypotheses. Fin d -> Z_p satisfies both, even at d=0. The local Z_p completeness
instance was located in the pinned source. These are existing formal library
dependencies, not assumed new research claims.

The control module has one failed development compile, caused by numeral-cast
normalization and a residue nonzero goal; both were fixed. Two subsequent
compiles passed, the latter including unconditional sharpness existence. See
`dev/audit/development_record.json`. No failure was removed by weakening the
control statement or changing the mathematical hypothesis.

Remaining mathematical gap for this target: **none identified**. Fresh whole-block
compilation, strict source scanning, expanded public contracts, negative controls,
and declaration axiom closure are separate verification gates; their exact
outcomes belong to the generated gate report. General singular systems,
analyticity, native invariance, and descent remain outside this theorem.
