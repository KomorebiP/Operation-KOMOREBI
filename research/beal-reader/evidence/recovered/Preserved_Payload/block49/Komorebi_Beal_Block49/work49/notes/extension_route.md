# Opposite residual extensions and an additional prime in C

Base checkpoint: frozen Block48 archive
`bbf78879d4b5714c818dd1521053dcd6b80c0694799b120b440fa850efec091a`.
Owner: Block49 extension route. No Block48 file is modified.

Status: written proof with primary-source inputs checked. Fresh independent
review is recorded separately in `extension_audit.md`. This is a necessary
condition on the remaining branch, not a proof of the (3,5,7) equation.

## Target and conclusion

Let positive pairwise-coprime integers satisfy A^3+B^5=C^7 and assume 3990|C.
Put K=Q(sqrt(5)), let J be the Jacobian of

    y^2+(x^3+B)y=2Bx^3+3Ax+B^2,

and let nu be the even quadratic character of
Q(zeta_15)^+/K identified in Block48. Write rho for its rank-two RM seven-adic
Tate representation over E=Q_7(sqrt(5)), chi_7 for the seven-adic cyclotomic
character, and chi for its reduction in k=F_49.

The additional restriction is

    some rational prime q|C satisfies q mod 35 in {1,8,13,22,27,29}.

All these primes are outside {2,3,5,7,19}. Equivalently, at least one prime
v of K over a rational prime dividing C has Nv=1 modulo7. In particular,
the set of prime divisors of C cannot be exactly {2,3,5,7,19}.

This is an existence condition on a new prime, not divisibility by one fixed
new prime. It is strictly weaker than excluding the entire 3990|C branch.

## 1. The residual characters and the lattice issue

Block48 `solution_divisibility_corollary.md` implies that a primitive solution
with 15|C has absolutely reducible residual RM representation. The character
classification in `character_sieve.md`, together with det(rho)=chi_7 from
`level_lowering.md`, identifies its semisimplification as

    bar(rho)^ss = nu + chi nu.

Set V=rho tensor nu, using the characteristic-zero quadratic lift. Its residual
semisimplification is 1+chi. These two characters are distinct globally, and
are already distinct on inertia at seven.

An arbitrary new stable lattice in V need not retain unramified residual
inertia at variable primes q|C. Nor does finite flatness of the Jacobian's
J[7] imply finite flatness after every lattice change. Thus it is invalid to
apply Ribet's lemma and then simply import the original residual local
conditions. The argument below works with characteristic-zero local sublines,
which do survive every stable-lattice change, and explicitly leaves Nv=1
primes as possible ramification places.

## 2. Characteristic-zero absolute irreducibility

Faltings's semisimplicity theorem makes the Q_7 Tate representation of J
semisimple. Scalar extension in characteristic zero preserves semisimplicity;
the rank-two RM factors, and their quadratic twists, are therefore absolutely
semisimple.

At the prime above three, 3|C and the inherited potential-multiplicative
local type has nonzero Weil--Deligne monodromy. After the quadratic extension
that gives semistable reduction, a prime-to-three Tate module therefore has
a nonidentity unipotent inertia element. The rank-two RM factor has monodromy
rank one: the full four-dimensional module has toric rank two and its
coefficient-field dimension is two. The quadratic twist changes neither the
rank nor the nonzero nature of this monodromy.

If V were reducible over an algebraic coefficient extension, absolute
semisimplicity would make it the direct sum of two characters. Such a direct
sum cannot contain a nonidentity unipotent element. Hence V is absolutely
irreducible. This uses characteristic-zero semisimplicity and monodromy at
three, not residual irreducibility, finite flatness, or residual level
lowering.

## 3. Ribet's lemma with the opposite orientation

Apply Ophir--Weiss, arXiv:2111.01559v3, Theorem1.3, with n=1 and the distinct
characters chi_1=chi, chi_2=1. Their m=0 and s=1. It supplies a stable lattice
Lambda whose reduction W is a nonsplit extension

    0 -> k -> W -> k(chi) -> 0.                       (R)

The extension class e is nonzero in H^1(K,k(chi^-1)). No prescribed local
conditions are part of Ribet's lemma. They must be proved separately for W.

## 4. A local splitting lemma that is invariant under lattice changes

Suppose a two-dimensional characteristic-zero local representation has a
G-stable line with character alpha, whose reduction is chi, and quotient
reducing to1. Intersect that line with any stable lattice. The intersection
is saturated, because the quotient embeds in the characteristic-zero
one-dimensional quotient space. Its reduction therefore gives a nonzero
chi-subline of W.

If chi is nontrivial on the local decomposition group, this line is distinct
from the global1-subline in(R). Their direct sum is W, so(R) splits locally.
This does not assert splitting if chi=1 locally. That omitted case is exactly
the surviving source of extension ramification.

At seven, Block48's canonical toric sequence has characteristic-zero
characters chi_7 psi below and psi above, where psi is the unramified
quadratic character. Block48 also identifies nu|G_K7=psi. After twisting,
the local sequence has chi_7 below and1 above. Since chi on inertia has
order 6, the splitting lemma shows e|G_K7=0 for the Ribet lattice, without any
finite-flat assumption on that lattice.

At v over q|C, q outside {2,3,5,7}, the normalized nodal reduction is

    (X^2+X-1)^2 (X^2-2X+5).

Both nodes are K_v-rational. Their branch radicands are
3(5+sqrt(5))/2 and3(5-sqrt(5))/2, whose ratio is a square in K. Thus their
common torus character is precisely nu|G_Kv, as proved in Block48's character
sieve. The local characteristic-zero toric sequence after twisting again has
chi_7 below and1 above. If Nv!=1 mod 7, chi is locally nontrivial and e splits.
The same conclusion holds above 2 from the inherited even-C torus calculation:
its character equals nu, and N(2)=4!=1 mod 7.

## 5. The primes three and five

For a non-seven local field F with residue cardinalityQ and M=k(chi^-1),
chi is unramified. The wild inertia group is pro-ell with ell!=7, hence has
no nonzero continuous maps to the additive7-group M. The relevant tame
inertia quotient is Z_7(1).

For arithmetic Frobenius F and a tame generator tau,
F tau F^-1=tau^Q. If c is an extension cocycle, its restriction to inertia
can be nonzero only when chi^-1(F)=Q in k. Since chi(F)=Q, this requires
Q^2=1 mod 7. The unramified cohomology is M/(F-1)M, which is zero whenQ!=1.
Consequently

    Q notin {1,-1} mod 7  =>  H^1(F,k(chi^-1))=0.

For K_(3), Q=9=2 mod 7; for K_(sqrt5), Q=5 mod 7. Both local classes vanish.
This proves the needed local property even though the original Jacobian
lattice can have nonzero upper-triangular unipotent inertia after the twist.

## 6. Restriction to the cyclotomic field

Assume for contradiction that no primev overC has Nv=1 mod 7. Then(R) is
split at seven and at every bad finite prime. At every remaining finite
prime, the characteristic-zero representation is unramified (J has good
reduction and nu is unramified), so every lattice, including Lambda, is
unramified there. Thus e restricts to an everywhere-unramified class over

    L=K(zeta_7),      [L:K]=6.

On G_L the coefficient character is trivial. Inflation--restriction is
injective on H^1(K,k(chi^-1)) because 6 is invertible in k. A nonzero e would
therefore give a nonzero continuous homomorphism G_L -> (k,+), unramified
at every finite prime. Since L is totally imaginary, there is no additional
real-place ramification. Class field theory turns such a homomorphism into
a nonzero quotient of the7-primary ideal class group ofL.

Let M=Q(zeta_35). Then L is a subfield ofM and[M:L]=2. Masley's 1976 Main Theorem gives h(M)=1: phi(35)=24 and 35 is absent
from the displayed exceptional table on printed page 179. Extension followed by norm on ideal
classes is multiplication by2. Therefore Cl(L)[7^infty]=0: an element whose
extension is principal has square trivial, which kills no nonzero7-class.
This contradicts the nonzero restriction of e.

The conclusion is that at least one primev over a divisor ofC satisfies
Nv=1 mod 7.

## 7. Translation to rational residue classes

For q outside {5,7}, q splits in K iff q mod5 is1 or4. In that case Nv=q, so
q must be1 mod 7. If q mod5 is2 or3, it is inert andNv=q^2, so q can be1 or-1
mod 7. The Chinese remainder theorem gives exactly

    q mod 35 in {1,8,13,22,27,29}.

None of 2,3,5,7,19 meets this condition. The smallest possible new prime is13;
29 is the smallest split example. These are examples of eligible primes,
not claims that either must divideC.

## 8. Where the attempted complete contradiction fails

At Nv=1 mod 7, the two residual toric characters coincide locally. A global
1-subline and the local cyclotomic subline need not be different modulo7.
Ribet's lattice change can therefore expose residual inertia at that prime.
Neither monodromy divisibility in the original lattice nor finite-flatness
at seven prevents this. The class-field obstruction then involves a ray
class group ramified at those primes, not the ordinary class group. The
class-number-one input no longer forces that ray class group to vanish.

A complete elimination would require additional control of the selected
lattice or of those ray-class extension classes. This route does not supply
that control, and no reducible level-lowering theorem has been assumed.

## Primary sources and review boundary

- Ophir--Weiss, *On Ribet's Lemma for GL2 modulo prime powers*,
  arXiv:2111.01559v3 (1 February 2024), Theorem 1.3 and section 4.1.
  [Versioned manuscript](https://arxiv.org/pdf/2111.01559v3).
  Its Theorem 1.3 says an extension of chi_1 by chi_2, so the choice
  chi_1=chi, chi_2=1 gives exactly the orientation in (R).
- Faltings, *Die Vermutungen von Tate und Mordell*, Jahresbericht DMV
  86 (1984), 1--13. His own exposition states Tate-module semisimplicity
  on printed page 5, explains the arbitrary-number-field scope on page 8,
  and uses the established semisimplicity again on page 10.
  [Author's published exposition](https://www.mathematik.de/images/DMV/Jahresberichte/Jahresberichte_Archiv/JB_DMV_086_1.pdf).
  This is the checked primary source for the theorem, not a claim that the
  original 1983 proof has been reverified in this block. The retained scan
  contains damaged lower portions on some pages; the cited semisimplicity
  statement and number-field sentences are legible and were inspected.
- Masley, *Solution of small class number problems for cyclotomic fields*,
  Compositio Mathematica 33 (1976), 179--186. Main Theorem, printed
  pages 179 and 184; the complete table on page 179 was visually inspected.
  It lists m=39,56,23,52,72,120,51,80,63,29,68,31,57,96,55 as exceptions
  with class numbers 2 through 10. Since phi(35)=24 and 35 is absent,
  h(Q(zeta_35))=1. The norm/extension argument is also explicit in the
  proof of Lemma 1, page 180.
  [Primary article](https://www.numdam.org/article/CM_1976__33_2_179_0.pdf).
- Local geometric inputs are inherited frozen Block48 written proofs,
  not new source-independent or Lean-formalized theorems.

Exact source-byte hashes, successful locators, and failed retrievals are in
`../source_records/extension_sources.json`. No novelty claim is made. The
search was limited to the exact Ribet lemma, semisimplicity input, and the
class-number input. A companion, separately reviewed statement in
`extension_selmer_sharpness.md` computes the surviving abstract extension
space when eligible primes are present.
