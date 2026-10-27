# Independent audit: reducibility forces 15 dividing C

Verdict: the local argument is valid under the inherited global character
contract. The previously missing potential-good-reduction case at three
is supplied below by a direct cluster calculation and a checked primary
theorem. Thus the conclusion is not conditional on an unverified reading
of Liu's criterion. This proves a condition on reducibility; it does not
prove nonexistence of a primitive solution.

## Scope and reviewed inputs

Let positive pairwise-coprime integers satisfy A^3+B^5=C^7. Put
K=Q(sqrt(5)) and let J be the Jacobian of

    y^2+(x^3+B)y=2Bx^3+3Ax+B^2.

Writing Z=2y+x^3+B gives

    Z^2=f(X),    f(X)=X^6+10BX^3+12AX+5B^2,
    disc(f)=2^12 3^6 5^5 C^14.

The discriminant is the predecessor's exact polynomial identity. The
inherited consequence of hypothetical absolute reducibility is

    J[7]^ss = nu direct-sum nu direct-sum chi*nu direct-sum chi*nu,

where chi is the mod-seven cyclotomic character, and nu is the quadratic character of
Q(zeta_15)^+/K. This is a consequence of the ray-character calculation,
the prime-eleven exclusion and the Weil pairing; it is not a new
assumption about the determinant. Odd C is already excluded under
reducibility by the canonical predecessor theorem.

Final reviewed main-proof snapshot, after its Liu source update:

    work48/notes/reducibility_local_inertia.md
    SHA256 6d7c417e9453fd6aca7635034eb491d8e04f4633410573f3e359d45e67a8afe1

The review below checks its scalar-inertia, twisting, two-torsion and
discriminant arguments independently, and supplies an alternative to its
three-adic source leaf. The primary Liu pages were independently read
after the main proof was updated; see the source addendum below. The
main proof is not edited here.
The relevant current character note has SHA256
80cbeb444c3bfed163022a169ea22e8de76be7c84e1148fc5b78cb1b20628a3a.
The canonical Block-47 note retains the assigned SHA256
fb939ab48ffd726781aabd41328e7a31c594502cc9585c22e7a4df0b4d7448a1.

## Exact source checks

1. Tim and Vladimir Dokchitser, Celine Maistret and Adam Morgan,
   *Arithmetic of hyperelliptic curves over local fields*,
   [arXiv:1808.02936v2](https://arxiv.org/pdf/1808.02936), header dated
   15 October 2018. Theorem 10.3(6), printed p.55, equivalently
   Theorem 1.8(6), says that the Jacobian is potentially good precisely
   when every cluster except the full root set has odd cardinality.
   The setup is a hyperelliptic curve over a local field of odd residue
   characteristic. No prior semistability or tame-root-extension
   assumption is present. Definition 1.1 defines clusters by discs.
   Theorem 10.3's proof applies its preceding inertia description and
   the Neron--Ogg--Shafarevich criterion.

2. Pacetti--Villagra Torcomian,
   [arXiv:2512.17845v1, Proposition 7.4](https://arxiv.org/html/2512.17845v1#S7.SS1),
   printed pp.29--30. Its potentially-good conclusion applies to the
   Jacobian of the family Y^2=5x^6-12x^5+10t x^3+t^2 when v_l(t-1)=0,
   for l=3 or 5, with the additional condition v3(17t+108)<=3 at three.
   We use exactly this stated conclusion, only where these conditions
   hold. Negative v3(t) is handled separately below.

3. Gyujin Oh,
   [arXiv:2302.13255v1, Theorem 2.2](https://arxiv.org/pdf/2302.13255),
   header dated 26 February 2023, printed p.3: for an abelian variety
   over a finite extension of Q_p, good reduction is equivalent to
   trivial inertia on T_l for l distinct from p. The paper supplies a
   proof in Section 4. Both Tate primes used here, 7 and 2, differ
   from the residue primes 3 and 5.

The DDMM primary PDF was downloaded and its actual header checked.
Its authenticated source copy is kept outside the work48 deliverables:

    bytes 1323191
    SHA256 f46f20a4adf8215c566252779a3b4b9028890df36013c7b747fcec2c0313f3a5

The DDMM theorem is about potential good reduction of the Jacobian,
which is exactly what is needed. In the three-adic case below the curve
itself does not have potentially good reduction: its two triple
clusters must not be discarded.

## The source-family identification and the covered branches

Set t=-B^5/A^3. The rational substitution

    x=-B^2/(A X),    Y=B^5 Z/(A^3 X^3)

transforms Y^2=5x^6-12x^5+10t x^3+t^2 into Z^2=f(X).
Indeed multiplication by A^6 X^6/B^10 gives the four terms
5B^2, 12AX, 10BX^3, X^6 respectively. The smooth projective curves
are isomorphic. No unrecorded quadratic twist is involved in this step.

Suppose l is 3 or 5 and l does not divide C. If l does not divide A,
then t-1=-C^7/A^3 is an l-adic unit. At three, if B is also a unit,
17t+108 is a unit; if 3 divides B, v3(t)=5v3(B)>=5, so
v3(17t+108)=3. Thus PV Proposition 7.4 applies to all these branches.
Potential good reduction is preserved by base extension from Q_l to
the completion of K.

## Direct three-adic proof when 3 divides A

Use the rationally normalized valuation v3(3)=1 on an algebraic closure.
Write a=v3(A)>=1. Primitivity gives v3(B)=0. Adjoin sqrt(5), an element
s with s^2=3, and roots alpha_+, alpha_- satisfying

    alpha_+^3=B(-5+2sqrt(5)),
    alpha_-^3=B(-5-2sqrt(5)).

Both centers are units. Their cubes have distinct reductions because
their difference is 4B sqrt(5), a unit; since the cube map is injective
over the algebraic residue field of characteristic three, the centers
also have distinct reductions. Therefore

    v3(alpha_+-alpha_-)=0.

For either center alpha, the polynomial X^6+10BX^3+5B^2 vanishes at
alpha. Expand g_alpha(U)=f(alpha+sU)/s^3. Its coefficients are as follows.

| power | coefficient | valuation or lower bound |
|---:|---|---:|
| 0 | 12A alpha/s^3 | a-1/2 > 0 |
| 1 | 2alpha^2(alpha^3+5B)+4A | 0 |
| 2 | (15alpha^4+30B alpha)/s | >=1/2 |
| 3 | 10(2alpha^3+B) | 0 |
| 4 | 15alpha^2 s | 3/2 |
| 5 | 6alpha s^2 | 2 |
| 6 | s^3 | 3/2 |

The two asserted units follow from

    alpha^3+5B = plus-or-minus 2B sqrt(5),
    2alpha^3+B = -9B plus-or-minus 4B sqrt(5).

Consequently g_alpha is integral and its reduction has the form

    c3 U^3+c1 U,       c1*c3 != 0.

In characteristic three its derivative is the nonzero constant c1.
It has exactly three distinct roots over the algebraic residue field.
After a finite unramified extension of the chosen field of coefficients,
Hensel's lemma lifts these roots to three roots of g_alpha with distinct
reductions. Their corresponding roots of f all lie in the disc
v3(X-alpha)>=1/2, and any two have difference valuation exactly 1/2.

The two center discs are disjoint, so this construction produces all
six roots of f. Between the two groups every difference has valuation
zero. Thus the full cluster picture consists of the top set of six,
its two children of size three, and their singleton children. In
particular there are no hidden clusters of size two: all three pairwise
distances within either triple are equal. Every non-top cluster has odd
size. DDMM Theorem 10.3(6) therefore proves potentially good reduction
of J in this remaining branch.

This is an exact argument for every a>=1, not a valuation sample. It
does not use the Beal relation except for the primitive unit conditions.

## Direct five-adic proof when 5 divides A

Primitivity gives 5 not dividing B. Adjoin pi with pi^6=5 and substitute
X=pi U, Z=pi^3 V. Then

    V^2=U^6+2B pi^3 U^3+(12A pi/5)U+B^2.

For v5(5)=1 the middle coefficient valuations are at least 1/2 and
1/6, respectively. The reduction is V^2=U^6+Bbar^2. Its sextic has
nonzero constant term and derivative U^5 in characteristic five, hence
is separable. At infinity the chart has equation W^2=1+terms divisible
by the inverse coordinate; W=+1 and W=-1 are smooth. The usual two
hyperelliptic charts therefore give a smooth proper genus-two model.
This proves potentially good reduction of J after a finite extension.

Together with the previous covered branches, J is potentially good at
each prime above l whenever l is 3 or 5 and l does not divide C.

## Independent verification of the scalar-inertia implication

Let D be an abelian surface over a finite extension F of Q_p, p in
{3,5}, with potentially good reduction. Suppose D[7] has four inertia
composition factors equal to the restriction of a quadratic character
epsilon of G_F. The image H of inertia in GL(T7(D)) is finite: an
extension giving good reduction kills an open subgroup of inertia.

The order of H is prime to seven. If it were divisible by seven,
Cauchy's theorem would supply an element of order seven in GL4(Q7).
Its nontrivial eigenvalue would have minimal polynomial Phi_7 of degree
six over Q7, since Phi_7(X+1) is Eisenstein. This contradicts dimension
four.

The reduction of the H-action is semisimple by Maschke's theorem. A
composition filtration with four scalar epsilon factors then splits,
so every inertia element reduces to epsilon times the identity. This
justifies restriction from the global semisimplification: no unsupported
claim that local extension classes vanish under restriction is used.

Each eigenvalue of h in H is a root of unity of order prime to seven.
Reduction is injective on those roots of unity, so if its reduction is
epsilon in {+1,-1}, the eigenvalue itself is that same sign. A finite
order matrix in characteristic zero is diagonalizable; hence h is
exactly the scalar epsilon I4.

Twist D by the given quadratic character through [-1]. Its T7 is now
unramified, so NOS gives good reduction of the twist. Applying the
good-reduction implication of NOS at Tate prime two makes its T2, and
therefore its 2-torsion, unramified. Since [-1] acts trivially on
D[2], twisting has left the 2-torsion Galois module unchanged. It
follows that D[2] is unramified. This step does not transfer a matrix
between unrelated Tate-module bases.

For J, chi is unramified at 3 and 5. The inherited global character
decomposition therefore gives exactly the four required local factors;
the quadratic extension defining nu supplies epsilon on all of G_F.

## Root faithfulness and the exact discriminant contradictions

For a separable sextic genus-two curve the 2-torsion is the space of
even subsets of the six Weierstrass points, modulo complementation.
Its fifteen nonzero classes have unique representatives of cardinality
two. Therefore a permutation acting trivially on J[2] fixes every
two-element subset, and hence each of the six points. One can check
the subset model directly by assigning {Wi,Wj} to Wi+Wj-D, where D
is a hyperelliptic fiber; uniqueness follows from the unique degree-two
pencil of a genus-two curve. Thus unramified J[2] implies all roots
of the displayed sextic are unramified over F.

Normalize the base-field valuation to have value group Z. Every root
of the monic integral f is integral. If all roots are unramified,
all root differences have integral valuation. In a residue cluster of
multiplicity n, each of the n(n-1)/2 pair differences has valuation at
least one. The discriminant identity then gives the universal bound

    v(disc(f)) >= sum n(n-1),

summed over the distinct roots of the reduced polynomial. This bound
needs no stable-model hypothesis.

At the inert prime three of K, v(3)=1. If 3 does not divide C,
the actual discriminant valuation is 6. When 3 divides B, the reduced
sextic is X^6, so unramified roots would require valuation at least 30.
When B is a unit, the reduction is

    X^6+Bbar X^3+2Bbar^2=(X^2+Bbar X+2Bbar^2)^3.

The quadratic discriminant is 2Bbar^2, nonzero in characteristic three.
Thus there are two residue roots of multiplicity three, forcing
valuation at least 12. Both alternatives contradict 6.

At the ramified prime above five of K, v(sqrt(5))=1 and v(5)=2. If
5 does not divide C, the actual discriminant valuation is 10. The
reduced sextic is X^6+2Abar X. For Abar=0 it is X^6 and the bound
is 30. Otherwise, since Abar belongs to F5,

    X^6+2Abar X=X(X+2Abar)^5,

with distinct roots of multiplicities one and five; the bound is 20.
Again both alternatives contradict the actual valuation.

## Accepted conclusion and remaining scope

Under hypothetical absolute reducibility, the scalar-inertia lemma and
potential good reduction force the impossible unramified-root bounds
unless both 3 and 5 divide C. Therefore

    absolute reducibility implies 15 divides C.

The already audited character sieve and canonical predecessor force
266 dividing C under the same hypothesis. Since gcd(15,266)=1, the
combined conclusion is

    absolute reducibility implies 3990 divides C,

or absolute irreducibility whenever 3990 does not divide C. All
new local branches are covered. No claim of irreducibility when 3990
divides C, and no integer-solution exclusion, follows from this audit
alone. Combining with any modular elimination requires its separate
modularity, level-lowering and complete-form-list hypotheses.

## Final source addendum: the alternative Liu route also passes

After completing the cluster replacement, I independently inspected the
rendered primary Liu scan on printed pp.203--204, downloaded from the
[author's site](https://www.math.u-bordeaux.fr/~qliu/articles/genre2.pdf).
The authenticated PDF has 2305853 bytes and SHA256
602f883d7f3115ce87a9ab2c2050f8002df7c45db951f023ce73149b196b527d.
It is retained outside the deliverables. This was a visual page check;
the nearly empty text layer was not used as evidence.

Equation (2) on p.203 defines I4 and I12 exactly as used in the main
proof. Equation (3) on p.204 gives epsilon=3 in residue characteristic
three, so I_(2epsilon)=I6=J6. Theorem 1(V*) requires the first three
ratios in the main proof's table to lie in the maximal ideal. It yields
two irreducible stable components meeting once. Part (V) requires the
last two ratios to be integral and makes those components smooth.
Thus the source distinguishes the three strict inequalities from the
two weak ones exactly as the updated main proof does.

For m=v3(t)=-3v3(A)<=-3, the factors t-1 and 17t+108 have valuation m,
and 9t+16 has valuation m+2. The invariant formulas give

    v3(I4)=4+4m,    v3(I6)=6m,
    v3(J10)=6+10m,  v3(I12)=11+12m.

The five ratio valuations are therefore 12,18,33,18,15, all satisfying
their exact inequalities. Smoothness and stability force the two
components to be elliptic, and their tree dual graph gives compact
type, hence potential good reduction of the Jacobian. The main proof's
Liu route is accepted as well. The independent cluster route above
remains sufficient if this additional invariant comparison is omitted.
