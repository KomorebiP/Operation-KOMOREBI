# Focused self-review of canonical F.3

Primary verdict: **proved as written within the registered canonical F.3
contract**. Provenance: self-review, not an independent referee report.
Exact source revision is identified by declarations.json and the replay
input hashes, based on c6c529a58b70ebdedac1d0a7dc232153688735b3.

Claim card: for every real scale quadruple in (0,1)^4, the actual real
lower/upper maximum-modulus types are finite positive ordered multiples of
the already max-normalized positive characteristic vector. Their ratios
equal both explicit row ratios. Existence of either ordinary component
type limit is equivalent to existence of the other; the convergent vector
is conditionally a positive multiple of w. No unconditional limit is claimed.

Dependency graph: Block07 exponent/vector identities + Block08 real/maximum
identities and recurrences + Blocks09-11 bounded positive types -> affine
power-factor limit and epsilon envelopes -> lower/upper row comparisons ->
left weighted rigidity -> fixed-space proportions/ratios -> bounded
liminf=limsup criterion -> conditional vector convergence. Earlier sources
contain no dependency on this module. Leaves are internal Lean proofs or
exact pinned Mathlib filter, power, little-o and matrix identities.

| Obligation | Result | Evidence |
| --- | --- | --- |
| Actual UReal/VReal, real type convention and spherical supremum | passed | Reuses Block11 definitions and eventual equality; no substitute numerical profile. |
| Scaling domains | passed | p>0; eventually R>max(c,0); numerator and denominator positive for arbitrary real power. |
| No invented type convergence | passed | Envelopes use liminf/limsup with F.2 boundedness; only the power factor converges. |
| Directions of filter comparisons | passed | Lower comparison requires an upper bound on target f; upper comparison requires a lower bound; convergent comparison supplies its other bound. |
| Two row recurrences and shifts | passed | Final-unit lower uses p(R-1); full upper uses pR and minScale*R>=1 eventually. |
| Vanishing error and epsilon passage | passed | rho>0; pinned log=o(R^rho); continuous polynomial envelopes at epsilon=0 through a nontrivial right neighborhood. |
| Left/right vector distinction | passed | Positive left vector gives weighted cancellation; the normalized right vector gives proportions. |
| Strict left weights | passed | Both are positive for strict contractions; zero-weight control is rejected. |
| Fixed space and ratio denominators | passed | 1-q^rho>0, a^rho>0, w1>0, type1>0; explicit two-row algebra. |
| Scalar order and positivity | passed | Divides actual positive ordered types by the same positive w1. |
| Ordinary limits and vector topology | passed | Bounded real liminf=limsup criterion; positive w coordinates transfer scalar equality; Pi neighborhood convergence. |
| Actual maximum transfer | passed | Eventually equal at nonnegative R; same types and limit-existence predicates. |
| Generic finite-core or full-book coverage | out of scope | Declaration count includes supporting lemmas; no manuscript-wide audit or percentage. |

The positive interface exercises rho=1/2 affine transport, strict weighted
rigidity, the actual canonical proportions, actual type ratios, a vector
limit with an explicit one-component limit premise, and the actual maximum
limit equivalence. Rejection fixtures retain boundedness, strict weights,
the distinction <= versus = for scalar types, and no placeholders.

Validation: accepted 51-step fresh source-bound compilation/axiom/control
and kernel replay; exact counts and raw command results are in the receipt.
Allowed logical axioms are propext, Classical.choice and Quot.sound.
Cached imports are not independently reverified by this run.

No gap remains in the registered F.3 theorem. Broader remaining obligations
are separately listed; exact scaled-liminf equalities were not needed or
claimed. Manuscripts and reading PDFs were not edited.
