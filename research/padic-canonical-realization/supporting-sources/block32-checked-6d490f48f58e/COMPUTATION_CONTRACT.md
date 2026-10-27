# Block 32 computation contract

## Mathematical target
For a finite module over ZMod(p^r), p prime, construct a chosen finite product
of nontrivial cyclic factors of exponents 1..r. Recover their multiplicities
from intrinsic p^k-annihilator cardinalities. Transport the actual Block31
reachable-mask digit system and preserve its canonical coefficient outputs.
The signature is canonical; the coordinate equivalence and literal matrices are not.

## Formal evidence
The final plan removes only the project-local .lake/build and retains exact pinned
mathlib and toolchain caches. Each production module has warningAsError enabled.
All source-declared theorem axiom closures and all project-owned environment theorem
constants are inspected. leanchecker reuses Lean's own kernel. New concrete examples,
universal theorem applications, predecessor examples, positive and deliberately
invalid controls run as distinct commands. A negative control counts only when its
expected contradiction/placeholder diagnostic is present, not from any failed exit.
All final execution inputs are hashed before and after each command. The retained
project-local computation-manifest validator supports schema1 with separate input
hash checking; no installed schema2 validator execution is claimed.

## Numerical executable and domains
Run `python verification/audit_presentation.py`. Python arbitrary-precision integers
and SymPy 1.14.0 exact integer matrices only; no floats or tolerance decisions.
Random generator: Python random.Random, seed 32092026.

Generic lane: (p,r) in [(2,0),(2,1),(2,2),(2,3),(3,1),(3,2),(5,1)], dimensions
n=0,1,2,3, excluding (p^r)^n>800; alphabet sizes 0,1,2; two sampled systems per
parameter tuple. This is 168 executions, not a claim of distinct systems (empty and
trivial cases repeat). For each, independently enumerate the digit orbit and its
additive span. Exhaust all that span's elements and all proposed cyclic coordinates
for the two roundtrips, and all coordinate states under each digit. Also check
additivity and scalar reduction on three sampled pairs/scalars per system.

Each Smith proposal (D,U,V) must satisfy D=U*K*V, integral entries, unimodularity,
positive diagonal and divisibility chain before use. K=H^-1*(p^r I), where H is
Block31's integer lattice basis. H is not treated as a vector-space basis modulo p^r.
Check source-relation annihilation on every mixed-modulus matrix entry. Mutated
certificates and wrong coordinate lengths must raise explicit errors.

Intrinsic signatures: for k=0..r+1 compare p^sum(min(k,e_i)) with |M|/|p^k M|, where
the image lattice is computed by HNF from [p^r I, p^k H]. In the generic lane also
count annihilated elements exhaustively, without either normal-form algorithm.
Check every multiplicity and an integer generator-basis permutation/shear.

Actual-mask lane: p=2,3,5; r=1,2,3; five masks per pair:
(A,B)=(1,1-z),(1,1+p^2 z),(1+z,1),(1+z,1+z),(1+z^2,1-z^2).
Add four stress cases (all A=1): (2,4,1+4z), (2,8,1-z), (2,8,1+16z),
(3,6,1+81z). Total 49 cases. Derive matrices from the inherited polynomial/profile
construction. Compare every original profile matrix column with direct polynomial
routing. Check every cyclic generator and three sampled coordinate vectors under
every digit against that polynomial route. Compare coefficient indices 0..31 with
both the independent Mahler recurrence and the preceding support machine. Retain
full Smith certificates and transition matrices for the four stress cases.

A vector/matrix equality counts as ONE assertion, not one per component. Test counts
are accumulated where the assertion executes, and the result must have no failures.
The standalone generator-basis change tests are module-signature tests, not an
assertion that all bases produce equal transition matrices.

## Outcomes and limits
A successful finite run verifies only this implementation and declared input range.
A mathematical counterexample, a code defect, and a timeout are distinct outcomes.
A timeout is inconclusive and is not promoted to a pass. The universal conclusions
come from Lean proofs. Smith/Hermite implementations share SymPy, so small exhaustive
oracles provide an additional genuinely separate computation route. This is
adversarial self-review, not independent human or independent-kernel review.

No formal Python-to-Lean executable refinement, optimized noncomputable polynomial
execution, wall-time/bit/memory bound, canonical basis, full-system classification,
observable quotient, minimum automaton, or cross-precision state isomorphism is
claimed. State cardinality is unchanged at this stage.
