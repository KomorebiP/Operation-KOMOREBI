# Beal formal evidence

**Final check report, 8 October 2026, America/Chicago.** The original Block 47
and Block 48 sources passed a fresh check under their exact compiler and library
pins. A new eleven-statement module passed strict source elaboration and axiom
inspection for the ordinary cochain and affine linear algebra used in the reader.

## Result and distinct scopes

| Development | Exact pin used in the successful current run | Public statements checked | Fresh result |
|---|---|---:|---|
| Block 47 | Lean 4.34.0-rc2, mathlib `aeb72f1e9981b6d35b426b16dca7759be3e7ba06` | 21 | Unchanged verifier passed strict compilation, all axiom reports, project-only kernel replay and three expected rejected negative controls |
| Block 48 | The same Lean and mathlib pins | 8 | Unchanged source passed direct warning-as-error elaboration and all eight axiom reports |
| Reader affine module | Lean 4.19.0, mathlib `c44e0c8ee63ca166450922a373c7409c5d26b00b` | 11 | Final minimal-import source passed warning-as-error elaboration and all eleven axiom reports |

These are forty named public statements in three scopes. The counts exclude the
Block 48 private helper and the intentionally invalid negative controls. They
are not forty proofs of the Beal conjecture or forty arithmetic realizations.
No successful current axiom report contains `sorryAx` or a custom axiom. The
dependencies are subsets of Lean's standard `propext`, `Classical.choice` and
`Quot.sound`.

## Historical source authentication and replay

All four Block 47 source hashes match the archived verification report. The
Block 48 source hash matches its archived result. The recovered files and the
historical compiler logs are preserved unchanged. Source authentication is
recorded in `formal/HISTORICAL_INPUT_AUTHENTICATION.json`.

The historical Block 47 compiler is Lean 4.34.0-rc2 at commit
`6a10ac8c22beadecabdbb0919c2b50214762f91d`. Its compiler binary was reused from
the preceding ABC check without modification. The exact historical mathlib
checkout was freshly fetched at
`aeb72f1e9981b6d35b426b16dca7759be3e7ba06`. Its official cache downloader
completed successfully and downloaded 8,849 cache objects. Fresh dependency
checks matched every declared revision in both environments. All checked tracked
package sources were clean. The eighteen dependency records, compiler hashes,
and acquisition records are in `formal/RUNTIME_DEPENDENCY_AUTHENTICATION.json`
and the mathlib acquisition and cache logs.

The original `verify_block47.py` was copied unchanged to a private working
project. All four original sources compiled with warnings treated as errors.
The source scan found no admitted proof, custom axiom, unsafe declaration or
`native_decide`. All twenty-one requested theorem axiom reports appeared and
used only the three standard axioms listed above.

The verifier assembled its original replay module and compiled it. The exact
`leanchecker` then replayed only `Beal47Replay`, as requested. Imported pinned
mathlib objects remain trusted in the ordinary workflow. This is a separate
check of the project module, not a rebuild or independent verification of every
mathlib dependency.

All three deliberate negative controls were rejected for their expected reasons:
an invalid single-candidate choice across two tests, a false off-diagonal
coefficient cancellation, and a placeholder proof under warning-as-error
settings. The placeholder is a negative-control input and is never counted as
a proved theorem.

Block 48's unchanged source separately compiled with one Lean worker and strict
warnings. All eight public axiom reports appeared, with no nonstandard axiom
dependency. The source bytes before and after both successful checks matched
the recovered originals. The final current run is
`formal/historical_exact_run02`.

## What the historical statements establish

Block 47 has seven generic lane-certificate statements, five finite Boolean
correlation statements and nine exact mod-seven polynomial or matrix statements.
The generic exclusion implication explicitly assumes a complete lane cover,
an attachment of a globally fixed candidate and soundness of each selected test.
Compilation proves the implication with those hypotheses. It does not supply
their arithmetic instantiation.

The polynomial module checks the cube of the displayed sextic over `ZMod 7`,
four coefficient positions, their determinant expression, the assembled
two-by-two matrix and its square. The module documentation explicitly leaves
the identification of that coefficient matrix with a geometric Cartier operator
outside the formalization.

Block 48 proves common-root and trace exclusions over any characteristic-seven
field. It also proves the elementary bounded natural-number statement that
`d₀,d₁ ≤ 2` and `(d₀+7*d₁) mod 48 = 8` force both dimensions to equal one.
The curve's Frobenius polynomials, database eigenvalues, modular attachment,
finite-flatness and the determinant-to-inertia dictionary are external arithmetic
inputs. None becomes a checked arithmetic theorem merely because its associated
polynomial calculation compiles.

## New ordinary-cochain and affine statements

The final source is `formal/BealAffineReader.lean`, namespace
`KomorebiBeal.ReaderAffine`. The matching project copy is supplied in
`formal/reader_project`. Its eleven statements are:

| Statement | Quantified domain and exact conclusion |
|---|---|
| `differential_add` | Arbitrary monoid and additive commutative coefficient group. The trivial-action differential is additive in the cochain |
| `differential_sub` | The same domain. The differential of a difference is the difference of differentials |
| `same_primitive_difference_additive` | Two cochains with equal differentials have an additive difference |
| `add_character_preserves_differential` | Adding an additive function preserves a cochain's differential |
| `fixed_primitive_differential` | A monoid character into field units and a supplied twisted cocycle. The explicit fixed primitive has the displayed negative cup differential |
| `fixed_primitive_trace` | The same field-unit setup. The explicit fixed primitive satisfies the displayed toric trace identity |
| `solvability_translation` | A linear map over an arbitrary commutative ring. `Az=t` is solvable if and only if `Az=t−Az₀` is solvable |
| `cokernel_origin_invariance` | The classes of `t` and `t−Az₀` in `W/im A` agree |
| `null_test_necessary` | An explicitly supplied linear map `N` annihilating the image gives `Nt=0` for every solvable target |
| `complete_null_test` | The stronger, explicit hypothesis `ker N=im A` makes `Nt=0` equivalent to target solvability |
| `fiber_is_kernel_translate` | After one solution is supplied, every other solution differs from it by an element of `ker A` |

The differential convention is

\[
 dp(g,h)=p(g)+p(h)-p(gh).
\]

The field-valued formulas use a character into units, so every character value
is nonzero. With a supplied cocycle
`alpha(gh)=alpha(g)+chi(g)*alpha(h)`, they define

\[
 \beta(g)=(\chi(g)^{-1}-1)\lambda,
 \qquad p^{\mathrm{fix}}(g)=\lambda\chi(g)^{-1}\alpha(g).
\]

The compiled conclusions are

\[
 dp^{\mathrm{fix}}(g,h)=-\alpha(g)\chi(g)^{-1}\beta(h),
 \qquad
 (\chi(g)-1)p^{\mathrm{fix}}(g)+\alpha(g)\beta(g)=0.
\]

These are general algebraic identities. The module does not encode continuity,
an actual Galois group, the existence of a restricted primitive, or the uniqueness
argument requiring a separating character value. Those application statements
have their own prose proofs and source dependencies.

In the affine part, no completeness hypothesis is hidden. An arbitrary `N`
with `NA=0` supplies only the necessary test. The equivalence theorem requires
`ker N=im A` explicitly. It does not compute the actual fifteen-by-ten matrix,
prove its rank, construct a full left-null basis or evaluate an arithmetic
target. It does not compute the finite cardinality of an affine fiber. Its
last theorem describes that fiber once a solution has been supplied.

## Reader source editions and current check

The corrected broad-import source is retained as `formal/BealAffine.lean`.
It passed direct strict elaboration during development. Its provenance wrapper
first requested a nonexistent optional Lean 4.19 checker binary, then a separate
bounded attempt hit a one-core import timeout. A four-import edition subsequently
revealed one missing library import.

The final `BealAffineReader.lean` replaces the broad import with the five actual
library imports. All definitions, statements, proof bodies and axiom targets
below those imports are byte-identical to the corrected broad-import source.
`formal/AFFINE_READER_IMPORT_PATCH.json` records that change. No theorem statement
was weakened and no linter was disabled.

The final run, `formal/affine_formal_run04`, checks the exact Lean 4.19 version,
the exact mathlib revision, source hashes, strict elaboration, all eleven axiom
reports and a nested-comment-aware forbidden-token scan. All passed. Compiler,
dependency-manifest, shim and source hashes are recorded in its result. The
official Lean 4.19 distribution here has no extra `leanchecker` executable.
No separate checker replay is claimed for this new module. Its generated proofs
are checked by Lean's normal elaboration kernel.

## Host compatibility and failures

This host denies a process's own numeric `/proc/PID/exe` lookup while permitting
`/proc/self/exe`. The already authenticated, narrowly scoped `LD_PRELOAD` shim
redirects only that own-process executable lookup. Other paths pass unchanged.
Its source is included as `formal/proc_self_compat.c`, and the binary used has
SHA-256
`f9d97611cfbbab4b36bfa7a33d0812a38f7f35384683c5fcab0954f7008bbcc1`.
Compiler and proof bytes were not edited by the compatibility layer.

All unsuccessful development and provenance attempts remain in the package.
`formal/DEVELOPMENT_FAILURES.md` distinguishes the older-library import mismatch,
the quotient-lemma API correction, the absent optional checker, the private
runtime layout correction, the bounded import timeout and the missing narrow
import. Failed records are not included in the passed counts. Original historical
thread and cache failures are preserved separately as predecessor history.

## Provenance and remaining mathematical boundary

The current two successful runs and five unsuccessful provenance runs each have
a version 2 computation-audit manifest. All seven passed manifest validation with
the project root, including actual input and output hash checks. An unsuccessful
run can be a valid provenance record. Validation does not change its failure
status or turn the record into a proof.

Commands, raw logs, input snapshots where relevant and exact result files are
included. Compiler binaries, private workspaces and large dependency caches are
external dependencies. Reproduction instructions and small Lake projects are in
`formal/REPRODUCE.md`, `formal/historical_project` and `formal/reader_project`.

The formal evidence verifies the stated logical, polynomial, cochain and affine
algebra. Finite-S Poitou–Tate duality, the arithmetic ordinary localization map,
the actual bare primitive and its labelled evaluations, the seven or eight
arithmetic affine obstruction coordinates, higher lifting and the connection to
integer Beal solutions remain separate mathematical obligations. No successful
compiler output supplies the missing arithmetic target.
