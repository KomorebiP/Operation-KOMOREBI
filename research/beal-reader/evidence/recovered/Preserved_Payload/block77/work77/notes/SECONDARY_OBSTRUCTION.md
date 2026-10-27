# B77.1. The secondary adjoint obstruction

Let `k=F_49`.  Let `chi:G_K -> F_7^*`,

    alpha in Z^1(K,k(chi)),
    beta  in Z^1(K,k(chi^-1)).

Use inhomogeneous cochains.  For a trivial-coefficient one-cochain `p`,

    dp(g,h)=p(g)+p(h)-p(gh).

For a `k(chi)` one-cochain `q`,

    d_chi q(g,h)=q(g)+chi(g)q(h)-q(gh).

The Block 73 adjoint equations give

    dp = - alpha cup beta,                                    (1)

and

    d_chi q = R_p,                                           (2)

where

    R_p(g,h)=2 alpha(g)p(h)
             +alpha(g)^2 chi(g)^(-1) beta(h).                (3)

The already established cup-zero theorem is precisely what makes (1) soluble.
The purpose of this note is to identify the obstruction to (2).

## A symmetric defining system

Put the pointwise product

    s(g)=alpha(g) beta(g) in k.

A direct cocycle calculation gives

    ds = -(alpha cup beta + beta cup alpha).                 (4)

Fix a solution `p` of (1), and set

    D12=-p,
    D23=p-s.

Then

    dD12=alpha cup beta,
    dD23=beta cup alpha.

Thus `(D12,D23)` is a defining system for the twisted triple product
`<alpha,beta,alpha>`.  Its associated two-cocycle is

    mu_p = alpha cup (p-s) - p cup alpha.                    (5)

Explicitly,

    mu_p(g,h)=alpha(g)(p(h)-alpha(h)beta(h))
              -p(g)chi(g)alpha(h).                          (6)

Now define the `k(chi)` one-cochain

    f(g)=alpha(g)p(g).

Expanding with (1) gives the exact cochain identity

    R_p + d_chi f = mu_p.                                   (7)

Consequently

    [R_p]=[mu_p] in H^2(K,k(chi)).                          (8)

For this fixed `p`, a global `q` solving the actual second adjoint equation
exists if and only if `[mu_p]=0`.

This is the precise sense in which the missing equation is a twisted
triple-Massey-type obstruction.  We do not identify it with an unconstrained
standard Massey product over `F_7`: the coefficients, cyclotomic actions, and
local deformation conditions are part of the project problem.

## Dependence on the first-stage solution

Every other solution of (1) is

    p'=p+z,      z in Z^1(K,k)

with trivial coefficient action.  From (5),

    mu_(p+z)-mu_p = alpha cup z - z cup alpha.               (9)

In cohomology, graded commutativity in odd characteristic gives

    [z cup alpha]=-[alpha cup z],

so

    [mu_(p+z)]-[mu_p] = 2[alpha] cup [z].                  (10)

Therefore the first choice-independent obstruction is the affine coset

    M(alpha,beta)
      =[mu_p]+2[alpha] cup H^1(K,k)
      subset H^2(K,k(chi)).                                (11)

There is some global first-stage solution for which the `q` equation is soluble
if and only if

    0 in M(alpha,beta).                                     (12)

This is stronger and more precise than speaking of one canonical H^2 class.

## Symmetrizing an arbitrary defining system

Suppose `(A12,A23)` is any defining system with

    dA12=alpha cup beta,
    dA23=beta cup alpha.

Equation (4) shows

    u=A12+A23+s

is a one-cocycle.  Since two is invertible in characteristic seven, replacing
both defining cochains by

    A12-u/2,   A23-u/2

forces their sum to be `-s`.  The Massey cocycle changes by

    -1/2 (alpha cup u + u cup alpha),

which is cohomologically zero by graded commutativity.  Hence the symmetric
normalization used above loses no ordinary cohomology class.

## A negative control: cup-zero does not formally solve q

Let `G=U_3(F_7)`, written as triples `(a,b,c)` with

    (a,b,c)(A,B,C)=(a+A,b+B,c+C+aB).

Take trivial cyclotomic action and

    alpha(a,b,c)=a,
    beta(a,b,c)=b,
    p(a,b,c)=c.

Then

    dp=-alpha cup beta

exactly, so the first cup obstruction vanishes.  But for

    x=(1,0,0),   z=(0,0,1)

we have `xz=zx` while

    R_p(x,z)=2,
    R_p(z,x)=0.

Any one-cochain `q` would satisfy `dq(x,z)=dq(z,x)` because `xz=zx`.  Therefore
no `q` exists.

This is not an absolute Galois group or a Frey representation.  It is a control
showing that the Block 73 `q` equation is a real secondary condition and does
not follow formally from cup-zero.

The primary computation checks the cochain identities exhaustively in 705,894
scalar cases, on 117,649 deterministic `F_49` cases, and checks all 117,649
ordered pairs in this Heisenberg control.  A second implementation uses another
basis of `F_49` and explicit 3-by-3 Heisenberg matrices.
