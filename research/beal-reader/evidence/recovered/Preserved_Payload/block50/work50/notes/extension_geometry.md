# Polarized RM isogenies and the exact coupling of opposite extensions

Base checkpoint: Block49 archive
`1acc4e1492719cb5456092fead71b30a6054deaf0df7c052b36a3cc0d1d806d1`.
Owner: Block50 extension geometry. Earlier blocks are frozen.

Status: written proofs and an exact counterexample, awaiting fresh review.
The remaining branch of A^3+B^5=C^7 is not eliminated.

## 1. The first geometric test: alternating duality

Let k=F_49 and let V be any two-dimensional k-representation of a group G
whose determinant is the mod-seven cyclotomic character chi, valued in F_7^*.
No semisimplicity is assumed. Choose an isomorphism det(V)=k(chi). The wedge
product gives a perfect alternating pairing

    omega: V x V -> k(chi).

For any nonzero a in k, the formula

    B_a(v,w)=Tr_(k/F7)(a omega(v,w))

is a nondegenerate alternating F_7-valued pairing with multiplier chi.
Nondegeneracy follows because, for v nonzero, omega(v,-) maps onto k and
the field-trace pairing is nondegenerate. Scalar multiplication by every
r in k is self-adjoint:

    B_a(rv,w)=B_a(v,rw).

Consequently every opposite extension constructed in Block49 already has
these alternating duality and self-adjoint RM structures. This statement
is about representation-theoretic structures. It does not assert that
an arbitrary extension is the torsion of an abelian variety.

The canonical map V -> V^vee(chi) also preserves the extension orientation:
if 0 -> 1 -> V -> chi -> 0, its dual twisted by chi is again an extension
of chi by 1. Self-duality does not interchange this with the natural
extension 0 -> chi -> V -> 1 -> 0.

## 2. Principal polarizations do survive the RM lattice moves

Here the geometric hypotheses are explicit. Let A/K be a principally
polarized abelian surface with principal polarization lambda and an action
of O=Z[(1+sqrt(5))/2] that is self-adjoint for lambda. Suppose its seven-adic
Tate module is free of rank two over O tensor Z_7. The latter is the integer
ring of the unramified quadratic extension of Q_7.

Every O/7O-line H in A[7] is maximal isotropic for the Weil pairing induced
by lambda. To see isotropy directly, write H=k v. For a,b in k,

    <av,bv>=<v,ab v>=<ab v,v>=-<v,ab v>.

Since two is invertible, this is zero. H has F_7-dimension two inside the
four-dimensional symplectic space A[7], so it is maximal isotropic.

If H is G_K-stable, it defines a finite subgroup scheme over K and the
quotient pi:A -> B=A/H is a K-isogeny of degree49. Over the algebraic
closure, Dolgachev--Lehavi, arXiv:0710.1298v3, Corollary2.2 gives a principal
polarization lambda_B satisfying

    pi^vee lambda_B pi = 7 lambda.                 (P)

As a homomorphism, lambda_B is uniquely determined by (P): composition
with isogenies is injective on Hom groups. Its Galois conjugates satisfy
the same identity, so it descends to K. No claim that a particular theta
line bundle descends to K is required.

The O action descends because H is O-stable. It remains self-adjoint:
pull the desired identity on B back through pi and pi^vee, and use (P)
and the self-adjoint identity on A. Injectivity of composition by the
isogenies then gives the identity on B.

Iterating, any finite path of G_K-stable adjacent O tensor Z_7 lattices is
realized by a sequence of degree49 K-isogenies through principally polarized
abelian surfaces with self-adjoint O action. At each step, choose the
homothety representative that enlarges the old lattice with quotient
one-dimensional over k, and use the associated subgroup H. The polarization
is multiplied by seven under pullback at each step.

In particular, when these geometric RM hypotheses hold for the starting
Jacobian, the path to an opposite Ribet lattice need not leave the class of
principally polarized RM abelian surfaces. This assertion does not identify
the quotients with members of the original one-parameter Frey family, does
not assert rational theta divisors, and does not realize every abstract
Selmer class geometrically. It rules out only the suggested obstruction
that a lattice reversal must destroy the principal polarization or RM.

## 3. The actual coupling identity includes a character-lifting obstruction

Let O_7 be the unramified quadratic integer ring above seven, with residue
field k=F_49. Suppose a continuous representation of a compact group has,
in one fixed basis, matrices

    rho(g) = [[a(g), b(g)], [7^n c(g), d(g)]],       n>=1,

with entries in O_7, and reductions

    a_bar(g)=chi(g),       d_bar(g)=1.

All a(g),d(g) are units. Modulo7^n, a and d are multiplicative characters,
because their failure to multiply is divisible by7^n. The two reductions,
before and after the lattice change that multiplies upper entries by7^n
and divides lower entries by7^n, have extension cocycles

    alpha(g)=b(g) mod7                 in k(chi),
    beta(g)=c(g)/chi(g) mod7            in k(chi^-1).

The matrix product laws give

    alpha(gh)=alpha(g)+chi(g) alpha(h),
    beta(gh)=beta(g)+chi(g)^(-1) beta(h).

The relevant coefficient sequence has trivial G action:

    0 -> k -> (O_7/7^(n+1))^* -> (O_7/7^n)^* -> 1,

where x maps to1+7^n x in the kernel. Define its connecting class delta
using the multiplicative coboundary

    da(g,h)=a(g)a(h)/a(gh).

From a(gh)=a(g)a(h)+7^n b(g)c(h), reduction modulo7^(n+1) gives

    da(g,h)=1-7^n alpha(g) chi(g)^(-1) beta(h).

Using the usual left-module inhomogeneous cup convention, this proves

    [alpha] cup [beta] = -delta(a mod7^n) in H^2(G,k).       (C)

Thus the two extension classes are coupled, but the coupling need not be
zero. At depth n=1, a mod7 is chi, which has its Teichmuller lift (and in the
geometric application its cyclotomic lift). Hence delta=0 and the cup is
zero. More generally cup-zero holds whenever the diagonal character modulo
7^n lifts to a character modulo7^(n+1).

No bound n=1, and no lifting theorem for that higher diagonal character,
has been proved for the remaining Frey representation. In particular,
replacing a mod7^n by the cyclotomic character merely because their
reductions agree would discard the exact obstruction on the right of (C).

## 4. An exact irreducible compact-group counterexample to automatic cup-zero

All matrices in this section have integer entries, viewed in Z_7. Put

    F = [[1,4],[0,29]],
    N = [[-49,7],[-343,49]],
    T = I+N,
    D = [[2,0],[0,1]].

Let G be the closure of the subgroup generated by F,T,D inside GL_2(Z_7),
and let rho be its tautological representation. Define chi=det(rho) mod7.
Every lower-left entry of rho(g) is divisible by343, because that condition
defines a closed multiplicatively and inversely stable subgroup. It is
exactly divisible by343 for T. All lower-right entries are1 modulo7, and
all upper-left entries reduce tochi. Thus section3 applies with n=3.

There are exact identities

    N^2=0,        F N=29 N,        N F=N,
    F T=(I+29N)F=T^29 F.                         (1)

The representation is absolutely irreducible: N has unique invariant line
ker(N)=span((1,7)), whereas D does not preserve this line. Any common
one-dimensional invariant space for G would have to be that line.

Let P=[[1,0],[7,1]]. Then

    N=P [[0,7],[0,0]] P^(-1),
    F=P [[29,4],[0,1]] P^(-1).

Thus on the subgroup generated by F and T, this is the ordinary local
Tate shape with residue cardinality29 and monodromy parameter7. In
particular, the natural residual inertia is trivial. The local Frobenius
extension is nevertheless nontrivial: modulo7,

    alpha(F)=4,      alpha(T)=0.

At the opposite lattice, obtained by multiplying upper entries by343 and
dividing lower entries by343, the matrices reduce to

    F' mod7=I,       T' mod7=[[1,0],[-1,1]],

so

    beta(F)=0,       beta(T)=-1.

Here chi(F)=chi(T)=1. The cup product is nonzero even after restricting
to the subgroup generated by F and T. Indeed, if this cup were a
coboundary, alpha and beta would be the adjacent upper entries in a
homomorphism to the three-by-three upper unitriangular group U_3(F_7).
Every element of U_3(F_7) has exponent dividing7. Relation (1) would then
force the images of F and T to commute, since29=1 modulo7. Their
commutator instead has central entry

    alpha(F) beta(T)-alpha(T) beta(F)=-4 !=0 mod7.

This is a contradiction. Hence [alpha] cup [beta] is nonzero, and (C)
identifies the missing diagonal lifting obstruction.

The example is an irreducible representation of a compact abstract group,
with determinant character, both extension orientations, and the canonical
alternating pairing. Its displayed two-generator subgroup has the exact
prime-to-seven local tame relation for residue cardinality29. It is not
claimed to be a global Galois representation of K or a Frey Jacobian.
It refutes the proposed general algebraic shortcut, not Beal's conjecture.

## 5. Relation to the natural Kummer class

On the remaining branch the natural Jacobian lattice has the nonsplit
orientation 0 -> chi -> V -> 1 -> 0, established by the nonzero monodromy
at three in Block49. Its extension class belongs to H^1(K,k(1)). The
natural-lattice unramifiedness at two, together with the earlier local
inputs, puts this class in

    span_k([phi],[3],[sqrt(5)]),       phi=(1+sqrt(5))/2.       (K)

Here the notation means the Kummer group K^*/(K^*)^7 tensored with k;
exponents in k are not being applied literally to algebraic numbers.
To prove (K), all valuations away from three,five,seven vanish modulo7
by unramifiedness. The finite-flat unit Kummer condition at seven gives
zero valuation there too. Since K has class number one and unit group
generated by -1 andphi, division by seventh powers leaves precisely the
three stated generators; -1 is already a seventh power. Their independence
follows from the valuations at3 andsqrt(5), followed by the unit assertion.
The coefficients of [3] and [sqrt(5)] are nonzero because the natural
monodromy at those places is nonzero modulo7. Their exact ratio and the
unit coefficient are not determined by separate local choices of bases.

The dyadic input is the exact thickness proof in
`work50/notes/local5_dyadic_thickness.md`, SHA256
`9892dcb1f9ca70c816a375e0b6cfaf4e2927c5a4bb85c3fe06d238958cc2040d`,
accepted by the independent review `work50/notes/local5_dyadic_audit.md`,
SHA256 `244574183afe1eb9d164fea484ad1f514521d6f6ade36c1d4445ca6dd2fcd515`.
It proves that both actual node thicknesses are 7v_2(C), and then uses the
period Kummer extension to establish unramifiedness of the full natural
J[7]. No conclusion about a changed Ribet lattice is inferred from (K).

Combining (K) with (C) produces a specific research obligation: calculate
the natural Kummer class and the higher diagonal lifting obstruction in
compatible global bases. Polarization is already available and the
opposite Selmer space is already known. Neither supplies those missing
quantities automatically.

## 6. Global ray characters do not remove the higher obstruction

The obstruction in (C) is not merely an artifact of an abstract compact
group. There are actual global characters satisfying the presently known
fixed-prime local restrictions and having a nonzero connecting obstruction
at arbitrarily large diagonal depth. This still does not construct the
irreducible two-dimensional Frey representation.

Set q=1504231. Exact integer checks certify that q is prime,

    q=1 mod35,       v_7(q-1)=1,
    t^((q-1)/7)=1 modq for t=2,3,5,7.              (Q)

In particular q splits in K=Q(sqrt(5)). The cyclic group (Z/qZ)^* has a
quotient of order seven. Let t:G_Q -> F_7 be a nonzero character of this
quotient, obtained from the action on the q-th roots of unity. It is
unramified away from q. The power-residue tests in (Q) say precisely that
its Frobenius values at2,3,5,7 are zero; its entire local restrictions at
these primes are therefore zero. Restrict t to G_K. It is still nonzero
on inertia at either prime of K above q, because K_v=Q_q there.

For every n>=2 define the global character

    eta_n(g)=1+7^(n-1)t(g) mod7^n.

This formula is independent of the lift of t(g) to an integer and is
multiplicative. The possible nonzero cross term is divisible by7^n since
2n-2>=n. Thus eta_n is locally trivial at2,3,5,7 and unramified outside the
primes above q. It extends to G_Q, so an additional demand for invariance
under Gal(K/Q) would not exclude it.

Nevertheless eta_n cannot lift to a character with values in
(O_7/7^(n+1))^*. Indeed choose local inertia sigma above q with t(sigma)=1.
Every lift of its value has the form

    u=1+7^(n-1)+7^n z,        z in O_7/7O_7,
    u^7=1+7^n mod7^(n+1) !=1.                    (L)

Every such u has order49. On the other hand any abelian seven-primary
character of G_(K_v)=G_(Q_q) has tame inertia order dividing q-1: the tame
Frobenius relation sends an inertia generator to its q-th power, and an
abelian image makes that action trivial. Wild inertia is pro-q and cannot
supply seven-primary image. Since v_7(q-1)=1, (L) is impossible for a
character lift. Hence delta(eta_n) restricts nontrivially at each prime
above q.

Take a_n=chi_7 eta_n mod7^n, where chi_7 is the actual seven-adic
cyclotomic character. Because chi_7 lifts, delta(a_n)=delta(eta_n) is
nonzero too. The complementary character d_n=eta_n^(-1) has determinant
product chi_7. These two characters agree with the required cyclotomic
and trivial local characters at2,3,5,7. Moreover their trace at a prime
above q agrees modulo7^n with the split toric trace chi_7+1. Indeed
chi_7(g)=1 mod7 for every g in G_(Q_q), and

    chi_7 eta_n+eta_n^(-1)-chi_7-1
       =(eta_n-1)(chi_7 eta_n-1)/eta_n=0 mod7^n.

This construction has all the fixed local character restrictions and the
local toric pseudotrace condition just stated, at every n>=2. It proves
that those restrictions alone give neither a uniform bound on n nor the
vanishing of delta(a_n). It does not prove that these characters occur as
the diagonal characters of an irreducible representation, of a polarized
abelian surface, or of the Frey Jacobian attached to a Diophantine solution.

The precise remaining obstruction is therefore geometric and simultaneous:
for the actual Frey representation one would have to calculate or restrict
its higher diagonal character and its natural Kummer class together, so
that (C), or stronger integral information, contradicts all admissible
opposite extensions. Neither the class-number calculation nor the known
local ray-character conditions currently does this. Merely adding the
cyclotomic lift of the residual character to the argument is insufficient.

## 7. Sources, exact checks, and status

For the quotient polarization, the exact checked source is Dolgachev and
Lehavi, *On isogenous principally polarized abelian surfaces*,
arXiv:0710.1298v3, dated8 March2008, Corollary2.2, printedp3. It assumes
an algebraically closed field and n prime to its characteristic. We apply
it with n=7 in characteristic zero and then give the separate Galois
descent argument above. Its explicit (3,3)-isogeny algorithms are not used.
[Versioned primary manuscript](https://arxiv.org/pdf/0710.1298v3).

The pairing identities, the RM descent calculation, (C), and the compact
matrix counterexample are proved directly here. No unverified deformation
or reducible level-lowering theorem is cited. The exact computation
`extgeo_matrix_checks.py` checks only the displayed matrices, lattice
changes, the finite Heisenberg commutator, and the integer prime/power
checks in (Q). Its finite unit-lift test treats n=2,3,4 over Z/7^(n+1);
the general O_7 statement (L) is proved by the binomial formula above. It does not verify the geometric
source theorem, universal cohomology identities, or any Diophantine claim.

Fresh review and computational provenance are recorded separately. The
outcome of this route is an exact coupling identity, two eliminated
proof shortcuts, and an explicit global character obstruction to the
proposed ray-class repair. The branch3990|C remains open.
