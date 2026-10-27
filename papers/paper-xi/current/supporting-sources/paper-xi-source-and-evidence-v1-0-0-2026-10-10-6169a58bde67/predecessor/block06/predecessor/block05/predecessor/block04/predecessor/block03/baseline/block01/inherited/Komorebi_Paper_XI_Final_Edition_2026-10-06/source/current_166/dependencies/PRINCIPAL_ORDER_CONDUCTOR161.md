# A conductor test that separates the new arithmetic constructions

Base160, SHA256
`04cce97a4909a859b8463bc98266e93e8bb2345fb48d0890c98b359687b62068`.
Ordinary proof using a locally retained primary source already checked in158.
This evaluates an existing arithmetic invariant. It adds no new factor
hypothesis and proves no local-factor identity beyond the displayed exponent.

## Proposition: general principal-order grade count

Let F have residue size q. Fix psi_F trivial on p_F and nontrivial on O_F.
Let A be a principal hereditary order in End_F(V), with dim_F V=n and
O_F-period e. Its successive lattice quotients all have k_F-dimension
d=n/e. Let P be its radical and let [A,r,0,beta] be a positive-level
simple stratum, r>=1. If a smooth irreducible representation pi of GL_n(F)
contains a central type belonging to this stratum, then

    f(pi,psi_F)=n*r/e,     a(pi)=n+n*r/e.                    (1)

Here f is the exponent in

    epsilon(pi,s,psi_F)=q^(f*(1/2-s))*epsilon(pi,1/2,psi_F),

and a is the ordinary conductor exponent. No restriction on the
characteristic of F or on the ramification of F[beta]/F is imposed.

**Proof.** In a basis adapted to the principal chain, each radical grade
P^j/P^(j+1) consists of e cyclic matrix blocks of size d by d over k_F.
It therefore has dimension e*d^2=n^2/e, for every integer j. Taking r
successive grades gives

    [P^(-r):A]=q^(r*n^2/e).                                 (2)

Bushnell--Henniart1999, Section6.1 Lemma2, gives

    epsilon(pi,s,psi_F)
      =[P^(-r):A]^((1/2-s)/n)*C(Lambda,beta,psi_F),           (3)

where C is independent of s. Its value is nonzero because the local
constant is nonzero. Substitute (2) in (3) and compare exponents. In this
additive-character convention f=a-n, proving (1).

This proof does not assume that beta is minimal, that F[beta] is totally
ramified, or that the finite Heisenberg quotient has any particular size.
It also shows that changing the noncompact extension scalar leaves (1)
unchanged. The residue factor does not change the exponent while the same
positive-level central type remains contained.

For a source of rank n and positive Swan exponent w with no inertia-fixed
vectors (in particular an irreducible wild source), equality of these
existing conductor exponents forces

    r=e*w/n in Z,     n/gcd(n,w) divides e,     e divides n.  (4)

The middle equivalence follows by dividing n and w by their greatest
common divisor. Thus the source already gives a necessary choice of
hereditary-order period, before any finite packet is placed in a host.
This is a necessary arithmetic design condition, not an existence theorem
for a stratum at each permitted period.

## Consequence: the maximal-order unramified route misses the original source

The construction160 unramified tower uses the maximal order
End_{O_F}(O_{E_s}^m), so e=1. Its leading native level N_1 is a positive
integer. Every resulting completion therefore satisfies

    f(pi,psi_F)=n*N_1.

The ORIGINAL actual rank-nine two-cubic Weil source over F_3((t)) has
Swan24 and ordinary conductor33. This was proved from its actual upper
ramification groups and the two unequal slopes in158, independently of LLC.
Thus no positive-level maximal-order unramified tower in160 at rank nine
can match this source's conductor: 9*N_1 cannot equal24.
Formula (4) says more concretely that the possible principal periods are
3 and9, with necessary leading levels8 and24 respectively. Period1 is
excluded before computing any finite bridge.

In particular the depth-two host of ALL_RANK_ORIGINAL_INPUT_PLACEMENT161
has f=18 and a=27. Its full finite character attachment cannot change
those invariants to24 and33. Increasing its integer depth cannot fix the
divisibility failure. This is a failure of that arithmetic family for this
source, not a failure of its finite placement theorem and not a refutation
of original16.2. It does not affect the valid compatible-family theorem160.

## Consequence: the new noncommuting original-parameter construction passes

The construction in
`../wildtower161/ORIGINAL_CUBIC_NONCOMMUTING_ASSEMBLY161.md` has an actual
rank-nine principal order of period3 and the actual leading level8. The
parameter is the sum of the original level-eight parameter and a conjugate
of the original level-four parameter. Its final parameter field has
ramification degree3 and residue degree3; its critical exponent is -4.
The order period and leading level, not the critical exponent, enter (1).

Consequently every completion containing its positive-level central type
satisfies

    f(pi_new,psi_F)=9*8/3=24,
    a(pi_new)=33.

These equal the original source's Swan and ordinary conductor. This is a
necessary arithmetic test passed by the new construction. It proves no
equality of root numbers, twist factors, prescribed native cyclic actions,
or complete H5 profiles. The original source and this actual candidate
still require their stated finite-data and normalization attachment.
Moreover, the companion `UNRAMIFIED_SELF_TWIST_OBSTRUCTION161.md` proves
that the new field's residue degree3 gives this candidate a nontrivial
unramified self twist absent from the original source. Thus the necessary
conductor test does pass, but this particular field cannot produce the
source's correspondence atom. The construction must change its arithmetic
field as well as retain the correct conductor.

## Primary source extraction and exact translation

Colin J. Bushnell and Guy Henniart, *Local tame lifting for GL(n) II:
wildly ramified supercuspidals*, Astérisque254 (1999), Section6.1, printed
pp53--54, Lemma2. Stable publication:
https://www.numdam.org/item/AST_1999__254__R3_0/ .

The project-authorized full text is
`scratch158/information158/input_cache/BH1999_source.txt`, SHA256
`84249a1539dc76fb8714ada93777c0899468679832932e0f566ed092d471f26f`.
The retained printed54 image is separately pinned. The Section6.1 opening
expressly assumes a principal order and positive native level, with no
assumption on the field extension. Its Lemma2 applies to any irreducible
smooth pi containing the central type. These paragraphs and the formula
were reread for this note.

| Primary-source symbol | This note |
| --- | --- |
| dim_F V | n |
| n in the simple stratum [A,n,0,beta] | r |
| (P^(-n):A) | q^(r*n^2/e) |
| sole s-dependent factor raised to 1/dim V | q^((n*r/e)*(1/2-s)) |
| additive character trivial on p_F, nontrivial on O_F | psi_F; f=a-n |

The distinction between native level r and critical exponent -k0 is
essential: the new example uses r=8 although -k0=4. Replacing r by4 would
give an erroneous exponent12. Classification: a direct grade-count
corollary of the published formula, with a new application to the actual
construction161. This is not a new local-factor theorem. No computation
or Lean verification was run or claimed.
