# An ambient dual slice for the pure cubic Hilbert 12 experiment

**Author:** Komorebi P.  
**Research status:** New exact organization and checks of finite algebra. The analytic comparison is open.  
**Working case:** \(K=\mathbb Q(\beta)\), \(\beta^3=7\), with the selected complex embedding.

## Abstract

The cubic unit matrix in the pure cubic elliptic gamma experiment admits a codifferent self-adjoint pairing whose reduction at seven is a length-three Frobenius algebra. Its socle and top quotient are dual. Complementary Eisenstein torsion points reveal the familiar cubic Gauss sum, and cubing removes the nonzero character-slice choice. Pairing fixed eigendirections alone gives the trivial character, so a moving generalized-eigenvector direction is essential. The geometric principal-seven gamma shift is exactly the universal-cover projection of the sum of the two complementary Eisenstein torsion components. Finally, the cubic character projection of the seven gamma translates admits two meromorphic scalar coordinates with a precise order-three monomial action. Its putative one-coordinate logarithmic product is obstructed by a nonintegral residue. None of these observations supplies the missing analytic-to-arithmetic equality.

## 1. Arithmetic module and codifferent

Put \(\omega^2+\omega+1=0\), \(J=2+3\omega\), \(\bar J=-1-3\omega\). Then \(J+\bar J=1\), \(J\bar J=7\). With

\[
L=\mathbb Z(\beta^2+2\beta)+\mathbb Z(-\beta-2)+15\mathbb Z
\]

and basis \(b_0=\beta^2+2\beta\), \(b_1=-\beta-2\), \(b_2=15\), multiplication by \(\epsilon=2-\beta\) has matrix

\[
M=\begin{pmatrix}0&1&0\\-4&2&15\\-1&0&4\end{pmatrix},\quad \det M=1.
\]

The coefficient functional \(\lambda(x)=[\beta^2]x\), applied after reduction via \(\beta^3=7\), is equivalently \(\operatorname{Tr}_{K/\mathbb Q}(x/(3\beta^2))\). The Gram matrix \(H_{ij}=\lambda(b_i b_j)\) is

\[
H=\begin{pmatrix}4&-4&15\\-4&1&0\\15&0&0\end{pmatrix},\qquad \det H=-225,\qquad M^{\mathsf T}H=HM.
\]

Also \((M-2I)^3=-7I\). Thus over \(\mathbb F_7\), \(N=M-2I\) has one nilpotent block of length three. Set \(u=(1,2,4)^{\mathsf T}\), \(v=(0,1,2)^{\mathsf T}\), \(w=(0,0,1)^{\mathsf T}\). Then \(Nu=0\), \(Nv=u\), \(Nw=v\) modulo seven, and

\[
[u\ v\ w]^{\mathsf T}H[u\ v\ w]\equiv
\begin{pmatrix}0&0&1\\0&1&0\\1&0&0\end{pmatrix}\pmod7.
\]

Indeed \(u\) represents \(\beta^2+56\equiv\beta^2\), \(v\) represents \(28-\beta\equiv-\beta\), and \(w\) represents \(15\equiv1\) in \(\mathbb F_7[\beta]/(\beta^3)\). The codifferent pairing extracts the coefficient of \(\beta^2\). It is perfect, and pairs the socle against the top quotient. In particular, \(u^{\mathsf T}H\) vanishes on \(\ker N^2=\operatorname{span}(u,v)\) and is nonzero on \(w\).

This is a classical Frobenius-algebra mechanism realized by the specific Hilbert 12 unit matrix. No novelty claim is attached to Frobenius duality itself.

## 2. CM torsion and a fixed-point no-go theorem

On \(A=E_\omega^3\), \(E_\omega=\mathbb C/\mathbb Z[\omega]\), use the product principal Weil pairing composed with the integral symmetric isogeny represented by \(H\). For seventh-torsion coordinates \(X=(a+\omega b)/7\), \(Y=(c+\omega d)/7\), write

\[
e_{7,H}(X,Y)=\zeta_7^{a^{\mathsf T}Hd-b^{\mathsf T}Hc}.
\]

The pairing is perfect since \(7\nmid\det H\). Its source is the canonical pairing of \(A[7]\) with \(A^\vee[7]\). The symmetric map \(H:A\to A^\vee\) need not define an ample polarization: it is indefinite. The exact matrix identity gives contragredient covariance

\[
e_{7,H}(MX,M^{-1}Y)=e_{7,H}(X,Y).
\]

Define \(P=u/J\), \(P'=u/\bar J\), and \(Q=w/\bar J\). The coefficient expansions \(1/J=(-1-3\omega)/7\) and \(1/\bar J=(2+3\omega)/7\) yield

\[
e_{7,H}(P,Q)=\zeta_7^3,\qquad e_{7,H}(P,P')=1.
\]

**Fixed-point no-go theorem.** If \(Y=a/\bar J\) is an opposite-twist fixed direction, equivalently \(Ma=2a\pmod7\), then \(a\) is a multiple of \(u\) because \(\ker(M-2I)\) is one-dimensional. Consequently \(e_{7,H}(P,Y)=1\). Thus this pairing cannot recover the Gauss phase from opposite fixed eigendirections alone. One must use the generalized eigenchain, a covariantly transported dual, or an equivalent extension datum.

The nontrivial phase remains unchanged for \(Q=(w+su+tv)/\bar J\), since \(u\) pairs trivially with \(u,v\) modulo seven. Other nonzero top-quotient choices produce phases \(\zeta_7^{3r}\), \(r\in\mathbb F_7^\times\).

There cannot be a positive definite real symmetric matrix \(H_+\) with \(M^\mathsf TH_+=H_+M\): that would make \(M\) similar to a real symmetric matrix, but \(\chi_M(X)=X^3-6X^2+12X-1\) has negative discriminant \(-1323\) and two nonreal roots. Hence the Poincare duality description is safer than requiring an invariant ample polarization. Positive-definite lifts congruent to \(H\) modulo seven still give the same finite pairing, but do not preserve the global self-adjoint identity.

## 3. Universal Gauss-cube lemma

Let \(\chi(1),\ldots,\chi(6)=(1,\omega,\omega^2,\omega^2,\omega,1)\) and \(G_r=\sum_{k=1}^{6}\chi(k)\zeta_7^{rk}\). Then for every \(r\ne0\),

\[
G_r=\chi(r)^{-1}G_1,\qquad G_r^3=7J.
\]

The first identity follows by index substitution and the second by the classical Gauss and Jacobi identities. All six cubes were also checked by exact coefficient convolution in \(\mathbb Z[\omega,z]/(\omega^2+\omega+1,z^7-1)\). Thus \((G_r/\beta)^3=J\), independent of the chosen nonzero dual direction. The individual cube-root branch is not fixed by this statement.

Equivalently, the primitive multiplicative-character projector applied to the additive function \(f(k)=e_{7,H}(kP,Q)=\zeta_7^{3k}\) produces \(G_3/6\):

\[
(\Pi_{\chi^{-1}}f)(1)=\frac16\sum_{k\ne0}\chi(k)f(k)=\frac{G_3}{6}.
\]

## 4. Direct link to the principal-seven gamma cover

In the original analytic period row \(p=(\tau,\sigma,1)\), let

\[
\tau=\frac{\beta^2+2\beta}{15},\quad\sigma=-\frac{\beta+2}{15},\quad
\delta=\frac{\tau+2\sigma+4}{7}=\frac{\beta^2+56}{105}.
\]

The period projection \(\pi(v)=pv\) on the universal cover satisfies \(\pi(u/7)=\delta\), \(\pi(w)=1\), and

\[
P+P'=\frac{u}{7},\quad\pi(P)=\bar J\delta,\quad\pi(P')=J\delta,\quad\pi(P+P')=\delta.
\]

Thus the exact principal-seven shifts \(z+k\delta\) in the earlier gamma-divisor paper are the projections of \(k(P+P')\). This holds **on the universal cover**; \(\pi\) does not automatically descend from \(A=\mathbb C^3/\mathbb Z[\omega]^3\) to the original triptic quotient because of the extra Eisenstein periods. The missing deck multipliers cannot be discarded.

From \(\beta\delta=-8\sigma-1\) follows the exact unit carry

\[
\epsilon\delta=2\delta+8\sigma+1,\qquad\epsilon=2-\beta.
\]

Hence unit multiplication acts on the seven cover labels by \(k\mapsto2k\pmod7\), with explicit period shifts. The inverse unit acts by \(k\mapsto4k\). These are precisely the finite orbits present in the earlier divisor-transport calculations.

## 5. Two honest meromorphic coordinates for the primitive cubic sector

Let \(F(z)=\Gamma_{\mathrm{ell}}(z;\tau,\sigma)^5/\Gamma_{\mathrm{ell}}(5z;5\tau,5\sigma)\) and \(f_k(z)=F(z+k\delta)\). The inherited principal-seven product is \(P_7(z)=\prod_{k=0}^6 f_k(z)\), the trivial character sector.

The cubic character \(\chi(k)=a_k+\omega b_k\) has integer coefficient vectors

\[
(a_1,\ldots,a_6)=(1,0,-1,-1,0,1),\quad
(b_1,\ldots,b_6)=(0,1,-1,-1,1,0).
\]

Define the two ordinary meromorphic functions

\[
A(z)=\frac{f_1f_6}{f_3f_4},\qquad
B(z)=\frac{f_2f_5}{f_3f_4}.
\]

Then the character weighted logarithmic derivative

\[
D_\chi(z)=\sum_{k=1}^6\chi(k)\frac{f'_k(z)}{f_k(z)}
=\frac{A'(z)}{A(z)}+\omega\frac{B'(z)}{B(z)}
\]

is unambiguous and meromorphic. Under formal unit relabeling \(f_k\mapsto f_{2k\bmod7}\) the functions transform exactly as

\[
(A,B)\longmapsto(B/A,1/A),\qquad
T=\begin{pmatrix}-1&1\\-1&0\end{pmatrix},\quad T^3=I.
\]

The eigenvalues of \(T\) are \(\omega,\omega^2\), and \(D_\chi\) transforms by \(\omega^2\). This relabeling statement is exact, but it is **not** by itself an analytic functional equation under \(z\mapsto\epsilon z\): the period carries and the gamma unit cocycle must be included.

There is a concrete obstruction to replacing the pair \((A,B)\) by a single character-power product. The prior divisor formula gives \(\operatorname{ord}_\tau F=4\), and \(\delta\) has order seven modulo \(\Lambda_5=\mathbb Z\tau+\mathbb Z\sigma+(1/5)\mathbb Z\). At \(z=\tau-2\delta\), exactly the term \(f_2\) has a zero, hence

\[
\operatorname{Res}_{z=\tau-2\delta}D_\chi(z)=4\chi(2)=4\omega.
\]

A logarithmic derivative of a single-valued meromorphic function has an integer residue. Since \(4\omega\notin\mathbb Z\), **no single meromorphic scalar** has logarithmic derivative \(D_\chi\). The two-component meromorphic realization avoids this obstruction and carries an integral order-three monomial action.

This residue conclusion uses the inherited divisor theorem, not a new independent analytic proof of that theorem.

## 6. Exact carry as a calculational next step

The inherited shift law is \(F(z+\sigma)/F(z)=q_t(z)^{-1}\), where \(t=-\tau\) and \(q_t(z)=\theta_0(z;t)^5/\theta_0(5z;5t)\). Therefore for \(k=1,\ldots,6\),

\[
F(\epsilon(z+k\delta))=
F(\epsilon z+2k\delta)
\prod_{j=0}^{8k-1}q_t(\epsilon z+2k\delta+j\sigma)^{-1}.
\]

This is an explicit theta-carry formula for the same label permutation driving the two coordinate monomials. Its utility is to separate the **known period carry** from the **unknown genuine unit descent/comparison**.

## 7. Missing theorem and exact claim boundary

The analytic-to-arithmetic equality \(U_\Gamma=U_{\mathrm{alg}}\) is still unproved. In the later polarized presentation the remaining statement is \(\operatorname{Im}(C_{\mathrm{pol}}U_\Gamma^3)=0\), given the established modulus and independent branch conditions. The two-coordinate packet identifies where a primitive character can live, but no identification with the analytic gamma packet has been proved. In particular, no gerbe trivialization, Eisenstein deck descent, normalized scalar comparison, or new Lean compilation is supplied here.

Next test: use the exact theta carries and existing cocycle data to determine whether the unit-scaled analytic two-coordinate packet has the predicted monomial transformation with a **computable, normalized multiplier**. A theorem controlling that multiplier, not simply the finite Weil pairing, is required to close the gap.

## Sources and provenance

1. Bergeron, Charollois and García, *Elliptic units for complex cubic fields*, arXiv:2311.04110v2 (2023). Algebraicity and reciprocity are conjectural; a logarithmic modulus formula is proved.
2. Teymour Gray, *Cocycle Relations and Elliptic Gamma Values*, arXiv:2610.10365v2 (19 October 2026). Proves congruence independence of admissible elements under stated hypotheses. Does not prove algebraicity or the present scalar comparison.
3. The earlier Komorebi cubic working archive, `Komorebi_H12_ALL_MARKDOWN_2026-10-02.md`, including the unit matrix and Jacobi calculation.
4. `PROOF(20261003-233652).md`, for the complementary torsion and gerbe descent obstruction.
5. `Cubic Divisor Transport and Reconstruction`, 8 October 2026, for the principal-seven product, divisor formulas, and remaining polarized reality target.

Run `python h12_ambient_dual_slice_verify.py` to reproduce the fresh finite-algebra checks. This checker does not prove the analytic input, does not invoke Lean, and does not claim a solution of Hilbert's twelfth problem.
