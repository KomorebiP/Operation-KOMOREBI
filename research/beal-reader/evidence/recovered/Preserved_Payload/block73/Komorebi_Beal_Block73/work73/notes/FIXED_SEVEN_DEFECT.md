# B73.2. A fixed-seven valuation condition on the GLOBAL adjoint deformation

Use the reference rho0 of ADJOINT_DEFORMATION.md, not a purported actual global
upper extension. At F=K_(7), the actual local representation has its toric chi-line.
The nontrivial residual cyclotomic character identifies its reduction with the
global natural residual line. A strict local change of basis aligns the lifted
toric line with the reference line. In that aligned basis the actual local
representation is [[chi,b7],[0,1]] modulo49, because these are the exact toric
characters. Accordingly the local representative of X has p=beta=0, and q is
an ordinary k(chi) Kummer cocycle.

Define nu_7(X) as the [7] valuation coordinate of this local q-class.
It is well defined under strict equivalence. After aligning the same toric line,
the remaining strict changes are upper triangular. Their effect on q is a
coboundary plus a scalar multiple of the residual alpha. The latter is a unit
class at seven, so both changes have valuation zero. The residual chi-line is
unique here: alpha|F is nonzero and chi differs from 1 on inertia.

Put c0=v7(C). Block72 gives the ACTUAL local class g2*kappa2, with

    kappa2=2 epsilon*w [phi]+Lambda2 [3]+7*c0 [7],
    g2 mod7=v/(2 epsilon).

The reference b0 uses only the global unit generators phi,3,sqrt5 and has
valuation zero at F. The local difference b7-b0=7q therefore yields

    BOX: nu_7(X)=c0*v/(2 epsilon) in k, epsilon=+/-1.       (6)

This is valid at actual depth one, where there is NO actual global alpha_2.
The object X is global and nontriangular; only its locally aligned upper
component is compared to periods. The unknown lower-left 7*beta is never erased
from the global representation. Equation (6) is a nonhomogeneous local condition
on the same GLOBAL adjoint cocycle satisfying equations (3)-(5).

The numerical value is in F7 under the inherited normalization. For c0=1,v=3,
epsilon=-1 it is2; its modulo49 valuation contribution is14, agreeing with the
retained positive local period example. It is not zero automatically.

## Why modulo49 alone still allows an apparent adjustment

For every xi in Z1(G_K,k(chi)),

    rho_xi(g)=rho(g)+7*xi(g)*E12                           (7)

is a representation modulo49, has the same determinant and trace at EVERY g,
and preserves both residual endpoint classes alpha and beta. This follows
directly from the upper triangular residual matrix:

    E12*rhobar(h)=E12, rhobar(g)*E12=chi(g)E12.

The lower-left times added upper-right product is divisible by49. Equivalently
X is changed by xi*E12, an adjoint cocycle. At seven, the upper perturbation acts as zero on a toric-line generator
(1,7t) modulo49. The two local representations therefore have the same toric
line, and the same strict alignment can be used. It follows that

    nu_7(X+xi*E12)=nu_7(X)+val_7(xi).                     (8)

Thus xi=lambda*[7] can change the new local valuation arbitrarily at the level
of mod49 REPRESENTATIONS. This is not a Frey realization, and (7) need not lift
to the next modulus. The next note proves an obstruction that prevents treating
this direction as free for the actual integral representation.
