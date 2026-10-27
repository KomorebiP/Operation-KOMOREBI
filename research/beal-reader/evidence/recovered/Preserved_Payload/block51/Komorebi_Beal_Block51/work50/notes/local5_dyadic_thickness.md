# Actual dyadic thickness and unramified natural seven-torsion

Status: written local proof, awaiting fresh review. This supplements the
frozen Block47 even-C stable model with its integral node thicknesses.
It concerns the natural Jacobian lattice and does not use a residual
semisimplification or an arbitrary change of lattice.

Let A^3+B^5=C^7 be a primitive positive solution with C even. Put
F=Q_2(sqrt(5)), an unramified quadratic extension of Q_2, and
c=v_2(C). The claim is that both stable nodes have thickness 7c,
the period valuation pairing is 7c I_2, and the actual J[7] is
unramified at F. Twisting by an unramified character preserves this.

## A transverse integral smoothing parameter

A and B are odd. Fifth powering is an automorphism of Z_2^*, so
choose u in Z_2^* with u^5=-A. Put beta=B/u^3=1+epsilon. Then

    beta^5-1=C^7/u^15,
    v_2(epsilon)=7c.

The second equality follows because beta is odd and
beta^4+beta^3+beta^2+beta+1 is odd. Scaling x=uX and y=u^3Y in
the original integral generalized Weierstrass equation gives

    G(X,Y,beta)=Y^2+(X^3+beta)Y-2beta X^3+3X-beta^2=0.

At beta=1 the two nodes are (r,-r), where r is a root of
g(X)=X^2+X-1. Both roots lie in O_F and are distinct modulo two.
Using r^2=1-r, direct calculation gives

    G(r,-r,1)=G_X(r,-r,1)=G_Y(r,-r,1)=0,
    G_XX=-6r^2-12r,  G_XY=3r^2,  G_YY=2,
    det(Hessian G)=15(r-2),
    G_beta(r,-r,1)=-5r.

Both the Hessian determinant and G_beta are units of O_F. The
special tangent cone is the nondegenerate ordinary-node quadratic
already computed in Block47. Its two branches split after a finite
unramified extension, which is harmless for thicknesses and inertia.

Here is the complete formal argument that the parameter is epsilon
times a unit; it avoids dividing by two in residue characteristic two.
Work over R=O_L[[epsilon]], where L/F is an unramified extension
splitting the tangent branches. The formal implicit-function theorem
applied to (G_X,G_Y), whose derivative in (X,Y) is the invertible
Hessian, supplies a unique critical section

    X=x(epsilon), Y=y(epsilon),
    x(0)=r, y(0)=-r.

Let k(epsilon)=G(x(epsilon),y(epsilon),1+epsilon). The chain rule
and vanishing gradient at epsilon=0 give

    k(0)=0,  k'(0)=-5r,

so k(epsilon)=epsilon times a unit of R. Translate by the critical
section. There are no linear terms in the two curve coordinates.
The quadratic part has two transverse factors over R by Hensel
lifting the split tangent cone. An invertible linear change makes
that part uv.

Every higher homogeneous term of degree n>=3 can be removed by a
coordinate change u -> u+a, v -> v+b with a,b homogeneous of
degree n-1: its degree-n change is av+bu, and every degree-n
monomial belongs to the ideal (u,v). All lower-degree terms stay
unchanged. Iterating in the formal topology produces the equation

    uv+k(epsilon)=0.

No step divides by two. The constant k(epsilon) remains unchanged.
Specializing the actual epsilon in 2O_L gives a split node with
smoothing parameter of valuation v_2(k(epsilon))=7c. The argument
applies to both nodes. Thus their exact thickness is 7c, with no
extra constant from the factor 2^12 in the completed-square sextic
discriminant.

## The natural torsion representation

The frozen stable-model proof in
`work47/notes/evenC_semistability_at2.md` gives one rational
normalization component with two ordinary self-nodes. Its dual
graph therefore has two independent loops. The exact branch action
in `work47/notes/evenC_torus_frobenius.md` is unramified; over an
unramified quadratic extension both torus and period lattice split.
The edge-length pairing is consequently 7c I_2 in the two-loop basis.

The graph/analytic comparison is Baker--Rabinoff,
arXiv:1308.3864v1, Theorem 2.9 and Remark 6.7, already read and
pinned in `work49/notes/local_types.md`. It has no odd-residue-
characteristic restriction. For the split uniformization J=T/Y,
the actual multiplicative period entries therefore satisfy

    v_2(q_ij)=7c delta_ij.

The generic seven-torsion is the actual extension

    0 -> mu_7^2 -> J[7] -> (Z/7)^2 -> 0

over that unramified splitting field. Its Kummer parameters are the
q_ij. Each has valuation divisible by seven. Removing its seventh-
power uniformizer part leaves a unit. Every unit has a seventh
root over the maximal unramified extension: take a seventh root of
its residue and apply Hensel's lemma, whose derivative seven is a
unit in residue characteristic two. The roots of unity mu_7 are
also unramified. Hence inertia acts trivially on the entire J[7],
including its extension class.

Descent from the unramified splitting field preserves this
conclusion because inertia is unchanged by unramified extension.
This proves actual unramifiedness of the natural lattice at two.
It does not claim that every other stable lattice has unramified
reduction.

## Source and interpretation boundary

The stable model and unramified graph action are imported from their
separately audited predecessor proofs. The local smoothing and
unit-Kummer arguments above are given in full. For comparison, the
characteristic-two quadratic-form normal-form method is also
explained in the Stacks Project, Section 53.19, Lemma 53.19.3,
[tag 0C46](https://stacks.math.columbia.edu/tag/0C46), read directly
on 2026-09-19. That source concerns a curve over a field; the
relative mixed-characteristic argument here is proved separately
and is not attributed to a stronger statement in that lemma.

The initial general web search returned unrelated results. Only the
direct Stacks source and the retained primary monodromy source are
used. No bounded computation is needed for the displayed exact
polynomial identities or the formal coordinate argument.
