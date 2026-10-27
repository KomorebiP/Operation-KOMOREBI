# Block 49: CM realization supplies Hilbert modularity

Status: source-verified theorem translation and direct representation argument; fresh audit pending. This note supplies modularity, not the separate conductor calculation or identification with the surviving eigenform. Base snapshot: `bbf78879d4b5714c818dd1521053dcd6b80c0694799b120b440fa850efec091a`.

Let \(K=\mathbf Q(\sqrt5)\), \(L=\mathbf Q(\zeta_5)\), and \(J=\operatorname{Jac}(D)\), where \(D:y^2=x^6+324x\). Use \(E=L\) for the **CM coefficient field** when distinguishing it from the identical number field \(L\) used as the field of definition of endomorphisms.

## Exact sources inspected

1. J. S. Milne, *Abelian Varieties with Complex Multiplication (for Pedestrians)*, arXiv:math/9806172v1, [author's mathematical exposition](https://arxiv.org/pdf/math/9806172), Theorems 13.1–13.2, printed pp. 30–31, and statement 15.1, printed p. 42 (PDF pages 30–31 and 42). The latter gives the compatible \(\ell\)-adic realization of the algebraic Hecke characters attached to an abelian variety whose CM endomorphisms are defined over the base field. Their infinity types have nonnegative exponents whose conjugate pairs sum to one. Theorem 13.1 identifies Frobenius with the CM reciprocity character; 13.2 identifies the Euler factors. Milne explicitly attributes 13.1 to Shimura–Taniyama and its formulation to Serre–Tate (1968), Theorem 10. Thus this is an inspected precise restatement, not an assertion that the original 1968 paper has been inspected.

2. H. Jacquet and R. P. Langlands, *Automorphic Forms on GL(2)*, Lecture Notes in Mathematics 114 (1970), [IAS author archive edition](https://publications.ias.edu/sites/default/files/automorphic-forms-on-gl2_rpl_9.pdf), **Proposition 12.1**, printed p. 207 (PDF page 213). For a quadratic extension and an idele class character not pulled back by the norm, it constructs the cuspidal representation whose local parameters are the corresponding induced characters. The preceding paragraph covers split and nonsplit places. **Lemma 5.12 and the following calculation**, printed pp. 88–90 (PDF pages 94–96), give angular exponent of absolute value one the lowest positive compact-group weight two. These are the required global induction and archimedean weight statements. The IAS edition contains later editorial comments, but these numbered results are the original book's mathematics.

Both sources were read on 2026-09-19. No source-access failure is being used as evidence. Arthur–Clozel is unnecessary for this quadratic induction. Labesse–Langlands Proposition 6.5, inspected during the search, is a reverse implication and is not used as the forward theorem.

## Geometric and representation translation

The automorphism
\[
u:(x,y)\longmapsto(\zeta_5x,\zeta_5^3y)
\]
is defined over \(L\). Its action on the basis \(dx/y,x\,dx/y\) of holomorphic differentials has eigenvalues \(\zeta_5^3,\zeta_5^4\). Together with the conjugate eigenspaces this proves that \(\mathbf Q[u]\cong E\) acts on the rational first homology as a rank-one module. Thus \(J_L\) has CM by \(E\). Every such CM endomorphism is defined over \(L\), which is exactly the hypothesis required in Milne 15.1; no claim that the CM endomorphisms are all defined over \(K\) is made.

The nontrivial element of \(\operatorname{Gal}(L/K)\) sends \(u\) to \(u^{-1}\). Hence the real subalgebra \(\mathbf Q[u+u^{-1}]\cong K\) is defined over \(K\). Fix an embedding of this real coefficient field and enlarge the coefficient field to split \(E\). The resulting two-dimensional \(K\)-RM Tate realization \(V_\lambda\), restricted to \(G_L\), is the sum of the two CM character spaces over that embedding. An element of \(G_K\setminus G_L\) exchanges them. Consequently, by the elementary index-two induction construction,
\[
V_\lambda\simeq\operatorname{Ind}_{G_L}^{G_K}\theta_\lambda.
\]
Here \(\theta_\lambda\) belongs to the compatible algebraic Hecke character furnished by the CM theorem. This argument concerns a characteristic-zero compatible system; it does not assume irreducibility of any residual representation.

At each complex place over a real place of \(K\), the two Hodge exponents are \((1,0)\). Therefore the associated complex idele class character has nonzero angular exponent \(\pm1\). A character pulled back from \(K\) by \(N_{L/K}\) has zero angular exponent at that place, so the norm-factorization obstruction in Jacquet–Langlands Proposition 12.1 is absent. Automorphic induction is therefore cuspidal. Its archimedean factors have holomorphic lowest weight two, at both real places. It determines a Hilbert cuspidal eigenform of parallel weight two over \(K\).

## Normalizations and central character

Use arithmetic reciprocity: an unramified local uniformizer maps to arithmetic Frobenius. Write \(\Theta\) for the complex idele class character normalized so that \(\Theta(\varpi_w)=\alpha_w\) equals the Frobenius eigenvalue on the CM Tate character. Then \(|\alpha_w|=(Nw)^{1/2}\), and the idelic absolute value is \(|\varpi_w|_L=(Nw)^{-1}\). The unitary character used for the weight-two automorphic representation is
\[
\Theta^{u}=\Theta\,|\cdot|_L^{1/2}.
\]
Its unramified values are \(\alpha_w/(Nw)^{1/2}\); its complex angular character is \(z/|z|\) or its inverse. Equivalently one may apply Proposition 12.1 first to \(\Theta\), then twist the induced representation by \(|\det|_K^{1/2}\). If geometric reciprocity is used instead, the Galois comparison must invert Frobenius consistently; it must not mix this with the displayed arithmetic formula.

The canonical polarization of \(J\) is preserved by curve automorphisms, so Rosati sends \(u\) to \(u^{-1}\) and fixes the RM subfield. The induced alternating pairing on each rank-two RM realization has multiplier the cyclotomic character. Thus
\[
\det V_\lambda=\chi_\ell.
\]
After the unitary normalization, the induced local determinants are one. Its central character, and hence the finite nebentypus of the weight-two form, is trivial. At an unramified prime \(\mathfrak q\), the classical polynomial is accordingly
\[
X^2-a_{\mathfrak q}X+N\mathfrak q,
\]
while the unitary Satake polynomial has roots divided by \((N\mathfrak q)^{1/2}\). The normalized induction and the Tate realization have matching ramification, since the norm twist is unramified at finite places.

## Exact remaining dependencies

This proves existence of a characteristic-zero Hilbert modular realization with the correct weight and central character. The assertion that its exact level is \((45)\) still requires the separate local conductor proof. Identifying it with the particular surviving form still requires completeness of the form enumeration and the recorded distinguishing eigenvalue. This note does not derive either assertion from the appearance of a matching genus-two curve in a database.
