# Block31 exact computation contract

Universal theorem: the reachable module is the R-span of all ordered digit iterates,
least among invariant R-submodules containing the seed. If the ambient additive
module has p^b elements, closure from zero is fixed by round b. The actual mask
instance uses b=sum of the checked coordinate ideal capacities. Canonical coefficient
outputs are preserved. These conclusions are established by Lean, not by this audit.

Finite assertion: an integer column-lattice HNF algorithm computes that reachable
submodule in declared finite examples. The lattice contains modulus*Z^n and starts
there, representing the zero residue submodule. Each step appends the seed and
transition images of the current lattice basis. All operations use integers and
exact SymPy matrices, not floating point, Gaussian elimination over an assumed
field, or inversion of a nonunit in a residue ring.

Generic domain: p,r=(2,0),(2,1),(2,2),(2,3),(3,1),(3,2),(5,1); coordinate count n=0..3,
retaining cases with (p^r)^n<=800; alphabet size 0,1,2; three seeded random systems
per combination. This produces 252 systems. Seed 31092026, Python random.Random.
For each system, enumerate the exact initial orbit and its additive span without
HNF. Compare every ambient vector's membership, cardinality, invariance, fixed
point, all early iterates, and containment in the predecessor ideal product.
Three additional restriction systems distinguish correlated reachability, zero
divisors, and orbit-set versus linear-span semantics.

Actual masks: p in {2,3,5}, r in {1,2,3}, and five mask pairs
(1,1-z), (1,1+p^2 z), (1+z,1), (1+z,1+z), (1+z^2,1-z^2).
Four stress cases: (2,4,1,1+4z), (2,8,1,1-z), (2,8,1,1+16z),
(3,6,1,1+81z). Total 49 distinct cases. Check every complete profile matrix column
against direct polynomial multiply/section/routing. Restrict only zero-capacity
coordinates, then compute correlated closure. A second route forms the span of
short words by the direct polynomial transition, without HNF-basis image iteration.
Check lattice equality of both routes. Also check generator and random-module-vector
transition embeddings and coefficients n=0..31 against the direct Mahler recurrence
and the unchanged support machine. A vector equality counts as one assertion.

A pass establishes implementation agreement in these finite domains. A timeout
is inconclusive. A nonzero exit is inspected rather than interpreted as a
mathematical counterexample. HNF-library semantics and exactness are additionally
cross-checked by exhaustive small modules. The HNF code is NOT formally refined
to compiled Lean. No arbitrary basis classification, observable minimization,
time/bit/memory theorem, or external independent review is claimed.

Toolchain: Lean 4.34.0-rc2, commit 6a10ac8c22beadecabdbb0919c2b50214762f91d;
mathlib aeb72f1e9981b6d35b426b16dca7759be3e7ba06. Python and SymPy versions are
recorded by the executed audit. Official primary references checked for the
cardinality input and integer normal-form API are recorded in SOURCES.md.
The inherited project-local v1 manifest validator is used, with separate complete
before/after source hashing. No installed full v2-validator run is claimed.
