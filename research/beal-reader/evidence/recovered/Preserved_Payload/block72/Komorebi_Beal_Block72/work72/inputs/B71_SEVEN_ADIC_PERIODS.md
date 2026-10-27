# B71.1. Exact residual period classes at the fixed prime seven

Retain H1-H4. Write c=v7(C)>=1, F=Q7(omega), omega^2=5, phi=(1+omega)/2.
F/Q7 is unramified quadratic. Put epsilon=C^7/A^3, so v7(epsilon)=7c.

## Integral specialization of the marked family

The unit substitution of Block60 gives the EXACT family

    f_epsilon(X)=X^6+10(epsilon-1)^2 X^3
                       +12(epsilon-1)^3 X+5(epsilon-1)^4,
    f_0=(X^2+X-1)^2*(X^2-2X+5).

Its paired nodes, branches, derivatives, and normalization are the same algebraic
expressions recorded in B60_DIAGONAL_PERIODS.md. Their denominators and nonzero
branch separations have norms supported only at2,3,5. Thus they are7-adic units.
The node smoothing derivatives are units and each node has thickness7c. The
special fiber is one split rational component with two self-nodes.

The universal marked deformation ring has integral coefficients with only branch
separations inverted (Ichikawa1909.10149v4, section2.3). Specialize it to this
one-parameter family, keeping the exact central branch coordinates in O_F. The
formal implicit-function and smoothing changes involve only the preceding units.
Thus the Schottky parameters are kappa_i*epsilon+O(epsilon^2), integrally over O_F.
The inherited marked product comparison gives, more precisely than a bare1+m:

    Pi_aa = epsilon*(-phi^2/(675*omega))*(1+epsilon O_F),
    Pi_bb = epsilon*( phi^-2/(675*omega))*(1+epsilon O_F),
    Pi_ab = Pi_ba = -phi^-4*(1+epsilon O_F).

This is the same leading-unit computation, not a new guess of a residue unit.
Every remaining factor in the integral product is1 modulo the smoothing ideal;
the moving marked positions also differ from their central positions by that
ideal. It maps into epsilon O_F. The valuation matrix is7c I_2. The analytic
universal-family comparison remains an explicitly inherited written dependency.

## Why the error terms ARE seventh powers at7

For t in O_F,

    ((1+7t)^7-1)/49 = t+21t^2+245t^3+1715t^4+7203t^5+16807t^6+16807t^7.

All coefficients after the linear term are divisible by7. This polynomial induces
a bijection O_F -> O_F by Hensel lifting, with derivative1 modulo7. Therefore

    (1+7O_F)^7 = 1+49O_F.

Our errors belong to1+7^(7c)O_F, a subgroup of1+49O_F, so their classes vanish in
F*/F*7. It would be FALSE to replace their proved depth by an arbitrary principal
unit:8=1+7 is not a seventh power in F.

Write Kummer groups additively. Since[-1]=0 and7[C]=0, set

    X=[phi],
    Z=7[C]-3[A]-3[3]-5[omega]=-3[A]-3[3]-5[omega].

The exact residual period matrix is

    P = [[Z+2X,-4X],[-4X,Z-2X]] = Z I+2X R,
    R=[[1,-2],[-2,-1]],  R^2=5I.

This is a matrix with entries in H1(F,F7(chi)), not a matrix of scalars obtained
by identifying the local residue field with the coefficient field.

## Unit Kummer coordinates

For a7-adic unit z, define

    L(z)=(z^48-1)/7 mod7 in O_F/7O_F.

This homomorphism identifies O_F*/O_F*7 with the two-dimensional F7 space
O_F/7O_F. Teichmuller units of order48 are seventh powers. On1+7t it is48t=-t
mod7; its kernel is1+49O_F after removing the Teichmuller part. The preceding
Hensel argument proves the assertion without discarding principal units.

Direct arithmetic modulo49 gives

    L(phi)=5*bar(omega), L(3)=6, L(omega)=3, L(5)=6.

Hence X=[phi] and H=[3] are independent. In their F7 basis,

    [omega]=4H,
    [A]=6*q7(A)*H,
    q7(A)=(A^6-1)/7 mod7,
    Z=(3*q7(A)+5)H.

The sixth and forty-eighth Fermat quotients agree for rational units because
A^48=(A^6)^8 and8=1 modulo7. The finite check covers every one of the2304 units
mod49 and every one of the42 rational unit residues. The universal assertions
are the preceding unit and Kummer arguments, not consequences of a finite bound.
