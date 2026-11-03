# Focused self-review: SF-LEAN-B06

Primary verdict: **proved as written**, for the G.1 equivalence, explicit scalar
representation, scalar uniqueness and boundary entire collision in the source
digest bound by declarations.json. Review provenance is self-review, against
base `433fecf0b21011af7774fa41fde336e788949411` and the pinned replay receipt.
This is not independent review or a whole-manuscript correctness verdict.

## Claim card and dependency graph

Objects: real labeled scales in (0,1), their canonical entire functions, and
arbitrary nonzero complex amplitude/argument witnesses A,B. Conclusion:
existence of V=A U(Bz) on all of ℂ is equivalent to D=0 and to the union of
the two stated parameter surfaces. The representation uses positive real
S=sqrt(k/p), c=sqrt(S), and the unique normalized scalar solution at (q,Sr).
The boundary example compares two different ordered tuples with equal full
labeled entire pairs.

Necessity: complex HasSum reindexing -> scalar Taylor uniqueness -> rescaling
coefficient identity -> normalization, cubic and quintic identities -> D=0
-> inherited exact defect factorization. Sufficiency: positive square roots
-> surface identities and effective-scale bounds -> scalar solution from
equal-row canonical pair -> chain-rule construction -> inherited entire
uniqueness -> explicit representation -> nonzero rescaling witnesses.
Scalar uniqueness -> symmetry -> full boundary collision. No cycle uses
the target equivalence to construct its own scalar solution.

## Obligation matrix

| Obligation | Result | Evidence |
|---|---|---|
| Complex witness domain | passed | Necessity quantifies over complex A,B; coefficient bridge is complex-valued |
| Ordinary coefficient normalization | passed | HasSum scalar-series representation; exponents 2n+1; indices 0,1,2 |
| Initial normalization | passed | c0=(1,1) yields AB=1; no zero amplitude can satisfy it |
| Nonzero denominators | passed | Positive p,k,S,c; explicit nonzero complex casts before inverses |
| Root branches | passed | Real.sqrt, positive roots, checked squared identities |
| Both exceptional surfaces | passed | Ordered and interchanged factor cases in the scalar construction |
| Effective domain | passed | q,Sr strictly between zero and one, proved before scalar existence |
| Differentiability and chain rule | passed | Actual HasDerivAt statements at all points, with composition and constant factors |
| Global identification | passed | Constructed pair satisfies IsEntireSolution; whole-plane uniqueness supplies equality |
| Scalar uniqueness | passed | Any normalized scalar solution gives an equal-component coupled solution |
| Collision scope | passed | Function equalities for both labeled components, plus tuple inequality |
| Nonreal candidate | passed | Normalized A=-i,B=i is ruled out at the cubic coefficient in the positive fixture |
| Dependency and I/O freshness | passed | Revision pins, exact input hashes before/after, output hashes, immutable source manifest |
| Extra axioms or placeholders | passed | Source guard, exact axiom inventories and kernel replay; placeholder isolated in rejected fixture |
| Operator decoupling, stable inversion and Perron growth | out of scope | No theorem or current catalogue claim marks these complete |

The zero coefficient degree and the first nontrivial odd degrees are checked
at indices 0,1,2. The rescaling of z contributes B^(2n+1), which combines with
AB=1 to yield B² and B⁴ for the cubic and quintic coefficients. These powers
are not kth derivatives and carry no factorial correction.

For the interchanged-factor surface, the two scalar inputs are reversed only
inside a product of scalar values. No U/V label exchange is assumed. The
explicit root formulas agree with the manuscript: c^-1 z=z/sqrt(S), and the
second amplitude is S^-1/2. The strict-contraction boundary at one is not
included.

All external leaves are the pinned local Mathlib APIs used by the checked
proof terms: HasSum multiplication, formal-series uniqueness, HasDerivAt
composition and multiplication, and positive real square roots. No unchecked
external citation or load-bearing numerical computation is used. The
logical axiom inventory is restricted to the three standard axioms recorded
by the verifier. Imported Mathlib cache is not independently rebuilt.

No implication remains missing in this block's target. The strongest safe
statement is the full stated G.1 contract and the explicit entire collision;
it is not a classification of every parameter collision or of the defining
operator under arbitrary coordinate changes. The next check is a precise
positive characteristic-exponent contract for the growth theorem.
