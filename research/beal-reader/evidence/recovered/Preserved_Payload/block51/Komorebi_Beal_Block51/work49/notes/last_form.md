# The remaining level-(45) form and an explicit CM Jacobian

Status: written proof, with exact finite verification and independently
checked arithmetic sources. The modularity bridge is recorded in
`alt_cm_modularity_source.md`; the fresh independent review is recorded
in `last_form_audit.md`. The resulting restrictions retain the explicit
direct normalized residual-comparison hypothesis.
This file does not claim a proof of the (3,5,7) equation or Beal's conjecture.

## 1. The concrete object

Put K=Q(sqrt(5)) and let D be the smooth projective genus-two curve

    D: Y^2=X^6+324X.

This is the B=0, A=27 member of the completed-square Frey family. It is a
smooth curve, although (27,0,C) is not a positive primitive solution of the
Diophantine equation. The automorphism

    alpha(X,Y)=(zeta_5 X,zeta_5^3 Y)

is defined over E=Q(zeta_5). On the regular differentials dX/Y and X dX/Y it
has eigenvalues zeta_5^3 and zeta_5^4. Together with their complex conjugates
these give all four nontrivial fifth roots. Thus Q[alpha] is the quartic CM
field E, and J_D has CM by E. The Rosati involution sends alpha to alpha^-1.
Consequently alpha+alpha^-1 is self-adjoint and gives RM by K over K: it is
fixed by Gal(E/K). Each real embedding of K occurs once in the CM type, so
the corresponding rank-two system has parallel Hodge type {0,1}.

This establishes actual CM of this Jacobian. It does not infer CM from the
positive flag on an LMFDB page.

## 2. Exact conductor of the RM system over K

At primes away from 2,3,5, the displayed monic sextic has unit discriminant,
so the curve has good reduction. At two use the integral model

    y^2+X^3 y=81X.

Modulo two its affine equation is y^2+X^3y=X. A singular point would satisfy
X^3=0 and X^2y-1=0, impossible. At infinity put u=1/X, v=y/X^3; the equation
is v^2+v=81u^5. At u=0 its derivative in v is one. This supplies smooth
reduction at two.

At three, in the maximal unramified extension adjoin pi with pi^5=3 and
make the change X=pi^4 U, Y=pi^12 V. The equation becomes

    V^2=U^6+4U.

Its reduction in characteristic three is smooth: the derivative of the
right side is one. This is a tame extension of ramification degree five.
A tame inertia generator sends pi to zeta_5 pi, and on the special fiber
acts as (U,V)->(zeta_5 U,zeta_5^3 V), up to inverting the chosen generator.
The four eigenvalues on H^1 are all nontrivial fifth roots. The inertia
image is cyclic of order five, with no invariant vectors. Each rank-two
factor has two inverse nontrivial inertia characters. Since Frobenius at
the K-prime above three conjugates tame inertia by the ninth power, it
interchanges these two characters. The rank-two residual representation
at seven is therefore already absolutely irreducible on this local
decomposition group. Three is
unramified in K. The full four-dimensional conductor exponent is four,
and each RM factor has exponent two. There is no Swan contribution.

At five, first note that -324 belongs to 1+25 Z_5. The fifth-power map
1+5Z_5 -> 1+25Z_5 is surjective, by the convergent 5-adic logarithm. Hence
choose a in Q_5 with a^5=-324 and a congruent to one modulo five. Put
lambda=zeta_5-1, choose pi with pi^2=lambda, and use

    X=a+lambda U,       Y=pi^5 V.

The sextic is X(X^5-a^5). After division by lambda^5 the equation is

    V^2=(a+lambda U)(U^5+(5a/lambda)U^4
                    +(10a^2/lambda^2)U^3
                    +(10a^3/lambda^3)U^2+(5a^4/lambda^4)U).

Since 5/lambda^4 is congruent to -1 modulo lambda, the reduction is

    V^2=U^5-U.

It is smooth in characteristic five. The tame ramification degree over
Q_5 is eight, hence four over K_(sqrt(5)). Over the maximal unramified
base, a tame generator for the latter extension has pi multiplier i and
lambda multiplier -1 on the residue-scaled coordinates. Its action on
the good special fiber is (U,V)->(-U,-iV), up to inversion. Its square is
the hyperelliptic involution. Thus its eigenvalues on H^1 are i and -i,
each twice. There are no inertia invariants and no wild contribution.
Each RM factor again has conductor exponent two.

The resulting exact rank-two conductor is

    (3)^2 (sqrt(5))^2 = (45).

The determinant is cyclotomic by the polarized, totally real GL2-type
determinant theorem already authenticated in Block48, BCDF v5 Theorem 2.8.
The local models above show the full finite inertial types, not just their
conductor exponents.

## 3. Modularity bridge and identification inside the complete level

The arithmetic bridge is source-checked in
`alt_cm_modularity_source.md`. Milne's *Abelian Varieties with Complex
Multiplication (for Pedestrians)*, arXiv:math/9806172v1, statement 15.1
and Theorems 13.1–13.2 give the compatible CM Hecke characters; this is
an explicitly identified restatement of the CM theorem, not a claim to
have inspected its original 1968 proof. Jacquet–Langlands, *Automorphic
Forms on GL(2)*, Proposition 12.1 supplies the quadratic automorphic
induction. Lemma 5.12 and the following calculation identify its weight.

The actual rank-two representation over K restricts over E to two
conjugate character spaces; Gal(E/K) interchanges them. It is induced
from one of the algebraic Hecke characters. The angular infinity type
is nonzero, so that character cannot factor through the norm to K.
The induction is cuspidal and gives parallel weight two. The determinant
above makes its nebentypus trivial, after the explicitly recorded
unitary half-norm normalization. Local-global compatibility makes its
level the conductor (45). Bounded Hecke matching is not used in this
existence step.

Given that bridge, the modular form belongs to the complete fourteen-orbit
level-(45) list retained in Block48. Exact point counts for D over F_11 and
F_121 give

    P_11(T)=T^4-9T^3+41T^2-99T+121.

The trace of a rank-two RM factor therefore satisfies

    Q_11(Z)=Z^2-9Z+19.

Among all fourteen listed orbits, only **2.2.5.1-2025.1-l** has this minimal
polynomial for its eigenvalue at a prime above eleven. Both primes above
eleven are checked, and taking the coefficient conjugate leaves the same
minimal polynomial. Since a form has already been proved to exist in
this finite list, a distinguishing fingerprint suffices. This is not a
claim that agreement at eleven alone proves equality for arbitrary forms.

The exact computation additionally matches all eight odd split good
primes present in the retained twenty-row page: 11,19,29,31,41,59,61,71.
These extra matches are consistency checks. No Sturm bound is invoked.
The crucial q11 point count is independently computed by two finite-field
implementations. The result and pinned source pages are recorded under
`verification/lastform_run/`.

Thus, using the separately sourced modularity bridge, the surviving form is
identified with the RM compatible system of J_D, up to its coefficient
conjugation. Its inducing CM field is rigorously E/K, independently of
both the database CM flag and the ambiguous PV numerical-index labels.

## 4. Local three forces three into B

Assume a primitive positive solution A^3+B^5=C^7 has its residual RM
representation directly congruent to that of the named form l. After the
identification above, its inertia image at three must have an element of
order five, because J_D has the tame cyclic-five type, and reduction
modulo seven preserves that type.

If 3 divides C, the Frey Jacobian is potentially multiplicative at three.
Its inertia is a quadratic scalar times a unipotent group. Modulo seven
its finite image has order with prime factors only two and seven. It
cannot contain an element of order five.

Suppose instead that 3 does not divide C. The Frey Jacobian is potentially
good by the fully covered Block48 argument, including its negative
parameter-valuation case. Its finite inertia image in GL4(Q_7) has order
prime to seven: an element of order seven would require the irreducible
degree-six polynomial Phi_7 in dimension four. Reduction therefore
preserves an order-five inertia element. To compare Tate primes, take a
finite Galois extension over which J has good reduction. The inertia
quotient acts on the good special-fiber abelian variety. Its actions on
all prime-to-three rational Tate modules are faithful: an automorphism
acting trivially on a Tate module is the identity. Thus the same
order-five geometric automorphism acts with order five on T_2. It also
has order five on J[2], since an odd-order finite element cannot die in
the pro-two reduction kernel. This uses a common geometric inertia
action; it does not reduce a Q_7 matrix modulo two.

If 3 does not divide B, the sextic has reduction

    Fbar(X)=(X^2+Bbar X+2Bbar^2)^3.

The quadratic has two distinct roots, so inertia fixes each of two residue
clusters of size three. Its permutation action on the six roots belongs
to S3 x S3 and has no element of order five. The genus-two identification
S6=Sp4(F2), explained explicitly in Block48, makes this action faithful
on J[2]. This is a contradiction. Thus

    3 divides B, and 3 does not divide AC.

The proof uses the actual inertia type and residue clusters. It does not
infer order-five inertia from conductor exponent two alone.

## 5. Local five excludes five dividing C

At five the boundary system has tame inertia of order four, with its
square equal to -I. This remains order four modulo seven. If 5 divides C,
the Frey system is potentially multiplicative. Its residual inertia
matrices are a scalar sign times a unipotent matrix with square-zero
nilpotent part. Each matrix consequently has order dividing 14, and
none has order four. Therefore

    5 does not divide C.

This is a comparison of actual finite groups. The fact that both a tame
order-four representation and a ramified quadratic special representation
can have conductor exponent two does not erase this obstruction.

## 6. Finite-flat comparison at seven

The inherited finite-flat model and full-faithfulness input were
independently reviewed. The passage from an abstract residual
RM constituent to the actual full J[7] needs particular care. Both
systems have coefficient residue field F_49, but we do not assume that
their actual Tate lattices are stable under the maximal RM order.

The rank-two representation of D is absolutely irreducible, as proved
by its local decomposition group at three above. Its Frobenius trace at
eleven has polynomial Z^2-9Z+19, whose discriminant five is nonsquare
modulo seven. That trace is not in F_7, so the representation is not
isomorphic to its coefficient-Frobenius conjugate. Its restriction of
scalars from F_49 to F_7 is therefore an irreducible four-dimensional
representation. Indeed after extension to F_49 it is the sum of two
distinct absolutely irreducible conjugate representations; an F_7
submodule would select a conjugation-stable subset, hence either neither
or both.

Choose an RM-stable lattice in each rational representation. The direct
residual comparison identifies their restrictions of scalars over F_7.
Stable-lattice independence identifies the semisimplification of each
actual J[7] with this simple four-dimensional module. A module with
simple semisimplification is already simple. Thus the actual full Frey
J[7] and D[7] are isomorphic, not only their global semisimplifications.
The usual descent of an isomorphism from the algebraic closure is valid
for these representations over a finite field. Coefficient conjugation
itself is an F_7-linear change of coordinates on the underlying module.
No potentially nonsplit local extension has been discarded.

The local base K_(7) is unramified over Q_7, so its absolute ramification
index one is strictly less than 7-1. The finite-flat generic-fiber functor
is fully faithful in this range. Thus the isomorphism extends to their
finite-flat seven-torsion models.

For D the good-reduction Cartier matrix is the B=0,A=27 specialization of
the actual family matrix

    M=[[0,A^2 B],[A,0]].

It has rank one and square zero. Its Jacobian special fiber has p-rank
zero and a-number one.

The a-number identity used here has been independently source-checked:
Sarah Frei, *The a-number of hyperelliptic curves*, arXiv:1703.03516v2
(26 June 2017), section 2.4, printed p.3, defines
a(J)=dim Hom(alpha_p,J[p]) and gives a(J)=g-rank(Cartier).
The inspected [primary PDF](https://arxiv.org/pdf/1703.03516) has the v2
header; the exact-version URL did not load. Geometric base change to
an algebraic closure of F_7 meets the source hypotheses. The p-rank
identity and actual family Cartier matrix were already authenticated
in Block47.

If 7 divides C, the inherited Block48 model of the Frey J[7], after an
unramified extension splitting the torus, is an extension of an etale
group of rank 7^2 by a multiplicative group of rank 7^2. This follows
from the unit-Kummer construction after removing the seventh-power
valuation part of the periods. Its special fiber has etale rank 7^2.
It cannot be isomorphic to D[7], whose special fiber has etale rank one.
Thus 7 does not divide C.

For good-seven Frey fibers, the Cartier trichotomy is exhaustive:

| Residue branch | p-rank | a-number |
|---|---:|---:|
| A and B both nonzero | 2 | 0 |
| A=0, B nonzero | 0 | 2 |
| A nonzero, B=0 | 0 | 1 |

Both invariants are determined by the seven-torsion special fiber. Only
the last row matches D. Therefore

    7 divides B, and 7 does not divide AC.

This argument uses a finite-flat group-scheme comparison at the residual
prime. It is not an invalid comparison of a good Frobenius trace at
auxiliary prime seven.

## 7. Consequence and exact remaining boundary

Combining the new local-type restrictions with the prior complete-level
calculation gives

    8778 divides B,      gcd(C,210)=1,
    A,C odd,
    (A,C)=(5,9) or (6,2) modulo eleven.

Here 8778=2*3*7*11*19. The gcd statement uses old odd-C and new exclusions
at 3,5,7. The form itself is not excluded. Its exact identification
replaces a heuristic CM flag by a concrete CM Jacobian and turns the
remaining congruence into a specific seven-torsion comparison problem.

The global boundary B=0 does not give an allowed positive primitive
solution. Conversely, no proof has been given that a nonzero B cannot
produce the same residual representation. A finite list of additional
prime divisibilities cannot supply that global rigidity assertion.

## 8. Reproducibility and failures

Run the bounded contract in `computations/lastform_contract.json` with
`computations/lastform_boundary.py`. The archived manifest validates and
pins all fourteen source pages, both point-count implementations, the
parser, and the computation script. Arithmetic is exact throughout.

A public LMFDB genus-two search at conductor 50625 returned the unique
listed curve y^2+y=x^5-1. This curve is related by a quadratic twist to D,
not automatically the same curve or the same Hilbert form. That lookup is
retained only as exploratory evidence and is not used in the proof.
General web searches for a CM-modularity theorem initially returned
mostly irrelevant results. They were not treated as a verification of
the modularity bridge; the independently sourced Milne and
Jacquet–Langlands statements now supply it. No CAPTCHA export was
retried or bypassed.
