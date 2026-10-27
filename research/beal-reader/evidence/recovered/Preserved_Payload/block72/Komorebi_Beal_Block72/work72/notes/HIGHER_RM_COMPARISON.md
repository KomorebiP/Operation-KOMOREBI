# B72.2. The actual coefficient action through the same precision window

The actual integral O_E action induces matrices S_T,S_Y overZ7 on the marked
local toric submodule and the period quotient. The completed-period functoriality
of an existing Galois-equivariant endomorphism yields their intertwining relation.
Applying valuations gives

    (7c I) S_T = S_Y (7c I).

Cancellation is overZ7, BEFORE reduction. Since7c is nonzero, S_T=S_Y=S.
On both graded pieces multiplication by the actual coefficient w has characteristic
polynomial T^2-5. Thus tr S=0 and S^2=5I.

For j<=7c-1, B72.1 and full completed-period functoriality imply

    (Z_j I+2X_j R) S_j = S_j (Z_j I+2X_j R).

X_j is a primitive free coordinate of G_j, not merely a nonzero element that might
be annihilated by a nonzero7-power scalar. Comparing its coefficient gives

    R S_j=S_j R.

The centralizer of R in M2(Z/7^j) is (Z/7^j)[R]. This can also be checked entrywise:
if S=[[a,b],[c,d]], commutation gives c=b and d=a+b. In the polynomial description
write S=xI+yR. Trace zero forces x=0; S^2=5I forces y^2=1. Since7 is odd and
Z/7^j is local, one of y-1,y+1 is a unit, and the other is zero. Therefore

    S_j=epsilon R, epsilon in{+1,-1}.                    (3)

The same sign is used at EVERY level in the window, because reduction modulo7
already distinguishes the two signs. We do not select a new embedding at each j.

In matched O_E/7^j graded bases the actual scalar period extension is

    kappa_j=2epsilon*w X_j+Lambda_j H_j+7c T_j.            (4)

This extends B71's residual matrix identification. It does NOT establish S=+/-R
as an exact integer matrix beyond the proven window, nor global semilinear
Tate-lattice descent. Functoriality is a statement about the existing integral
coefficient action, not a claim that all Galois endomorphisms are algebraic.

## Strict comparison control

P=[[1,7],[0,1]], S=P R P^-1=[[-13,82],[-2,13]] satisfies S^2=5I and S=R mod7,
but S does NOT commute with R modulo49. Lifting the square-root relation alone
would wrongly admit it. The full period intertwiner excludes this lift.

This is an algebraic negative control, not a claimed actual coefficient action.
