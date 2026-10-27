# A normal weighted-Fano carrier for a Fermat degree-70 Hodge packet

Research note, 21 September 2026, America/Chicago.

**Status:** Manuscript-level special-case proof, with a separately replayable exact algebraic certificate. The geometric proof is not Lean-verified or independently reviewed. This note does not prove the general Hodge conjecture, does not cover every degree-70 packet, and makes no historical novelty claim.

## 1. Precise statement

Write

\[
X_m=\{x_0^m+\cdots+x_5^m=0\}\subset\mathbf P^5_\mathbf C.
\]

The diagonal group is \(G_m=(\mu_m)^6/\mu_m\). For a character \(a=(a_0,\ldots,a_5)\) with all entries nonzero modulo \(m\) and sum zero modulo \(m\), let \(W_{[a]}\) denote the rational character-orbit summand of primitive \(H^4(X_m,\mathbf Q)\).

**Proposition.** For

\[
m=70,\qquad a=(1,20,24,42,61,62),
\]

all classes in the 24-dimensional rational space \(W_{[a]}\) are rational linear combinations of classes of algebraic surfaces on \(X_{70}\). For every positive integer \(k\), the corresponding pulled-back packet \(W_{[ka]}\) on \(X_{70k}\) is also algebraic.

The proof below uses the established rational Hodge theorem for smooth projective uniruled fourfolds. It constructs the carrier and the monomial correspondence explicitly. It does **not** list equations for a basis of the surfaces supplied by that theorem.

## 2. Hodge type of the packet

The primitive Fermat eigenspaces for full-support characters are one-dimensional over the splitting field. The Griffiths residue description assigns type \((2,2)\) when the least-positive residues have sum \(3m\). A rational orbit is of type \((2,2)\) precisely when this holds for all its unit conjugates.

For every \(t\in(\mathbf Z/70\mathbf Z)^\times\), exact enumeration gives

\[
\sum_{i=0}^{5}\langle ta_i\rangle_{70}=210.
\]

There are 24 conjugates, all distinct because \(a_0=1\). Thus the entire rational orbit, not just a single complex residue vector, has type \((2,2)\). The verifier stores every conjugate. The distinction between a complex residue vector and a rational Hodge class is essential here.

The standard residue basis follows from Griffiths' description; a modern source with the formula is Villaflor Loyola, *Small codimension components of the Hodge locus containing the Fermat variety*, arXiv:2001.01019, Section 1. For Fermat, the basis monomials diagonalize the group action, giving the character description used here.

## 3. The exact carrier

Let

\[
A=\begin{pmatrix}
0&0&2&0&0&3\\
0&0&1&2&7&0\\
1&0&2&2&0&1\\
0&5&0&0&0&0\\
0&0&0&2&0&3\\
3&0&0&0&0&0
\end{pmatrix}.
\]

Rows are monomial exponents; columns correspond to \(y_0,\ldots,y_5\). Direct rational arithmetic gives

\[
\det A=-2100,\qquad
A^{-1}\mathbf1=(1/3,1/5,1/10,1/10,1/10,4/15),
\]

\[
\mathbf1^TA^{-1}\mathbf1=11/10.
\]

Set \(W=(10,6,3,3,3,8)\) and \(D=30\), so \(AW=D\mathbf1\). Define

\[
Y=\{F=0\}\subset\mathbf P(10,6,3,3,3,8),
\]

\[
F=y_0^3+y_1^5+y_2^2y_5^3+y_2y_3^2y_4^7
  +y_0y_2^2y_3^2y_5+y_3^2y_5^3.
\]

Every monomial has weighted degree 30. The adjunction coefficient is

\[
D-\sum W_i=30-33=-3.
\]

This model is singular and is not quasismooth. The argument therefore cannot invoke a quasismooth residue theorem or assume that its resolution is Fano. Normality and uniruledness are proved separately below.

## 4. An explicit finite cover on the tori

Let \(M=210\), \(\alpha=3a\), and

\[
B=210A^{-1}=\begin{pmatrix}
0&0&0&0&0&70\\
0&0&0&42&0&0\\
42&0&63&0&-63&-21\\
-63&0&63&0&42&-21\\
12&30&-27&0&-3&9\\
42&0&-42&0&42&14
\end{pmatrix}.
\]

Then

\[
AB=210I,\qquad B\mathbf1=7W.
\]

On the projective tori define \(y_i=\prod_jx_j^{B_{ij}}\). Negative exponents are allowed there. The second identity makes this well-defined into the weighted projective torus; the first gives

\[
F(y(x))=x_0^{210}+\cdots+x_5^{210}.
\]

The induced map of five-dimensional tori is an isogeny. Consequently its restriction is a finite étale cover

\[
q:U_{210}\longrightarrow U_Y,
\]

where \(U_{210}=X_{210}\cap\{\prod x_i\ne0\}\) and \(U_Y=Y\cap\{\prod y_i\ne0\}\).

The target torus hypersurface is smooth because its finite étale pullback is smooth. It is irreducible because its Laurent polynomial pulls back under an injective full-rank monomial substitution to an irreducible Fermat Laurent polynomial. Non-monomial factors remain non-monomial under this substitution. The polynomial \(F\) has no coordinate factor, so its projective closure \(Y\) is also irreducible.

## 5. Normality and the canonical class

Put \((u,v,s,t,c,z)=(y_0,y_1,y_2,y_3,y_4,y_5)\), so

\[
F=u^3+v^5+z^3(s^2+t^2)+st^2c^7+us^2t^2z.
\]

Its gradient is

\[
\begin{aligned}
F_u&=3u^2+s^2t^2z, &F_v&=5v^4,\\
F_s&=2sz^3+t^2c^7+2ust^2z,
&F_t&=2t(z^3+sc^7+us^2z),\\
F_c&=7st^2c^6,
&F_z&=3z^2(s^2+t^2)+us^2t^2.
\end{aligned}
\]

The cone singular locus is exactly

\[
\{y_0=y_1=y_2=y_3=0\}
\ \cup\ \{y_0=y_1=y_3=y_5=0\}
\ \cup\ \{y_0=y_1=y_4=y_5=0\}.
\]

Here is a direct verification of exhaustion. At a singular point, \(v=0\) and \(st^2c^6=0\). The cases \(s=0\) or \(t=0\) give the displayed planes immediately from the other derivatives. In the remaining case \(s,t\ne0\), one has \(c=0\). If \(z=0\), then \(u=0\), giving the third plane. If \(z\ne0\), the equations \(F_s=F_t=0\) give

\[
z^2+ut^2=z^2+us^2=0.
\]

Hence \(s^2=t^2=R\ne0\) and \(u=-z^2/R\). But then \(F_z=5Rz^2\ne0\), a contradiction.

There is also an independent exact ideal certificate. For the gradient ideal \(J\), the verifier proves

\[
\sqrt J=(y_0,y_1,y_2y_5,y_3y_4,y_3y_5).
\]

It checks that the gradient vanishes on the three planes and that the powers

\[
y_0^3,\quad y_1^4,\quad (y_2y_5)^3,\quad
(y_3y_4)^{13},\quad (y_3y_5)^3
\]

belong to \(J\) by Gröbner reduction over \(\mathbf Q\). The ideal on the right is the intersection of the three coordinate prime ideals, so these two inclusions prove equality of radicals.

The cone has dimension five and singular locus dimension two. It is a hypersurface, hence Cohen–Macaulay, and is regular in codimension one. Serre's criterion proves normality. Taking the weighted quotient preserves normality.

The ambient weighted projective space is well formed. Its largest singular stratum is the \(\mu_3\)-stratum \(y_0=y_5=0\), of dimension three. The restriction of \(F\) there is \(y_1^5+y_2y_3^2y_4^7\), not identically zero. All other ambient singular strata have dimension at most two. Thus \(Y\) meets the ambient singular locus in codimension at least two. The verifier checks all coordinate strata, not just the largest one.

On the smooth ambient locus, the weighted Euler sequence gives canonical class \(-33H\). Ordinary hypersurface adjunction gives \(-3H\) on the smooth part of \(Y\) there. Both complements have codimension at least two, so normality extends the equality as a canonical Weil divisor class:

\[
K_Y\sim_{\mathbf Q}-3H.
\]

Here \(H\) is the ample rational hyperplane class, not an assertion that \(\mathcal O_Y(1)\) is everywhere a line bundle. This argument establishes the adjunction formula in the present non-quasismooth example directly.

## 6. Why a resolution is uniruled

Take a projective resolution \(r:\widetilde Y\to Y\) which is an isomorphism over \(U_Y\). A general complete-intersection curve \(C\) cut out by three sufficiently ample Cartier divisors avoids the singular locus of \(Y\), which has dimension at most two. Its strict transform avoids the exceptional divisors. Therefore

\[
K_{\widetilde Y}\cdot\widetilde C=K_Y\cdot C=-3H\cdot C<0.
\]

These curves move in a covering family. Thus \(K_{\widetilde Y}\) is not pseudoeffective. The theorem of Boucksom–Demailly–Păun–Peternell implies that \(\widetilde Y\) is uniruled.

No assertion of log terminal singularities, rational connectedness, or Fano positivity on the resolution is used.

The rational Hodge conjecture for smooth projective uniruled fourfolds is a proved theorem of Conte–Murre, also stated as Corollary 4.2 of Arapura, arXiv:0706.2506. Therefore every rational \((2,2)\)-class on \(\widetilde Y\) is algebraic.

For context, this theorem does not use the unknown general fourfold case: a uniruled fourfold is dominated generically finitely by a resolution of \(T\times\mathbf P^1\), with \(\dim T=3\). The relevant Hodge classes on the product are algebraic by the threefold case and Künneth; blowup centers have dimension at most two; push-pull transfers algebraicity.

## 7. The packet is actually carried by this cover

It remains to verify that the target is not merely a convenient variety unrelated to the desired character.

Direct computation gives

\[
A^Ta=70\beta,\qquad \beta=(3,3,1,3,2,3),
\]

and hence \(B^T\beta=\alpha\). To obtain a genuine character of the projective torus, let \(r_0=(0,0,2,0,0,3)\) be the first row of \(A\) and set

\[
u=\beta-3r_0=(3,3,-5,3,2,-6).
\]

Then

\[
W\cdot u=0,\qquad B^Tu=\alpha-630e_0.
\]

Thus \(u\) is a character of the weighted projective torus. Its pullback restricts on \(G_{210}\) to the Fermat character \(\alpha\), since \(630=3\cdot210\).

Let \(K\) be the kernel of the torus isogeny. The relation \(AB=210I\) shows that \(K\) embeds in \(G_{210}\): an element in the kernel has representatives whose 210th powers are all the same, and a common scalar makes them roots of unity. The displayed character identity proves \(\chi_\alpha|_K=1\). The same holds for every rational conjugate. Therefore the whole rational packet is \(K\)-invariant.

## 8. Boundary control and Hodge lifting

### 8.1 No full-support packet is lost at the Fermat boundary

The coordinate boundary of \(X_{210}\) is a simple normal crossing divisor. Every nonempty coordinate stratum is fixed pointwise by at least one coordinate scaling subgroup \(\mu_{210}\). Our full-support character is nontrivial on that subgroup. The same is true for every character in its rational orbit.

In the boundary Gysin spectral sequence, the corresponding character projector therefore kills every boundary term. The normal orientation/Tate factors have trivial coordinate-scaling action. Consequently restriction induces an isomorphism on the packet:

\[
e_{[\alpha]}H^4(X_{210},\mathbf Q)
\xrightarrow{\sim}
e_{[\alpha]}H^4(U_{210},\mathbf Q).
\]

This argument is independent of any asserted torus-residue extension for singular weighted hypersurfaces.

### 8.2 Descent to the open carrier

Because \(q\) is finite étale with deck group \(K\),

\[
q^*:H^4(U_Y,\mathbf Q)
\xrightarrow{\sim}H^4(U_{210},\mathbf Q)^K.
\]

This is an isomorphism of mixed Hodge structures onto its image. Normalized transfer supplies the inverse. The rational pure \((2,2)\)-packet therefore descends to a pure weight-four Hodge substructure of \(H^4(U_Y,\mathbf Q)\).

### 8.3 Lifting is justified by the lowest-weight theorem

Deligne's Corollary 3.2.17 in *Théorie de Hodge II* gives

\[
W_4H^4(U_Y,\mathbf Q)
=\operatorname{im}\bigl(H^4(\widetilde Y,\mathbf Q)
\to H^4(U_Y,\mathbf Q)\bigr).
\]

Here \(W_4\) denotes the weight filtration, not the Fermat packet notation. The descended classes have weight four, so belong to this image. The category of polarizable pure rational Hodge structures is semisimple. The surjection from \(H^4(\widetilde Y)\) onto its image thus has a Hodge-theoretic section. Every descended rational \((2,2)\)-class has a rational \((2,2)\)-lift on \(\widetilde Y\).

This lifting is not being inferred from an arbitrary complex residue numerator. Rationality, purity, and the surjection of pure Hodge structures have all been checked separately.

## 9. Producing the algebraic classes and returning to degree 70

By the uniruled-fourfold theorem, each lifted class on \(\widetilde Y\) is a rational combination of algebraic surface classes. The resolved graph of the monomial rational map

\[
X_{210}\dashrightarrow\widetilde Y
\]

defines an algebraic correspondence. Its pullback on cohomology agrees with \(q^*\) on the torus. Apply the rational orbit projector \(e_{[\alpha]}\), which is a rational linear combination of graphs of diagonal automorphisms. Therefore it preserves the span of algebraic cycle classes.

The resulting class and the prescribed class agree on \(U_{210}\); their difference lies in the packet and restricts to zero. Section 8.1 proves that difference is zero. This establishes algebraicity of the entire \(W_{[\alpha]}\) packet on \(X_{210}\).

Finally, use the finite coordinate-cube map

\[
\pi:X_{210}\longrightarrow X_{70},\qquad
[x_i]\longmapsto[x_i^3].
\]

Its pullback identifies \(W_{[a]}\) with \(W_{[3a]}\). The identity

\[
\pi_*\pi^*=(\deg\pi)\operatorname{id}
\]

then transports the algebraic classes down to \(X_{70}\). Division by the positive degree is legitimate because all cycle coefficients are rational.

For arbitrary \(k\ge1\), the coordinate-power map \(X_{70k}\to X_{70}\) pulls the same packet back algebraically. This proves the stated infinite family of packets. It does not prove the full Hodge conjecture for those varieties.

## 10. Reusable criterion and the remaining universal problem

The argument proves this criterion:

**Torus-carrier criterion.** Let \(W\) be a full-support rational middle Hodge packet on a Fermat fourfold. Suppose a finite torus isogeny identifies its open Fermat variety with the inverse image of a smooth torus hypersurface, the deck group acts trivially on \(W\), and that torus hypersurface has a smooth projective compactification for which the rational degree-four Hodge conjecture is known. Then \(W\) is algebraic.

A normal, well-formed weighted hypersurface with negative canonical hyperplane coefficient supplies one such compactification after resolution: the resolution is uniruled by Section 6.

For searching, choose nonnegative integral columns \(v_j\) satisfying \(a\cdot v_j\equiv0\pmod m\). Seek a nonsingular six-column matrix \(A\) with

\[
A^{-1}\mathbf1>0,\qquad \mathbf1^TA^{-1}\mathbf1>1.
\]

These inequalities discover candidate weights only. Normality and codimension of the ambient singular intersections still require geometric certificates.

**Matrix-carrier corollary.** Let \(a\) be a full-support balanced rational Hodge character modulo \(m\). Suppose \(A\) is a nonsingular nonnegative integral \(6\times6\) matrix such that

\[
A^Ta\in m\mathbf Z^6,\qquad A^{-1}\mathbf1>0,
\qquad\mathbf1^TA^{-1}\mathbf1>1.
\]

Let \(W/D=A^{-1}\mathbf1\), with primitive positive integral weights \(W\), and assume the row-monomial hypersurface is integral, normal, and well formed in \(\mathbf P(W)\). Then the rational Fermat packet \(W_{[a]}\) is algebraic.

Indeed, choose \(M\) divisible by \(m\) and all denominators of \(A^{-1}\). Put \(B=MA^{-1}\), \(\alpha=(M/m)a\), and \(\beta=A^Ta/m\). For any row \(r_i\) of \(A\),

\[
u=\beta-3r_i,\qquad W\cdot u=0,\qquad
B^Tu=\alpha-3Me_i.
\]

Here \(W\cdot\beta=3D\) follows from \(\sum a_j=3m\). Thus deck invariance follows uniformly from the matrix congruence; it is not an extra conjecture. The positive weight sum gives negative canonical coefficient, normality and well-formedness justify the canonical computation, and Sections 6–9 finish the proof. This corollary replaces an assumed cycle seed with a finite exponent matrix and checkable geometric hypotheses.

There is no proof here that such carriers exist for every balanced packet. Still less is there a reduction of arbitrary smooth projective varieties to these diagonal Fermat packets. Those are the missing universal coverage statements; they are not consequences of the successful example.

The earlier proposed fixed-degree central-defect realization lemma remains unproved and is not used anywhere in this proof. Likewise, this construction does not establish the general CM half-twist Chow correspondence listed as open in the pre-existing Komorebi manuscript.

## 11. Computation audit

The narrower atomic chain/loop search considered 6,600 labeled graphs and 24 unit conjugates, for 158,400 pairs. Its maximum normalized weight sum was \(296/315<1\); it found no Fano candidate in that implemented family. A broader functional-graph search also failed to find one. These failures are not evidence against the Hodge conjecture.

The unrestricted column search enumerated 1,955 invariant columns of total degree at most 18. A floating-point linear program selected a six-column support. Its result was then replaced by exact rational matrix arithmetic. The actual certificate and all conclusions about the selected matrix are independent of floating-point tolerances.

The final verifier checks 24 assertions, including every unit conjugate, matrix identities, all ambient coordinate singular strata, and the exact radical-gradient ideal certificate. It does not compute algebraic cycles, formally prove mixed Hodge theory, or independently authenticate the cited geometric theorems.

## References and external inputs

1. P. Griffiths, *On the periods of certain rational integrals I, II*, 1969. For the exact Jacobian/residue formula used here see R. Villaflor Loyola, *Small codimension components of the Hodge locus containing the Fermat variety*, arXiv:2001.01019, Section 1.
2. P. Deligne, *Théorie de Hodge II*, Publications Mathématiques de l'IHÉS 40 (1971), 5–58, Corollary 3.2.17. Numdam identifier PMIHES_1971__40__5_0.
3. P. Deligne, *Théorie de Hodge III*, Publications Mathématiques de l'IHÉS 44 (1974), 5–77. For a directly stated use of semisimplicity of pure polarizable Hodge structures, see Arapura below, proof following Lemma 2.6.
4. S. Boucksom, J.-P. Demailly, M. Păun, T. Peternell, *The pseudo-effective cone of a compact Kähler manifold and varieties of negative Kodaira dimension*, arXiv:math/0405285. Used only for the equivalence between non-uniruledness and pseudoeffectivity of the canonical bundle on a smooth projective variety.
5. A. Conte, J. P. Murre, *The Hodge conjecture for fourfolds admitting a covering by rational curves*, Mathematische Annalen 238 (1978), 79–88. The theorem is directly available in D. Arapura, *Varieties with very little transcendental cohomology*, arXiv:0706.2506, Corollary 4.2; its proof mechanism is summarized in Section 6 above.

No publication-priority audit has been completed for the displayed degree-70 carrier.
