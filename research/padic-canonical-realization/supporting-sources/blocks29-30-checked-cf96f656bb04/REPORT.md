# Blocks 29–30 — Least coordinate ideals and exact cyclic normalization

**Status is controlled by RESULTS.json, not by this report's presence.**
Goal I phases A and B are the targets. Block28 is the verified predecessor.

## Main result
For prime p, r>=0, R=ZMod(p^r), finitely many coordinate positions I and a finite
digit alphabet, let v0 and T_d be the complete initial vector and linear maps.
Capacity c in [0,r] means J(c)=p^(r-c)R. Capacity zero means zero, not an arbitrary
constant residue. Define capped order nu(0)=r. The exact generator law is

    t*J(c) subset J(b) iff max(0,c-nu(t)) <= b.

This holds even for zero divisors. Tests use the complete summed transition
columns t[d,j,i]=(T_d e_i)_j, not branchwise support unions. Closure is exactly

    r-nu(v0_i) <= c_i,
    max(0,c_i-nu(t[d,j,i])) <= c_j for every d,i,j.

Starting from zero capacities, the monotone inflationary propagation reaches its
least fixed point within |I|*r steps. Invariance is for every vector in the product
of ideals, not just the initial orbit. The result is least among all such invariant
coordinate p-power-ideal products containing v0. No field hypothesis or inverse of
p is used.

The ideal state embeds injectively into Block28's support machine. Initial states,
individual digit transitions, and all ordered words commute exactly with the
embedding. For the actual masks A,B and positive precision, the existing assumptions
(p prime, p not dividing B(0), A(0)=B(0) modulo p^r) yield the inherited canonical
Mahler series F. The new ideal machine computes coefficient n of F for every n.

## Cyclic normalization
For c<=r there is an additive equivalence

    ZMod(p^c) ≃+ J(c),
    y |-> p^(r-c)*y.val mod p^r.

The inverse divides the canonical natural representative by p^(r-c). Membership
proves exact divisibility, and the representative bound controls the smaller
modulus. Both roundtrips and the scalar-reduction compatibility are proved.
This is NOT a unital ring equivalence. A concrete test shows encoding a product
can differ from multiplying its encoded factors.

The whole state is normalized to product_i ZMod(p^(c_i)). An explicit additive
equivalence removes all capacity-zero singleton factors. Transition conjugacy is
exact. The coordinate formula sums in the full residue ring, takes its canonical
natural representative, and only then performs exact integer division. The exact
ambient state cardinality is p^(sum_i c_i). It does not count reachable states.

The cyclic machine retains the all-natural coefficient theorem and output
compatibility across positive precision reductions. State modules at different
precisions are not asserted identical or canonically isomorphic.

## Distinguishing examples
In ZMod4 with v0=(2,0) and T(x0,x1)=(0,2*x0), the old coordinate box has 16 states.
The least capacities are (1,0); the ideal box has 2 states and normalizes to
ZMod2 x ZMod1. The entire ideal box maps to zero, not only its initial vector.
Production theorems check its profile and both cardinalities; a new universal
Lean example checks the entire-box zero transition.

The correlation example over ZMod5 remains a strict boundary: v0=(1,1,0) and
T(x)=(0,0,x0-x1) allow the smaller correlated submodule {(a,a,0)} although individual
coordinate ideals permit all coordinates. A universal example checks vanishing
under the relation x0=x1. Arbitrary-submodule leastness is not a claim here.

## Fresh actual-mask audit
The extension applies the ideal algorithm to actual profiled mask matrices and
compares every complete column with direct polynomial multiply/section/routing.
It tests 76 mask-case executions, including four named stress runs, and 32 output
coefficients per case against an independent Mahler recurrence and the unchanged
support machine. The generic suite is separately replayed on 432 seeded systems
plus two restriction witnesses, including r=0, empty coordinates/alphabet, and
small exhaustive ideal-profile enumeration.

All following table entries are exact Python audit results, NOT concrete kernel
reductions of the entire noncomputable mask construction. A=1 in each row.

| p | r | B(z) | Block28 positions | New nontrivial cyclic factors | Old ambient exponent | New ambient exponent |
|---:|---:|---|---:|---:|---:|---:|
| 2 | 4 | 1+4z | 5 | 4 | 20 | 10 |
| 2 | 8 | 1-z | 54 | 28 | 432 | 101 |
| 2 | 8 | 1+16z | 6 | 4 | 48 | 20 |
| 3 | 6 | 1+81z | 4 | 4 | 24 | 11 |

An ambient exponent e means p^e possible coordinate states. It is a mathematical
cardinality, not a runtime or memory measurement. Strict exponent improvement
occurs in 43 of the 76 executions; strict improvement is not universal.

## Verification and repairs
The incoming candidate did not finish its build: IdealClosureExamples had two
unsolved omega steps and one unused simp argument. The repair uses its existing
upper/lower bounds directly with le_antisymm and removes the unused lemma.
All 78 candidate theorem statements are preserved. All 800 inherited theorem
statements reside in unchanged predecessor modules; only the root import list is
extended relative to Block28.

A preliminary fresh build passed. After repairing supplementary test type and
scope issues, all source and execution-input files were frozen for the final
project-only clean rebuild. Final results must be read from RESULTS.json and
results_current/final_*.json. The exact runtime archive was reconstructed and
hash-verified in this turn, not presumed still running from a prior conversation.

The inventory contains 878 source-declared theorems in 75 production modules.
The axiom checks include every declared theorem and a second inventory of all
project-owned theorem constants, including compiler-generated support constants.
The latter is a completeness check through the same Lean infrastructure, NOT
independently implemented proof verification. Extra leanchecker replay uses the
same Lean kernel. No direct or indirect sorry/native-evaluation axiom is permitted.

85 positive Lean examples (77 concrete and eight universally quantified examples
or equivalence/certificate constructions) are checked separately from three
expected negative controls and one positive arithmetic control. Finite audits
record 52,375 generic assertions and 7,223 mask assertions; each vector equality
counts once. Historical numerical suites are preserved, not relabeled fresh.

Toolchain: Lean4.34.0-rc2, commit 6a10ac8c22beadecabdbb0919c2b50214762f91d;
mathlib aeb72f1e9981b6d35b426b16dca7759be3e7ba06. Dependency caches are pinned but
not independently rebuilt. Stable4.34.0 compatibility remains unperformed.

## Next milestone
After a verified release, Block31 should construct the least correlated invariant
submodule generated by the initial digit orbit. Reachability is not observational
minimization; an unobservable quotient remains a later target. This release closes
the coordinate-ideal and cyclic-coordinate steps, not the full minimal-machine goal.
