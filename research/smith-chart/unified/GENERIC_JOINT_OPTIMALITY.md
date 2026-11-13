# Generic minimum total size of the open synthesis families

Author: Komorebi P.

Written theorem with project self-review. This is the standard parameter-
dimension obstruction applied to the existing open F_n families. No novelty
claim, no assertion about every rational example, and no unrestricted resistor
minimum claim.

Use real coefficient coordinates (P0,...,Pn,Q0,...,Q_(n-1)), with Qn=1 and
coprime numerator and denominator, each of degree n. This is an open subset
of R^(2n+1). For every n>=3, the positive interior of the existing F_n chart
is an open subset of these coordinates. The forward endcap operation has the
displayed unique smooth inverse wherever its strict chart inequalities hold;
the base coefficient box has a nonempty seven-dimensional interior.

For Lebesgue almost every member of this open family, every ordinary finite
positive transformer-free uncoupled realization has at least $2n+1$ total physical
branches. The retained construction uses n reactives and n+1 resistors and
therefore attains this generic total minimum, as well as the pointwise reactive
minimum n. Among realizations using the minimum n reactives, the generic
resistor minimum is n+1. A realization with more storage may trade reactives
against resistors; that separate unrestricted resistor minimum is not proved.

Proof. Fix a graph with m<=2n branches. Remove detached components and loops;
a connected graph has at most m+1 vertices, so there are finitely many labeled
port-fixed graph/type possibilities for each m. Positive physical values
parametrize an open subset of R^m. At2n+1 fixed distinct positive Laplace
arguments, its reflection or impedance values are smooth rational functions
of those m values (finite connected positive graphs have positive real-axis
admittance). Choose impedance samples for definiteness.

At a coprime degree-n target the linear monic interpolation system for the
2n+1 coefficient coordinates is invertible. For a null variation dP,dQ, with
degree(dP)<=n and degree(dQ)<=n-1, the cross polynomial dP*Q-P*dQ has degree
at most2n. Vanishing at2n+1 distinct points makes it identically zero.
Coprimality then gives (dP,dQ)=(cP,cQ), and the monic-denominator variation
forces c=0. Thus local coefficient recovery from the sample vector is smooth
and rational wherever that interpolation determinant is nonzero.

Compose sample evaluation with this recovery map. For any physical parameter
vector realizing a coprime degree-n target, recovery returns that target's
coefficients, regardless of the graph's larger possible natural degree or
cancellation at other parameter values. On countably many compact charts
(positive parameters bounded above/below, interpolation determinant bounded
away from zero), this is a Lipschitz map from at most m<=2n variables into
R^(2n+1). Its image has measure zero: an epsilon grid in the parameter chart
uses O(epsilon^-m) cubes, and their Lipschitz image can be covered with total
(2n+1)-dimensional volume O(epsilon^(2n+1-m)), tending to zero. The countable
union of these images, and the finite union over graphs, still has measure
zero. Every degree-n target admitting an m<=2n branch realization lies in it.

The retained n-reactive/n+1-resistor construction has exactly $2n+1$ branches.
For all family members the degree bound forces at least n reactives. Off the
exceptional measure-zero set the total bound then forces at least n+1 R in
every n-reactive realization, and the construction attains both bounds.

Limits: almost-everywhere over real coefficient coordinates says nothing by
itself about any individual rational target. In particular this does not prove
that the original rational degree-six target needs seven R, nor that the
frozen rational regression examples are outside the exceptional set. It does
not solve practical arbitrary-target synthesis or unrestricted R optimality.
