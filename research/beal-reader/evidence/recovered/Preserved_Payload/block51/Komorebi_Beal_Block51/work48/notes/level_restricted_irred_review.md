# Absolute irreducibility after adjoining seventh roots of unity

Checked 2026-09-19. Primary verdict: **proved as written**, for the conditional implication below. This independent derivation was completed before comparison with the exact primary lemma identified by the level-lowering investigator. It is a written argument with named local arithmetic inputs, not a Lean formalization.

## Claim card

Let \(K=\mathbf Q(\sqrt5)\), let \(J/K\) be the Block 47 Jacobian, and let
\[
\bar\rho:G_K\longrightarrow\mathrm{GL}_2(\mathbf F_{49})
\]
be its residual real-multiplication representation, with the lattice-independent interpretation used in Block 47. If \(\bar\rho\) is absolutely irreducible, then
\[
\boxed{\bar\rho|_{G_{K(\zeta_7)}}\text{ is absolutely irreducible}.}
\]
The local hypotheses used are that \(K\) is unramified at seven, \(J\) is semistable there, and the inertia constituents of \(\bar\rho\) occur among those of \(J[7]\) after extending coefficients. The determinant identity \(\det\bar\rho=\bar\chi_7\) is **not needed** for this implication. In particular the weaker determinant normalization actually retained in the Block 47 audit causes no gap here.

Combining this implication with the canonical Block 47 theorem establishes the boxed conclusion whenever \(14\nmid C\). If a subsequent argument proves absolute irreducibility on the remaining branch, the same implication applies there without a new restriction argument.

## Elementary group argument

Work over \(k=\overline{\mathbf F}_7\). Put \(G=G_K\), \(H=G_{K(\zeta_7)}=\ker\bar\chi_7\), and \(V=k^2\). The mod-seven cyclotomic character is surjective on inertia at the unique prime above seven: the local base field is unramified over \(\mathbf Q_7\), whereas \(\mathbf Q_7(\zeta_7)/\mathbf Q_7\) is totally ramified of degree six. Thus \(G/H\) is cyclic of order six.

Suppose that \(V|_H\) is reducible, and choose an \(H\)-stable line \(L\). Since \(H\) is normal, every translate \(gL\) is \(H\)-stable. Absolute irreducibility provides a translate \(L'\ne L\), so
\[
V|_H=\lambda\oplus\mu.
\]
If \(\lambda=\mu\), then \(H\) acts by scalars. For a lift \(g\) of a generator of the cyclic quotient \(G/H\), every element of \(\bar\rho(G)\) is a scalar times a power of \(\bar\rho(g)\). An eigenline of \(\bar\rho(g)\) over \(k\) is then \(G\)-stable, a contradiction. Consequently \(\lambda\ne\mu\), and \(L,L'\) are exactly the two \(H\)-stable lines.

The group \(G\) permutes these two lines, nontrivially by irreducibility. The resulting quadratic character \(\varepsilon:G\to\{\pm1\}\) factors through \(G/H\). Hence
\[
\varepsilon=\bar\chi_7^3.
\]
This is also the familiar quadratic subextension \(K(\sqrt{-7})/K\). In particular, inertia at seven acts nontrivially on the two lines.

In the basis given by \(L,L'\), the image consists of diagonal and antidiagonal matrices. Its diagonal subgroup has finite order prime to seven, and its index is two. Thus the entire image has order prime to seven. Wild inertia, being pro-seven, acts trivially.

The remaining tame inertia image is finite cyclic. Choose a generator \(t\) of that image. Its permutation of the two lines is nontrivial, so \(t\) is antidiagonal and \(t^2\) is scalar. Its projective image has order exactly two. Since the characteristic is odd, the eigenvalues of \(t\) are \(a,-a\) for some nonzero \(a\). Therefore the two inertia characters \(\eta_1,\eta_2\) have quotient of order exactly two.

## Local weight contradiction

For a semistable abelian variety over an absolutely unramified seven-adic field, each character in the semisimplified tame inertia action on its seven-torsion has fundamental-character digits in \(\{0,1\}\). Here is the exact source bridge: the finite-flat part of the torsion has these digits by Raynaud, Corollary 3.4.4; the semistable quotient is unramified, as recorded in the proof of Larson–Vaintrob, Lemma 4.10. These statements apply to inertia constituents, without requiring those constituents to extend individually to the full local or global Galois group.

Consequently, for a common sufficiently divisible niveau \(n\), a fundamental character \(\theta_n\) of order \(7^n-1\) gives
\[
\eta_1=\theta_n^u,\qquad \eta_2=\theta_n^v,
\qquad
u=\sum_{i=0}^{n-1}a_i7^i,\quad
v=\sum_{i=0}^{n-1}b_i7^i,
\quad a_i,b_i\in\{0,1\}.
\]
To pass to a common niveau, replace the original niveaux by a common multiple and use compatibility of fundamental characters; this repeats their digit strings. A different coefficient embedding cyclically permutes the digits. A simultaneous inverse convention changes both exponent signs and leaves the following bound unchanged.

Set \(M=7^n-1\). Then
\[
|u-v|\le 1+7+\cdots+7^{n-1}=M/6.
\]
But a quotient of order two requires
\[
u-v\equiv M/2\pmod M,
\]
which is impossible for an integer of absolute value at most \(M/6\). This contradiction proves the claim.

One must not import the shorter list \(0,1,7,8\) from the proof about *global one-dimensional constituents*: inertia eigencharacters in this argument can have a higher niveau. The common-niveau bound handles all possibilities and needs no separate ordinary/supersingular classification.

## Primary-source verification

The search was an exact theorem/application check, not a novelty search. The local Block 47 proofs were read first. The exact external lemma was located independently by the parent investigator and then read directly here, including the version header and proof.

| Source | Checked input and application |
|---|---|
| [Billerey–Chen–Dieulefait–Freitas, arXiv:2205.15861v5](https://arxiv.org/pdf/2205.15861v5), *On Darmon's program for the generalized Fermat equation, I*, arXiv header 16 April 2025, manuscript date 17 April 2025 | Lemma 6.9, printed pp.37–38: for an RM \(\mathrm{GL}_2\)-type abelian variety, an absolutely irreducible residual representation at \(p>3\) remains so over a quadratic extension ramified above \(p\), provided \(p\) is unramified in the base and the variety has good or multiplicative reduction above \(p\). The proof of Theorem 8.3, printed p.43, explains the reduction from cyclotomic restriction to the unique quadratic subextension. This directly corroborates the present application. |
| [Raynaud, BSMF 102 (1974), 241–280](https://www.numdam.org/article/BSMF_1974__102__241_0.pdf), DOI 10.24033/bsmf.1779 | Theorem 3.4.3 and Corollary 3.4.4, printed p.270: finite-flat Jordan–Hölder characters have fundamental-character exponents between zero and the absolute ramification index. Use index one. |
| [Larson–Vaintrob, arXiv:1110.0255v4](https://arxiv.org/pdf/1110.0255), version header 30 March 2012 | Proof of Lemma 4.10, printed p.25: the semistable torsion has a finite-flat part and an unramified quotient. Together with Raynaud this supplies the local input used above. No asymptotic-prime hypothesis is used. |

The versioned BCDF web endpoint failed in this audit; the unversioned endpoint succeeded and its first page explicitly identified v5. The parent-provided PDF and text have the same authenticated version header. The longer v5 manuscript warns that its numbering differs from the shorter published version; no theorem numbers from that shorter paper are substituted.

Source copies inspected (temporary shared-workspace locations):

| Artifact | SHA-256 |
|---|---|
| `/tmp/level_bcdf25.pdf` | `50076644a1a513f24afb736320f8a69bad8a467af9c3fb3aaf867ae88ad63a78` |
| `/tmp/level_bcdf25.txt` | `9639542ad7daa0c3c9f50ef51dd85d0a78a987a11d7054424368960382325dbd` |
| `work47/notes/mod7_good_reduction_irreducibility.md` | `fb939ab48ffd726781aabd41328e7a31c594502cc9585c22e7a4df0b4d7448a1` |
| `work47/predecessor/mod7_oddC_written_proof.md` | `faa4c7962eab007dd200b8af05f2905c8329125b22aed0e6471b6fffe3f1d0ce` |

The BCDF lemma requires good or multiplicative reduction. The present family meets that stronger condition: the Block 47 model is smooth at seven when \(7\nmid C\), and when \(7\mid C\) its stable special fiber has rational normalization and two nodes, hence the Jacobian is totally toric. The reconstructed argument above in fact uses only semistability and the stated inertia-constituent input.

## Audit matrix and boundary

| Obligation | Status | Reason |
|---|---|---|
| Cyclotomic quotient and ramification | Passed | Local cyclotomic extension has degree six after unramified base change. |
| Reducible restriction implies a swapped pair of lines | Passed | Direct normal-subgroup argument; the equal-character case is excluded separately. |
| Quadratic inertia quotient | Passed | Monomial image has order prime to seven; tame inertia is cyclic. |
| Coefficient and lattice compatibility | Passed, inherited arithmetic input | Restriction of scalars gives the two coefficient embeddings of the RM representation inside the semisimplified \(J[7]\) representation; restricting a composition filtration preserves its inertia composition factors. |
| Semistable weight bound | Passed, source-checked | Raynaud plus the semistable finite-flat/unramified filtration. |
| Higher-niveau cases | Passed | Common-niveau exponent bound, not a niveau-two assumption. |
| Rank-two determinant normalization | Not required | The quotient \(G/H\) is defined by \(\bar\chi_7\), independently of \(\det\bar\rho\). |
| Absolute irreducibility of the original representation | Input | Block 47 supplies it for \(14\nmid C\); this note does not settle the remaining branch. |
| Modularity, residual finiteness at seven, level lowering, form elimination | Out of scope | None is inferred from restricted irreducibility alone. |

There is no remaining implication in the restriction lemma. Without the semistable tame-weight input, absolute irreducibility and a cyclotomic determinant alone would not rule out the dihedral obstruction. The cheapest remaining step is therefore to cite this lemma in the level-lowering hypothesis audit and continue checking its other hypotheses.

Self-review used the conservative mathematical proofreading workflow on this note alone: no notation or mathematical-token correction was required, and no unresolved local inconsistency was found. No numerical testing is needed for the exact inequality.

## Appendix: finite-flat residual representation to a crystalline lift

Checked 2026-09-19 in a second adversarial review requested by the level-lowering investigator. Verdict: **proved as written**, with the coefficient and functor conventions made explicit below. This appendix assumes, separately, that the actual local representation is finite flat and has determinant \(\bar\chi_7\). It does not deduce either assertion from semistability or from the rank-four determinant norm identity.

Let \(F/\mathbf Q_7\) be unramified quadratic, let \(k=\mathbf F_{49}\), and put \(\mathcal O=W(k)\), viewed as the coefficient ring. If
\[
r:G_F\longrightarrow\mathrm{GL}_2(k)
\]
is finite flat with \(\det r=\bar\chi_7\), then it admits an \(\mathcal O\)-valued crystalline lift of parallel Barsotti–Tate Hodge type, determinant \(\chi_7\), trivial Weil–Deligne inertia and zero monodromy.

Use [Fontaine–Laffaille, *Construction de représentations p-adiques*, Ann. Sci. ENS 15 (1982), 547–608](https://www.imo.universite-paris-saclay.fr/~fontaine/laffaille.pdf) with the paper's parameter \(E=\mathbf Q_7\), on the underlying four-dimensional representation, and retain the commuting \(k\)-coefficient action. The paper's relative construction with parameter \(E=F\) is a different filtration convention and must not be substituted here. The exact passages read were §§9.10–9.12 (finite-flat comparison), Remark 6.13(b) (tensor compatibility), Theorem 5.3 (inertia), §§7.12–7.15 (integral realization and reduction), and Theorem 8.4 (crystallinity); printed pages 604–605, 589, 570, 592–594 and 595–596 respectively.

The \(k\)-action extends from the generic fiber to the finite-flat model by full faithfulness at absolute ramification index one. The associated killed-seven Fontaine–Laffaille module is a module over
\[
\mathcal O_F\otimes_{\mathbf Z_7}k\simeq k\times k.
\]
Write it as \(M_0\oplus M_1\). Frobenius is semilinear in the base and linear in the coefficients, so it exchanges the two factors. The divided-Frobenius generation condition gives surjections from the graded space of each component onto the next. Thus their dimensions agree; their sum is four, so each dimension is two. Set \(d_i=\dim_k\operatorname{Fil}^1M_i\in\{0,1,2\}\).

Tensor compatibility is applicable: all weights in the required tensor square lie in \([0,2]\), strictly below the exceptional endpoint six. Because \(k/\mathbf F_7\) is separable, the balanced coefficient tensor product is a direct summand; the alternating summand is also available since two is invertible. Consequently the coefficient determinant has filtration weights \(d_0,d_1\), and the rank-one inertia formula gives
\[
\det r|_{I_F}=\theta_2^{d_0+7d_1},\qquad
\bar\chi_7|_{I_F}=\theta_2^8,
\]
up to exchanging the component labels. A simultaneous inverse convention changes both exponents' signs. Since \(0\le d_0+7d_1\le16<48\), equality forces \(d_0+7d_1=8\), hence \(d_0=d_1=1\).

Choose a basis \((e_{i,1},e_{i,2})\) of each component with \(\operatorname{Fil}^1M_i=k e_{i,1}\). The two vectors
\[
\varphi_1(e_{i,1}),\quad\varphi_0(e_{i,2})
\]
form a basis of \(M_{i+1}\), with indices modulo two. Lift each corresponding matrix to \(\mathrm{GL}_2(\mathcal O)\). Lift the components to \(\mathcal O^2\), the filtration to the rank-one direct summand \(\mathcal O e_{i,1}\), and impose
\[
\varphi_0(e_{i,1})=7\varphi_1(e_{i,1}).
\]
Using \(\mathcal O_F\otimes_{\mathbf Z_7}\mathcal O\simeq\mathcal O\times\mathcal O\), these component maps are precisely base-Frobenius-semilinear and coefficient-linear. They supply a free, strongly divisible module reducing to the given module. The integral realization gives a coefficient-rank-two lattice reducing to \(r\), and its rational representation is crystalline. The filtration has weights \(\{0,1\}\) at each embedding in the convention assigning cyclotomic character weight one. Equivalently it has the usual parallel Barsotti–Tate type, independently of the sign convention for Hodge–Tate weights.

For this lift \(\widetilde r\), the character
\[
\eta=(\det\widetilde r)\chi_7^{-1}
\]
is crystalline of weight zero at both embeddings, hence unramified; this also follows from its rank-one filtered module having only filtration degree zero. It is congruent to one modulo seven. If \(u=\eta(\mathrm{Frob}_F)\in1+7\mathcal O\), Hensel's lemma gives a unique \(v\in1+7\mathcal O\) with \(v^2=u^{-1}\). Twist by the unramified character taking \(\mathrm{Frob}_F\) to \(v\). The twist still reduces to \(r\), preserves the crystalline Hodge type, and has determinant exactly \(\chi_7\).

This proves the local existence assertion needed when prescribing the trivial crystalline type. It supplies no global automorphy conclusion by itself. In particular, on the branch \(7\mid C\), one must first prove that the residual representation is finite flat; the semistable characteristic-zero Tate module need not itself be crystalline. The weak determinant norm identity \(\delta^8=\bar\chi_7^2\) alone does not replace the determinant hypothesis in this appendix.
