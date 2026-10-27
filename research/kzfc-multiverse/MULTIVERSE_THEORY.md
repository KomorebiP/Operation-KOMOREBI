# Komorebi Multiverse Residual Formalization v0.11.0

## Scope

This block formalizes the proposed geometry of multiple ZFC worlds without claiming that the
collection of all ZFC models is a set.  The Lean layer uses externally indexed families of worlds.
A future forcing implementation can instantiate the reachability relation.

## 1. World geometry

A `WorldNetwork` consists of a type of worlds and a reflexive/transitive relation `reach`.
When `reach A B` means that B is an admissible extension of A, a finite family S is jointly
amalgamable exactly when

    exists U, forall W in S, reach W U.

`PairwiseAmalgamable S` asks only for a common upper world separately for each pair.
`HigherObstruction S` means pairwise amalgamability holds while joint amalgamability fails.

The predicate `Simplex S := JointAmalgamable S` is proved downward closed.  This is the
finite amalgamation nerve.  The dual network reverses reachability, so upward amalgamation in
the dual is exactly common-ground compatibility in the original network.

## 2. A kernel-checked higher obstruction

`TriangleWorld` contains six worlds corresponding to the three vertices and three edges of a
triangle, ordered by inclusion of supports.  For the three vertex worlds a,b,c, Lean proves

    PairwiseAmalgamable {a,b,c}
    not JointAmalgamable {a,b,c}.

Thus a boundary can exist without its filling simplex.  This is the first exact higher
amalgamation obstruction in the project.

The example is abstract.  No forcing construction is assumed in Lean.  Externally, Mostowski's
theorem as presented in *Set-Theoretic Blockchains*, Theorem 2.1, says that for a finite set of
indices every downward-closed family of allowed subsets containing the singletons can be realized
by Cohen extensions whose subfamilies are amalgamable exactly for the allowed subsets.  Choosing
all proper subsets of a three-element set realizes precisely the triangle-boundary pattern.

## 3. Transport and residuals

A `TransportSystem` assigns a fiber `Fiber W` to each world and a coherent map along every reach
arrow.  For local values x in A and y in B, compatibility at an apex U is equality after transport:

    map(A -> U)(x) = map(B -> U)(y).

Pair compatibility allows the apex to vary.  A finite `LocalFamily` is jointly compatible when all
its transported values agree at one common upper world.

Lean proves:

* joint data compatibility implies underlying world amalgamability;
* world obstruction blocks joint gluing for every coefficient system;
* joint compatibility implies pairwise compatibility.

With the constant Unit coefficient system on the triangle example, every pair residual vanishes
but the triple still cannot glue.  Hence geometric obstruction survives even with trivial
coefficient data.

## 4. Additive residuals

At a fixed common apex whose fiber is an additive group, define

    r_AB = T_AU(x_A) - T_BU(x_B).

Lean proves

    r_AB = 0 iff the two transported values agree,
    r_BA = -r_AB,
    r_AB + r_BC + r_CA = 0

for a jointly reachable triple.  The last identity is the first Cech-style cocycle law in the
formalization.  No cohomology quotient or derived-category identification is claimed yet.

## 5. Logical residuals

A `WorldSemantics` gives a truth predicate `Holds W phi`.  For a sentence fragment Gamma,
`AgreeOn Gamma A B` says the worlds assign the same truth value to every phi in Gamma.
`ResidualAt Gamma A B phi` records exact disagreement.

Lean proves:

* all residuals vanish iff the worlds agree on the fragment;
* sentence residuals are symmetric;
* fragment agreement is reflexive, symmetric, and transitive;
* the common theory of all worlds is contained in the reach-invariant fragment;
* reachable worlds agree on every reach-invariant sentence.

For an indexed collection of actual models of the explicit ZFC theory from v0.10, Lean proves
that all worlds agree on every ZFC axiom sentence and that the ZFC axiom theory lies in their
common logical core.  Independent sentences are not asserted to agree.

## 6. Residual descent and the nontriviality audit

An `ObstructionTheory` is a graded obstruction predicate satisfying soundness: jointly glued data
cannot be obstructed.  Completeness says every failure of joint gluing is detected at some degree.
Soundness plus completeness gives the exact descent criterion

    JointCompatible x iff every graded obstruction vanishes.

However, Lean also constructs the degenerate `packedFailureTheory`:

    Obstruction(q,x) iff q = 0 and x is not jointly compatible.

This tower is complete for every transport system.  Therefore existence of an arbitrary complete
obstruction tower is vacuous.  A substantive Komorebi axiom must constrain the production of the
tower by locality, naturality, derived limits, sheaf/descent structure, complexity bounds, or some
other independent admissibility condition.

A separate `pairwiseBoundaryTheory` places pairwise-compatible failure at degree one, and the
explicit triangle/Unit example is proved to be detected there.

## 7. ZFC-world interface

A `ZFCWorld` stores a carrier, its membership-language structure, and a proof that it models the
explicit ZFC theory developed in the predecessor branch.  `ZFCWorldNetwork` is an externally
indexed family of such worlds plus an abstract reflexive/transitive reach relation.

This avoids two invalid shortcuts:

1. it does not assert that all ZFC models form a set inside ZFC;
2. it does not identify reachability with forcing until forcing has actually been formalized.

The current Mathlib snapshot used by this project does not expose a ready forcing/geology
formalization from which the generic multiverse relation can simply be imported.

## 8. Candidate next principle

The intended future object is not merely

    exists some complete obstruction tower.

That is already formally shown trivial.  A meaningful candidate is closer to:

    for every admissible world diagram and admissible residual coefficient system,
    the canonical derived obstruction tower is complete for descent.

The words `admissible` and `canonical derived obstruction tower` are deliberately unresolved.
They are the next mathematical content, not placeholders to be silently assumed.

The most concrete next route is to build a finite Cech/cochain layer over the amalgamation nerve,
prove d^2 = 0, and then investigate whether forcing-amalgamation patterns supply nontrivial
cohomology or only combinatorial missing-face data.
