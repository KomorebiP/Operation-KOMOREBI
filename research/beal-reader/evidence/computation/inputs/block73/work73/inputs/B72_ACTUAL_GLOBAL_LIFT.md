# B72.3. The valuation coordinate of an actual global upper extension

This note distinguishes a local lift from the actual upper extension extracted
from the SAME global natural matrix representation.

Let n be the actual depth, and m=floor(n/2)+1. The inherited diagonal theorem gives

    rho mod7^j = [[chi,b_j],[0,1]]        for every1<=j<=m.

Since m<=n, the lower-left entry really vanishes. Matrix multiplication makes b_j
a continuous1-cocycle in O_E/7^j(chi). Denote its class by alpha_j. It reduces to
the normalized natural alpha. No analogous assertion at j>n is inserted.

## Comparing the actual line, not a separately chosen one

At F=K_(7), the toric exact sequence has characters chi and1. The projection of
the global chi-line into the local trivial quotient is a G_F-map chi->1.
There is an inertia element with chi-1 a unit modulo7, so that map is zero at
EVERY finite precision. Hence the global line is contained in the toric line.
Both are primitive free rank-one O_E/7^j direct summands, so they agree.
The two graded bases therefore differ by one unit g_j, not independent units
on the three Kummer coordinates.

Write the local class, in the three fixed base-field Kummer coordinates, as

    alpha_j|F=U_j X_j+V_j H_j+W_j T_j.

For j<=min(m,7c-1), B72.2 gives a single unit g_j with

    U_j=2epsilon*w*g_j,
    V_j=Lambda_j*g_j,
    W_j=7c*g_j.                                          (5)

In particular,

    2epsilon*w*V_j=Lambda_j*U_j,
    2epsilon*w*W_j=7c*U_j,
    7c*V_j=Lambda_j*W_j.                                 (6)

The sign and graded choices can be made coherently at all these levels.

## The valuation theorem does not need the finite period window

Even if j>7c-1, the ACTUAL period valuation matrix is exactly7c I, and the induced
coefficient actions on torus and quotient agree. Choosing one matched O_E graded
basis identifies that valuation map with multiplication by7c. Thus, whenever
1<=j<=m, the valuation coordinate is a unit multiple of7c, whether or not the
higher UNIT coordinates have been computed. Therefore

    v7_truncated(W_j)=min(j,1+v7(c)).                     (7)

Here v7_truncated(0)=j. This is a statement about a coordinate of the ACTUAL
global Kummer lift where such a lift exists, not a free abstract choice.

Equivalently, if that actual lift has zero valuation coordinate at7, then

    7^(j-1) divides v7(C).                               (8)

The zero-valuation hypothesis in(8) is ADDITIONAL, not proved for arbitrary alpha_j.
Zero valuation must not be called an unramified Galois representation at residue
characteristic7. The cyclotomic character remains ramified.

## The first new level: j=2

For n>=2, the actual alpha_2 exists. Reducing the gauge modulo7 and comparing the
residual X-coordinate gives g_j mod7=v/(2epsilon). Hence W_2 is rational modulo49:

    W_2=7c*v/(2epsilon) mod49,   W_2/7 inF7,
    (2*(W_2/7))^2 = c^2*v^2 mod7.                        (9)

If7 does not divide c, W_2 is nonzero. Thus the naive higher lift that keeps only
[phi],[3],[sqrt5] and omits the[7] valuation coordinate cannot be the actual alpha_2
in that case. The general actual lift may and must contain the required coordinate.
No bound or contradiction is obtained merely from its presence.

## Why this does not finish the eight depth-one patterns

For n=1, m=1. A globally triangular mod49 representation is NOT supplied by the
inherited theorem. Local geometry still has a mod49 extension, but identifying it
with a freely chosen GLOBAL lift of the residual alpha would erase the actual
lower-left7*beta terms. This is the unresolved integral-representation comparison.

An elementary control shows the issue. Modulo49, matrices
U=[[1,1],[0,1]] and L=[[1,0],[7,1]] preserve the natural line modulo7. Every primitive
line lifting it has generator(1,7t), t inF7. L sends this to(1,7(t+1)), which is not
on the same line. Hence no such common line lifts modulo49. These matrices are
not asserted to be a Frey representation; they refute the automatic-lift inference.
