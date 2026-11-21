# Self-review of the interior classification

Claim: Theorem N in INTERIOR_ORDERS.md, checkpoint SEQ-DH-2026-11-21-005.
Primary verdict: **proved as written**. Provenance: a separate adversarial
reconstruction by the project authoring agent; this is project self-review,
not independent review or Lean formalization.

## Claim card and dependency graph

The theorem quantifies over all characteristic-zero fields and all a,b,u,v
with abuv nonzero, for precisely Theorems L/M's moments. It determines minimal
eventual scalar constant-coefficient recurrence order by the finite gcd rule.
It retains W0=1 and the minimal recurrence start at one. Theorem M supplies
the complementary coordinate boundary. Higher-degree weights and higher-order
operators are not included.

Dependencies: defining moments -> normalized quartic from L -> sixteen branch
coefficients -> collision geometry and confluent degree lemma -> coefficient
degrees after grouping -> exact pole orders -> minimal recurrence. The finite
characteristic and Bezout identities are leaves with explicit coverage bounds.
No dependency points back to the order rule being proved.

| Obligation | Outcome and decisive argument |
|---|---|
| Scalar normalization | passed: W_N scales by (au)^N, with au nonzero |
| Root-free quartic H | passed: H(Z)=R(wZ), so root multiplicities are unchanged; all coefficients use t,q only |
| Characteristic F | passed: Newton power sums of normalized product bases, reciprocal multiset, and 45 degree-complete nodes for all first-eight coefficients |
| Original coefficient field | passed: gcd degrees are extension-invariant; the minimal annihilator is fixed by the finite splitting field's Galois group |
| Endpoints and opposite roots | passed: R(+/-2)=+/-12tw; simultaneous even/odd equations give 24t^2=0 for distinct opposite roots |
| Zero repeated root | passed: R(0)=0 forces t=2 and R'(0)=8w nonzero |
| Simple-root cluster size | passed: only Hamming distances three/four are allowed; three such vertices would have a forbidden distance-one/two pair |
| Degree-six leading coefficient | passed: alternating Laurent determinant divided by n(n-1) and Vandermonde; every coefficient has the same possible cross-branch poles |
| Next coefficient | passed: determinant multilinearity and trace give -15-6S after division; 136 separate exact rational-jet checks |
| Triple-product collisions | passed: the leading-coefficient sum reduces to nonzero endpoint factors; repeated entries in an A mode are permitted |
| Negative full collision | passed: degree six cancels and degree five remains; its vanishing would force q=-16(t+1), contradicting B=-576t^3 |
| Confluent degree increase | passed: after grouping fixed branch counts, alternating divided differences are regular; only k(m-k) cross poles occur and the local first/second divided differences have nonzero highest coefficient |
| Hidden poles in lower coefficients | passed: Q_n/(n(n-1)Delta(v)) is Laurent polynomial, so no coefficient can have poles beyond the displayed cross factors |
| Spectral specialization after confluence | passed: the confluent coefficients are regular for distinct nonendpoint root groups; equal frequencies combine finite polynomials without a further degree increase |
| Single-double intersections | passed: four distinct degree-seven B modes cannot cancel against degree-six A modes; A-only clusters have at most two entries; the negative base is never a B mode |
| Two double roots | passed: coefficient matching forces one rational t,q pair; exact h=9 check covers that entire type, and confluent degrees give 69 |
| Triple root | passed: exact elimination to P(y), eight reconstructed Bezout leaves excluding every possible collision, and degrees 6/8 give 64 |
| Quadruple root | passed: the two forced equations have nonzero remainder -3136/289 |
| Exhaustiveness of gcd cases | passed: gcd(H,H') degree is four minus the number of distinct roots; its quadratic gcd distinguishes 2+2 from 3+1; the only remaining type is impossible |
| Minimality rather than an upper bound | passed: distinct nonzero exponential bases give distinct GF poles, whose exact orders are degree+1 |
| Low indices | passed: L's complete coefficient boundary identities survive confluence; continuation at zero remains 1/2 |
| Start at zero | fails for the stronger start: the actual W0 differs by 1/2 and every minimal annihilator has nonzero constant coefficient |
| Historical novelty, external acceptance, Lean | out of scope and unassessed |

The confluence argument was reconstructed independently of the numerical
examples. In particular, the common leading local factor depends on the branch
count k, not on which split roots carry those signs. Its cross denominator is
the product of alpha(e_i-e_j); the finite divided-difference identities leave
the nonzero highest n coefficient. This resolves the main possible source of
an erroneous degree correction. The single-double proof counts four B clusters
even when A modes join them, so it covers nonsmooth intersection points as well.

## Exact computation provenance

- sequence-interior-structure-001: failed at a syntactic SymPy expression
  equality in an endpoint assertion. It is an implementation failure, not a
  mathematical counterexample. Its source and failed manifest are preserved.
- sequence-interior-structure-002: corrected comparison by expansion; completed.
  Constructs the characteristic, discriminant/collision polynomials and
  triple-root equations over exact rational polynomial rings.
- sequence-interior-subresultant-001: completed; constructs eight exact
  triple-root noncollision Bezout witnesses. The final classification uses
  gcds of H, so the auxiliary linear subresultant is not a hidden assumption.
- sequence-interior-gf-001: completed; ten all-index sample minimal orders,
  using L's bound, complete q interpolation and degree-preserving modular
  coprimality certificates. These samples test the proposed rule, not its
  universal coverage.
- sequence-interior-intersections-001: completed; examines discriminant and
  collision intersections. Rational extraction is explicitly not an exhaustive
  algebraic-point search. The universal proof handles the remaining points.
- sequence-interior-replay-001: completed, Python 3.12.14 standard library only.
  Reconstructs 765 characteristic coefficient comparisons at 45 complete nodes,
  verifies eight Bezout identities and all ten exact GF cross multiplications
  and modular witnesses, and checks 2,732 direct monomial determinants. The
  sample interpolation covers 342 nodes and 38,646 defining prefix values.

The jet regressions include eleven patterns and two choice-invariance checks:
simple, triple/full collisions, single-double AA/AB collisions, negative/full
collisions, two-double and triple-root patterns. They include general quartics
outside the mixed family; their numerical orders 74,80,81 are not asserted to
occur in that family from these regressions. The actual mixed examples are
the ten t,q points in the certificate. The algebraic order-64 type is covered
by its universal derivation and exact noncollision witnesses.

All six run manifests validate, including the preserved failed run. The five
successful runs do not rely on that failed result. Claimed finite evidence
comes from the bounded records, not unrecorded development checks. The parent
checkpoint's 36 artifacts and published 89-member source were rehashed.

## Proofreading self-review

Scope: the new Theorem N and this review only. Checked hypotheses, fields,
gcd conventions, root multiplicities, normalization, display integration,
formula signs, references, low indices and the distinction between a finite
algebraic decision rule and a finite sample. New mathematical arguments are
research additions, not typographical repairs. Mathematical-token typo
corrections: none. Earlier theorem sources are preserved.

## Route disposition

The spectral route resolves the target via collisions and confluence. The GF
route supplies certified all-index discriminators without a huge two-variable
numerator construction. That broad numerator construction is deferred as an
optional alternative, not called impossible or exhausted. The falsification
route found no counterexample in its explicitly recorded regimes and exposed
the necessary corrections for negative full collisions and repeated roots.

The bounded mathematical target is reached. Publication and live verification
remain delivery steps. Theorem M plus N classifies this mixed linear family;
pointwise quadratic-weight orders and higher-degree/higher-order families
remain separate open work.
