# Local inertia forces the primes three and five into C

Status: written proof with primary-source verification of the
potential-good-reduction and Neron–Ogg–Shafarevich inputs. A fresh audit is
recorded separately. This is not a Lean theorem or a proof of integer
nonexistence.

## Statement and retained arithmetic contract

Let A,B,C be positive pairwise-coprime integers satisfying A^3+B^5=C^7,
let K=Q(sqrt(5)), and let J be the Jacobian of

    y^2+(x^3+B)y=2Bx^3+3Ax+B^2.

Use the rank-two residual RM representation at seven from the preceding
blocks. The canonical Block-47 theorem already forces 14 dividing C in
any hypothetically reducible case, so the even-C hypothesis of the
character calculation is satisfied. The character classification and pairing argument in
`character_sieve.md` prove that hypothetical absolute reducibility forces

    J[7]^ss = nu + nu + chi*nu + chi*nu,

where plus denotes direct sum, chi is the mod-seven cyclotomic character,
and nu is the quadratic character of Q(zeta_15)^+/K. In particular nu
takes values in {+1,-1}. This is the only global character input below.

We prove that reducibility forces both 3 and 5 to divide C. Combining with the
canonical Block-47 theorem and the prime-19 character sieve gives

    reducibility implies 3990 divides C,

equivalently absolute irreducibility whenever 3990 does not divide C.
This is a statement about an attached representation, not nonexistence
of integer solutions.

## A scalar-inertia lemma for an abelian surface

Let F be a finite extension of Q_p with p outside {2,7}. Let D/F be an
abelian surface with potentially good reduction. Suppose the four
composition factors of D[7] restricted to inertia are copies of one
quadratic character epsilon, with values in {+1,-1}. Assume epsilon is
the restriction of a quadratic character of G_F. Then D[2] is unramified.

Indeed, potential good reduction implies that the image H of inertia on
T7(D) is finite. Its order is prime to seven. Otherwise Cauchy's theorem
would give an element of order seven in GL4(Q7). Such an element needs a
nontrivial seventh root of unity as an eigenvalue, whose minimal
polynomial over Q7 is Phi_7 of degree six. The polynomial
Phi_7(X+1) is Eisenstein at seven, so this cannot occur in dimension four.

By Maschke's theorem the action of H on D[7] is semisimple. Restricting a
global composition series is still an exact filtration on inertia. Hence
the assumed four composition factors imply that every inertia element
acts on D[7] as epsilon(sigma) times the identity. There is no assertion
here that arbitrary global semisimplification preserves local extensions;
semisimplicity follows from the specific finite group H of order prime
to seven.

Every eigenvalue of an element h of H is a root of unity of order prime
to seven. Such roots reduce injectively in characteristic seven. As all
four reductions equal epsilon(h), all four characteristic-zero
eigenvalues equal that same sign. A finite-order matrix in characteristic
zero is diagonalizable, so h=epsilon(h) I4. Thus the entire T7(D) inertia
action is the quadratic scalar epsilon.

Twist D by epsilon through its central automorphism [-1]. The twisted
abelian variety D^epsilon has unramified T7. The Neron–Ogg–Shafarevich
criterion therefore gives good reduction of D^epsilon. Consequently its
2-torsion is unramified. Quadratic twisting through [-1] leaves the
2-torsion representation unchanged, since [-1] acts identically there.
This proves the lemma without assuming prime independence of a chosen
inertia matrix or transferring a sign from T7 directly to T2.

For the application, p=3 or 5, D=J over the appropriate completion, and
epsilon is the restriction of the characteristic-zero quadratic lift of
nu. The cyclotomic character chi is unramified at p, so all four residual
inertia factors are precisely nu. The chosen global quadratic character
supplies the twist required in the lemma.

The exact Neron–Ogg–Shafarevich input is Theorem 2.2, printed p.3, in
Gyujin Oh, *A proof of Neron–Ogg–Shafarevich criterion via its archimedean
analogue*, arXiv:2302.13255v1, 26 February 2023. It applies to any abelian
variety over a finite extension of Q_p and any Tate prime different from
p. The [PDF](https://arxiv.org/pdf/2302.13255) was read with its v1 header;
Section 4 proves the general assertion. Both uses here satisfy these
hypotheses.

## From unramified two-torsion to unramified roots

Completing the square gives the monic sextic

    F(X)=X^6+10BX^3+12AX+5B^2,
    disc(F)=2^12 3^6 5^5 C^14.

The exact discriminant identity is the predecessor's proved polynomial
identity. Its roots are the six finite Weierstrass branch points.

For a genus-two curve given by a separable sextic in characteristic zero,
the action on these six points is faithful on its Jacobian's 2-torsion.
One explicit explanation is that the fifteen nonzero 2-torsion points
correspond to the fifteen unordered pairs of distinct Weierstrass points.
For a pair {Wi,Wj}, the class is Wi+Wj-D, where D is a hyperelliptic fiber
divisor of degree two. Twice this class is principal. It is nonzero and
different for distinct pairs: distinct linearly equivalent effective
divisors of degree two on a genus-two curve belong to its unique degree-
two pencil, whereas a pair of distinct Weierstrass points is not a fiber
of the hyperelliptic map. Thus the fifteen classes are all distinct and
exhaust the nonzero 2-torsion. A permutation of six points fixing every
unordered pair is the identity.

Therefore unramified J[2] implies that all six roots of F lie in the
maximal unramified extension of the local base field.

Here is the elementary discriminant consequence. Normalize the valuation
of the base field so that its value group is Z. A monic integral sextic
whose six roots are unramified has integral roots with integral-valued
differences. If its reduction has distinct roots of multiplicities
n1,...,nr, each pair of roots with the same reduction has difference of
valuation at least one. The product formula for the discriminant gives

    v(disc(F)) >= sum_i ni(ni-1).

No assertion of semistable reduction or cluster-theory classification is
needed for this inequality.

## Potential good reduction at five when 5 does not divide C

The model is isomorphic over Q to the source family

    C^+_(5,3)(t): Y^2=5x^6-12x^5+10t x^3+t^2,
    t=-B^5/A^3,

as explicitly proved in the predecessor. Thus t-1=-C^7/A^3.

If 5 does not divide A, then v5(t-1)=0. Proposition 7.4 of
[Pacetti–Villagra Torcomian, arXiv:2512.17845v1](https://arxiv.org/html/2512.17845v1#S7.SS1)
gives potentially good reduction at five, with no further condition at
this prime. This applies whether or not five divides B.

If 5 divides A, primitivity gives 5 not dividing B. Potential good
reduction is visible directly. Adjoin pi with pi^6=5, and put
X=pi U and Z=pi^3 V in Z^2=F(X). The equation becomes

    V^2=U^6+2B pi^3 U^3+(12A pi/5)U+B^2.

All coefficients are integral. The two middle coefficients have positive
valuation, because v5(A)>=1. The special fiber is

    V^2=U^6+Bbar^2

in characteristic five. Its sextic is separable: its derivative is U^5
and its constant term is nonzero. Its two points at infinity are smooth.
This is a smooth proper genus-two model after a finite extension, proving
potential good reduction of J. The extension need not be minimal.

## The contradiction at five

Assume five does not divide C and the residual RM representation is
reducible. The preceding section and the scalar-inertia lemma imply that
all roots of F are unramified over K_(sqrt(5)). Normalize v(sqrt(5))=1,
so v(5)=2. The discriminant identity gives

    v(disc(F))=10.

Modulo the uniformizer the sextic becomes

    Fbar(X)=X^6+2Abar X.

If five divides A this is X^6, with one root of multiplicity six. The
unramified-root inequality requires discriminant valuation at least 30.
If five does not divide A, then over the residue field F5,

    Fbar(X)=X(X+2Abar)^5.

Its two distinct roots have multiplicities one and five, giving the lower
bound 20. Either bound contradicts 10. Therefore reducibility forces

    5 divides C.

## Potential good reduction at three when 3 does not divide C

If three does not divide A, again v3(t-1)=0. When three also does not
divide B, v3(17t+108)=0. When three divides B, v3(t)=5v3(B)>=5, and hence
v3(17t+108)=3. Proposition 7.4 applies in both cases, since its extra
three-adic requirement is v3(17t+108)<=3.

When three divides A, primitivity gives three not dividing BC and
m=v3(t)=-3v3(A)<=-3. The proposition as stated does not directly apply:
v3(t-1)=m, not zero. This case must be supplied separately, and is not
hidden inside its hypotheses.

For this missing case, use Liu's Theorem 1, cases (V*) and (V), printed
p.204, with the invariant formulas displayed in the proof of PV
Proposition 7.4. In residue characteristic three set I6=J6. The five
rational quantities and their valuations are

| Quantity | valuation at three |
|---|---:|
| I4^3/I6^2 | 12 |
| J10^3/I6^5 | 18 |
| I12^3/I6^6 | 33 |
| I4^9/(J10^3 I6) | 18 |
| I12^3/(J10^3 I6) | 15 |

Here I4=J2^2-24J4 and
I12=-8J4^3+9J2J4J6-27J6^2-J2^2J8, exactly as defined in Liu's equation
(2), printed p.203. Equivalently, using the expanded ratios in PV, their
valuations are

    12,18,33,18,15.

Indeed v3(t-1)=v3(17t+108)=m, while v3(9t+16)=m+2. Substituting these in
the five displayed ratios gives the listed constants, independently of
A and B. The first three are strictly positive and the last two are
nonnegative. The first three inequalities are Liu's (V*) and give two
irreducible components meeting in one point. The last two are (V) and
make both components smooth. They are elliptic by arithmetic genus and
stability. Thus this is stable reduction of compact type, and its
Jacobian has good reduction after extension. This proves potential good
reduction for every three-not-dividing-C branch.

The primary source was checked directly, not through PV's citation:
Qing Liu, *Courbes stables de genre 2 et leur schema de modules*,
Mathematische Annalen 295 (1993), 201–222,
[author-hosted scan](https://www.math.u-bordeaux.fr/~qliu/articles/genre2.pdf).
Theorem 1 on printed p.204 applies to a smooth geometrically connected
genus-two curve over the fraction field of a DVR. Equation (3) explicitly
sets epsilon=3 in residue characteristic three. The scanned definitions
and all five required inequalities were visually read on printed
pp.203–204. The locally downloaded PDF has SHA-256
`602f883d7f3115ce87a9ab2c2050f8002df7c45db951f023ce73149b196b527d`.
Its text layer contains only cover metadata; verification used rendered
page images, not OCR or a search snippet.

## The contradiction at three

Assume three does not divide C and residual reducibility. The
scalar-inertia lemma again makes every
root of F unramified. The prime three is inert in K, so the normalized
valuation still has v(3)=1. The actual discriminant valuation is six.
The reduction is

    Fbar(X)=X^6+Bbar X^3+2Bbar^2.

If three divides B, this is X^6 and gives the impossible discriminant
lower bound 30. If three does not divide B, the identity over F3 is

    Fbar(X)=(X^2+Bbar X+2Bbar^2)^3.

The quadratic inside has discriminant 2Bbar^2, which is nonzero. Over an
algebraic closure its two roots are distinct, each having multiplicity
three in Fbar. Thus the lower bound is 3*2+3*2=12, again exceeding the
actual value six. Therefore reducibility forces three dividing C.

## Audit boundary

All matrix, twisting, root-permutation and discriminant steps above are
written arguments. No new finite point-count table is needed. The prior
discriminant computation is used as an exact polynomial identity.
Potential good reduction at five is fully covered by the source's stated
hypotheses and a direct smooth model. At three, the two nonnegative-t-
valuation cases meet PV Proposition 7.4 exactly; the negative-valuation
case is separately verified using the primary statement of Liu's
criterion and exact valuations.

The initially considered switches to E3^+ modulo five and C5^+ modulo
three are not used in this proof. In particular, no application of PV
Proposition 3.10 with its p,q>3 hypothesis violated is made.
