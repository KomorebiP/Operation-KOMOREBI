# Odd-C branch: a direct mod-seven irreducibility argument

Status: written proof with named arithmetic inputs, reviewed collaboratively after repair. The source reviewer independently checked the initial source hypotheses, then contributed to and reviewed the replacement argument below. The finite algebra has exact executable checks. This is not a Lean formalization and not a proof of Beal.

## Statement

Let A,B,C be positive pairwise-coprime integers satisfying A^3+B^5=C^7, with C odd. Let J be the Jacobian of

\[
\mathcal C:\quad y^2+y(X^3+B)=2BX^3+3AX+B^2.
\]

Put K=Q(sqrt(5)), and let \(\mathfrak p=(7)\), which is inert in K. For the rank-two representation from the real multiplication by K on J, the residual representation at \(\mathfrak p\) is absolutely irreducible.

This conclusion does not exclude an initial solution. It removes a representation-theoretic obstruction to applying level lowering on the C-odd branch.

## Arithmetic inputs and exact scope

1. The genus-two realization over K and the rank-two conductor bounds at (3) and (sqrt(5)) are taken from Pacetti–Villagra Torcomian, arXiv:2512.17845v1, Section 7.1, Corollary 3.6 and Proposition 3.14. Each bound is at most three. These conductor statements do not assume residual irreducibility. The source dictionary is (a,b,c,p)=(B,-C,A,7). A Tate twist in the motive convention is unramified at 3 and 5, so does not alter these bounds. [Versioned source](https://arxiv.org/html/2512.17845v1).

2. Larson–Vaintrob, arXiv:1110.0255v4, Lemma 4.10: a degree-one associated character of an abelian variety semistable at an unramified prime over seven has local algebraic weights zero or one. With the two embeddings of K this gives inertia exponents 0,1,7,8, up to a common reciprocity sign. There is no large-prime exclusion in this lemma. [Versioned source](https://arxiv.org/pdf/1110.0255v4).

3. Standard arithmetic facts used: semistable curves have semistable Jacobians, and inertia on prime-to-residue-characteristic Tate modules of semistable abelian varieties is unipotent. Source locators are [Dokchitser–Dokchitser–Maistret–Morgan, Theorem 10.3(1)](https://arxiv.org/pdf/1808.02936v2) and Larson–Vaintrob, proof of Lemma 4.6. The Weil pairing, lattice independence of residual semisimplification, and local and global class field theory are also used. Larson–Vaintrob's proof of Lemma 5.4 gives the principal-idele relation; [BCDF17, proof of Theorem 2](https://lmbp.uca.fr/~billerey/Research/Published/CDF17_ppr.pdf) records the class-group step. These are written-proof inputs, not new formalizations. Only K-defined real multiplication is needed, without a claim that the specialized endomorphism algebra is exactly K or a self-adjointness hypothesis.

The character argument below avoids both the number 6084 and the general large-prime irreducibility bound. It never uses a residual-unramified statement whose hypotheses already include irreducibility.

Here is the conductor-reduction justification used below. At residue characteristic q different from seven, wild inertia has finite q-group image. Its invariant dimensions are preserved on reduction modulo seven by averaging, since the group order is invertible. Thus Swan conductor is preserved. Integral inertia invariants reduce injectively into residual inertia invariants, so the tame codimension cannot increase. Semisimplification can only enlarge invariant dimensions and preserves the wild contribution. Therefore the conductor of the semisimplified residual representation is at most the characteristic-zero conductor.

## Comparison of the integral curve with the source family

The source family is \(Y^2=5x^6-12x^5+10s x^3+s^2\). Invert x and divide Y by x cubed, obtaining

\[
V^2=5-12x+10s x^3+s^2x^6.
\]

Set \(V=2U+(sx^3+1)\). Then

\[
U^2+U(sx^3+1)=2s x^3-3x+1.
\]

At \(s=-B^5/A^3\), substitute \(x=-AX/B^2\) and \(U=y/B\), and multiply by B squared. The result is exactly the integral curve in the statement. All changes are over Q because AB is nonzero. There is no quadratic twist in this comparison.

Write chi for the mod-seven cyclotomic character and delta for the determinant of the rank-two representation over F49. Choose a Galois-stable lattice over the integer ring of K at seven in the rank-two rational Tate representation. Its underlying Z7 lattice is commensurable with T7(J), so lattice independence of semisimplification shows that its four-dimensional reduction has the same semisimplification as J[7]. This suffices to identify determinants, Frobenius characteristic polynomials, and degree-one associated characters. It avoids any assumption that the specialized integral endomorphism order is maximal at seven. The usual Weil pairing therefore gives

\[
\delta^8=\operatorname{Norm}_{\mathbf F_{49}/\mathbf F_7}(\delta)
=\det_{\mathbf F_7}J[7]=\chi^2.
\]

This identity requires no choice of a rank-two polarization or determinant normalization.

## Semistability away from 2,3,5, proved from the displayed model

Completing the square gives

\[
Z^2=F_{A,B}(X)=X^6+10BX^3+12AX+5B^2,
\]

whose discriminant is \(2^{12}3^65^5 C^{14}\), as proved in `signature_route.md` by exact Sylvester determinants and weighted homogeneity.

Let ell be a prime at least seven. If ell does not divide C, this polynomial has distinct roots modulo ell and the curve has good reduction. If ell divides C, primitivity implies AB is a unit modulo ell and A cubed equals minus B to the fifth power. Define

\[
u=A^2/B^3=-B^2/A
\]

in the residue field. Then u cubed equals B and u to the fifth power equals minus A. Thus

\[
F_{A,B}(uX)=u^6 (X^2+X-1)^2(X^2-2X+5).
\]

The two quadratics have discriminants 5 and -16, and their resultant is 45. All are units for ell at least seven. Over an algebraic closure the special fiber therefore has exactly two ordinary nodes and no other singularity. Its normalization is the genus-zero double cover defined by the second quadratic. Infinity is smooth. The normalization has four distinct preimages of the nodes, so the irreducible nodal fiber is stable. This gives a semistable curve model, hence semistable J. In particular J is semistable at seven. No residual irreducibility was assumed.

## Good reduction at two and its exact Frobenius data

Because C is odd, A and B have opposite parity. In characteristic two the integral equation becomes one of

\[
y^2+(X^3+1)y=1,\qquad y^2+X^3y=X.
\]

Both are smooth. In the first case an affine singularity would have X cubed equal to one and X squared times y equal to zero, so y=0, contrary to the curve equation. In the second case a putative singularity with X=0 fails the X derivative, which equals one. At infinity the equation is \(v^2+v=0\) and its v derivative equals one, giving two smooth rational points.

The exact counts, including infinity, are

| (A mod 2, B mod 2) | #C(F2) | #C(F4) | Frobenius at 2 on the 4-dimensional Tate module |
|---|---:|---:|---|
| (0,1) | 3 | 7 | T^4+T^2+4 |
| (1,0) | 3 | 5 | T^4+4 |

The prime two is inert in K. Squaring the Frobenius eigenvalues gives, at the K-prime of norm four,

\[
(T^2+T+4)^2\quad\hbox{or}\quad(T^2+4)^2.
\]

Consequently every Frobenius eigenvalue on J[7], and in particular any eigenvalue of the rank-two representation or its subquotients, satisfies the corresponding quadratic after reduction modulo seven. This deduction uses the full characteristic polynomial and does not require choosing a square-root factor or normalizing a rank-two trace.

## Contradiction from a hypothetical one-dimensional constituent

Suppose the residual rank-two representation is reducible over the algebraic closure of F7. Write the semisimplification as \(\lambda\oplus\mu\). These characters have finite image; they need not be assumed F49-valued. Their product is delta, so

\[
(\lambda\mu)^8=\chi^2.
\]

At a finite prime away from 2,3,5,7, semistability implies that both characters are unramified. They are unramified at two because J has good reduction there.

At (3) and (sqrt(5)), chi is unramified, so delta to the eighth power is trivial on wild inertia. The finite image of wild inertia is a three-group or a five-group, respectively, and taking the eighth power is injective on either such abelian group. Thus delta itself is trivial on wild inertia. If lambda were nontrivial there, mu would also be nontrivial there. Each would then have Artin conductor exponent at least two, contrary to their sum being at most three by the source conductor bound and its behavior under reduction and semisimplification. Thus both are tame at both primes. A tame character of the full local Galois group has inertia order dividing the residue-field unit-group order: eight at (3), and four at (sqrt(5)). This follows directly from Frobenius conjugation of tame inertia and remains true for characters valued in the algebraic closure of F7. Hence both \(\lambda^8\) and \(\mu^8\) are unramified at every finite prime other than seven. Their values at real complex-conjugation elements are also one.

Let phi=(1+sqrt(5))/2. It is a global unit. Its reduction in F49 satisfies phi squared equals phi plus one and has order sixteen. By the local-weight input at seven, \(\lambda|_{I_7}\) has exponent e in {0,1,7,8}, using a fundamental character normalized consistently with reciprocity. The opposite reciprocity convention negates all exponents and makes no difference to the next argument.

Apply global reciprocity to the principal idele of phi and the character \(\lambda^8\). Every local factor outside seven equals one, since phi is a unit and the character is unramified there, including infinity. Thus

\[
\overline\phi^{8e}=1.
\]

Order sixteen excludes e=1 and e=7. Apply the same reasoning to mu, obtaining inertia exponents e,f in {0,8}. A fundamental character has order 48 and chi has exponent eight in the chosen convention. The determinant identity now implies

\[
8(e+f)\equiv16\pmod {48}.
\]

Among the four pairs in {0,8} squared, exactly (0,8) and (8,0) satisfy this congruence. Changing the reciprocity convention negates both sides and preserves the conclusion. Hence one constituent is unramified at seven. Call it nu. Its eighth power is therefore unramified at every finite and infinite prime.

The ordinary class number of K is one by a direct Euclidean argument. Its integer ring is Z[phi]. For any element of K, round its two rational coefficients in the basis 1,phi to integers. The remainder is u+v phi with |u|,|v| at most one half, so

\[
|\operatorname{Norm}(u+v\phi)|=|u^2+uv-v^2|\le 3/4<1.
\]

Thus absolute norm is a Euclidean function and the integer ring is a principal ideal domain. Global class field theory now gives

\[
\nu^8=1.
\]

At the prime of norm four, nu(Frob) must be a root of one of

\[
Q_0(T)=T^2+4,\qquad Q_1(T)=T^2+T+4.
\]

It must simultaneously satisfy T to the eighth power equals one. But exact resultant calculations give

\[
\operatorname{Res}(T^8-1,Q_0)=65025,\qquad
\operatorname{Res}(T^8-1,Q_1)=65760.
\]

Both are congruent to two modulo seven. Thus neither polynomial shares a root with T to the eighth power minus one over the algebraic closure of F7. This contradiction proves absolute irreducibility, subject to the explicitly declared arithmetic inputs.

There is also a short direct check of the last step. Modulo seven, a root alpha of Q0 satisfies alpha squared equals three, hence alpha to the eighth power equals four. For a root of Q1, reducing successive powers gives alpha to the fourth power equals five, again giving alpha to the eighth power equals four. In neither case can it equal one.

## What this establishes and leaves open

The proof is specific to C odd. It closes the reducible-representation branch needed before level lowering in that case. It does not eliminate the Hilbert modular forms that can be congruent to this irreducible representation. For example, the pinned authors' transcript for level \(3^3(\sqrt5)^2\) still leaves nine form indices at seven, as recorded in `signature_source_extract.json`; that transcript has not been freshly replayed. The C-even branch is not covered by the good-reduction/Frobenius argument at two.

The failed shortcut is retained explicitly: merely observing that seven does not divide 6084 cannot justify applying a large-prime theorem at seven. The proof above replaces that shortcut with a direct unit, inertia, and Frobenius contradiction.

Computational evidence: `computations/signature_audit.py` verifies the point counts, order-sixteen unit, elimination of the two mixed weights, and exact eighth-power resultants. Those computations do not formalize the declared Galois-theoretic inputs.
