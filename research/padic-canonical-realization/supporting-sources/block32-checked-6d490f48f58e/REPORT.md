# Block 32 — Intrinsic cyclic presentations of reachable modules

**Status: PASS.** Goal I / phase D is complete under the proof boundary below.
This release adds 53 theorem declarations to 934 inherited declarations,
total 987 in 83 production modules. All inherited mathematical files are
byte-identical except for one root import addition. The exact checked Block31 archive
is retained at `predecessor/Block31_Checked.zip`.

## Finite coordinates and intrinsic signature
For any finite module V over ZMod(p^r), p prime, the source constructs a chosen
presentation V ≃+ product_i ZMod(p^e_i), with 1<=e_i<=r. Scalar action is reduction
from ZMod(p^r) in each factor. The initial state, digit maps, outputs and every
ordered word are transported exactly. At precision zero the factor index is empty.

This invokes mathlib's classical finite abelian group decomposition, not a newly
claimed structure theorem. The exponent restriction, intrinsic-signature proof,
operator interfaces and actual-mask integration are compiled in this release.

The p^k-annihilator has cardinality p^sum_i min(k,e_i). Its logarithmic first
differences count factors of exponent at least k; second differences recover
the exact multiplicity of exponent k. Thus the exponent multiset, and its sorted
list, are independent of the chosen presentation. Equality of the signatures is
proved equivalent to additive isomorphism and to ZMod-module isomorphism.

The generators have exactly the diagonal p-power integer relations. Digit matrices
are mixed-modulus homomorphisms: an entry in destination factor p^e_j must satisfy
p^e_i*t_ji=0 for source factor p^e_i. Equivalently its integer representative is
divisible by p^max(e_j-e_i,0). The exact retained-entry sum formula is proved.

**Canonical signature does not mean canonical basis or matrices.** The chosen
equivalences can produce distinct conjugate matrices. Also Z/4 and (Z/2)^2 have
equal cardinality but unequal signatures and are proved nonisomorphic. Both are
production restriction witnesses.

## Actual mask end-to-end theorem
The state presented is the actual Block31 correlated reachable submodule. For
prime p, positive r, integer masks A,B, p not dividing B(0), and A(0)=B(0) mod p^r,
the new machine outputs coeff_n(F) for every n, where F is the inherited constructed
normalized Mahler series. No externally supplied series/equation oracle is added.
Positive-precision output reduction is preserved. Coordinates at different
precisions are not identified.

Unlike Blocks25–31, this stage does not reduce state cardinality. It supplies exact
independent cyclic components for the already reduced module, which prepares the
observable-quotient stage. It is not a minimal automaton theorem.

## Exact finite examples
All rows have A=1. Exponents mean cyclic factors Z/(p^e), not free vector-space
dimensions. The numerical signatures are verified by the exact Python audit,
including independent p^k-image HNF cardinalities; they are not concrete kernel
reductions of Lean's noncomputable chosen presentation.

| p | r | B(z) | Cyclic exponents | Number of factors | State cardinality |
|--:|--:|---|---|--:|---|
| 2 | 4 | 1+4z | 2,2,4 | 3 | 2^8 |
| 2 | 8 | 1-z | 2,2,4,4,5,5,7,7,8,8 | 10 | 2^52 |
| 2 | 8 | 1+16z | 4,4,8 | 3 | 2^16 |
| 3 | 6 | 1+81z | 1,2,6 | 3 | 3^9 |

Every cardinality equals its Block31 predecessor. Full lattice/Smith certificates
and transported matrices for these four cases are in `results/audit_presentation.json`.

## Fresh verification
A predecessor baseline built before extension. The authoritative final plan then
removed only project .lake/build and rebuilt all 83 modules under explicit
warning-as-error settings: 2609 jobs completed. All 18 final recorded phases retained
identical before/after execution-input hashes. Each intended negative exit was
checked for its exact contradiction or placeholder diagnostic.

All 987 source theorem axiom closures were inspected, including
18 axiom-free declarations. The environment inventory additionally covers
2263 project-owned theorem constants, including generated ones; it is an
audit-completeness count, not additional new mathematical results. Only propext,
Quot.sound and Classical.choice occur. The PresentationExamples module passed
leanchecker replay through the same Lean kernel, not an independent implementation.
83 .olean and 83 .ilean files are retained.

New tests: 42 concrete examples, 9 universal applications, five deliberately
invalid controls and one positive control. 56 immediate-predecessor examples were
freshly replayed. Other historical finite suites are retained, not relabeled fresh.

The exact-integer audit passed 30,665 assertions across 168 generic executions
and 49 actual-mask cases. It compares exhaustive small orbit spans and cyclic states,
all declared annihilator regimes, intrinsic multiplicities, arbitrary coordinate changes,
all 809 actual profile-column operations, 448 cyclic-generator digit operations,
477 arbitrary-state digit operations, and 1,568 coefficient values each against the
direct Mahler recurrence and predecessor support machine. Precise counters and
ranges are in COMPUTATION_CONTRACT.md and the audit JSON.

## Scope and failures
See DEVELOPMENT_FAILURES.md for prototype type/normalization repairs and the added
p>0 hypothesis needed by natural-representative expansions. No inherited theorem
was weakened. A failed early matrix negative control produced a decidability error
and was not accepted as a control; the final explicit contradiction passed.

The presentation remains noncomputable Lean mathematics. The runnable Python Smith
reference verifies its proposal certificates, but is not proved as a Lean executable
refinement or claimed equal to Lean's chosen coordinates. No new runtime, memory,
bit-complexity or minimal-generator-count theorem is asserted. No novelty claim.

Pins: Lean4.34.0-rc2, commit6a10ac8c22beadecabdbb0919c2b50214762f91d; mathlib
 aeb72f1e9981b6d35b426b16dca7759be3e7ba06. Dependencies are pinned cached artifacts,
not independently rebuilt. Stable4.34.0 and independent human/kernel review remain
unperformed. The next distinct target is Block33: the unobservable submodule and
reachable-observable quotient, with a precisely stated linear-realization contract.
