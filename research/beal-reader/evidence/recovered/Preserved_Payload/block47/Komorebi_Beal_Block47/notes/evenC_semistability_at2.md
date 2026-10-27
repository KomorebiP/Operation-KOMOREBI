# Block47: stable reduction at two in the even-C branch

Status: written proof. This note supplies the missing inertia-at-two input for extending the Block46 global character calculation. It does not assert that all even-C solutions are impossible.

Let A,B,C be positive pairwise-coprime integers satisfying A^3+B^5=C^7, with C even. Then A and B are odd. Consider the genus-two curve with integral equation

\[
 y^2+(x^3+B)y=2Bx^3+3Ax+B^2. \tag{1}
\]

## Proper flat model

Set R=Z_2. The affine chart (1) is monic quadratic in y and hence finite free of rank two over R[x]. On the chart u=1/x put v=y/x^3. The equation becomes

\[
 v^2+(1+Bu^3)v=2Bu^3+3Au^5+B^2u^6. \tag{2}
\]

It is again monic quadratic, now in v over R[u]. The substitutions glue the charts to a finite flat degree-two cover of P^1_R, so the resulting model X/R is proper, flat and finitely presented. Its underlying rank-two module over P^1 is O ⊕ O(-3), giving arithmetic genus two on each fiber. The generic fiber is smooth: completing the square gives the sextic with discriminant 2^12 3^6 5^5 C^14, which is nonzero in Q_2.

## Exactly two ordinary nodes

Over k=Fbar_2, equation (1) reduces to

\[
 F(x,y)=y^2+(x^3+1)y+x+1=0.
\]

Its partial derivatives are

\[
 F_y=x^3+1,\qquad F_x=x^2y+1.
\]

At a singular point, x^3=1 and y=x^{-2}=x. Substitution into F gives x^2+x+1=0. Therefore the only geometric singularities are (r,r), where r is one of the two roots of r^2+r+1=0.

Put x=r+s, y=r+t. An exact expansion in k[s,t] gives

\[
 F(r+s,r+t)
 =t^2+r^2st+r^2s^2+rs^3+rs^2t+s^3t. \tag{3}
\]

The quadratic tangent cone is

\[
 Q(s,t)=t^2+r^2st+r^2s^2.
\]

Since Q(0,1)=1, its projective roots are detected by t=ks. Their equation is k^2+r^2k+r^2=0, whose derivative is the nonzero element r^2. It has two distinct roots over k. Thus each singularity is an ordinary double point.

At infinity, equation (2) reduces to

\[
 v^2+(1+u^3)v=u^5+u^6.
\]

At u=0 the two points have v=0 and v=1; the derivative with respect to v is 1. Both points are smooth. This proves the singularity list is exhaustive.

## Geometric irreducibility and stability

In k(x), divide by (x^3+1)^2 and put w=y/(x^3+1). The generic equation of the special fiber is

\[
 w^2+w=\frac{x+1}{(x^3+1)^2}
 =\frac1{(x+1)(x^2+x+1)^2}. \tag{4}
\]

The rational function on the right has a pole of order one at x=1. A rational function h^2+h either has no pole at a given place or has pole order 2m, where m>0 is the pole order of h; its leading pole cannot cancel. Therefore the right side is not h^2+h for any h in k(x). The Artin–Schreier quadratic is irreducible over k(x).

Since the cover is finite flat over P^1_k, the special fiber has no one-dimensional component supported above a point of P^1_k. Equation (4) therefore proves geometric irreducibility of the entire special fiber; the smooth and nodal local descriptions also establish reducedness.

The special fiber has arithmetic genus two and precisely two nodes of delta invariant one. Its normalization has genus zero. The two nodes have four distinct preimages on the normalization. Hence the rational normalization component has four distinguished branches and is stable. Together with the smooth generic fiber, X/R is a stable curve of genus two.

## Jacobian and inertia consequences

The Jacobian J consequently has semistable reduction at two. This implication is valid in residue characteristic two: Deligne–Mumford, Theorem 2.4, proves the equivalence between stable reduction of a genus-at-least-two curve and semistable reduction of its Jacobian, using Raynaud's Picard description in Theorem 2.5. The forward implication appears explicitly on printed page 89. [Primary source](https://www.numdam.org/item/PMIHES_1969__36__75_0.pdf).

Semistability persists after the unramified quadratic extension K_2/Q_2 for K=Q(sqrt5). By the semistable unipotence theorem, inertia at two acts unipotently on the seven-adic Tate module and on the rank-two RM factor. Reduction of a stable lattice preserves the characteristic polynomial (T-1)^2 of every inertia element. Therefore every one-dimensional residual Jordan–Hölder constituent is trivial on inertia at two. In particular, the characters lambda and mu in a hypothetical absolutely reducible RM representation are unramified at two.

This replaces the use of good reduction at two in the early part of the Block46 odd-C character proof. It does not replace that proof's final good-reduction Frobenius-at-two contradiction. The latter remains specific to odd C.

For even C, the global unit and determinant argument can now be rerun with unramified characters at two. If the remaining Block46 hypotheses are retained, it produces an unramified constituent at seven. When 7 divides AB, coprimality gives 7 not dividing C, and the Block47 Cartier computation gives good reduction with 7-rank zero. The separately audited Raynaud lemma then forbids such a constituent. The resulting irreducibility corollary should be stated only after that combined dependency chain is reviewed.

No computer enumeration is needed for the two-adic proposition: the node, infinity and irreducibility arguments above are uniform in all odd A,B satisfying the nonzero generic discriminant condition.
