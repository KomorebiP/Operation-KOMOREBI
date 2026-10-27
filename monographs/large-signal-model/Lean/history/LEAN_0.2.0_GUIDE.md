# Lean 0.2.0 — complete packet trees and minimal predictive completion

**Komorebi Large Signal Model · Foundations 1.0.0 · Komorebi P.**

## The second proof block

This block closes the two finite arguments identified in Lean 0.1.0: P3's complete-tree reconstruction and orthogonal energy identity, and P8's finite-dimensional minimal predictive completion. The frozen manuscript and production PR-LASM 2.3.0 are unchanged. All ten inherited proof files are preserved byte for byte and recompiled with the new files.

The cumulative mapping covers **P1, P2, P3, P4, P5, P6, P7, P8, P10 and P22**. No proposition is now marked partial. **77 of the 87 manuscript propositions remain unformalized.** These counts describe the correspondence ledger, not difficulty-weighted progress.

There are 135 explicitly named theorems, of which 34 are in the two example modules and 101 are foundation or supporting results. The new block contributes 64 of those theorems, including 20 example/supporting example results. There are 190 explicitly named declarations including definitions, structures, one inductive type and a named instance. Automatically generated constructors and recursors are not separately inflated into this count. Module replay checks their actual environment as well.

## 1. Completeness is a property of paths, not an assumed sum

The inductive `PacketTree` has a terminal leaf and a branch with a finite nonempty child family. Each child can have its own shape and depth. `Node` gives structural addresses and `Leaf` indexes the full root-to-leaf paths. Different nodes remain distinct even when their labels or projectors agree.

A selection is any Boolean-valued function on nodes. The definition

```lean
IsCompleteCut t s := ∀ p : Leaf t, pathCount t s p = 1
```

says exactly that each full path meets one selected node. It does not mention reconstruction, sums or energy. It allows a root-only cut, all leaves, or a mixture of internal nodes and leaves at different depths.

`completeCut_branch` derives the recursive alternative: either the root is selected and every descendant is unselected, or the root is unselected and each child has a complete cut. The proof uses `firstLeaf` to ensure that a missing or extra selection cannot hide in a descendant with no path. No nullary internal branch is admitted; a node without children is represented by `leaf`.

For any additive labels with local parent-equals-child-sum conservation, the theorem

```lean
PacketTree.complete_cut_sum
```

proves that the ordinary finite sum over selected nodes equals the root label. The finite-sum statement is bridged explicitly from the structural recursive sum. There is no assumption that a supplied antichain already sums to the identity.

## 2. P3 operator, signal and energy identities

Let `P` label the tree nodes by actual linear endomorphisms. `Conservative t P` states the local child sums. With the root equal to the identity, the checked statements are

\[
\sum_{v\text{ selected}}P_v=I,
\qquad
\sum_{v\text{ selected}}P_vx=x.
\]

These are `complete_cut_operator` and `complete_cut_reconstruction`.

For the energy result, `SiblingOrthogonal` imposes orthogonality only between different child ranges at each internal node. It does not assume that the final mixed-depth selection is orthogonal or that its squared norms add up correctly. `orthogonal_sum_energy` proves the finite Pythagorean identity by expanding the inner product. `conservative_energy` then shows that the scalar labels `‖P_v x‖^2` obey local conservation, and the same complete-cut theorem gives

\[
\sum_{v\text{ selected}}\|P_vx\|^2=\|x\|^2.
\]

The formal theorem works for real or complex inner-product spaces. The bridge `range_orthogonal_of_projector_products` derives the required range orthogonality from a self-adjoint projector and zero product with its sibling. Thus the manuscript's local orthogonal-projector assumptions provide the formal hypotheses. The conservation theorems are stronger in allowing arbitrary additive labels, but no projector claim is silently inferred for arbitrary labels.

This does not formalize best-basis cost optimization, thresholded deletion or probabilistic interpretation of signed packets. P3 concerns complete finite decomposition.

## 3. P8 constructs and terminates the refinement sequence

For operators `L_i` on a vector space and an initial subspace `W0`, the definitions are actual subspace operations:

\[
W_{n+1}=W_n+\sum_i L_i(W_n).
\]

In the row-observable application, `L_i` is the dual pullback of the original signal operator. Thus this is exactly the manuscript iteration that adds every row composed with a declared signal transition.

`invariantSequence_dimension_growth` proves that every strict enlargement increases the dimension by at least one. `invariantSequence_exists_stable` proves

\[
\exists n\leq\dim V-\dim W_0,\qquad W_{n+1}=W_n.
\]

Equality is also proved to persist: `invariantSequence_stays` fixes every later iterate. `invariantCompletion` is defined at the explicit dimension-deficit index, not by assuming the existence of a completed invariant state. Its fixed-point and invariance theorems follow from the stopping argument.

Finally, `invariantCompletion_isLeast` proves that the completed subspace is the least common invariant extension of `W0`. Any invariant subspace containing the original observables contains every iterate and hence the completion. This is a minimality theorem, not just an assertion that some larger closed state exists.

The algebraic sequence permits an arbitrary action-index type; the finite-dimensional proof even works for an infinite declared family. This generality is mathematical, not an efficient algorithm for enumerating infinitely many operations. The empty action family is checked to give `W0` unchanged.

## 4. An invariant row space becomes an actual predictive state

For a row space `W`, `observableState W` evaluates all its linear observables on the input signal. Its codomain is the dual of `W`. The restricted row pullback produces a dual transition, and Lean checks its composition with the observation map exactly.

In finite dimension, `observableState_surjective` proves that the algebraic state space is the actual image of the full signal vector space, rather than an arbitrary padded coordinate space. This is an algebraic realizability statement. It does not mean that an initially limited measuring device can obtain each newly required observable. A physically admissible subset or partial-observation protocol requires a separate restriction and accessibility argument.

For any finite basis of the completed row space, the development constructs the maps called `R`, `H` and `B_i` in P8:

\[
C_0=HR,
\qquad
RL_i=B_iR.
\]

`basisObservation_independent` proves full row independence. `basisReadout_correct` recovers every initial row for every signal. `basisTransition_correct` establishes exact action dynamics. The capstone is

```lean
predictiveCompletion_coordinate_realization
```

which chooses a finite basis and returns all these maps together with their properties. `predictiveCompletion_le_competing_summary` separately proves that any linear summary with an exact readout and closed transitions must contain the completed row space. The comparison applies to real competing linear maps, not merely to a predicate named “minimal.”

The basis and subspace constructions are marked noncomputable where appropriate. This is a proof of the finite mathematical construction, not an implemented Gaussian-elimination routine or a noisy operator learner. No global predictive-rank inference from finite samples is established here. The single-operator Cayley–Hamilton discussion surrounding P8 is not counted as an additional checked theorem in this block.

## 5. A completion that genuinely omits an irrelevant coordinate

The exact rational example uses

\[
L(x,y,z)=\left(\frac{x}{2}+y,\frac{x}{4}+\frac{y}{3},\frac56z\right)
\]

and initially retains only `x`. The original first coordinate does not close: signals `(0,0,0)` and `(0,1,0)` have the same first coordinate but different next first coordinates. `first_coordinate_not_closed` proves that even an arbitrary scalar function cannot repair this without additional state.

Pulling back the first row gives `x/2+y`, so subtracting half the original row supplies the second row. Lean proves that the actual abstract completion equals precisely the row space that annihilates `(0,0,1)`:

```lean
completion_is_exactly_two_coordinate_rows
```

The third-coordinate row is not in the completion, and the completion is a proper subspace of the full dual. Thus the example does not achieve closure by automatically storing the whole signal. It retains the first two dynamically relevant coordinates and omits the independent third coordinate.

The familiar coordinates `(x,y)` have reduced transition

\[
\begin{pmatrix}1/2&1\\1/4&1/3\end{pmatrix},
\]

with the first coordinate as readout. This matrix is the mathematical interpretation of the checked row-space and transition identities; the release does not claim its noncomputable basis choice prints this particular basis.

## 6. Boundary checks

The tree example selects one internal child and both leaves of the other child. It is a complete mixed-depth cut with three selected nodes. A conservative integer labeling reconstructs its root exactly. Separate checked negations show that overlapping parent/descendant selection and deletion of a branch are not complete cuts.

The energy counterexample uses two equal half-components. Their sum reconstructs one, but their squared norms sum to one half. Conservation cannot substitute for orthogonality.

Five new deliberately invalid Lean files fail under the strict compiler: uncovered paths, overcounted paths, energy conservation without orthogonality, a premature first-coordinate predictor and an invented third-coordinate value. They remain outside the imported proof library, alongside the six inherited controls.

## 7. Verification and trust boundary

Read `AUDIT.md` and the actual report in `verification/release_run/report.json`. The separate fresh-extraction report belongs to the delivered ZIP, not to an assumed persistent environment.

The verifier removes project compiled objects, checks the compiler and dependency revisions, compiles all modules with one worker and warnings as errors, inventories the axioms of every explicitly named declaration, and invokes the pinned upstream kernel replay function once per proof module. The imported Mathlib cache is reused; upstream dependencies are not rebuilt or exhaustively replayed. The extra replay uses Lean itself, not a second proof assistant.

The permitted axiom dependencies are `propext`, `Classical.choice` and `Quot.sound`. Classical basis or representative choice is not hidden. No custom mathematical axiom, admitted proof, unsafe proof definition or native-decision shortcut is introduced in the active proof sources. The finite theorem count is not a novelty count or a completed-program claim.

## Next formal sector

P12's Bayesian coarsening criterion and exact defect are the next prerequisite for P9's finite joint transition-and-likelihood refinement. The nontrivial-partition condition and the one-block exception must remain explicit. Their expected conclusions must not be installed as assumptions of a nominal closure construction.
