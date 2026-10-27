# B79.3. Restricted ordinary characters bound first-stage differences

Compare two actual candidates in the same residual frame, with the same alpha,
beta cocycle and reference. Put z=p'-p. The first-stage equation gives dz=0;
z is a k-valued ordinary character. B79.1 makes it unramified outside S0 union S,
where S is the complete beta support.

At a fixed place, both actual traces equal chi+1. The trace formula for the
adjoint deformation gives

    (chi(g)-1) z(g)=0 mod7.

Choose h with chi(h)!=1; then z(h)=0. If chi(g)=1, both h and hg have nontrivial
cyclotomic value, so z(hg)=0 and z(g)=0. The other g already have z(g)=0.
Consequently z is ZERO ON THE FULL LOCAL GROUP at2,3,5,7. This uses no equality
of arbitrary good-prime traces, and no unproved local value of p itself.

Thus every difference lies in the finite vector space

 V_S={z in H1(K,k): unramified outside S, z|G_v=0 at v|2,3,5,7}.       (6)

Class number one and units +/-phi follow from the norm-Euclidean argument
preserved in Block73. The ray-class exact sequence (Milne, CFT V.1.7 and V.3)
then presents exponent-seven characters by one residue coordinate per prime
ideal of S. No wild conductor factor is needed at S: its residue characteristic
is not7, and wild inertia has pro-ell order. Fixed-seven local triviality has
already removed all ramification there.

For any compatible surjective residue logarithms ell_v, (6) is exactly

    sum_v ell_v(a) z_v=0   for a=phi,2,3,sqrt5,7.      (7)

Phi supplies the unit relation. The other four rows impose Frobenius zero at
the principal fixed ideals (2),(3),(sqrt5),(7), with inertia already zero.
This is an ORDINARY character matrix for z=p'-p. It is NOT applied to beta,
whose chi^-1 twist is different.

## Extra justified rows in the eight frozen patterns

All supporting rational primes are inert. The inherited beta descends to a
rational chi^-1 cocycle gamma. If q=-1 mod7 is in S and F_q is a rational
Frobenius lift, then

    beta(F_q^2)=gamma(F_q)+chi(F_q)^-1 gamma(F_q)=0.

The compatible K-Frobenius is F_q^2, equivalently the local Artin uniformizer q
under the unramified quadratic transfer. Block78's toric hyperplane therefore
fixes p(F_q^2)=-h. Both candidates satisfy this, so z(F_q^2)=0.

The principal-idele q relation gives the ADDITIONAL homogeneous row

    sum_(v in S, v not over q) ell_v(q) z_v=0.         (8)

At v over q, use q itself as uniformizer; its unit component is1 and contributes
zero. This convention is necessary at a conductor place. The other residue
components are units. The sign of the Frobenius relation is immaterial for zero.

The exact residue matrices and kernels are in verification/primary79.json, under
restricted_p_tangent. Both field implementations reconstruct all columns.

|pattern|rank of five fixed/unit rows|rank after (8)|k-dimension bound|
|---|---:|---:|---:|
|A|3|6|3|
|B|3|6|3|
|C|3|5|4|
|D|3|6|3|

The five-row matrix alone has dimension6 over k in all four cases. Its phi row
is zero, and its3 and sqrt5 rows agree in the chosen log normalization. The
remaining three rows are independent. Adding the two or three -1-mod7 support
Frobenius rows gives the displayed stronger ranks.

These are exact dimensions of the stated HOMOGENEOUS character constraints.
Differences of actual admissible p's lie in them. Further toric conditions,
particularly at the +1-mod7 support primes, may reduce them. No particular p0
or affine translate is computed, and no claim that all these directions extend
to full q solutions or geometric deformations is made.

If the affine Stage-P problem is nonempty, fixing one p0 bounds the number of
framed first-stage p-cochains by 49^3,49^3,49^4,49^3 respectively. This is not a
count of representations or of any of the eight frozen residual tuples.

## Optional common pointwise semilinear frame

ADDITIONALLY impose z(jgj^-1)=sigma(z(g)) for the SAME j and frame/reference.
Conjugation acts on the inert residue logarithm by q mod7. Thus +1 conductor
coordinates are rational and -1 coordinates lie in w F7. All rows of (7)-(8)
vanish on the latter columns. The resulting F7 dimensions are again3,3,4,3,
with plus/minus dimensions (0,3),(0,3),(2,2),(0,3).

In THIS fixed pointwise semilinear problem the bounds become343,343,2401,343.
This extra assertion does not compare arbitrarily unrelated j's or integral
frames; it does not reclassify an uncomputed affine solution as existing.
