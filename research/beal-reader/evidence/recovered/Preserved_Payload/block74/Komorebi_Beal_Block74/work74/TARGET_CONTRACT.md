# Block 74 target contract

Sole execution predecessor: Block73 v7.3.0, SHA256
8dd6961f1c9e43d57c6486f811e5af7b8923ca5b9b80eaef3b0f5390ae9fff7c.
Its default verifier was rerun cleanly in this interaction and returned
PASS_DECLARED_CHECKS in 29.342 seconds. This was NOT the entire historical chain.
The original ZIP is retained unchanged. Eight immediate source leaves are pinned.

## Actual goal and attained result

Continue the actual nontriangular deformation rather than replace it by a global
upper Kummer lift. This block constructs a valuation-selecting local Galois element
and proves an exact polarized rank-two trace formula. At depth one three correctly
labelled traces modulo343 determine the fixed-seven valuation defect once the
normalized nonzero opposite value is known. An all-depth version detects
n+1+v7(v7(C)). No actual joint-word traces have been numerically determined for the
eight residual patterns, so none is eliminated.

## Domains and explicit inherited inputs

K=Q(sqrt5), F=K_(7), phi=(1+sqrt5)/2. O=Z_7[w]/(w^2-5), k=F49.
The base-field and coefficient-field quadratic generators remain distinct.
The actual natural representation rho:G_K->GL2(O) has determinant chi,
lower-left entry in7^n O, residual [[chi,alpha],[0,1]], and nonzero endpoint
class beta(g)=bar(rho21(g)/7^n)/bar chi(g). The normalized natural class is
alpha=vw[phi]+r[3]+[sqrt5], v,r inF7*, with the inherited all-depth normalization.

At F retain the ACTUAL split toric Tate sequence with characters chi and1,
the integral coefficient action on its two graded lattices, and the marked period
valuation matrix exactly7c I, c=v7(C)>=1. The residual local comparison fixes the
upper graded factor modulo7 as kappa=v/(2epsilon), epsilon=+/-1. These are
inherited geometric inputs, not consequences of the finite matrix checks here.
The local unit basis phi,3 is independently rechecked modulo49 and its all-level
basis property is proved using the7-adic logarithm.

No global triangularity modulo49 is assumed at n=1. No full inertia equality,
complete trace-function equality, bounded conductor, or ordinary beta descent is
needed for the new single-representation identity.

## Routes actually pursued

A. Global adjoint-obstruction route: the p,q system remains unsolved. A brief
Massey-product literature probe supplies no applicable vanishing/exclusion claim
for the required twisted, locally constrained F49 problem. No such shortcut is used.
B. Polarized trace route: achieved a precise identity and a valuation-selecting
Galois probe; this replaces the complete-data fibre comparison by three labelled
rank-two traces at one extra digit in the depth-one case.
C. Direct numerical elimination: not attained. The current data do not identify
the three joint trace labels, their integral traces, or a contradictory global
value. Positive matrix families exist for all declared local values. All eight
patterns and the old local Frey controls are preserved.

Finite evidence uses two independently written arithmetic programs, not a Lean
certificate or an independent mathematical reviewer. No new point counts.
