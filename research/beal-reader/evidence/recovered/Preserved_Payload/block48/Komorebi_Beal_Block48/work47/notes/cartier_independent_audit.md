# Independent Cartier computation and local finite-flat consequence

Checked 2026-09-19. Scope: the smooth genus-2 curve

\[
X_{A,B}: y^2=f(x)=x^6+10Bx^3+12Ax+5B^2,
\qquad A,B\in\mathbf F_7,\quad A^3+B^5\ne0,
\]

and a separate local consequence for an abelian variety with this good
reduction over an unramified extension of \(\mathbf Q_7\). This is not a
global irreducibility proof or a Beal theorem.

## Exact derivation and conventions

Write \(f(x)^3=\sum_n c_nx^n\). The only contributing exponent triples give

\[
\begin{aligned}
c_5&=3(10B)(12A)^2=4320A^2B\equiv A^2B,\\
c_6&=3(5B^2)^2+3(10B)^2(5B^2)=1575B^4\equiv0,\\
c_{12}&=3(5B^2)+3(10B)^2=315B^2\equiv0,\\
c_{13}&=3(12A)=36A\equiv A\pmod7.
\end{aligned}
\]

The exponent triples are respectively \((3,1,1)\),
\((6,0,0),(3,3,0)\), \((6,6,0),(6,3,3)\), and \((6,6,1)\).

Put \(\omega_j=x^{j-1}dx/y\), \(j=1,2\). We use matrices acting on
column vectors: column \(j\) gives the coefficients of the image of
\(\omega_j\). Since

\[
\omega_j=y^{-7}\sum_n c_nx^{n+j-1}\,dx,
\]

Cartier retains the exponents \(n+j-1\equiv6\pmod7\), and hence

\[
\mathcal C(\omega_j)=\sum_{i=1}^2c_{7i-j}^{1/7}\omega_i.
\]

All coefficients lie in \(\mathbf F_7\), so inverse Frobenius fixes them.
Thus the Cartier–Manin matrix on the stated differential basis is

\[
M=\begin{pmatrix}c_6&c_5\\c_{13}&c_{12}\end{pmatrix}
 =\begin{pmatrix}0&A^2B\\A&0\end{pmatrix},
\qquad M^2=A^3B\,I_2,\qquad\det M=-A^3B.
\]

The Hasse–Witt matrix, meaning the Frobenius action on \(H^1(X,\mathcal O_X)\)
in the Serre-dual basis and with column action, is \(H=M^{\mathsf T}\).
Over a general perfect field the adjoint relation is
\(H=(M^{(7)})^{\mathsf T}\), and Cartier is inverse-Frobenius semilinear.
Over \(\mathbf F_{49}\), the same entries still lie in \(\mathbf F_7\);
Cartier itself is semilinear, while its second iterate has matrix \(M^2\).

The source for these conventions and the explicit formula is Achter–Howe,
*Hasse–Witt and Cartier–Manin matrices: A warning and a request*,
arXiv:1710.10726v5, dated 5 February 2020, §§2.4 and 3.1, printed pp.6–7.
The v5 PDF was checked directly; it corrects a zeta-function formula from
earlier versions. [Author preprint](https://arxiv.org/pdf/1710.10726).

## Rank classification

The geometric \(7\)-rank is the stable rank of Cartier. For genus two it
equals the rank of its second iterate. This is stated explicitly in
Ozman–Pries–Weir, *The boundary of the p-rank 0 stratum of the moduli space
of cyclic covers of the projective line*, Nagoya Mathematical Journal
**248** (2022), 865–887, §7.1, second paragraph; their cyclic-cover setting
includes hyperelliptic curves in characteristic 7. The stable-rank
formulation is also stated in §2.3 after Lemma 2.2.
[Published paper, DOI 10.1017/nmj.2022.12](https://doi.org/10.1017/nmj.2022.12).
Therefore:

| Parameters | Rank of Cartier | Rank of Cartier squared | Geometric 7-rank | Ordinary? |
|---|---:|---:|---:|---|
| \(A\ne0,\ B\ne0\) | 2 | 2 | 2 | Yes |
| \(A=0,\ B\ne0\) | 0 | 0 | 0 | No |
| \(A\ne0,\ B=0\) | 1 | 0 | 0 | No |

The remaining pair \((0,0)\) is excluded by the hypothesis. In particular,
there is no \(7\)-rank-one stratum in this family. The rank-one matrix in
the third row is nilpotent, so its rank must not be mistaken for the
\(7\)-rank. Passing from \(\mathbf F_7\) to \(\mathbf F_{49}\) leaves the
geometric \(7\)-rank unchanged.

## Exact finite audit and provenance

The independently written standard-library script
`computations/cartier_independent.py` performs sparse polynomial arithmetic
in \(\mathbf F_7[x,A,B]\). A separate dense convolution checks the four
coefficients for all 49 parameter pairs. Euclidean polynomial gcd checks
that the 42 admitted pairs are exactly the squarefree sextics. There are
30 ordinary pairs and 12 pairs of \(7\)-rank zero, with six in each zero
parameter stratum.

An independent point count over \(\mathbf F_7\) and
\(\mathbf F_{49}=\mathbf F_7[u]/(u^2-3)\), including the two rational
points at infinity, checks the first two coefficients of the zeta numerator
and gives

\[
L_X(T)\equiv1-A^3BT^2\pmod7
\]

for every admitted pair. These counts corroborate the matrix computation;
they do not authenticate the external geometric theorems.

The bounded run used Python 3.12.14, no randomness, exact arithmetic, a
30-second wall limit, a 20-second CPU limit, and a 512 MiB address-space
limit. Its provenance and all 42 count records are under
`verification/cartier_independent_run/`. The v2 manifest passed
`validate_manifest.py --root work47`. The symbolic coefficient argument
above supplies the uniform calculation; the enumeration is an exhaustive
finite audit over the explicitly stated field.

## Local no-unramified-subquotient theorem

**Statement.** Let \(K/\mathbf Q_7\) be finite and unramified, let
\(R=\mathcal O_K\), and let \(J/K\) be an abelian variety with good
reduction. If its geometric special fiber has \(7\)-rank zero, then
\(J[7](\overline K)\) has no nonzero unramified \(G_K\)-subquotient.
In particular it has no one-dimensional unramified constituent.

**Proof.** Suppose \(U\subset W\subset J[7](\overline K)\) are invariant
\(\mathbf F_7\)-subspaces and \(W/U\ne0\) is unramified. After a finite
unramified extension, this finite representation becomes trivial. Good
reduction, geometric \(7\)-rank zero, and absolute ramification index
\(e=1\) are preserved. Let \(\mathcal J/R\) be the abelian scheme, and
take the schematic closures
\(\mathcal U\subset\mathcal W\subset\mathcal J[7]\). They are finite
flat closed subgroup schemes, and the fppf quotient
\(\mathcal Q=\mathcal W/\mathcal U\) is finite flat. Its generic fiber is
the now constant nonzero group \(W/U\).

Raynaud's uniqueness theorem applies because \(e=1<7-1\). Comparing
\(\mathcal Q\) with the constant finite étale model of \(W/U\), it follows
that \(\mathcal Q\) is finite étale. But \(7\)-rank zero means
\(\mathcal J_{\bar k}[7](\bar k)=\{0\}\). Thus its underlying finite
scheme has a single point; its nonempty closed subgroup
\(\mathcal W_{\bar k}\) also has a single point. The quotient morphism
\(\mathcal W_{\bar k}\to\mathcal Q_{\bar k}\) is surjective, so the
target is connected. A nonzero finite étale group scheme killed by 7
over \(\bar k\) has at least seven points. This is a contradiction.

The exact primary source is Michel Raynaud, *Schémas en groupes de type
\((p,\ldots,p)\)*, Bulletin de la Société Mathématique de France **102**
(1974), 241–280, DOI 10.24033/bsmf.1779. Theorem 3.3.3, printed p.268,
states uniqueness of finite flat extensions when \(e<p-1\). Corollary
3.3.6(1) gives unique extension of generic morphisms with flat kernels and
cokernels. The closure and quotient construction is treated in §2.1,
printed pp.259–260. These passages were checked in the
[original published paper](https://www.numdam.org/article/BSMF_1974__102__241_0.pdf).
The local theorem above is a formal corollary, not a verbatim source theorem.

**Coefficient-field and constituent distinctions.** An invariant line is
a submodule; a Jordan–Hölder constituent may only be a quotient of a
submodule. The use of both \(U\) and \(W\) handles that distinction. If
\(J[7]\) carries a commuting \(\mathbf F_{49}\)-action, a line over
\(\mathbf F_{49}\) has dimension two over \(\mathbf F_7\); the proof
applies to its underlying nonzero \(\mathbf F_7\)-subquotient, with no
need to assume it is one-dimensional over the prime field. For scalar
extension to an arbitrary finite coefficient field, the underlying
\(\mathbf F_7\)-representation is a direct sum of copies of \(J[7]\),
realized by a power of \(J\); its special fiber still has \(7\)-rank zero,
so the same proof applies. An algebraic-closure constituent descends to
such a finite coefficient field.

This proves the local obstruction for either \(7\mid A\) or \(7\mid B\)
under good reduction and \(A^3+B^5\not\equiv0\pmod7\). It does not prove
that a constituent from a hypothetical global reducibility is unramified
at 7. That requires the separate global character argument and all its
local hypotheses. In particular, extending an argument from odd to even
\(C\) requires checking its control at 2 (for example semistability or
the ramification of the eighth power of a character). No such global
extension is asserted here.

## Subsequent independent audit of the two-adic input

After completing the preceding local calculation, the separate proof in
`notes/evenC_semistability_at2.md` was independently reviewed. The
substitution from the sextic, the finite flat cover charts, all derivatives,
the exact local expansions, the infinity calculation, and the
Artin–Schreier pole argument were rederived and agree. The irreducible
special fiber has two ordinary nodes and arithmetic genus two; its
normalization is rational with four node branches. It is a stable fiber.
No algebraic gap was found in the resulting stable model for odd \(A,B\).

Deligne–Mumford, *The irreducibility of the space of curves of given
genus*, Publications Mathématiques de l'IHÉS **36** (1969), 75–109,
Theorem 2.4 and its forward proof on printed p.89 were independently
checked in the [original paper](https://www.numdam.org/item/PMIHES_1969__36__75_0.pdf).
They identify the connected special fiber of the Jacobian's Néron model
with the generalized Jacobian of a reduced nodal curve, an extension of
an abelian variety by a torus. Their term “stable reduction” for the
Jacobian is the semistable reduction used here. The forward implication
has no residue-characteristic-two exclusion.

Thus the curve-to-Jacobian step in the separate note is validated. Once
the semistable inertia-unipotence theorem is applied at 2, every
one-dimensional residual constituent is unramified there: for each
inertia element, the integral characteristic polynomial has all roots
equal to one, and its reduction has the same property. This supplies the
local input; the complete global unit-character calculation still must
be checked as a separate dependency.
