# Final independent audit of the mod-seven irreducibility extension

Checked 2026-09-19. Primary verdict: **proved as written**, for the normalized combined claim below, using the named arithmetic theorems in the audited notes. This is a written mathematical audit, not a Lean proof, a new theorem attribution, or a proof of nonexistence of integer solutions.

## Normalized claim and exact scope

For every positive pairwise-coprime integer triple \((A,B,C)\) satisfying
\(A^3+B^5=C^7\), let \(J\) be the Jacobian of

\[
y^2+(x^3+B)y=2Bx^3+3Ax+B^2,
\qquad K=\mathbf Q(\sqrt5).
\]

The two-dimensional representation over \(K_{(7)}\) supplied by the \(K\)-defined real multiplication has an absolutely irreducible residual representation whenever

\[
\boxed{C\text{ is odd}\quad\text{or}\quad 7\nmid C.}
\]

Here residual absolute irreducibility means irreducibility after extension to \(\overline{\mathbf F}_7\); it is independent of the stable lattice. The additional even-\(C\), good-at-seven branch is the proposed global application at the end of `ordinary7_candidate.md`, with its explicit dependencies supplied by the other audited notes. That note's own provisional status is not silently changed by this audit.

The canonical joined statement is `mod7_good_reduction_irreducibility.md`, whose equivalent hypothesis is \(14\nmid C\). Its proof was read after the component audit and reproduces the checked chain without strengthening its hypotheses or conclusion. The exact remaining branch for this argument is \(14\mid C\). There is no missing implication within the boxed scope. The older claim \(C\) odd or \(7\mid AB\) uses a narrower parity/divisibility condition: primitivity makes \(7\mid AB\) imply \(7\nmid C\).

## Pinned raw artifacts

Paths below are relative to the workspace root. SHA-256 hashes identify the revisions actually read; later edits require a new comparison.

| Artifact | SHA-256 |
|---|---|
| `work47/notes/mod7_good_reduction_irreducibility.md` | `fb939ab48ffd726781aabd41328e7a31c594502cc9585c22e7a4df0b4d7448a1` |
| `work46/mod7_oddC_written_proof.md` | `faa4c7962eab007dd200b8af05f2905c8329125b22aed0e6471b6fffe3f1d0ce` |
| `work47/notes/mod7_irreducibility_extension.md` | `633a1c392396eadd02d3872f31666acae7a2eef223aed37acb3f7c61b879e9ab` |
| `work47/notes/reciprocity_two_seven.md` | `acc12bbdd0d5dcd630fd93e24e6d122d5580488c68e3a307a5e4bd8d17e0da48` |
| `work47/notes/evenC_semistability_at2.md` | `73b5859b9eccfecdb250960b6f643501ae0a3620bb17c1985ff72331b20fd7a8` |
| `work47/notes/cartier_independent_audit.md` | `502fba199936fc28625b05cfe4ba83836fad50acad26c771414448ab010e0955` |
| `work47/notes/ordinary7_candidate.md` | `5562727f1b4185860b1511b2fbc32ba957baaf9bd6a951409a33e1ec5fa3c987` |
| `work47/notes/evenC_torus_frobenius.md` | `3ab575c044ba137ca8e39184330075e04460e29023928938239d0862f408a44a` |

The audit read these raw proofs rather than relying on a status table or earlier audit verdict. It independently derived the coefficient, character, reciprocity, tangent-branch, Frobenius, and finite-flat implications below. A separate source agent's torus locator was used as a discovery aid; the cited primary passage was then read directly. Agreement between agents is not treated as proof.

## Dependency graph

1. The source genus-two realization and its rational coordinate change identify the RM representation of \(J\). The source conductor bounds at the primes above three and five are at most three and do not require residual irreducibility.
2. The displayed models give semistability away from three and five. This includes seven, and includes two for either parity after the new even-\(C\) model.
3. Hypothetical reducibility, the determinant norm, the conductor bounds, the local weight theorem, and the unit \(\phi=(1+\sqrt5)/2\) give a single global constituent \(\nu\) unramified at seven. Class number one gives \(\nu^8=1\).
4. For odd \(C\), the original good-reduction Frobenius calculation at two contradicts \(\nu^8=1\).
5. For even \(C\), the two nonsplit nodes over \(\mathbf F_4\) give \(\nu(\mathrm{Frob}_{(2)})=-1\). Principal-idele reciprocity transports this same value to \(\mathrm{Frob}_{(7)}\).
6. If \(7\nmid C\), Raynaud's finite-flat uniqueness transports \(\nu\), with its Frobenius action intact, to a special-fiber subquotient. Cartier gives its only possible nonzero Frobenius eigenvalue \(A^3B\bmod7\). Equality to \(-1\) contradicts \(7\nmid C\).

There is no circular use of residual irreducibility in this graph. No level-lowering statement is used to establish irreducibility.

## Obligation matrix

| Obligation | Result | Decisive check |
|---|---|---|
| Source family and conductor bounds | Passed | Correct dictionary \((a,b,c,p)=(B,-C,A,7)\); direct rational coordinate change; source hypotheses include this case. |
| Coefficient field and lattice | Passed | \(\overline{\mathbf F}_7\)-characters are allowed; restriction of scalars and finite coefficient descent are explicit. |
| Determinant identity | Passed | Rank-four Weil pairing gives \(\delta^8=\chi^2\); no rank-two polarization normalization is assumed. |
| Wild and tame conductors at three and five | Passed | A wild constituent forces both characters wild; their conductor sum is at least four, contrary to the bound three. |
| Weights at seven and unit elimination | Passed | Degree-one means maximum local weight one; exponents are \(0,1,7,8\), with one common reciprocity sign. |
| Semistability at two for even \(C\) | Passed | The finite flat proper model has exactly two nodes, rational normalization, and four distinguished branches. |
| Torus Frobenius at two | Passed | Both \(\mathbf F_4\)-rational nodes are nonsplit; the saturated integral filtration gives \(-4,-4,-1,-1\). |
| One fixed global character in reciprocity | Passed | Both principal ideles are evaluated under the same \(\nu\), with the same Frobenius convention. |
| Good-at-seven comparison | Passed | Finite étale model and Raynaud uniqueness preserve the exact unramified representation, not merely its trivialization after extension. |
| Cartier/Frobenius conversion | Passed | Squared semilinear operator is scalar; full degree-four Frobenius polynomial annihilates the endomorphism. |
| Local zero-rank obstruction | Passed | Connected special-fiber torsion has no nonzero finite étale subquotient, including after coefficient extension. |
| Odd-\(C\) terminal contradiction | Passed | Roots of either displayed quadratic have eighth power four modulo seven. |
| Even \(C\), \(7\mid C\) | Not addressed | Good-reduction comparison at seven is unavailable. |
| Nonexistence, modular-form elimination, full Beal | Out of scope | None follows from residual irreducibility alone. |

## Critical independent derivations

### Coefficients, lattices, and global characters

Let \(\rho\) be the residual RM representation over \(\mathbf F_{49}\). Upon restriction of scalars and extension to \(\overline{\mathbf F}_7\), its four-dimensional representation is the direct sum of the two coefficient-embedding representations. Thus every character of a hypothetical decomposition \(\rho^{\mathrm{ss}}=\lambda\oplus\mu\) occurs in the scalar-extended semisimplification of \(J[7]\). The characters themselves need not be \(\mathbf F_{49}\)-valued.

A stable lattice over the unramified quadratic coefficient ring has an underlying \(\mathbf Z_7\)-lattice commensurable with \(T_7J\). Residual semisimplification is independent of this choice. One elementary justification is to put two such lattices into a common nested pair and use the multiplication-by-seven kernel/cokernel sequences of their finite quotient; the two reductions have the same class in the representation Grothendieck group. Consequently no maximality of the specialized integral endomorphism order is needed.

Write \(\delta=\det\rho\) and let \(\chi\) be the mod-seven cyclotomic character. The determinant of restriction of scalars is the coefficient norm, so

\[
\delta^8=\operatorname{Norm}_{\mathbf F_{49}/\mathbf F_7}\delta
=\det_{\mathbf F_7}J[7]=\chi^2.
\]

At three and five, this makes \(\delta\) trivial on wild inertia: its finite abelian wild image is a three-group or five-group, and eighth powers are injective on either. If one constituent were wild, so would the other; each one-dimensional wild character has Artin conductor at least two. Residual reduction and semisimplification cannot increase the total conductor. Both characters are therefore tame. Frobenius conjugation then bounds their inertia orders by \(9-1=8\) and \(5-1=4\), respectively. This argument is valid over arbitrary finite coefficient extensions.

The two local weights at seven lie in \(\{0,1\}\). Hence the possible fundamental-character exponents are \(0,1,7,8\). Since \(\bar\phi\) has order sixteen, reciprocity for \(\lambda^8\) forces its exponent to be even; the only surviving choices are zero and eight. The same holds for \(\mu\). The determinant congruence

\[
8(e+f)\equiv16\pmod{48}
\]

then leaves exactly \((e,f)=(0,8),(8,0)\). One global constituent \(\nu\) is unramified at seven and everywhere outside three and five. Its eighth power is unramified at every finite place and trivial at the real places. The norm-Euclidean argument in the predecessor proves ordinary class number one; global class field theory therefore gives \(\nu^8=1\). Using the ordinary class group is legitimate because the archimedean character has already been killed.

### Stable model, torus, and Frobenius at two

For odd \(A,B\), differentiation of the reduced affine equation gives singular points \((r,r)\), where \(r^2+r+1=0\). The tangent polynomial is

\[
t^2+r^2st+r^2s^2.
\]

With slope \(t=ks\), then \(k=r^2z\), its splitting equation becomes \(z^2+z=r\). Its right side has absolute trace one in \(\mathbf F_4\). Each node is rational over \(\mathbf F_4\), but its two branches are exchanged by arithmetic Frobenius. Therefore Frobenius acts by \(-I_2\) on both integral graph homology groups. Passing to the minimal regular model merely subdivides the loops by rational chains and preserves this equivariant homology.

The integral semistable filtration, whose middle abelian piece is zero here, gives

\[
0\longrightarrow H^1(\Gamma,\mathbf Z)\otimes\mathbf Z_7(1)
\longrightarrow T_7J
\longrightarrow H_1(\Gamma,\mathbf Z)\otimes\mathbf Z_7
\longrightarrow0.
\]

Arithmetic Frobenius multiplies the Tate twist by four. Its characteristic polynomial is therefore \((T+4)^2(T+1)^2\). The free graded pieces justify reduction modulo seven. This is a calculation on the full module for any Frobenius lift; it is not an unjustified good-reduction point count on a singular fiber. Since \((-4)^8=2\) and \((-1)^8=1\) modulo seven, \(\nu^8=1\) forces \(\nu(\mathrm{Frob}_{(2)})=-1\).

### Reciprocity preserves the character label

The unit \(\phi^4=3\phi+2\) is totally positive. Its residues at the primes above three and five are \(-1\) and \(1\). Tameness and reciprocity thus force the local unit character \(\nu_{(3)}(-1)=1\).

The positive rational number \(2/7\) has the same two residues. At the inert primes above two and seven it has valuations \(+1\) and \(-1\), respectively; all other finite valuations vanish. The other local factors are one, giving

\[
\nu(\mathrm{Frob}_{(2)})\nu(\mathrm{Frob}_{(7)})^{-1}=1.
\]

This equality is between values of the same global character. No independent choices of compatible local characters have been substituted. Reversing the Frobenius convention reverses both sides consistently and leaves the value \(-1\) unchanged.

### Finite-flat transport and the Frobenius value at seven

Suppose \(7\nmid C\). The smooth good reduction is over the unramified quadratic seven-adic field, so \(e=1<6\). Descend an unramified \(\overline{\mathbf F}_7\)-constituent to a finite field \(E\). Its underlying \(\mathbf F_7\)-representation is a subquotient of \(J^m[7]\), with \(m=[E:\mathbf F_7]\). Schematic closures and their finite flat quotient give a model of this generic representation. The unramified representation also has a finite étale model. Raynaud's theorem identifies these two models over the original DVR, with the generic identification preserved. Therefore the special-fiber subquotient has the original arithmetic Frobenius action.

The quotient map is surjective on geometric points: every nonempty finite fiber over an algebraically closed field has a point. Thus the transported representation is an actual Frobenius-stable subquotient of the special-fiber geometric seven-torsion. This avoids confusing a group-scheme subquotient with an unrelated representation of the same dimension.

The independent Cartier coefficient derivation gives

\[
M=\begin{pmatrix}0&A^2B\\A&0\end{pmatrix},\qquad
M^2=aI_2,\qquad a=\bar A^3\bar B.
\]

Over \(\mathbf F_{49}\), the second iterate of either relevant semilinear operator is scalar. The checked Frobenius congruence is

\[
P_{49}(T)\equiv T^2(T-a)^2\pmod7.
\]

The integral polynomial \(P_{49}\) annihilates the Frobenius endomorphism: apply Cayley–Hamilton on an auxiliary prime-to-seven Tate module and use faithfulness of that Tate-module action on endomorphisms. It follows that it annihilates the action on geometric seven-torsion, all its powers, and their subquotients. Arithmetic Frobenius on those geometric points is the forty-nine-power morphism. Its value on an unramified constituent is invertible, so it must equal \(a\ne0\). The argument applies to all coefficient conjugates of the descended representation and hence to the original \(E\)-line.

Reciprocity and the two-adic calculation now force \(a=-1\). In \(\mathbf F_7\), this gives \(B=-A^{-3}=-A^3\), since \(A^6=1\). Consequently

\[
A^3+B^5=A^3-A^{15}=0,
\]

contrary to \(7\nmid C\). If \(a=0\), the same polynomial already excludes a nonzero unramified constituent; the separately proved zero-\(7\)-rank obstruction is consistent with this stronger transport statement.

## Primary-source checks and search boundary

These were exact theorem/application checks, not a novelty search. Primary texts were read online; no source PDF was added to the project by this auditor. The initial direct versioned Larson–Vaintrob URL failed, but the unversioned PDF was available and its first page explicitly identified it as v4, so the required version was authenticated.

| Primary source | Exact checked input and translation |
|---|---|
| [Pacetti–Villagra Torcomian, arXiv:2512.17845v1](https://arxiv.org/html/2512.17845v1), 19 December 2025 | §7.1 equation (32) supplies the genus-two realization; Corollary 3.6 and Proposition 3.14 give the needed conductor upper bounds at three and five. Apply \((q,r,p)=(5,3,7)\) and \((a,b,c)=(B,-C,A)\). Neither conductor statement presupposes the residual irreducibility being proved here. |
| [Larson–Vaintrob, arXiv:1110.0255v4](https://arxiv.org/pdf/1110.0255), 30 March 2012 | The initial definition permits subquotients after algebraic-closure coefficient extension. Definition 2.8 makes algebraic degree the maximum of the absolute embedding weights. Lemma 4.10, printed p.25, applies to semistable reduction and gives degree at most \(d e\). Taking \(d=e=1\) gives the two weights used here. No large-prime hypothesis belongs to this lemma. |
| [Raynaud, BSMF 102 (1974), 241–280](https://www.numdam.org/article/BSMF_1974__102__241_0.pdf), DOI 10.24033/bsmf.1779 | Theorem 3.3.3 and Corollary 3.3.6(1), printed p.268, give finite-flat uniqueness and extension of generic morphisms with flat kernel/cokernel when \(e<p-1\). This mixed-characteristic DVR statement does not require algebraically closed residue field. It applies to the finite étale comparison before any unramified extension, preserving the Frobenius label. |
| [Deligne–Mumford, PMIHÉS 36 (1969), 75–109](https://www.numdam.org/item/PMIHES_1969__36__75_0.pdf) | Proposition 2.3 relates stable and regular semistable models. Theorem 2.4 and its forward proof using Theorem 2.5, printed p.89, identify the connected Jacobian reduction with the generalized Jacobian of the nodal fiber. The forward semistability implication includes residue characteristic two. |
| [Dokchitser–Dokchitser–Morgan, arXiv:1809.10208v2](https://arxiv.org/pdf/1809.10208), 18 February 2020; Proc. AMS 149 (2021), 1361–1372 | Theorem 1.5 and Corollary 4.8 give the integral equivariant filtration. Remark 4.7 checks saturation and the residue-cardinality action on the Tate twist. The local field and prime-to-residue-characteristic hypotheses allow \(K_2\) and \(\ell=7\). Its graph is that of the regular model, handled by the rational subdivisions above. |
| [Achter–Howe, author manuscript, §2.5](https://www.math.colostate.edu/~achter/math/hwcm0618.pdf) | The explicitly stated congruence for the relative Frobenius endomorphism of the Jacobian gives \(P_{49}(T)\bmod7\) from the second iterate of Hasse–Witt or Cartier. This audit uses that precise full-polynomial formula, not an unspecified reciprocal convention for a rank-two factor. |

Standard Weil pairing, norm determinants, local/global reciprocity, ordinary class field theory, and residual lattice independence are used at their explicitly stated levels. Their elementary application here was rederived above. No theorem asserting modularity or level lowering was substituted for any of these inputs.

Commands used to inspect and pin the proof artifacts were `rg --files`, `cat` on the eight listed files, and `sha256sum` on those files. No unrelated finite sweeps were rerun. The finite coefficient and congruence calculations above were rederived algebraically, so the verdict does not depend on an unchecked enumerator.

## Remaining boundary and cheapest next check

The strongest safe conclusion is the boxed absolute-irreducibility statement. The step that fails outside its scope is specifically the replacement of an unramified generic subquotient by a subquotient of a good special fiber at seven: when \(7\mid C\), this fiber is semistable and singular, and the abelian-scheme argument in `ordinary7_candidate.md` is unavailable.

The next local question is therefore the Frobenius value of the unramified constituent for the semistable, bad-at-seven branch \(14\mid C\). It must be checked on the relevant semistable seven-torsion filtration; the good-reduction Cartier matrix cannot be reused. Independently of that remaining branch, applying level lowering and eliminating all possible forms are separate unsolved obligations in this audit's scope.
