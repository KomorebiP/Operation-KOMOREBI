# Incremental integer-lattice discovery with verified exact semantics

Author: Komorebi P.

## v0.6 — scope and lineage

The sole immediate predecessor is `Komorebi_ModelTheory_Normalization_v0.5.zip`,
SHA-256 `33711d6db1507d309840e0fe17a41da8dc73a17b388484d79a084d8fd5b55945`.
It is preserved verbatim in `history/`; inherited Lean sources are unchanged.
This is Model-Theory Normalization v0.6, not a new p-adic or Representation
Calculus release. Completed verification outcomes are recorded in RESULTS.md.

The last checkpoint verified witness checking and complete-trace replay while its
fast Smith producer remained unverified. This block takes a different algorithmic
route: an executable, verified INTEGER ECHELON basis of the full modular preimage.
It does not claim to verify the old Python Smith implementation or compute a
canonical Smith/Hermite normal form. It supplies exact incremental membership
and plugs that implementation into the already verified discovery loop.

## 1. Integer preimages retain all modular relations

Let m be any positive integer, including m=1, and let rho:Z^d -> (Z/m)^d be
coefficientwise reduction. For residue rows g_1,...,g_l choose their canonical
integer lifts and put

    L = m Z^d + span_Z { lift(g_i) : 1<=i<=l }.

The proved identity is

    x in L  iff  rho(x) in span_(Z/m){g_1,...,g_l}.

The reverse implication lifts scalar combination coefficients and puts the
remaining vector into ker(rho)=m Z^d. The forward implication reduces the same
integer combination. This is an equality of the full preimage, not a rational
saturation. In particular it preserves nonzero torsion and coupled congruences.

The initial lattice m Z^d has a full triangular integer basis. Every subsequent
insertion preserves full rank, so a d-dimensional modular problem always uses
exactly d integer basis rows, even if its minimal MODULAR generating family has
fewer than d members. The auxiliary m Z^d rows may reduce to zero.

Example at m=64: the row (2,32) generates (4,0), but does not generate (0,32).
Dropping the coupling between the two coordinates would change membership. The
actual solver computes both answers correctly, and they are kernel-checked.

## 2. A typed triangular basis and a real membership algorithm

`Basis d` is a recursive data type. At positive dimension its first row is
(q,b), where q is a positive integer and b is a tail vector; the remaining rows
have leading coordinate zero and form a `Basis (d-1)`. Positivity is carried by
proof data. A zero or negative pivot cannot inhabit this type.

`synth B c` synthesizes the integer combination with coefficients c. Lean proves
that synthesis is injective. The lattice is the actual set of synthesized
vectors, with its integer submodule structure constructed from addition and
scalar multiplication proofs.

To decide membership of x=(a,v), test q|a. If divisibility fails, return none.
Otherwise subtract (a/q)b from v and recur on the tail. A returned vector c is
proved to satisfy synth B c=x. Conversely, such a vector is returned exactly
when x belongs to the lattice.

This algorithm uses at most d pivot divisibility tests and d triangular
substitutions. Integer division is performed only when the dividend is exactly
divisible by the positive pivot. It neither inverts nonunits modulo m nor
enumerates scalar coefficient tuples or source states.

Endpoints: `coordinates_correct`, `coordinates_solution`, `synth_injective`.

## 3. Exact insertion via one Bezout update per column

Suppose the current leading row is b=(q,b_tail), candidate v=(a,v_tail), q>0.
Use integer extended gcd to obtain

    g=gcd(q,a)>0,  s*q+t*a=g,  Q=q/g,  A=a/g,
    q=g*Q,  a=g*A,  s*Q+t*A=1.

Apply the two-row update

    b' = s*b+t*v,
    v' = -A*b+Q*v.

The first coordinate of b' is g; that of v' is zero. Its coefficient matrix is

    [ s   t ]
    [-A   Q ]

and has determinant one. The explicit inverse is

    [ Q  -t ]
    [ A   s ].

Thus the old pair and new pair have exactly the same INTEGER span. Recurse on
the old tail basis and the tail of v', retaining b' as the new first row.

The recursive program has exactly d insertion levels. Lean proves

    Represents(insert B v, x)
       iff exists c:Z, Represents(B, x-c*v),

and consequently

    lattice(insert B v) = lattice(B) + span_Z{v}.

No assumed invariant or desired span equality is a premise of the insertion
proof. The positivity and Bezout equations are derived from the actual gcd
implementation and imported integer theorems.

Endpoints: `gcd_update_data`, `insert_correct`, `lattice_insert`.

## 4. Cached basis state in the discovery loop

For source states in R^d, R=Z/(p^r), let A_a be column operation matrices and O_j
be observation rows. ALL source states are admissible. A word acts left to right;
right multiplication of an observation row prepends an operation to its word.
The mathematical target is

    M=span_R{O_j A_w : all finite words w, all observations j}.

The new stateful worklist retains a Basis d beside its accepted-test list L and
pending FIFO queue. Its invariant is

    Represents(B,x) iff reduce(x) in testSpan(L), for every integer x.

Initialization follows from the exact kernel of scalar reduction. Acceptance
updates B by inserting the candidate's actual lifted test row. The universal
insertion theorem proves the new state invariant. A skip leaves B unchanged.
The executable loop decides membership by `coordinates`; no proposer or
certificate data is an argument and no enumerative fallback occurs.

Lean proves equality with the old worklist using ANY correct span oracle at
every fuel budget. This covers both successful return and insufficient fuel.
The returned ordered LIST is identical, not merely a basis for the same span.

For prime p and all natural r,d,k,o, the inherited fuel o+k*r*d+1 suffices.
Therefore the concrete `fastPrimeDiscover` returns some L, spans the complete
observable module, accepts at most r*d tests and returns words of length <r*d.
Zero precision, zero dimension, no operations and no observations are included.

Endpoints: `stateCorrect_initial`, `stateCorrect_insert`, `fastWorklist_matches`,
`fastPrimeDiscover_eq_reference`, `fastPrimeDiscover_total_correct`.

The integer membership and update results apply to EVERY positive modulus m,
including composite m. The assembled enough-fuel statement uses prime p and
m=p^r because it reuses the earlier prime-power rank proof. Do not silently
extend that particular numerical bound to an arbitrary modulus factorization.

## 5. The logical endpoint comes from actual computation

The successful output constructs the existing finite code certificate. The
standard formula is

    State(x) and State(y) and
       AND_(w,j in L) [observe_j(T_w x)=observe_j(T_w y)].

Lean proves its actual Mathlib `IsQF` predicate and its satisfaction equivalence
with complete behavioral equality on tagged source states. No predicate for the
answer or encoding matrix is added to the original language.

`fastPrimeDiscover_defines_behavior` composes executable discovery, universal
termination and semantics. `fastPrimeDiscover_standard_formula` gives the result
for a particular computed successful list. The language retains the previous
state/value guards and observational restriction; unrestricted state equality,
full first-order elementarity and relational discovery are not added.

The raw test list is sufficient and deterministic. It is NOT asserted to have
minimum length, minimum formula size or minimum linear-coordinate count.
Earlier minimal-representation theorems remain distinct proof paths.

## 6. Executed instances versus traces

All 202 inherited sources plus the one-coordinate descending-torsion source
are exercised as actual evaluations of `fastPrimeDiscover` by kernel reduction:

    fastPrimeDiscover ... = some expectedTests := by decide +kernel.

There is no supplied membership evidence list or earlier search trace in this
computation. The old result serves as the asserted regression answer, not an
input to the algorithm. Each case also obtains its all-word code certificate.

The large inherited source has eight coordinates modulo 65536 and hence 2^128
admissible initial states. The algorithm accepts two tests and processes five
candidates. Actual kernel execution reaches its two-test answer without state
or coefficient-tuple enumeration. This differs from v0.5, where the reference
answer at this scale was established by checking a supplied trace.

The descending-torsion example has one coordinate modulo 2^24 and observations
2^23*x,...,x with identity dynamics. It accepts 24 rows and processes 48 decisions
but retains ONE integer basis row. This is not a claim of 24 independent final
modular directions.

These are synthetic regression and mechanism examples, not independently frozen
structural holdouts or evidence of broad mathematical-discovery superiority.
The Python source-to-Lean transcription is independently checked but not proved
correct as an executable parser.

## 7. Costs and unproved efficiency claims

Membership uses at most d pivot divisions. Insertion makes one gcd/Bezout update
per column, d updates per accepted row, and O(d^2) tail arithmetic operations.
The worklist retains exactly d basis rows. It also stores the accepted tests and
queue; reconstructing an observation row still depends on the word length.

Those are structural arithmetic-operation observations, not a formal asymptotic
bit-complexity theorem. This basis is not tail-reduced. Integer coefficients can
grow, and the Python audit records stored basis entries reaching 730 bits in its
retained suite. Intermediate operands can be larger. No uniform polynomial bit
bound, speedup over the old backend, or optimal memory theorem is claimed.

`integer_echelon.py` is a separate port used for auditing and convenient execution.
It is NOT code extracted from Lean, and its program correctness is not covered
by the Lean theorem. The Lean definitions themselves are executable and verified.
The old Python Smith implementation is unchanged and remains unverified.

## 8. Next exact obligation

The selected incremental membership/update and cached discovery correctness goals
are closed by the new Lean definitions and proofs. The next efficiency obligation
is controlling integer coefficient growth, for example by a proved tail-reduction
normalization that preserves the lattice and supports an explicit bit-cost bound.
Canonical Smith extraction, verified parser/exporter, minimum logical test selection,
learned proposals, and external review remain separate tasks.

This is an algorithm-integration and formal-verification advance using standard
integer lattice, Bezout and modular preimage arguments. No historical novelty or
independent-referee verdict is made.
