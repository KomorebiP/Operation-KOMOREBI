# Formalization coverage — Model-Theory Normalization v0.8

PASS: 49 cold-built modules, 82 completed expected-outcome tasks.
25 inherited dependencies and 24 new modules (six generic, one example, seventeen
computed batches). All 1633 explicit named declarations are
axiom-audited: {'def': 741, 'theorem': 669, 'inductive': 6, 'abbrev': 211, 'structure': 5, 'instance': 1}. Six new generic modules contain
37 theorems and 16 definitions.
The 203 actual kernel computations are regressions, not 203 new discoveries.

Only Classical.choice, Quot.sound, propext occur. No additional project axiom,
sorryAx or Lean.ofReduceBool occurs. All source/input hashes stayed unchanged.
Warnings are errors. One positive and six deliberately false/placeholder controls
have their expected outcomes. All controls reject for proof reasons, not missing
imports, timeouts or memory exhaustion. Upstream Mathlib was reused, not rebuilt.

| Module | Exact new scope |
|---|---|
| BoundedBezout | Executable Euclidean coefficients, signed correctness, coefficient bounds, explicit high-level Euclidean arithmetic peak |
| EuclidCost | Recursion counter for the same Euclidean descent; second input <2^b implies at most 2b nonterminal calls |
| BoundedInsertion | Determinant-one integer insertion, exact span, equality to the inherited canonical normalized result |
| EchelonPeakCore | Explicit residue arithmetic trace and its bound; modular normalized caches meet the bounded-input hypotheses |
| EchelonTemporaryBounds | Raw insertion trace, normalization trace, universal update bound m[2m(m+1)]^d |
| BoundedDiscovery | Identical ordered discovery, total exact semantics, standard defining formula, complete worklist trace bound and power-of-two operand budget |
| BoundedArithmeticExamples | Actual negative Bezout, recursion, coupling, temporary>modulus and zero-dimensional calculations |
| BoundedComputed00–16 | 203 direct solver evaluations by ordinary kernel reduction and inherited all-word code consequences |

## Boundaries

The formal endpoint bounds the explicit high-level coefficient-arithmetic trace.
It does not bound every CPU temporary inside integer primitives, total allocation,
proof terms, kernel checking, source-row transcription or all queue metadata.
The residue trace conservatively covers the membership subtractions; an additional
compiler-level operation-trace refinement theorem is not supplied.

COST_MODEL.md is a written polynomial analysis for a specified schoolbook array
model, not a Lean runtime theorem. The Python port is not verified extraction.
No minimal raw test-list/formula size, new relational discovery, learned policy,
historical-novelty claim or held-out benchmark is added.

All 645 inherited Lean and 42 Python sources are byte-preserved.
Only the 25 imported inherited Lean dependencies were newly cold rebuilt.
Standalone BoundedCase201/202 are convenience copies of cases already in the batches.

Lean: Lean (version 4.34.0-rc2, x86_64-unknown-linux-gnu, commit 6a10ac8c22beadecabdbb0919c2b50214762f91d, Release)
Mathlib: aeb72f1e9981b6d35b426b16dca7759be3e7ba06
Mathematical interpretation is self-review, not independent refereeing.
