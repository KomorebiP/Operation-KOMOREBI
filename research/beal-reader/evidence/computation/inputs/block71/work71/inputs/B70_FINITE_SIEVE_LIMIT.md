# B70.4. A limitation of a fixed homogeneous zero-or-good test family

This theorem concerns an ABSTRACT cohomological necessary system, not actual Frey
representations. It does not imply that Beal is false, that a proof is impossible,
or that new period, integral, conductor, or good-reduction constraints cannot work.

## Precise statement

Let T be any finite set of rational primes ell outside2,3,5,7 with ell=1 mod7.
Fix alpha=(v*w,r,1), v,r inF7*, and any lower bound B. There exists a nonzero class

    gamma in H1(Q,F7(chi^-1)), beta=res_K gamma,

ramified at a finite set S of rational primes outside T and greater than B, such that:
(1) every q in S is inert in K and q=1 mod7;
(2) all three natural Kummer generators phi,3,sqrt5 are locally seventh powers at q;
(3) gamma is locally zero at every ell in T and at2,3,5,7;
(4) consequently all paired trace products at T are zero.

Thus ANY FIXED finite collection of the necessary tests

    one permitted good polynomial OR both trace products zero

has a nonzero abstract larger-conductor survivor if its bad alternatives remain
available. The assertion does not preserve a previously fixed conductor bound,
construct an actual matrix representation, or satisfy all actual geometric data.
Any finite number of additional homogeneous linear character equations can likewise
be accommodated by choosing enough fresh conductor factors. Nonhomogeneous forced
values or a proved prohibition of bad reduction are not covered by this statement.

## Infinitely many common-zero eligible conductor primes

Put M=Q(zeta7) and H=M(3^(1/7),5^(1/7)). H is Galois over Q and H/M has degree a
power of7. The quadratic field K is not contained in M: its ramified prime5 is
not ramified in M. If K were contained in H, KM/M would have degree2 dividing
[H:M], impossible. Hence H and K are linearly disjoint over Q.

There is an element of Gal(HK/Q) acting identically on H and nontrivially on K.
Chebotarev supplies infinitely many primes with this Frobenius, beyond any bound
and outside any specified finite set. Each q is1 mod7, inert in K, and both3 and5
are seventh powers in F_q. At its K-residue field F_(q^2), phi^(q+1)=-1, so phi
has order dividing2(q+1), prime to7. It is therefore a seventh power. Since
(sqrt5)^2=5 and2 is invertible modulo7, sqrt5 is a seventh power too. This proves
that the entire three-generator natural Kummer row is zero for all such primes,
independently of v,r. This use of Chebotarev, not the finite scan, proves infinitude.

## Exact dimension of the available inverse-cyclotomic characters

For completeness, Cl(M)=1. The cyclotomic integral basis and discriminant give
|disc M|=7^5. Minkowski gives a representative norm at most

    (4/pi)^3 * (6!/6^6) * sqrt(7^5)
      < (4/3)^3 * (5/324) *147 =47040/8748 <6.

The residue degrees of2,3,5 in M are3,6,6, respectively, their orders modulo7.
There is no prime ideal of norm2,3,4,5. Consequently the only ideal norm below6
is1, and every ideal class is principal. This is a written classical reduction,
not a class-number inference from the finite vector calculation.

Choose N distinct primes of the preceding common-zero family. Each splits into
six degree-one primes in M. In the modulus containing those primes once, the ray
exact sequence presents the class group as residue units modulo global units,
since Cl(M)=1. The exponent-seven quotient of the residue factors for each rational q is a regular
F7[Gal(M/Q)] module. It has one chi^-1 eigenspace.

Global units have no chi^-1 component modulo seventh powers. For the CM field M,
units modulo roots of unity have trivial complex-conjugation action. The possible
odd7-primary root-of-unity part is mu7 with character chi, not chi^-1. The group
order6 is invertible in F7, so the eigenspace projection is exact. It follows that
the chi^-1 character space for these N conductor primes has dimension N.

Equivariant additive characters on G_M descend to H1(Q,F7(chi^-1)) by
inflation-restriction, since the quotient has order6. The character is unramified
at7 in M; its unique prime there is fixed by Gal(M/Q), forcing its Frobenius value
to be zero in a nontrivial chi^-1 component. Thus it is locally zero at7 after
descent. At2,3,5, unramified H1 is F7/(chi^-1(F)-1), which is zero. Real local
cohomology is zero because2 is invertible. These are statements about classes,
not that an arbitrary cocycle representative takes zero everywhere.

## Killing finitely many test values without killing the class

At a test ell in T, the character is unramified and chi(ell)=1. Requiring its
Frobenius value to vanish is at most one linear condition. Select N>|T| fresh
conductor primes. The evaluation map F7^N -> F7^T has a nonzero kernel. Its
nonzero vector defines a nonzero gamma and beta. No unramified class is hidden:
the residue inertia factors generate the ray group. On the two split K-places
the descended values vanish; at an inert K-place the value is twice zero.
All trace products at T are therefore zero, and the prescribed necessary sieve
accepts the bad alternative at each test. QED.

This does NOT claim that one actual global curve can be bad at all the tests
while satisfying every other requirement. Precisely that extra geometry is not
part of the homogeneous trace system proved insufficient here. The theorem is
about finite fixed test families with unrestricted conductor, not a uniform
failure of adaptive methods or of all finite arithmetic certificates.

## B70.5. An explicit witness against all24 current rows

The executable construction chooses25 common-zero conductor primes greater than3000
in the declared search bound500000. They range from5167 to194167. Its24-by-25
matrix has rank24 and a nonzero kernel vector with21 nonzero inertia coordinates.
Every current test value is zero. Choose alpha=(w,6,1). All natural Kummer rows
on this new support vanish. The separate checker verifies every weighted residue
product, the full matrix, rank, nonzero vector, and cyclotomic-unit relations.

At each nonzero supporting q, the certificate also chooses A=75^-1 modq and a
nonzero residue B0 with B0^5=-A^3. Since q is inert, q=2 or3 mod5, hence
5 is coprime to q-1. A fifth root exists uniquely. Hensel lifts B with C=q.
These are local level-seven period positive controls under the inherited Frey
criterion. They do not make the chosen gamma an actual opposite extension, nor
supply one global integer B or a common integral representation.

The explicit finite example is a check and a counterexample to an overly strong
finite-system vanishing claim. The universal existence statement is the separate
Chebotarev/ray-class proof above. No novelty claim is made.
