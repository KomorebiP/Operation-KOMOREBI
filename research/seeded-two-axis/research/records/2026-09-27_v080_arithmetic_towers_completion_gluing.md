# v0.8.0 route record: arithmetic towers, completion, and lattice gluing

Date: 27 September 2026.
Parent checkpoint: supplied v0.7.0. Source SHA-256:
`b17839ca3a745892f9ac08ef54a9277993eaf7d0dd97941d88c8c37929f64912`.
No Git worktree or executable Mathbox ledger was present. No unrelated user
project files were modified. The supplied archive/source/PDF are preserved.

## Target

Replace identity coarsenings in the integral scalar model by a genuinely
nonidentity arithmetic resolution system. Compute its exchange residuals and
repair kernels, determine what happens under completion, and obtain a concrete
arithmetic reconstruction theorem rather than only a categorical interface.

Success is an explicitly typed tower with written proofs and at least one
nontrivial reconstruction mechanism. A finite test is not a universal proof.
A global lattice is not an automorphic representation.

## Route A: derived coefficient reduction

Use B_n=Z/D^n and C_(m,n)=(-) tensor^L_(B_m) B_n on perfect complexes. Minimal
complexes over each Z/p^m prove conservativity; multiplication by D^n proves
nonfaithfulness. Canonical tensor/base-change has zero cone. Deliberately
weighted cells give explicit coherent noninvertible examples.

A Koszul row reduction over Z/p^n gives all cohomology groups. Octahedral scalar
cone sequences show a nilpotent cone thick-generates the unit. Thus exact
excision of two nonunit scalar directions at a single prime collapses the whole
perfect category. CRT instead gives nonzero selective multi-prime quotients.

Outcome: K42–K46 proved as written, with supplied scalar weights distinguished
from natural arithmetic obstructions.

## Route B: completion as a discriminator

Uniform based towers reconstruct by coefficient inverse limit and the surjective
Mittag-Leffler product model. Finite negative Koszul classes form a pro-zero
system although their abstract groups stay nonzero. The comparison between
complete-then-localize and localize-then-complete has fiber the sum of the
selected p-adic generic fibers. For D=30 and shared-prime pair (6,10), the lost
factor is Q_2. For one prime all finite repairs are zero while Q_p survives after
completion.

Outcome: K47–K49 proved as written. Unconditional commutation of repair and
completion is refuted. Equality holds on a perfect input precisely when its
selected generic fibers vanish. No arbitrary tower strictification is claimed.

## Route C: retain overlaps and reconstruct

CRT proves the exact arithmetic square Z -> Z[1/D] plus product Z_p -> product
Q_p. Derived tensor reconstructs each supplied perfect integral complex and
its residuals. A separate argument constructs a lattice from independent
localized and p-adic lattice data with specified generic identifications:
intersect integrality conditions, bound by D-powers, and reconstruct a finite
CRT subgroup. Compatible operators preserve the intersection.

Outcome: K50–K52 proved as written. K51 is an effective existence/uniqueness
result for lattices, not an automorphy theorem. Matching invariants does not
supply the generic identifications or operator intertwining.

## Dependencies and verification

Proofs are in the two `proofs/*.tex` files and the standalone manuscript.
Primary dependencies and exact statement translations are in
`audit/source_checks.md`. All new proofs received an authoring-session
adversarial self-review. No independent reviewer or Lean compiler was used.
Exact computation populations and all successful commands are in `checks/`
and `audit/release_manifest.json`. Both inherited regression suites were rerun.

## Unresolved continuation

Find an arithmetic functor whose natural exchange comparison with coarsening is
noninvertible, rather than adding scalar weights. Start with a fully specified
invariants or cohomology example and determine whether it stays in perfect
complexes. Preserve any unbounded derived residue rather than silently truncate
it. The eventual global correspondence still requires constructing the actual
generic objects and compatibility isomorphisms; lattice descent alone does not
provide them.
