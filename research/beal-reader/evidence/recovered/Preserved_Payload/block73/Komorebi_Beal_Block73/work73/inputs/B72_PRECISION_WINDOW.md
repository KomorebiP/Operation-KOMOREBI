# B72.1. A guaranteed higher-precision period window

Let F=Q7(omega), omega^2=5, O_F its integer ring, phi=(1+omega)/2,
c=v7(C)>=1, C=7^c C0, and d=7c. The coefficient prime and residue characteristic
are both7. They are NOT treated as distinct-prime torsion.

Write G_j=F*/F*^(7^j) additively. In the inherited marked family the actual periods
are the displayed leading terms times elements of1+7^d O_F:

    Pi_aa ~ - (C^7/A^3)*phi^2/(675omega),
    Pi_bb ~   (C^7/A^3)*phi^-2/(675omega),
    Pi_ab=Pi_ba ~ -phi^-4.

The quotient denoted by ~ belongs to1+7^d O_F, not just1+7O_F. Its proof is a
pinned source-dependent input from B71; we do not infer it from finite tests.

For U_s=1+7^s O_F, s>=1, seventh powering gives U_s^7=U_(s+1).
Indeed ((1+7^s t)^7-1)/7^(s+1)=t+7*(integral higher terms), with derivative1
modulo7. Hensel's lemma yields the bijection on O_F. Iteration gives

    U_1^(7^j)=U_(j+1).

Consequently all the inherited period errors disappear in G_j whenever

    1<=j<=d-1=7c-1.                                      (1)

At c=1 this includes j=1,2,3,4,5,6. It is a guaranteed window, not a claim that
the actual error becomes nontrivial immediately afterward. The generic error
1+7^d is NOT a7^d power: its logarithm has valuation exactly d, whereas the
7^d powers of principal units have logarithm valuation at least d+1. This is a
counterexample to extending (1) from the error bound alone, not a computed actual
Jacobian error.

## Three primitive local Kummer coordinates

The Teichmuller subgroup of O_F* has order48, prime to7. Principal units have
logarithm lattice7O_F. The unit coordinates

    X_j=[phi], H_j=[3]

form a free basis of the unit part of G_j over Z/7^j. To see primitivity, the
mod7 values of log(phi^48)/7 and log(3^48)/7 are5omega and6. Their determinant
is a unit. The higher basis follows either from the7-adic logarithm or from
successive multiplicative digit lifting. Adding T_j=[7] gives a free rank3 basis
of G_j. In particular, the valuation component is a separate summand.

For a rational7-adic unit a define

    ell_j(a)=log(a^6)/log(3^6) mod7^j,
    d_j=ell_j(5)/2 mod7^j.

The numerator and denominator have valuation at least1 and exactly1 respectively,
so the quotient lies inZ7. We have [a]=ell_j(a)H_j and [omega]=d_j H_j.
Thus, throughout (1),

    Z_j=7c T_j+Lambda_j H_j,
    Lambda_j=7ell_j(C0)-3ell_j(A)-3-5d_j,
    ([Pi_ij]) = Z_j I + 2X_j R,
    R=[[1,-2],[-2,-1]].                                 (2)

The term7c T_j is discarded at j=1 only because7=0 there. Its disappearance
cannot be repeated at higher precision. Equations(1)–(2) concern actual marked
periods conditional on the inherited analytic family, not an arbitrary torus lattice.
