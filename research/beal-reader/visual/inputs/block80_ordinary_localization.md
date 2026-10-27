# B80.3. The exact ramification-restricted ordinary localization image

Fix a frozen nine-prime set S. All its rational primes are inert in K and have
q=+/-1 modulo7. Sigma=S union{2,3,5,7,infinity} has thirteen finite places.
Throughout this note z is an ORDINARY k-valued character, not beta or p itself.

## Local coordinates

By local class field theory, the local spaces for z have coordinates

    2:F, 3:F, 5:F, 7:phi, 7:3, 7:7,
    q1:I,q1:F,...,q9:I,q9:F.                              (8)

At5 the chosen uniformizer is sqrt5. At every support prime it is the rational q.
The inertia coordinate evaluates on the local Artin image of g_q=phi+a_q whose
image generates the seventh-power quotient of F_(q^2)^*. It need NOT generate
the whole multiplicative group. All a_q and seventh-power symbols are pinned.
At7, phi and3 are a pro-seven unit basis since their normalized48th-power logs
are5sqrt5 and6. Together with7 these give the three local character coordinates.
At2,3,5 the residue norms4,9,5 have no7-factor, so only the unramified coordinate
remains. Infinite odd-primary local H1 is zero. The total dimension is24 over k.

## Fourteen principal relations are complete

A basis of the global Sigma-unit group modulo seventh powers is

    phi,2,3,sqrt5,7,q1,...,q9.                            (9)

Independence follows from valuations and the nonseventh unit phi; rank is14.
Global class number one supplies no additional ideal-class variables. Pairing
local characters with these units gives a14-by-24 matrix L. Its image kernel is
EXACTLY the global localization image: this is the H1 exactness in the finite-S
Poitou--Tate sequence, equivalently principal-idele reciprocity and the ray-class
presentation. No unrestricted-localization surjectivity is being used.

All support logs of phi are zero. Let a=z_7(3) and x_i=z(I_i). Define ell_i by
ell_i(g_i)=1 and let

    ell_7(t)=log(t^6)/log(3^6) mod7=6*((t^6-1)/7) mod7

for rational7-adic units. The remaining coordinates are forced by

    z_7(phi)=0,
    z(F2)=-5a-sum ell_i(2)x_i,
    z(F3)=-a-sum ell_i(3)x_i,
    z(F5)=-4a-sum ell_i(sqrt5)x_i,
    z_7(7)=-sum ell_i(7)x_i,
    z(F_q)=-ell_7(q)a-sum_(i:q_i!=q) ell_i(q)x_i.           (10)

At a conductor prime q its own unit component for the rational uniformizer is1,
so the corresponding self entry is zero, not an undefined logarithm of0.
The support rows include all nine primes simultaneously.

Equation(10) defines a24-by-10 image matrix J. Both implementations prove

    rank L=14, rank J=10, L J=0, im J=ker L.              (11)

Every free parameter occurs as a global ordinary character; the image is not
merely a necessary linear overapproximation. Localization is injective: if all
these local classes vanish, the global character is everywhere unramified,
including at7, hence zero by Cl(K)=1. Thus H1(G_Sigma,k) has dimension10.
The same dimension follows from the Euler-characteristic formula and B80.1.

The k-valued extension of the F7 matrices is intentional. The smaller common
semilinear problem is imposed only after its additional frame hypothesis.
These matrices classify differences of bare primitives. They do not construct
the origin of the affine p-torsor or a Frey representation.
