# H12 external-source and notation check

Checked 2026-10-07. Read-only primary-source review of `sources/v014/PROOF.md`, the retained v0.13 proof, and `sources/stark_modulus/PROOF.md`. This verifies named external leaves and their local applications; it is not a novelty survey, a new proof route, or an end-to-end replay of the inherited field, ray-field, CM-branch and algebraic-unit certificates.

**Verdict.** The classical analytic and arithmetic source leaves listed below are authenticated on the checked editions. The BCG product and modulus theorem are verified on the authors’ 44-page copy; the exact arXiv `2311.04110v2` artifact remains unauthenticated. This version boundary does not turn BCG Theorem 3.2 into a conjecture. Its unit algebraicity/reciprocity claims remain conjectural. The project’s exact complex equality remains open: the missing assertion is `Im(C_pol U_Gamma^3)=0`.

## Acquisition and evidence boundary

Before acquisition, the project-local exact-version cache lookup returned no match. Root and the manuscript author reported no cached external primary PDFs. All primary sources below were read through browser extraction from their authors’ or official hosts. No external PDF was downloaded into the project and no local PDF hash is claimed. Formula and theorem text were checked, not merely search snippets. Browser screenshot calls did not expose usable image pixels; they are not counted as visual inspection.

Our exact-v2 PDF request at `https://arxiv.org/pdf/2311.04110v2` failed with `DisabledError`; `https://export.arxiv.org/pdf/2311.04110v2` was inaccessible. Root separately reported failed exact-v2 HTML/abstract requests and failed canonical Milne `CFT.pdf` retrieval. Milne’s official cropped `CFTc.pdf` succeeded and identifies itself as Version 4.03, 6 August 2020. These are recorded acquisition outcomes, not evidence against any theorem.

## Primary source register

Page numbers below are printed pages, followed by 1-based PDF pages when different. Stable URLs and checked locators are the reproducible evidence; browser IDs are retrieval trace references.

| ID | Authenticated primary source and exact locator | Retrieval trace |
|---|---|---|
| BCG | N. Bergeron, P. Charollois, L. E. García, *Elliptic units for complex cubic fields (On Eisenstein’s Jugendtraum)*, [authors’ copy](https://webusers.imj-prg.fr/~pierre.charollois/BCG_cubic.pdf), 44 pages. Product/continuation/shifts p2 (1.1); raw value p3 (1.2); hypotheses §2.2 p7; proved Theorem 3.2 p15; conjectural comparison §3.3 p16; pure-cubic example §5.2 p38. Exact manuscript date/version not authenticated. | `turn16view0`, `turn25view3`, `turn25view4`, `turn28view0`, `turn29view1`, `turn31view0` |
| MILNE | J. S. Milne, *Class Field Theory*, [official cropped PDF](https://www.jmilne.org/math/CourseNotes/CFTc.pdf), Version 4.03, 6 August 2020. Cubic reciprocity VIII Example 5.13 p249 (PDF258); Artin induction VIII §10 pp261–262 (PDF270–271). | `turn15view0`, `turn16view3`, `turn20view1`, `turn20view2`, `turn20view3` |
| COGDELL | J. W. Cogdell, *On Artin L-functions*, [author PDF](https://math.osu.edu/~cogdell/artin-www.pdf), §2.2 p12, 31 pages. Undated copy; exact publication version not authenticated. Full finite-prime factors use inertia invariants and are compatible with induction. | `turn23view0`, `turn25view0`, `turn25view1`, `turn25view2` |
| SUTHERLAND | A. V. Sutherland, *18.785 Number Theory I, Lecture 19*, 15 November 2016, [MIT notes](https://math.mit.edu/classes/18.785/2016fa/LectureNotes19.pdf). Analytic class number formula p1; completed zeta and functional equation, Remark 19.13 p9. The latter is stated as a classical result, not reproved in that lecture. | `turn22view0`, `turn23view1`, `turn24view0` |
| THETA | [NIST DLMF §21.2](https://dlmf.nist.gov/21.2), equations 21.2.1–2: fixed symmetric period matrix with positive-definite imaginary part; bounded Gaussian-scaled theta. Live edition 1.2.8, accessed 2026-10-07. | `turn26view2` |
| PRODUCTS | [NIST DLMF §1.10(ix)–(x)](https://dlmf.nist.gov/1.10): compact-uniform product M-test, 1.10.20–21, and logarithmic derivative 1.10.24 for nonzero analytic factors. | `turn26view3`, `turn27view0` |
| SIGMA | [NIST DLMF §23.10](https://dlmf.nist.gov/23.10), 23.10.3, sigma addition sign; [§23.6](https://dlmf.nist.gov/23.6), 23.6.9, sigma–theta normalization with half-period convention. | `turn13view0`, `turn15view2` |
| SINE | [NIST DLMF §4.22](https://dlmf.nist.gov/4.22), 4.22.1, 4.22.3–4, sine product and cotangent/cosecant partial fractions. | `turn16view2`, `turn19view2`, `turn20view5` |
| JENSEN | T. Tao, [*246B Notes 1: Zeroes, poles, and factorisation of meromorphic functions*](https://terrytao.wordpress.com/2020/12/23/246b-notes-1-zeroes-poles-and-factorisation-of-meromorphic-functions/), 23 December 2020. Theorem 2 (Jensen), Proposition 8 (finite-order zero count). Author lecture notes, not a publication-priority source. | `turn13view2`, `turn15view3`, `turn20view4` |

## Exact project applications

### Gamma conventions and BCG modulus leaf

BCG p2 permits negative-period continuation. With the project’s lower embedding, `t=-tau` and `s` are in the upper half-plane, and

\[
\Gamma(z;-t,s)=\Gamma(z+t;t,s)^{-1}.
\]

Fifth smoothing therefore gives the project’s reciprocal positive-period definition of `F`. The period shifts give `F(z+tau)/F(z)=q_s(z)` and `F(z+s)/F(z)=q_t(z)^{-1}`. The extracted p3 half-plane label beside `tau` is inconsistent with its displayed lower embedding; the application uses the directly computed sign and p2 continuation, rather than that label.

Theorem 3.2 gives `zeta'_{f,a}(b,0)=log|Gamma_{a,h}(f b^{-1})|^2`, with smoothing `zeta_{f,a}(b,s)=zeta_f(ab,s)-Na*zeta_f(b,s)`. Section 5.2 assigns the raw value (1.2), in the lower embedding, to ray index 5. The project’s norm-five Artin class `sigma` is an inherited arithmetic identification. Consequently

\[
\log|U_\Gamma|^2=\zeta'_{\mathfrak f}(1,0)-5\zeta'_{\mathfrak f}(\sigma^5,0).
\]

Required conditions are visible: `f,b` coprime, smoothing prime norm5 coprime to `Nf=3`, positive unit generator `epsilon` with real image in `(0,1)`, and admissible geometric `h`. No negative-norm unit lies in `1+f`: units are `±epsilon^n`, `epsilon=1 mod f`, and `-1 != 1 mod f`. The raw example supplies the admissible geometry. This validates the external modulus implication under the project’s explicitly inherited arithmetic identifications; it supplies neither algebraicity nor exact phase.

### Artin induction, primitive factors and conductor

Milne authenticates induction invariance. His displayed definition there only writes unramified factors; Cogdell §2.2 supplies the full convention

\[
L_{\mathfrak p}(s,V)=\det(1-N\mathfrak p^{-s}\operatorname{Frob}_{\mathfrak p}\mid V^{I_{\mathfrak p}})^{-1}.
\]

It also states induction compatibility and agreement with the abelian convention. Thus the project’s character decomposition yields the primitive factor identity in Stark §2, including ramified primes. The `j=0` Dirichlet factor must retain conductor3 rather than its imprimitive modulus21 extension. No Artin holomorphy conjecture is used.

Milne’s reciprocity applies to coprime Eisenstein integers congruent to `±1 mod3`. Here the primary generator is `alpha=1 mod3` and `J=-1 mod3`. Arithmetic Frobenius for `X^3=J`, with inverse Kummer character, gives `(J/alpha)_3^2=(alpha/J)_3^2`. The conductor therefore divides `3J`. The valuation-one radicand at `J` forces ramification there. The internally calculated ray group modulo `(1-omega)J` has order2, so it cannot carry the nontrivial cubic character. Since the exponent above3 is already at most2, the conductor is exactly `3J`. Milne does not state this particular conductor; it is the project’s application of his reciprocity law and explicit ray arithmetic.

### Regulator and complex-place normalization

Sutherland’s residue formula and completed functional equation give, for signature `(1,1)`,

\[
\Gamma_{\mathbb R}(s)\Gamma_{\mathbb C}(s)\sim2s^{-2},\qquad
\zeta'_K(0)=-h_K\mathcal R/w_K.
\]

Using `h_K=3`, `w_K=2`, fundamental `epsilon=2-beta`, and `zeta_Q(0)=-1/2` gives `zeta'_K(0)=-3Rreg/2` and `L'_F(0,rho_ch)=3Rreg`. The regulator is `Rreg=-log(2-cuberoot(7))`; norm-one implies `log|epsilon|=Rreg/2`. The complex-place absolute value is squared modulus, so no further factor2 is introduced into the displayed Stark logarithm. The field and unit facts are recorded in BCG §5.2 and also remain inherited project arithmetic.

### Sigma addition and the common positive Green constant

DLMF’s sign is `wp(v)-wp(u)`. Substituting `u=T,v=z` gives exactly `wp(z)-wp(T)` in Stark §5. For lattice `Z+Z*omega`, the DLMF half periods are `2omega_1=1`, `2omega_3=omega`, and nome `q=exp(pi*i*omega)`. Equation23.6.9 yields

\[
H(z)=A e^{Q(z)}|\sigma(z)|,\quad
A=|\pi\theta_1'(0,q)/\eta(\omega)|>0,
\quad Q(z)=-\pi(\operatorname{Im}z)^2/\operatorname{Im}\omega-\operatorname{Re}(\eta_1z^2).
\]

The quadratic parallelogram expression vanishes, so the four-H ratio is `A^{-2}|wp(z)-wp(T)|`. This explicitly retains the shared positive normalization. The equalities `H(omega*z)=H(z)=H(-z)` follow from the project’s lattice-isometric Epstein sum and its internally derived continuation. Together they give the same positive constant for `u,omega*u,omega^2*u`; the project’s normalized ray-zeta product fixes it. The shifted Epstein identities `E_z(0)=0`, `E'_z(0)=-2log H(z)` were derived in the retained Appendix A and are not being inferred from an unrelated unsmoothed formula.

### Order, products and fourth derivative

The DLMF theta bound gives `|theta(Az+b;Omega)|<=C exp(C'|z|^2)` for each fixed affine map and fixed positive-definite period matrix. Finite derivatives retain order at most2 by Cauchy estimates. Finite sums/products/polynomials can be cleared to entire numerator and denominator with the same bound. Tao’s Jensen consequence, applied at radius `2r`, gives multiplicity counts `O(r^2)` for each nonzero numerator/denominator.

**Required grammar:** one global nowhere-zero entire prefactor may multiply the finite rational expression. Arbitrary unrelated prefactors inside sums are excluded: `1+exp(z^3)` has cubic zero count. This is the fresh audit’s necessary hypothesis restriction, not a broader exclusion of nonlinear theta arguments, varying periods, infinite theta products or special-value formulas.

The project’s cubic divisor bound gives `sum |m_lambda|/|lambda|^4<infinity`. It supplies the M-test needed for separate positive and negative genus-three canonical products. DLMF’s illustrated genus-one product is not asserted to be the project’s product; the general product test applies to its `E3` factors. Off the divisor, compact-normal convergence permits logarithmic differentiation. The remaining coefficient cancellation and minimal ungrouped absolute genus assertion are internal project proofs.

Finally `1-exp(2pi*i*w)=-2i exp(pi*i*w) sin(pi*w)`. DLMF4.22.4 gives the second logarithmic derivative `-sum_n(w-n)^(-2)`. Two further locally normal derivatives give

\[
(\log(1-e^{2\pi iw}))^{(4)}=-6\sum_{n\in\mathbb Z}(w-n)^{-4},\qquad w\notin\mathbb Z.
\]

The regrouping over gamma cones additionally needs the project’s absolute fourth-power summability; the sine identity alone does not license every rearrangement.

## Frozen source hashes and downstream status

| Original proof | SHA-256 |
|---|---|
| `sources/v014/PROOF.md` | `0a2c32818790213efc30dd566ed124841bf647357764e6424b4149083e7712d1` |
| `sources/continuation_chain/01/Komorebi_H12_Principal_Divisor_Transport_Lean_v0.13.0/PROOF.md` | `7b8b42ea194af5d14a9386f915819a3990724b4a26a56d89dc40c798b5c6f0b4` |
| `sources/stark_modulus/PROOF.md` | `2f5558f5a19572b5569c1d8af6eca559358a3813ffc45eeabb76d1754d669db1` |

This check closes the coordinated external-source condition in fresh-audit obligation A22 on the checked editions and the displayed inherited arithmetic hypotheses. It does not promote A21’s inherited field/unit certificates to a fresh end-to-end replay, A23’s numerical evidence to proof, or A24’s complex equality to a theorem. A02’s gamma convention is authenticated on the authors’ copy; its exact-v2 provenance label remains unverified. Final manuscripts should cite that distinction and the global-prefactor restriction explicitly. No priority or global novelty search was conducted.
