# A source-side discriminator for the explicit cubic example

This is a bounded exact calculation for the original character chi_0 and its
induced Weil representation. It identifies a further reason to retain the wild
extension data. It does not compute the entire intrinsic Clifford filtration.

Use F, L, pi and chi_0 from ARITHMETIC113, with the PLUS-trace additive
character. The six units u_r=1+pi^r, 1<=r<=6, generate U_L^1/U_L^7. All three
Galois conjugates of chi_0 have conductor7. Local reciprocity therefore
reduces their diagonal image on P_L to their values on these generators.

The script scripts/wild_image113.py evaluates those three characters by exact
rational traces. The nontrivial rows of their additive exponents modulo1 are:

| r | chi_0 | chi_0 composed with sigma | chi_0 composed with sigma² |
| --- | --- | --- | --- |
| 2 | 4/9 | 4/9 | 1/9 |
| 4 | 0 | 1/3 | 2/3 |
| 5 | 2/3 | 2/3 | 2/3 |
| 6 | 1/3 | 1/3 | 1/3 |

The rows r=1,3 are zero. Quotienting diagonal matrices by their common scalar
leaves two independent vectors (0,2) and (1,2) in F3². Thus the projective
diagonal image is exactly C3².

Since L/F is cyclic totally wild of degree3, P_F/P_L is C3 and a lift of its
generator cyclically permutes the three induced basis lines. The cube of its
matrix is scalar: in a three-cycle monomial matrix each diagonal cube entry
is the same product of the three weights. After a complex diagonal change of
basis and scalar normalization, its projective class is the permutation
three-cycle. This does not determine its original scalar cube.

Conjugation acts on relative diagonal coordinates by

    beta(a,b)=(-b,a-b).

This action is nontrivial of order3. Its image beta-1 and its fixed subgroup
each have order3. Consequently the complete projective wild image in this
example is the nonabelian group

    C3² semidirect C3, of order27.

This is an exact projective-image computation, not a count of some sampled
matrices. The scalar center of the full linear image and the scalar cube of
the chosen quotient lift are additional data.

## A concrete obstruction to extending the coprime normalization argument

The r=2 row gives the actual diagonal matrix

    rho(u_2)=diag(zeta9^4,zeta9^4,zeta9).

It has determinant1 and cube zeta3 times the identity. Its projective class
has the order-three representative

    D=diag(1,1,zeta3²),

whose determinant is zeta3². No scalar multiple cD can have both (cD)³=1 and
det(cD)=1: the first condition forces c³=1, while the determinant is then
still zeta3². This is an explicit instance of the missing coprimality, with
group order and carrier dimension both3. It is not a counterexample to the
new normalization theorem, whose coprimality hypothesis excludes it.

The actual type Heisenberg action eta has abelian projective image J^1/H^1
of order9, whereas the entire wild Weil image just computed has nonabelian
projective image of order27. They cannot be equated as whole projective group
actions. A packet comparison must specify the appropriate Heisenberg subgroup
or Clifford stage and retain its extra wild action. This does not exclude a
properly constructed packet comparison on the same three-dimensional carrier.

This observation supports concentrating on the wild extension and unit
correction, rather than applying the tame coprime phase theorem beyond its
range. It neither proves the corrected theta_1 occurs in AI(chi_0) nor shows
that a particular Heisenberg subgroup chosen abstractly is the prescribed
intrinsic break packet.

## Provenance

Contract: WILD_IMAGE_CONTRACT113.json. Completed exact run and character table:
evidence/wild_image/run01/RESULT.json, with the input-pinned v2 manifest in
the same directory. The script imports the authenticated exact field and
logarithm routines from the arithmetic calculation. Its separate finite-to-Weil
reduction is given above. No stochastic or floating arithmetic is used.
