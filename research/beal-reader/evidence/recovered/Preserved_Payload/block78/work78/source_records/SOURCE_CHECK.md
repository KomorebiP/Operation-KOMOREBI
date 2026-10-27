# Source check for Block 78

Checked 21 September 2026.

## Exact external result used

Danny Neftin, *Tamely ramified subfields of division algebras*, Journal of
Algebra 378 (2013), 184-195, author-hosted PDF:
https://neftin.net.technion.ac.il/files/2015/10/20-6-12.pdf

Theorem 2.1 explicitly reproduces Neukirch [18, Korollar 6.4]: for a finite
G_K-module A and finite set S, the localization map on H^1 is surjective under
six listed conditions, including H^1(G',A')=0. Corollary 2.3 states that under
conditions (a),(b),(c), or (e), prescribed local solutions at S can be imposed
while leaving the solution unchanged at another finite disjoint set T.

Neftin's reference [18] is:
J. Neukirch, *Uber das Einbettungsproblem der algebraischen Zahlentheorie*,
Invent. Math. 21 (1973), 59-116.

## Translation to this project

- For A=k trivial, A'=k(chi), G'=Gal(K(mu7)/K)=C6 and H^1(G',A')=0 because
  |G'|=6 is invertible on the 7-primary module.
- For A=k(chi), A' is trivial and G'=1, so H^1(G',A')=0.

Thus condition (c) applies to both Block 77 tangent modules.

## Boundary

The theorem prescribes behavior at FINITELY MANY places. It does not say the
resulting global correction is unramified at every other place, and it does not
supply Frey geometry at any new ramification prime. That limitation is retained
explicitly in every arithmetic application.
