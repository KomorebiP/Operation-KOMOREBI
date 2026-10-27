# Paper III: checked packet-coordinate continuation

**Version:** 0.2.0. **Local record date:** 19 October 2026, America/Chicago.
Execution receipts after midnight UTC are dated 20 October.

**Result: the Section 16 coordinate block is checked. Paper III as a whole remains in progress.**

## What is now proved in Lean
The continuation constructs actual coordinate modules from a finite complete family
of pairwise annihilating idempotent linear maps. Analysis sends an ambient vector to
its actual projected components. Synthesis sums a legal tuple. Both inverse
identities are proved, rather than supplied as an equivalence certificate. A separate
module connects the finite product representation to the literal algebraic direct
sum used in the manuscript.

The construction works over a semiring, without scalar commutativity or additive
inverses. The manuscript's unital-ring case is included. Zero projectors and the
empty index type are allowed where completeness permits them.

Theorem 16.2 now has both its reconstruction and composition identities checked for
arbitrary functions. Corollary 16.3 has separate checked targets for fixed points,
all finite iterates and return times, injectivity, surjectivity, bijectivity, and
actual left and right inverses. Proposition 16.4 has its complete two-sided
change-of-coordinates identity checked. The new representation is also literally
identified with the earlier arbitrary-equivalence coordinate API.

This closes the bridge from *given exact coordinates* to *coordinates constructed
from the projectors* for this nonlinear coordinate layer. It does not assert that
nonlinear interactions vanish or that a supplied connection is flat.

## Executed verification

| Check | Result |
|---|---|
| Original archive and source manifest | CRC pass, 819/819 manifested payloads match |
| Cold own-project compilation | 12/12 modules, including 10 mathematical modules and 2 import roots |
| Compiler policy | One thread, 4 GiB Lean ceiling, warnings treated as errors |
| Exact object correspondence | All cold-build production objects byte-identical to the audited and replayed objects |
| Owning-module inventory | 572 declarations, including 33 outside the project namespace |
| Logical kernel replay | 558/558 declarations, exact audited-name-set match |
| Starting replay environment | Upstream only, zero production overlaps |
| Generated runtime helpers | 14 explicitly inventoried, excluded from logical replay, no logical dependencies allowed |
| Standard transitive logical axioms | propext, Classical.choice, Quot.sound only |
| Compiler/audit controls | 12/12 expected outcomes: 6 positive and 6 correct rejections |
| Corrupt kernel proof | Correctly rejected Eq 0 0 as a proposed proof of Eq 0 1 |
| Concrete Lean boundary consumers | Passed against the cold-build object tree |
| New independent rational checks | 15,331 exact assertions passed |
| Preserved computational companions | 11 expanded groups and 124 exact visual checks passed, 4 false visual controls rejected |
| Runtime identity | Pinned archive, 3 binary/source hashes, all 9 package revisions matched |

The 71 declarations owned by the three new modules include definitions and generated
support. They are not 71 independent mathematical results. The 558 replayed entries
are the entire selected logical source closure, not 558 newly discovered theorems.

The baseline's finite audit also passed on the original finite import root, resolving
its 143 mapped declarations and expected namespace census. The broader owner audit
adds private/generated declarations that a namespace-only count does not enumerate.

## Exact worked example
On Q², use P0(x,y)=(x+y,0) and P1(x,y)=(-y,y). These are oblique projectors with
P0+P1=id and P0P1=P1P0=0. Analysis of (2,3) produces ((5,0),(-3,3)). The full tuple
sums back to (2,3). For F(x,y)=(xy,x²+y), the correct output is (6,7), with output
packets ((13,0),(-7,7)). Matching diagonal restrictions would instead give (0,3).
The complete nonlinear interaction is retained by the checked representation.

The exact checker also uses a missing-completeness example and three identical
identity projectors over F2. The latter are idempotent and sum to id, but without
pairwise annihilation analysis after synthesis need not recover a legal tuple.

## What changed in the predecessor
Only the proof of `gauge_triangleObstruction` changed in an existing mathematical
source. The theorem statement is byte-identical. It now applies the established
gauge holonomy identity instead of expanding the whole expression. Every other
predecessor Lean source is unchanged. New mathematics is isolated in
`PacketCoordinates.lean`, `NonlinearPacketCoordinates.lean`, and `PacketDirectSum.lean`.

## What is still open in this closeout
Paper III remains active. Section 17's multilinear packet reconstruction, jet norm
bounds, derivative and higher-composition bridges are the next block. Later tree,
correction, filtered-lifting, and convergence statements need their own reviewed
source correspondence. The unverified October 16 98+2/2693 claim has not been used.

The previous working directory did not survive. This continuation therefore starts
from a recovered, authenticated baseline and supplies its own evidence. The main,
visual, and older Lean readers remain unchanged historical components. The new
proof guide and current coverage records state the additional accepted scope.

The delivered baseline excludes 77 font binaries and records them explicitly.
Its original manifests are historical records, not false assertions that those
fonts are present. A fresh root manifest inventories the actual delivered files.
No upstream compiler cache or font binary is redistributed. Existing license status
is preserved. Detailed failures are in `docs/FAILURES_AND_LIMITATIONS.md`.
