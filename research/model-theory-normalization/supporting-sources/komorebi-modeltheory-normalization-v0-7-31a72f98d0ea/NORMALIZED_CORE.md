# Canonical bounded integer-preimage coordinates for verified discovery

Author: Komorebi P.

## v0.7: target, lineage, and scope

The sole immediate predecessor is `Komorebi_ModelTheory_Normalization_v0.6.zip`,
SHA-256 `7a10778aa0200d130b648f66dd90d76393ed3a8a3bf822cfb747304f1a5e7628`.
The original ZIP is retained verbatim. All predecessor Lean source files are
preserved unchanged. This advances Model-Theory Normalization, not the p-adic or
Representation Calculus version numbers. Counts and completed executions belong
in RESULTS.md and the evidence records, not inferred from this exposition.

The previous verified integer solver had unreduced tails. This block adds an
actual executable tail reduction, proves integer-lattice preservation, proves a
canonical-form theorem, bounds every persistent basis entry by the modulus, and
uses the normalization inside the cached discovery loop. The new construction is
classical integer triangular reduction integrated into the existing verified
semantics. No historical novelty or independent-referee judgment is claimed.

## 1. The representation remains the full modular preimage

For a positive modulus m and residue rows g_i in (Z/m)^d, the represented integer
lattice is

    L = m Z^d + span_Z {integer lifts of g_i}.

The inherited proof identifies L with the full preimage of the original modular
row span. No rational saturation, field-rank substitution, or removal of torsion
is performed. A triangular basis B has d positive diagonal pivots. These are d
auxiliary integer rows, NOT necessarily the minimum number of modular generators.

The discovery source is unchanged: all states of (Z/p^r)^d are admissible, actions
are unary linear maps, and observations are linear functionals. Words act left to
right; right multiplication of a test row PREPENDS an operation to its word. The
result is a sufficient ordered list of genuine tests, not a minimum test list.

## 2. A genuine residue algorithm for any full triangular integer basis

Write a positive-dimensional basis recursively as

    B = ((q,b), (0,B_tail)),  q>0.

For a vector x=(a,v), define

    residue_B(x) = (a mod q,
                    residue_Btail(v - floor(a/q)*b)).

At dimension zero the result is the unique empty vector. This is executable
Euclidean division in the integers, including for negative inputs.

Define Box(B) by

    0 <= x_i < pivot_i(B), for each coordinate i.

The formal proofs establish:

1. residue_B(x) belongs to Box(B).
2. x-residue_B(x) belongs to the ACTUAL integer lattice of B.
3. If x,y belong to Box(B) and x-y belongs to that lattice, then x=y.

For (2), the first quotient supplies the leading lattice coefficient, and the
recursive remainder supplies the tail coefficients. For (3), a lattice difference
has first coordinate a*q. A difference of two integers in [0,q) can be such a
multiple only when a=0. Induction applies to the remaining coordinates.

Endpoints: `residue_inBox`, `residue_coset`, `inBox_unique`, `residue_of_inBox`.
The statements are universal for positive-pivot integer bases, without a modulus.

## 3. Executable normalization and exact lattice preservation

Normalize the lower basis first, then reduce the leading row tail modulo it:

    C = normalize(B_tail)
    normalize(B) = ((q,residue_C(b)), (0,C)).

The leading pivot stays positive and unchanged. The subtracted vector is a true
integer combination of lower rows, so the old leading row is recoverable from the
new row and those same lower rows. This proves BOTH lattice inclusions:

    lattice(normalize B) = lattice(B).

The result is Reduced: every entry above the diagonal in column j belongs to
[0,pivot_j). Note the COLUMN pivot, not the pivot belonging to the upper row.
All lower entries are zero. Normalization fixes reduced inputs and is idempotent.

Endpoints: `lattice_normalize`, `represents_normalize`, `normalize_reduced`,
`normalize_of_reduced`, `normalize_idempotent`, `pivots_normalize`.

### A necessary compatibility check

The lattice with rows (2,32),(0,64) is already reduced. Reducing 32 modulo the ROW
pivot 2 would replace it by zero and change the lattice. In the original lattice,
(4,0) belongs but (2,0) does not. The incorrect clipped lattice admits (2,0).
This counterexample is kernel-checked. The correct algorithm keeps the coupling.

## 4. Canonicity in fixed ambient coordinates

If two reduced positive-pivot triangular bases generate the same integer lattice,
they are equal as the typed basis data.

Proof. Their leading pivots divide each other because each leading row belongs to
the other lattice. Positivity forces equality of pivots. Intersecting the lattice
with the first-coordinate-zero hyperplane identifies the two tail lattices. Their
reduced bases agree by induction. The two leading tails differ by an element of
that common tail lattice and both occupy its Box, so they agree by uniqueness.

Thus Lean proves

    normalize B = normalize C  iff  lattice B = lattice C.

This is an exact canonical representative RELATIVE TO THE GIVEN AMBIENT COLUMN
COORDINATES. It is not an invariant under arbitrary changes of ambient coordinates,
or a claim that all mathematical objects have one preferred representation.

The modular endpoint defines `canonicalBasis m rows` and proves

    canonicalBasis m rows = canonicalBasis m other
      iff rowSpan_(Z/m)(rows) = rowSpan_(Z/m)(other).

The modulus and dimension must agree. This supplies a certified exact cache key
for modular submodules. Equal keys do NOT identify action matrices, observation
decoders, or whole source systems; whole-machine reuse must still bind the full
semantic profile. It is not a canonical Smith diagonal and does not discard
coordinate coupling. Endpoints: `reduced_unique`, `normalize_eq_iff_lattice_eq`,
`canonicalBasis_eq_iff`.

## 5. Uniform bound on all persistent entries

Assume B contains m Z^d, with m>0. Every diagonal pivot divides m.

For the first pivot q, represent m*e_0 and compare its first coordinate. For a tail
pivot, first note that every vector (0,m*v) belongs to the full lattice. Its leading
coefficient must vanish because q>0, so m*v belongs to the tail lattice. Induction
proves the divisibility assertion for every pivot.

Consequently 0<pivot_j<=m. In a reduced basis, every upper tail satisfies

    0 <= B[i,j] < pivot_j <= m,  i<j.

The diagonal may equal m, and the lower triangle is zero. Lean proves the universal
entry theorem

    0 <= entries(normalize B,i,j) <= m.

It also proves that normalized insertion preserves m Z^d and establishes the same
bound after ANY insertion. Initial data, composite positive moduli, m=1, and d=0
are included in the appropriate universal statements.

Endpoints: `pivots_dvd_modulus`, `normalized_entry_bounds`,
`containsModulus_normalizedInsert`, `normalizedInsert_entry_bounds`.

An unsigned encoding therefore needs at most floor(log2 m)+1 bits per stored entry.
For m=2^r this is r+1 bits, including an initial diagonal equal to 2^r. A triangular
storage implementation has d(d+1)/2 such entries. This bit interpretation is an
elementary consequence of the checked numeric range, not a separate Lean theorem
about a particular serialization layout or total program memory.

## 6. The cached discovery loop uses the normalizer

`normalizedRun` stores a basis, accepted tests, and the pending FIFO queue. It
normalizes the initial kernel basis and normalizes after every accepted insertion.
Skips retain the current cache. A successful run returns BOTH the basis and tests.

The preserved contract is

    Represents(B,x) iff reduce_m(x) belongs to the accepted test span,
    and B is Reduced.

This implies the full modular kernel is retained, so every persistent basis at a
queue boundary satisfies the uniform entry bound. The theorem for a returned cache
is `normalizedRun_entry_bounds`; the insert and skip invariants establish the same
condition at intermediate queue boundaries.

Because normalization preserves actual membership, the ordered tests are unchanged:

    normalizedPrimeDiscover = finitePrimeDiscover = fastPrimeDiscover.

The generic worklist comparison is at EVERY fuel budget, including none on exhausted
fuel. For prime powers the existing enough-fuel bound therefore gives a successful
answer, complete observable span, at most r*d accepted tests, and word lengths <r*d.
Zero precision, zero dimension, and empty signatures are included.

The logical compiler constructs the inherited guarded first-order formula from
those actual computed tests and proves that it defines all future behavioral
equivalence. No predicate naming the answer is added, and unrestricted first-order
truth or relational discovery is not asserted.

Endpoints: `normalizedRun_matches`, `normalizedRun_invariant`,
`normalizedPrimeDiscover_eq_reference`, `normalizedPrimeDiscover_eq_fast`,
`normalizedPrimeDiscover_total_correct`, `normalizedPrimeDiscover_defines_behavior`.

## 7. Actual computation and independent executable evidence

The 203 inherited/stress profiles are emitted in 17 new Lean batches. Each one
EXECUTES `normalizedPrimeDiscover` by ordinary kernel reduction; its old expected
answer is a proposition being checked, not an input to the algorithm. No membership
trace, external solver, or exhaustive coefficient search is used by this new loop.

The Python port uses the same lower-first, column-pivot tail reduction, but is not
verified code extraction. Its audit checks every inherited ordered output, exact
small modular spans, positive reconstruction witnesses, bidirectional integer row
certificates, canonical-order and representative invariance, and comparisons with
the independent Smith solver. The source JSON is compared with the actual Lean
literal matrices and expected lists. Finite tests do not replace universal proofs.

The same 203 sources were remeasured in the old and new Python implementations.
At completed queue boundaries, the maximum basis-entry length was 730 bits in the
old solver and 25 in the normalized solver. For the particular source that reached
730, the normalized maximum was 12 bits. The large 2^128-state fixture changed from
69 to 17 bits; the one-dimensional 2^24 torsion case remained 25 bits. These are
basis-entry measurements, not an end-to-end memory or wall-time speedup claim.

New pre-normalization basis entries reached 39 bits in the executed suite. This
counter does not measure every intermediate arithmetic operand. The formal theorem
bounds persistent normalized entries, NOT all temporary values in raw insertion or
normalization.

## 8. What is still not proved

A normalization pass traverses the upper triangle and performs lower-row reductions.
It can increase arithmetic-operation count even while shrinking integers. This
release does not prove an asymptotic bit-complexity bound or optimal runtime. Raw
insertion, extended-gcd coefficients, and temporary subtraction operands still need
explicit verified size bounds before claiming an end-to-end bit-cost theorem.

Canonical triangular form is not canonical Smith extraction, a minimum modular
generating family, or a minimum observation/formula list. Earlier minimum-machine
results remain separate. The arbitrary positive-modulus normalization theorem does
not silently generalize the prime-power numerical discovery-fuel formula.

Parser correctness, verified Python extraction, learned proposals, independent
structural holdouts, relational/multi-input discovery, and independent refereeing
remain separate. The proofs are authoring-assistant self-review using pinned
Lean/Mathlib foundations and the unchanged verified predecessor.
