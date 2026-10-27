# B78.2. Finite-local flexibility for the two adjoint coefficient modules

Let K=Q(sqrt(5)), k=F_49, and chi be the mod-7 cyclotomic character. This note
uses an exact local-global theorem of Neukirch, in the formulation reproduced as
Theorem 2.1 and Corollary 2.3 of Danny Neftin, *Tamely ramified subfields of
division algebras*, J. Algebra 378 (2013), 184-195. Neftin's Theorem 2.1 cites
Neukirch, Invent. Math. 21 (1973), Korollar 6.4.

For a finite G_K-module A of exponent n, put A'=Hom(A,mu_n) and let G' be the
Galois group of the field cut out by A'. The cited criterion states, among other
cases, that for every finite set S the localization map

    H^1(K,A) -> product_(v in S) H^1(K_v,A)

is surjective if H^1(G',A')=0. Corollary 2.3 allows the prescribed change at S
while leaving the solution unchanged at another finite disjoint set T.

We apply this exactly to the two modules occurring in Block 77.

## B78.2a. Trivial coefficient module k

Take A=k with trivial G_K action. Its Cartier/Galois dual is a two-dimensional
F_7-space on which G_K acts by chi:

    A' ~= k(chi).

The field cut out by A' is K(mu_7). Since K is real quadratic and the unique
quadratic subfield of Q(mu_7) is imaginary, [K(mu_7):K]=6. Thus G'=C_6.

Because 6 is invertible on the 7-primary module A', averaging gives

    H^1(C_6,A')=0.

Therefore for every finite S,

    BOX: H^1(K,k) -> product_(v in S) H^1(K_v,k) is surjective.       (2)

Since k is trivial, B^1(K_v,k)=0. Equation (2) matches actual local cocycles,
not merely their classes.

## B78.2b. Cyclotomic coefficient module k(chi)

Take A=k(chi). In A'=Hom(A,mu_7), the chi action on the source cancels the chi
action on the target. Thus A' is a trivial two-dimensional F_7-module. Its
splitting field is K itself, so G'=1 and

    H^1(G',A')=0.

Hence for every finite S,

    BOX: H^1(K,k(chi)) -> product_(v in S) H^1(K_v,k(chi))
         is surjective.                                           (3)

The same theorem allows the localized correction to be zero at any additional
finite set T.

## Scope

Equations (2)-(3) are statements about finite prescribed local conditions. They
do NOT guarantee that the resulting global class is unramified at every place
outside S union T. In particular, they do not solve a ramification-restricted
Selmer problem with an infinite collection of unramified conditions.

This distinction is load-bearing for the Frey application: adding an auxiliary
ramified global correction may change the actual representation at a new prime.
The theorem therefore proves finite-local flexibility, not global geometric
realizability.
