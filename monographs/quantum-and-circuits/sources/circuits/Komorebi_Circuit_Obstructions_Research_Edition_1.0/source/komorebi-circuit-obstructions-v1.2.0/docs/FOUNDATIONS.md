# Foundations: restored computation and complete discrepancies

This document supplies the dependencies needed to read the maintained manuscript without opening a chain of predecessors. The exact cut-comparison statement in F2 (C01) has a Lean formalization in version 1.1.0. The other foundation statements remain written/self-reviewed unless explicitly listed in the Block 01 declaration map. Versioned external sources are listed in `REFERENCES.md`.

## Conventions

All functions are Boolean. A truth table on n inputs is an integer whose bit x is f(x), with coordinate i represented by bit i of the assignment x. The constant-one table has 2^n one bits. Degree means multilinear algebraic degree over F2; the zero polynomial has degree -1 in Python helpers and the stored profile table uses the documented zero sentinel 0.

NOT changes one target bit, CNOT adds one control bit to a distinct target, and Toffoli adds the product of two distinct controls to a third distinct wire. Every gate is its own inverse. A restored oracle is a permutation satisfying

\[
(x,0^a,y)\mapsto(x,0^a,y+f(x))
\]

for every x and both y. The all-zero workspace condition applies only to the boundary states. Arbitrary intermediate departures and output feedback are permitted.

## F1. Circuit and restored-oracle comparison

Let C(f) be the minimum number of fan-in-two AND/OR/NOT gates, allowing wires to fan out. Let L(f) be the minimum total NOT/CNOT/Toffoli length of a restored implementation, with any finite number of zero ancillas. Then

\[
C(f)/5\le L(f)\le 6C(f)+1.
\]

For the upper construction, compute each Boolean gate on a fresh zero wire. AND needs one Toffoli, NOT needs a NOT and a CNOT, and OR uses two CNOTs and one Toffoli. A repeated operand is simplified to a copy; it is not encoded as an illegal repeated-control Toffoli. Copy the result to the target, then reverse the computation. This costs at most 6C(f)+1 gates and restores all work wires.

For the reverse simulation, read each reversible gate as a small Boolean circuit updating one coordinate. XOR can be implemented with four AND/OR/NOT gates; a Toffoli adds one multiplication, for at most five. Substituting zero for initial workspace and reading the final target with y=0 gives a Boolean circuit for f. The comparison is a restatement of standard reversible simulation in the stated accounting, not a novelty claim.

## F2. Exact cut-comparison identity (C01)

Write a restored implementation as C=Q\circ P and set R=Q^{-1}. Suppress the fixed zero ancillas in the notation. Define

\[
A(x)=P(x,0),\quad B(x)=R(x,0),\quad
D(x)=P(x,1)+P(x,0).
\]

Correctness gives R(x,z)=P(x,z+f(x)) on the boundary inputs. Therefore, when f(x)=0, A(x)=B(x); when f(x)=1, B(x)=P(x,1). In both cases

\[
A(x)+B(x)=f(x)D(x).
\]

The vector D(x) is nonzero because P is a permutation and the two initial target values are distinct. Consequently H_i=A_i+B_i obey

\[
H_i\le f,\qquad \bigvee_i H_i=f.
\]

No inversion of a chosen coordinate is required. The comparison detects the output even when the output direction is spread through workspace.

## F3. Multiplicative degree bound

**Block 02 formal status.** The maintained NCT specialization is now checked by `workspaceDegree_run` and `canonical_run_coordinate_degree`. Its proof controls products of r current registers by t+r rather than unfolding a DAG into a formula. A separate arbitrary XOR-AND syntax compiler is not part of this formalization.


An XOR–AND computation with t AND gates has output degree at most t+1, with constants and arbitrary sharing. Introduce one formal Boolean variable for each AND output. Its defining expression is a product of two affine forms in input and earlier gate variables. Starting from an affine output expression, substitute gate variables in reverse topological order. In a multilinear monomial, replacing one formal variable by a quadratic increases degree by at most one. Multilinear reduction never increases degree. After t substitutions the degree is at most t+1. This is the familiar degree-minus-one bound; see S1.

A Toffoli contributes one such multiplication. NOT and CNOT contribute only affine operations. The same statement holds when a suffix is run backwards, because every gate is self-inverse.

## F4. Complete safe-packet degree (C02)

**Block 02 formal status.** `restored_degree_and_cover_bound` proves the numerical lower-bound component, including an actual zero-Toffoli affine-output construction. The evaluation-span dual that accompanies C02 remains unformalized.


Let I_f be the ideal of Boolean functions vanishing on every negative input. For f(v)=1 define

\[
\beta_v(f)=\min\{\deg h:h\in I_f,\ h(v)=1\},\quad
\beta(f)=\max_{v:f(v)=1}\beta_v(f).
\]

Set beta(0)=0. At a cut balanced by Toffoli count T, F2 supplies a complete safe cover and F3 gives every H_i degree at most ceil(T/2)+1. Therefore beta(f) is at most that quantity and T>=2beta(f)-3. Appending an affine function of restored inputs to the target costs no Toffolis. With

\[
\beta^*(f)=\max_{\ell\text{ affine}}\beta(f+\ell)
\]

we obtain

\[
T\ge\max\{0,\deg f-1,2\beta^*(f)-3\}.
\]

The manuscript supplies exact finite dual certificates, explicit calibration families, and the fact beta*(f)<=n. The latter prevents this parameter alone from furnishing a superpolynomial bound.

## F5. What a cut decomposition does not prove

The existence of a complete safe cover is necessary for restored computation. Semantic packet count, isolated degrees, expanded monomial counts, and dimensions of an ambient algebra do not on their own bound the shared total cost of constructing that cover. No reverse implication from those quantities to unrestricted circuit hardness is assumed in this release.
