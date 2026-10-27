# From opposite ramification to full natural torsion triviality

All applications use H1–H3 of TARGET_CONTRACT.md. Set w(7)=1 on the
unramified quadratic coefficient ring O, w(0)=infinity. The basis is the
fixed natural lattice, not the opposite endpoint lattice.

## B59.1. General natural precision at beta support

Suppose beta ramifies at v. Then n=t+2s with t>=1 and s=w(y), and

    rho_natural|G_v = I modulo 7^d,
    d=min(t, floor(t/2)+1).

Proof. Write m=floor(n/2)+1=floor(t/2)+s+1. The lower-left entry of F is
yp in7^n O, so w(p)>=n-s=t+s. The lower-right entry is 1+yr. Since it is
eta^(-1) modulo7^n and eta=1 modulo7^m,

    w(r)>=m-s=floor(t/2)+1.

Every entry of F-I=(x,y)^T(p,r) therefore has valuation at least
floor(t/2)+1. Every entry of N has valuation at least t by natural content.
Thus F and I+N are identity modulo7^d. The split toric representation is
tamely unipotent at q!=7, with inertia I+zN for z in Z_7 (with the chosen
unit normalization). Wild inertia is trivial. Inertia and Frobenius generate
the local quotient seen by the representation, proving the assertion for
the full decomposition group. No division by x, and no assumption that x
is a unit, was made. QED.

In particular every beta-supporting place has the full natural J^nu[7]
locally rational. This is stronger than making an arbitrarily chosen
residual extension split after changing its lattice.

## B59.2. The depth-two theorem

At n=2, eta_2 is trivial to its entire precision by the inherited global
half-precision theorem. At beta support its inertia order is 7^s, so s=0,
y is a unit and t=n=2. In the SAME basis,

    N in49 M_2(O), p in49 O, r in49 O, F-I in49 M_2(O).

Consequently

    rho_natural|G_v = I modulo49,
    J^nu[49] subset J^nu(K_v).

This does not assert local rationality of all 7-power torsion. The 49-torsion
assertion is about the actual natural Jacobian lattice, with underlying
Z_7 rank four. Identity over O/49 implies identity on that entire underlying
Z/49 module; a coefficient-field comparison map is not needed.

More generally, if eta_n is trivial on the full local group at beta support,
then s=0,t=n, and the same argument gives full natural J^nu[7^n] rationality.
Triviality on inertia alone does not justify this strengthening.

## B59.3. Maximal diagonal inertia

Suppose eta_n has global exponent7^e, e>=1, and local inertia attains7^e.
Block55 gives L=n-e=t+s, with x a unit and s=w(y)>0. Global exponent
control supplies F22=1 mod7^L. Hence

    w(r)>=L-s=t, w(p)>=n-s=t+e.

Together with content(N)=t this proves rho_natural|G_v=I mod7^t.
This remains valid when beta is unramified at v. It uses the complete global
exponent, not a local inertia exponent substituted for it.

## Evidence and sharpness

local_torsion_checks.py tests t=1,...,6, s=0,...,4 in 5,760 exact O-integral
instances over Q(phi), including 5,730 nonrational instances and 192 depth-two
instances. It also tests nonunit x with unit y. The general bound is tight
in all generated instances. Generic Q in that grid is an integer unit,
not claimed to be a residue-field cardinality. Actual norm controls use
97^2,197^2,14503^2.

These finite checks audit the formulas. The universal statement is the
valuation proof above. Exact local models at97 and14503 satisfy the abstract
depth-two matrix conditions but fail the new actual geometric period test.
They are not counterexamples to the matrix theorem or constructed Frey curves.
