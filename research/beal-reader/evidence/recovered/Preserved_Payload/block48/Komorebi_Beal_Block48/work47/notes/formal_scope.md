# Block 47 formal scope

Status: **21 theorems, 24 declarations, four production modules checked** with
Lean 4.34.0-rc2 and Mathlib revision
`aeb72f1e9981b6d35b426b16dca7759be3e7ba06`.

The formalization contains an interface for a future arithmetic exclusion
certificate and exact polynomial identities for the actual sextic modulo seven.
It does not assert that the arithmetic exclusion certificate has been obtained.

## What is proved

For a lane `l`, candidate `c`, test set `Q`, and compatibility relation `R`,

\[
S_Q(l)=\{c:\forall q\in Q,\ R(l,c,q)\}.
\]

The following facts are checked by the Lean kernel:

1. Adding tests can only shrink the survivor set.
2. Tests combine by intersection, with the same candidate retained throughout.
3. A sound refinement of compatibility maps survivors into the coarser survivor set.
4. Exhaustive lane coverage, attachment of a globally fixed candidate, sound
   local tests, and empty survivor sets together imply nonexistence of solutions.
5. Finite, explicit rejection witnesses for each candidate imply empty survivor sets.
6. Refining lane coverage remains exhaustive when every covered solution has a
   proved lift to a fine lane.
7. A single candidate passing all tests prevents emptiness.
8. Each of two Boolean tests can pass with a separately chosen candidate.
9. No single candidate passes both of those tests.
10. Their correctly correlated survivor intersection is empty.
11. Both coordinate projections of the Boolean diagonal are full.
12. Membership in both projections does not imply membership in the diagonal.

The last five statements are exact toy counterexamples. They establish that
discarding correlations can strictly weaken a test. They do not establish that
the published Beal computations discarded those correlations, or that restoring
them will eliminate any actual modular form.

## Actual sextic identities modulo seven

Nine further theorems concern

\[
f=X^6+10bX^3+12aX+5b^2\in\mathbf F_7[X].
\]

For every pair `a b : ZMod 7`, Lean proves a full expansion of `f^3`, the
coefficient identities

\[
[X^6]f^3=0,\quad [X^5]f^3=a^2b,\quad
[X^{13}]f^3=a,\quad [X^{12}]f^3=0,
\]

the determinant expression built from these four coefficients, and the three
matrix identities

\[
M=\begin{pmatrix}0&a^2b\\a&0\end{pmatrix},\qquad
\det M=-a^3b,\qquad M^2=a^3bI_2.
\]

Here `M` is defined by those four polynomial coefficients. Its identification
with a geometric Cartier operator is an external written argument, not a Lean
theorem in this package. The coefficient identities are universal over `ZMod 7`
and do not assume the Beal equation or smoothness.

## Arithmetic obligations still required

An application must supply the complete candidate type and prove all hypotheses
of `exclusion_from_empty_survivors`. In particular it must establish arithmetic
lane coverage, modular attachment, soundness of each test, and emptiness of every
survivor set. For modular elimination a candidate label should include all fixed
choices required by the congruence, such as the form, prime above seven, and
embedding or twist. The generic theorem does not manufacture these objects.

No geometric Cartier criterion, conductor, level-lowering, hypergeometric trace,
ramification, class field, or Beal nonexistence theorem has been formalized here.
No external arithmetic theorem has been added as a Lean axiom.

## Verification

`verification/formal/verify_block47.py` compiles the four production modules with
`-DwarningAsError=true`, separately rejects any printed warning, concatenates the
new declaration bodies into `Beal47Replay.lean`, and replays that module with
`leanchecker`. It then prints and checks the axioms of all 21 theorems, scans
production source for placeholders and custom axioms, and runs three negative
controls. The only reported axioms are `propext`, `Classical.choice`, and
`Quot.sound`. The cached pinned Mathlib imports are trusted in the normal Lean
workflow; the full Mathlib source is not independently replayed here.

All negative controls fail for their intended reasons: an invalid swapped-label
witness is rejected by `rfl`, a false claim that the fifth coefficient vanishes
at `a=b=1` is rejected by kernel-backed `decide`, and a `sorry` proof is rejected.
These expected failures are recorded as successful negative controls, not
mathematical results.

An initial successful compilation emitted a deprecated-import warning despite
the warning-as-error flag. The import was replaced by its current bounded-lattice
module and the driver was strengthened to reject printed warnings explicitly.
The final production compilation logs are clean.

Initial coefficient-proof attempts also failed: polynomial definitions needed
`noncomputable`, unrestricted simplification looped between constant-polynomial
identities, and direct coefficient normalization left symbolic terms. The repair
was an explicit polynomial expansion followed by controlled coefficient
extraction and kernel-checked numeral equalities in `ZMod 7`. Development logs
are retained as `verification/formal/logs/development_cartier_*.log`. No failed
proof bodies remain in production source.

To replay, using the existing retained runtime:

```sh
python3 verification/formal/verify_block47.py --runtime /absolute/path/to/Komorebi_Portable_Lean_4.34.0-rc2
```

Run that command from the Block 47 directory. The driver resolves its inputs
relative to its own location.
