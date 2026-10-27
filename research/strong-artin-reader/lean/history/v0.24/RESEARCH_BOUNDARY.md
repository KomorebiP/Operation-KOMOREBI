# Research boundary after v0.24

## Closed as written

1. `ker J* = S` implies `range J = S^perp` over any field.
2. `J u + e=0` is solvable exactly when every element of S annihilates e.
3. Actual selected auxiliary columns satisfy this target identity once their
   joint raw dual kernel is S.
4. v0.23's selected raw evaluations can be extended to the displayed relation
   space. The transpose of the combined relation/evaluation map reaches exactly
   the annihilator of the embedded relation syzygies.
5. A compatible nonlinear system lifts to an exact root inside a nilpotent
   thickening when its compatible target is integrally split, its projected
   Jacobian has the specified stable approximate right inverse, and its Taylor
   remainder gains one power. Compatibility is needed only on the residual fibre.
6. Exact extra equations B(x)F(x) can be eliminated by a pointwise invertible
   triangular transformation. Hensel lifting of F solves the whole graph system.

## False shortcuts excluded by checked counterexamples

Residual Jacobian syzygies need not annihilate nonlinear errors or remainders.
An element of a submodule that is divisible in the ambient module need not be
divisible in that submodule. A residual vector-space splitting does not by itself
supply an integral module retraction.

## What is not automatic

The image theorem over k does not construct an integral compatible target over
O/pi^m. The split-target Hensel theorem does not prove its own splitting or
nonlinear compatibility inputs. The graph theorem does not prove that arbitrary
syzygies are exact redundant equations of graph form.

The v0.23 comparison between cotangent H1 and the arithmetic Selmer obstruction
is still supplied as a Datum. It has not been established for the desired global
Strong Artin deformation problem. No statement here identifies cotangent H1
alone with the full derived obstruction theory in unrestricted settings.

## Next reachable construction

For an actual finite-level presentation, establish either:

A. exact integral relation identities defining a split compatible target, with
   filtration-strict inclusion, or
B. exact polynomial/formal combinations expressing removable equations through
   a retained subsystem, with a proof of equivalence of the presented functors.

For genuinely moving syzygies outside graph form, work on the associated graded
square-zero extension and prove normalized error compatibility there. Freezing
only the residual syzygy coefficients is insufficient.

## Global boundary

Continuous local Galois cohomology and local Tate comparison, Chebotarev
instantiation, actual Taylor-Wiles local variables, the Selmer/cotangent
comparison, determinant-bearing automorphic occurrence, patching, twist
compatibility, ramified local attachment, solvable recursion and unrestricted
Strong Artin remain unproved by this checkpoint.
