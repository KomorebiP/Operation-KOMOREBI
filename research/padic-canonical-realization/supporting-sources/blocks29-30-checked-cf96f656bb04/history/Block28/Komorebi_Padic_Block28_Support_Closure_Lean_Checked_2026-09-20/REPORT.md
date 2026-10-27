# Block 28 — Least invariant coefficient supports

## Outcome

The support-aware coordinate target is closed under the stated coordinate-box
contract. Four new modules add 61 theorem declarations. The 739 inherited theorem
statements and their mathematical source modules remain unchanged. The project has
800 theorem declarations in 68 production modules.

## Exact support of fully summed transition columns

Let I be the finite collection of individual coefficient positions inside the
already certified Block27 degree profile. For each legal digit d, T_d is the
complete profiled linear transition, including all routed branch additions. Let
v0 be the actual initial coordinate vector and e_i its coordinate unit vectors.
Define

    seed = {i | v0(i) != 0},
    i -> j iff there exists d with (T_d e_i)(j) != 0.

The source-column convention is explicit. The entry is tested only after every
branch contribution to it has been added in the coefficient ring. Intra-column
cancellation is therefore included; the union of raw branch supports is not used.

For sets of positions define

    Phi(S) = S union seed union {j | exists i in S, i -> j}.

Lean proves monotonicity and inflationarity. Starting at the empty set, each
nonstationary step increases cardinality. Since I is finite, after N=card(I)
rounds the result is fixed. The result S* is contained in every seed-containing
column-closed set. Empty position types and empty initial supports are allowed.
The generic mathematical theorem does not need a finite alphabet; the actual
mask instance uses the finite alphabet Fin p.

Most importantly, column closure is proved equivalent to invariance of the ENTIRE
coordinate-supported module:

    seed subset S and all outgoing columns from S land in S
      iff v0 vanishes off S, and
          every vector vanishing off S stays so under every T_d.

The proof reconstructs an arbitrary vector as sum_i x_i e_i. It uses only a
commutative coefficient ring, without a field or no-zero-divisors assumption.
The result is the least invariant coordinate box containing v0. It is not the
support of the particular reachable orbit, nor a minimum-dimensional invariant
submodule under arbitrary linear relations.

## Restricted coordinates and exact simulation

The restricted state is a function from {i : I | i in S*} to R. Zero-extension
into I is injective. Initial states, one-step transitions, and complete ordered
words commute exactly with that extension. For retained j the transition also has
the exact sparse-entry formula

    (T'_d x)(j) = sum_{i in S*} x_i (T_d e_i)(j).

The formal definition is restriction of the existing full transition after
zero-extension; the retained-entry formula is proved equal to it. No runtime or
memory saving is inferred merely from the smaller state type. Polynomial and
support constructions remain noncomputable where inherited interfaces require it.

The mask construction uses the sigma type

    (row : Fin L') x Fin(w_row)

for I, where w is Block27's least degree profile. A row of capacity zero contributes
no coefficient positions, not a spurious constant coefficient. The adapter proves
linearity of the inherited profile transition and applies the generic support
theory to that exact map, rather than a separately hypothesized matrix model.

## Canonical coefficient theorem

For prime p, r>0, integer masks A,B, p not dividing B(0), and equal mask constants
in ZMod(p^r), the inherited canonical series F is constructed and normalized:

    F(0)=1, B(z) F(z)=A(z) F(z^p).

The new support machine outputs coeff(n,F) for every natural n. All in-range digit
words are covered, least-significant first, including the empty word. The new
machine's initial state, transition and output do not take coefficients of F as
an oracle. Its outputs agree with Block27 and are compatible under positive
prime-power precision reductions. Supports at different precisions are not
identified as the same coordinate set.

SupportCanonicalMaskCertificate retains the full Block27 certificate and adds
support closure, leastness, canonical output and exact ambient cardinality.

## Cardinality and examples

If S* has s positions then the ambient state count is exactly

    p^(r*s) <= p^(r * sum_i w_i).

Whenever any profile position is omitted, the slot count is strictly smaller.
This is an ambient coordinate count, not reachable-state or minimal-automaton size.

The exact Python audit gives the following examples, all with A=1:

| p | r | B | Block26 slots | Block27 slots | Block28 slots |
|--:|--:|---|--:|--:|--:|
| 2 | 4 | 1+4z | 12 | 6 | 5 |
| 2 | 8 | 1-z | 192 | 79 | 54 |
| 2 | 8 | 1+16z | 12 | 6 | 6 |
| 3 | 6 | 1+81z | 8 | 4 | 4 |

For p=2,r=4,B=1+4z the omitted position is the constant coefficient in denominator
layer 3. Thus a whole row need not disappear for this refinement to help.
Twenty-four of the 124 audited mask-case executions have a strict support decrease.
The table is finite exact Python evidence, not separate kernel reduction of each
noncomputable full mask construction. The universal mask theorem is Lean-checked.

## Restriction witnesses

Over ZMod5, let v0=(1,1,0), T(e0)=e2, T(e1)=-e2, T(e2)=0. The least invariant
coordinate set is all three positions, but T(v0)=0 and coordinate 2 never appears
in the initial orbit. The statements least=univ and zero orbit coordinate for
every word are production theorems.

Over ZMod4, let v0=(2,0), T(e0)=2e1, T(e1)=0. Again closure includes both
positions, while T(v0)=0. A nonzero matrix entry can annihilate a nonzero initial
coefficient. The formal theorem handles this correctly because coordinate
invariance concerns arbitrary retained coefficients, not just that initial value.

These witnesses rule out a stronger orbit-support interpretation. They do not
refute the invariant-coordinate theorem. Coordinate-ideal products or correlated
invariant submodules are possible later refinements, not results claimed here.

## Fresh verification

A baseline root build completed first with inherited mathematical sources checked
byte-identical. The final build then deleted only project .lake/build, retained
the pinned dependency cache, and rebuilt all 68 modules under warning-as-error:
2280 Lake jobs completed. Every final recorded command retained identical before
and after execution-input hashes.

All 800 theorem axiom closures were inspected. Fifteen are axiom-free; the only
observed axioms are propext, Quot.sound and Classical.choice. The final witness
module also passed leanchecker replay using Lean's own kernel, not a second
implementation. There are 68 .olean and 68 .ilean project artifacts.

Fresh tests: 28 new concrete examples, four universal applications, 27 immediate
predecessor examples, four invalid controls correctly rejected, and one positive
control passed. Each negative control produced the intended explicit contradiction
or placeholder diagnostic, not merely an arbitrary nonzero process exit.

The exact-integer audit passed 20,625 assertions. It covers 216 generic systems,
124 mask-case executions, 2,805 matrix-column comparisons against the independently
routed polynomial operation, 409 arbitrary supported-state transition comparisons,
and 4,960 coefficient comparisons each against the direct recurrence, Block27,
and the original sufficient machine. All closed coordinate sets were enumerated
in the declared small cases. Finite comparisons are not the universal proof.
Historical large finite suites are preserved, not relabeled as fresh runs.

## Provenance and remaining limits

Lean4.34.0-rc2 commit 6a10ac8c22beadecabdbb0919c2b50214762f91d, mathlib
 aeb72f1e9981b6d35b426b16dca7759be3e7ba06. Runtime archive assembly matched its
retained SHA-256 and extraction succeeded. Git revisions of attached dependency
caches were checked. The caches were not rebuilt independently from source.

The manifest uses the inherited project-local schema1 validator; that checker
and additional before/after hash replay ran successfully. This is not a claim of
running the installed plugin's full schema2 validator.

The stable Lean4.34.0 compatibility lane and independent human/kernel review remain
unperformed. No novelty, optimality beyond coordinate boxes, time, bit-complexity,
memory, analytic convergence, or executable Python-to-Lean refinement is claimed.
See DEVELOPMENT_FAILURES.md and results/dev_* for unsuccessful proof drafts.
