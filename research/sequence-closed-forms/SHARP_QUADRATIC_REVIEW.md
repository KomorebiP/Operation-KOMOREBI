# Self-review of the sharp quadratic theorem

Claim: Theorem K in SHARP_QUADRATIC.md, checkpoint SEQ-DH-2026-11-21-003.
Primary verdict: **proved as written**. Review provenance: separate adversarial
pass by the project authoring agent; not independent review or Lean formalization.

The claim quantifies over every characteristic-zero field and every falling
quadratic weight, with identity differential operator. It asserts Gamma(S)^7
from index one, uniform order at most 63 and optimality of that uniform bound.
It does not assert order 63 at every parameter or for mixed operators.

## Dependency graph and obligations

| Step | Outcome | Decisive check |
|---|---|---|
| Formal moment functional | passed | Coefficient at infinity gives (K2), with moments zero at m=0,1 |
| Multiplication by R | passed | Exact shifted central-binomial ratios, including initial moments |
| Rodrigues object stays polynomial | passed | Successive differentiation leaves sigma^(-5/2) times a degree-n polynomial |
| Orthogonality | passed | Formal residue of a derivative vanishes; n derivatives kill every test degree below n |
| Norm and nonsingularity | passed | Explicit nonzero rational norm; size-five anti-triangular determinant one |
| Smaller singular initial blocks | passed | No orthogonal basis or inverse is used below degree five |
| Differential equation | passed | Formal self-adjointness and nonsingular Gram matrix; distinct eigenvalues for n>=5 |
| Laurent branch formula | passed | Monicity, symmetry and exact ODE substitution; separate sparse-polynomial implementation |
| Transformed determinant and sign | passed | Augmented Vandermonde expansion with four roots; only the first-N-column selection survives |
| Parity factor 4 | passed | Two negative-root rows; their (-1)^N factors cancel; det(P)=4DE and Delta=4rs(s^2-r^2)^2 |
| Normalization 4608 | passed | H_N divided by four consecutive d_n factors; 16 direct rational transformed determinants |
| Degree-six coefficients | passed | Every B term vanishes at n=1, every C term at n=0; each quotient has degree <=3 |
| Nine bases | passed | Exponent sums in {-2,0,2} independently; exact corner and axis factorization |
| Infinite recurrence | passed | Degree-six exponential polynomials are killed by the seventh power of each base factor |
| Initial boundary | passed | All coefficients in four Laurent-polynomial identities checked, not sampled parameter values |
| Start zero | failed for the stronger start | Exponential continuation has value 1/2; actual W0=1; residual Gamma(0)^7/2 is nonzero when a!=0 |
| Singular and degree-drop specializations | passed | Polynomial identity over Q[a,b,c] before specialization; no division survives in the recurrence |
| Sharpness of uniform bound | passed | The unchanged parent minimal-order-63 reduced-OGF certificate at a=b=c=1 |
| Historical novelty | out of scope | No literature or novelty audit requested or claimed |
| General mixed operators | not addressed | Separate remaining research target |

## Computation provenance

- computations/sequence-sharp-symbolic-001: completed, SymPy 1.14.0 exact
  rational identities in formal n,z,w. An exploratory implementation.
- computations/sequence-sharp-replay-001: completed, Python 3.12.14 standard
  library only, separate sparse Laurent algebra. Checks every coefficient of
  the load-bearing finite identities. Its 810 direct monomial block
  determinants supply 225 recurrence residues across nine parameter triples,
  including zero weights, zero leading weight and vanishing minors.
- The parent checkpoint's 85 artifacts were rehashed and are unchanged. The
  parent published source ZIP is pinned by SHA-256 daf022ed9211342577192b9a43ed208edfba1ba42dac9e02636f3d8e98090b66.

The finite determinant checks are regressions. Universal coverage comes from
the formal-moment proof, the coefficientwise symbolic leaves and polynomial
specialization, rather than from the nine numeric cases.

## Proofreading self-review

Scope: SHARP_QUADRATIC.md and this review, under proofread-math self-review
mode. Checked prose/display integration, definitions, delimiter balance,
section references, boundary indices and the difference between uniform
optimality and pointwise minimality. No mathematical-token typo corrections
were made. Removing the candidate status followed the proof audit and is a
research-status update, not a proofreading correction.
Two long displays were reflowed after desktop inspection; formulas and
mathematical scope are unchanged.

## Route disposition

The formal-moment route reaches the stated target. The companion/boundary
route's proposed degree-nine factor is identified analytically by the nine
bases; a full companion boundary-vector derivation is untried and deferred as
an optional independent derivation, not declared impossible or exhausted.
The counterexample route rejects the stronger index-zero start and finds no
counterexample to the stated start in its exact tested range. The full
mixed-parameter problem remains open and is the next substantive target.
