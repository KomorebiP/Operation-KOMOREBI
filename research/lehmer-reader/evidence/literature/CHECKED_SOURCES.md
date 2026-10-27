# Lehmer Series 07: checked external source contracts

Checked 9 October 2026. This report concerns Ramanujan's tau nonvanishing conjecture. It records a targeted source check for the publication's external mathematical inputs, not an exhaustive novelty search or a certification of every published proof. The project proofs, exact calculations, and formal compilation have separate audits. No third-party paper is bundled here; the links below identify the inspected sources.

## Publication boundaries

The statement is $\tau(n)\ne0$ for every integer $n\ge1$, where $\Delta(q)=q\prod_{m\ge1}(1-q^m)^{24}=\sum_{n\ge1}\tau(n)q^n$. The publication does not establish this statement. A finite computation, a fixed-modulus density theorem, or a locally realizable filtered module does not establish global nonvanishing.

For every fixed positive modulus $M$, the project may use the actual finite image of the compatible Galois representations and a complex-conjugation class to obtain positive natural density of primes satisfying $\tau(p)\equiv0\pmod M$ (and $p^{11}\equiv-1\pmod M$). This is an application of the checked inputs, conditional on the project's representation and class construction. The order of quantifiers is $\forall M\,\exists^\infty p$, not $\exists p\,\forall M$.

## S01 — Lehmer and prime reduction

D. H. Lehmer, *The vanishing of Ramanujan's function $\tau(n)$*, Duke Mathematical Journal **14** (1947), 429–433. DOI [10.1215/S0012-7094-47-01436-1](https://doi.org/10.1215/S0012-7094-47-01436-1). [Original scan](https://oeis.org/A000594/a000594.pdf).

The scan was authenticated but its page images did not yield extractable text in this access route. Consequently, this check does not claim to have reread its original proof. Theorem 2's least-zero-prime statement is explicitly attributed to Lehmer in the introduction of the primary research paper [*Non-vanishing Fourier coefficients of $\Delta_k$* (2018)](https://www.sciencedirect.com/science/article/abs/pii/S0096300318305800). Use the classical prime reduction as an attributed input, or supply the project's separate proof. Multiplicativity applies only when the two arguments are coprime; the recurrence is $\tau(p^{r+1})=\tau(p)\tau(p^r)-p^{11}\tau(p^{r-1})$ for prime $p$ and $r\ge1$. These formulas are also explicitly restated in S11, §2.1, equation (2.1).

## S02 — Han's packet normalization

Guo-Niu Han, *The Nekrasov–Okounkov hook length formula: refinement, elementary proof, extension and applications*, [arXiv:0805.1398v1](https://arxiv.org/abs/0805.1398v1), 9 May 2008, Definition 1.1 and Theorems 1.1–1.2, printed p.3. Inspected [PDF](https://arxiv.org/pdf/0805.1398) carries that exact v1 header. Published Annales de l'Institut Fourier **60** (2010), 1–29, DOI [10.5802/aif.2515](https://doi.org/10.5802/aif.2515).

For odd $t=2t'+1$, V-coding has $v_i\equiv i\pmod t$ and $\sum v_i=0$. Han gives $|\lambda|=\sum v_i^2/(2t)-(t^2-1)/24$ and hook product $(-1)^{t'}\prod_{i<j}(v_i-v_j)/(1!\cdots(t-1)!)$. Theorem 1.2 gives the partition hook generating product with exponent $z-1$. Specializing $t=5,z=25$ gives shell $\sum v_i^2=10n$ and weight $D(v)/288$, with positive prefactor. Reversing every difference preserves the sign because there are ten pairs. Thus the packet identity is a translated classical identity; packet integrality is a separate determinant argument. There is no all-positive packet conclusion in Han.

## S03 — Harmonic theta input

Tomoyoshi Ibukiyama and Brandon Williams, *Hermitian modular forms and algebraic modular forms on $SO(6)$*, [arXiv:2505.23497v1](https://arxiv.org/abs/2505.23497v1), §3.4, printed pp.18–19. The inspected [41-page PDF](https://arxiv.org/pdf/2505.23497) has the v1 header 29 May 2025 and internal date 12 June 2025.

For the positive-definite integral quadratic lattices and discriminant forms of that section, the vector theta series uses $\lambda\in L'$, component $e_{\lambda+L}$, and exponential $e^{\pi i\langle\lambda,\lambda\rangle z}$. A homogeneous harmonic polynomial of degree $\nu$ on rank $n$ gives weight $\nu+n/2$ for the Weil representation of the discriminant form. Therefore rank four and total degree $10+d$ give weight $12+d$. The project must verify its lattice, quadratic-form scaling, harmonicity, discriminant cosets, and scalar sign-line descent to full level. The paper's conjectural Hermitian correspondences are not an input to this assertion.

## S04 — Valence and level-one dimensions

William Stein, *Modular Forms: A Computational Approach*, author online chapter [*Modular Forms of Level 1*](https://wstein.org/books/modform/modform/level_one.html), Theorem 2.11; Theorem 2.14; Corollaries 2.15–2.16; Theorem 2.17. This is an inspected scholarly author exposition of the classical results.

For a nonzero holomorphic modular form of even weight $k$ for $SL_2(\mathbb Z)$, the valence sum equals $k/12$, with elliptic factors $1/2$ at $i$ and $1/3$ at $\rho$. Hence an already certified cusp form vanishes identically if its coefficients $q^1$ through $q^{\lfloor k/12\rfloor}$ vanish. This implication needs modularity first. Multiplication by $\Delta$ identifies $M_{k-12}$ with $S_k$. With constant-one Eisenstein normalization, $S_{20}$ and $S_{22}$ have respective generators $\Delta E_4^2$ and $\Delta E_4E_6$. Stein's displayed Eisenstein normalization differs by nonzero scalars; dimensions are unaffected.

## S05 — Established Galois representations

Jean-Pierre Serre, *Congruences et formes modulaires (d'après H. P. F. Swinnerton-Dyer)*, Séminaire Bourbaki 1971/72, exposé 416, Lecture Notes in Mathematics **317** (1973), 319–338. [Inspected NUMDAM PDF](https://www.numdam.org/item/SB_1971-1972__14__319_0.pdf), §3.1, printed pp.331–332; Theorem 10 and §3.3, printed p.335.

The established Deligne construction gives a continuous integral rank-two $\ell$-adic representation for an integral normalized level-one cuspidal Hecke eigenform, unramified outside $\ell$. For $\Delta$, use the arithmetic-Frobenius normalization $T^2-\tau(p)T+p^{11}$ for $p\ne\ell$; determinant is the eleventh cyclotomic power. This polynomial is independent of $\ell$ at common unramified primes. Reduction modulo any fixed $\ell^r$ has a finite image. The exceptional primes $\{2,3,5,7,23,691\}$ concern the image classification, not a claim that no other congruence exists. Joint surjectivity is unnecessary when using a conjugacy class in the actual finite image.

## S06 — Deligne bound and Frobenius convention

Pierre Deligne, *Formes modulaires et représentations $\ell$-adiques*, Séminaire Bourbaki 1968/69, exposé 355, published 1971, 139–172. [Original PDF](https://www.numdam.org/item/SB_1968-1969__11__139_0.pdf). Also inspected the author's [English translation](https://publications.ias.edu/sites/default/files/5_FormesModulaires.pdf), Proposition 4.8 and equation (5.7). Pierre Deligne, *La conjecture de Weil: I*, Publications Mathématiques de l'IHÉS **43** (1974), 273–307, [Theorem 1.6, p.276](https://www.numdam.org/article/PMIHES_1974__43__273_0.pdf), DOI [10.1007/BF02684373](https://doi.org/10.1007/BF02684373).

The modular paper gives Weil ⇒ Ramanujan in Theorem 5.6. Weil I supplies purity for smooth projective varieties over finite fields. Together they give $|\tau(p)|\le2p^{11/2}$. This is an upper bound, with no nonzero lower bound. Deligne's cohomological $F$ in Proposition 4.8 is inverse arithmetic Frobenius. The publication's arithmetic-Frobenius rank-two representation is normalized as in S05; it must not silently identify that arithmetic operator with this geometric cohomological $F$ without dualization/convention translation.

## S07 — Congruences

Jean-Pierre Serre, *Une interprétation des congruences relatives à la fonction $\tau$ de Ramanujan*, Séminaire Delange–Pisot–Poitou **9** (1967/68), no.1, exposé 14, 1–17. [Inspected PDF](https://www.numdam.org/item/SDPP_1967-1968__9_1_A13_0.pdf), §2.2, equation (21), printed p.4; §2.1, equation (16), p.3; §4.5, p.11.

The all-positive-integer congruence is $\tau(n)\equiv\sigma_{11}(n)\pmod{691}$. The mod23 prime classification excludes $p=23$: a quadratic nonresidue gives 0; $p=u^2+23v^2$ gives 2; other quadratic residues give −1. In the represented case §4.5 strengthens to $\tau(p)\equiv1+p^{11}\pmod{23^2}$. This 1968 source labels the general representation existence as conjectural in §3.2; use the later S05 for the established theorem.

For the sharper small-prime congruence table, see Nik Lygeros and Olivier Rozier, *Odd prime values of the Ramanujan tau function*, Ramanujan Journal (2013), DOI [10.1007/s11139-012-9420-8](https://doi.org/10.1007/s11139-012-9420-8), [author PDF](https://lygeros.org/wp-content/uploads/root/11713_Odd_prime_values_of_the_Ramanujan_tau_function.pdf), p.2, equations (3)–(11). These are checked restatements of earlier congruences, not a fresh audit of all original proofs. Inverse powers require unit arguments; the stronger mod49 branch applies only to $n\equiv3,5,6\pmod7$. S11, Proposition 6 supplies a direct proof of the parity criterion: $\tau(n)$ is odd exactly when $n$ is an odd square.

## S08 — Chebotarev natural density

Peter Stevenhagen and Hendrik W. Lenstra Jr., *Chebotarëv and his density theorem*, The Mathematical Intelligencer **18** (1996), no.2, 26–37. [Authenticated author scan](https://pub.math.leidenuniv.nl/~lenstrahw/PUBLICATIONS/1996d/art.pdf): the conjugacy-class theorem is on printed p.34; the discussion on p.31 explicitly permits natural as well as analytic density. The historical project URL currently failed, but this author copy was successfully inspected.

For a finite Galois splitting field over $\mathbb Q$ and a nonempty conjugacy class $C\subset G$, unramified rational primes with Frobenius in $C$ have natural density $|C|/|G|>0$. Only finitely many ramified primes are removed. Applied to an actual finite representation quotient, this gives a fixed-modulus statement; density may depend on that quotient and need not have a uniform positive lower bound as the modulus grows. [Milne, *Class Field Theory* v4.03, 6 August 2020](https://www.jmilne.org/math/CourseNotes/CFT.pdf), Theorem 3.23 p.164 and Remark 3.26(d) p.165, provides an independently checked author exposition for the number-field and natural-density formulations.

## S09 — Colmez–Fontaine local realization

Pierre Colmez and Jean-Marc Fontaine, *Construction des représentations $p$-adiques semi-stables*, Inventiones Mathematicae **140** (2000), 1–43, DOI [10.1007/s002220000042](https://doi.org/10.1007/s002220000042). [Author manuscript](https://webusers.imj-prg.fr/~pierre.colmez/CF.pdf): Theorem A p.2; §3.4 pp.21–22; §4.1 and Corollary 4.3 pp.23–24; $B_{\mathrm{cris}}=B_{\mathrm{st}}^{N=0}$ p.11. These locators refer to the inspected 37-page manuscript, not the published pagination.

For a finite filtered $(\varphi,N)$-module over the specified local field, with $N\varphi=p\varphi N$, weak admissibility requires $t_H(D)=t_N(D)$ and $t_H(D')\le t_N(D')$ for every stable subobject with induced filtration. Theorem A makes such an object admissible; the equivalence realizes it as a semistable representation. With $N=0$ it is crystalline. The project's $K=K_0=\mathbb Q_p$ specialization must check all these hypotheses. This existence theorem does not identify the resulting representation with the actual restriction of Deligne's representation, nor produce a global compatible system. Use filtration degrees unless a Hodge–Tate sign convention is explicitly fixed.

## S10 — Historical computational lower bound

Maarten Derickx, Mark van Hoeij, and Jinxiang Zeng, *Computing Galois representations and equations for modular curves $X_H(\ell)$*, [arXiv:1312.6819v2](https://arxiv.org/abs/1312.6819v2), 18 March 2014. [Inspected v2 PDF](https://arxiv.org/pdf/1312.6819v2), Corollary 1.2 printed p.2 and its computational proof in §4, printed p.11.

The published preprint bound is $\tau(n)\ne0$ for $n<816212624008487344127999$. Preserve the strict inequality. The endpoint is the first prime surviving their specified combined congruence tests; it is not asserted to be a zero. This is cited historical computation, not a replayed computation in Series 07 and not a verified latest world record.

## S11 — Scoped contemporary context

David Kurniadi Angdinata et al., *ABC implies that Ramanujan's tau function misses almost all primes*, [arXiv:2603.29970v3](https://arxiv.org/abs/2603.29970v3), 25 April 2026; inspected [PDF](https://arxiv.org/pdf/2603.29970) has internal date 28 April 2026. Introduction pp.1–2 restates Lehmer's conjecture; §2.1 equation (2.1) states the Hecke relations and Deligne bound; Proposition 6 p.4 proves the parity fact. Its conditional prime-value result is not needed here and is not being audited.

The title *Proof of the Lehmer conjecture on Ramanujan's $\tau$ function*, Minjia Shi, Lu Wang, and Patrick Solé, [arXiv:2503.23498v2](https://arxiv.org/abs/2503.23498), 1 April 2025, is explicitly withdrawn in the inspected arXiv metadata. It cannot serve as an established proof. These targeted checks support the publication's unresolved status within this program; they do not certify an exhaustive global literature search.

## S12 — Hurwitz moments and Catalan inversion

Nik Lygeros and Olivier Rozier, *A New Solution to the Equation $\tau(p)\equiv0\pmod p$*, Journal of Integer Sequences **13** (2010), article 10.7.4, [journal PDF](https://cs.uwaterloo.ca/journals/JIS/VOL13/Lygeros/lygeros5.pdf), §§4–6, printed pp.3–6. The inspected article states the trace system for even weights at least four, its six-by-six prime specialization, the Catalan inverse, and $s_{10}(p)=42p^6-90p^4-75p^3-35p^2-9p-1-\tau(p)$.

Here $s_j(n)=\frac12\sum_{|t|\le2\sqrt n}t^jH(4n-t^2)$. For $j=0$ the $t=0$ term keeps its half weight; for positive $j$ that term vanishes. The reduced-form enumeration in §6 has no primitivity condition: imprimitive forms are included. Ordinary forms have weight one, $(a,0,a)$ weight $1/2$, and $(a,a,a)$ weight $1/3$; the stored integer is $6H$. At a prime the endpoints cannot have discriminant zero, so no $H(0)$ convention enters. This is a checked classical source input; inversion does not force the residual cusp coefficient to be nonzero.

## S13 — Five-core count

Frank Garvan, Dongsu Kim, and Dennis Stanton, *Cranks and $t$-cores*, Inventiones Mathematicae **101** (1990), 1–17, DOI [10.1007/BF01231493](https://doi.org/10.1007/BF01231493). [Author manuscript](https://www-users.cse.umn.edu/~stant001/PAPERS/cra2.pdf), §2, Bijections 1–2, and §5, Theorem 4 and equation (5.3), printed p.8. The inspected author copy has 16 physical pages; these are its printed locators.

Its exact count is $a_5(n-1)=\sum_{d\mid n}\chi_5(d)n/d$ for $n\ge1$, where $\chi_5$ is the Legendre character including value zero at multiples of five. Thus for prime $p$, $a_5(p-1)=p+\chi_5(p)$, including $a_5(4)=5$. Translating this count to the project's V-coded shell uses Han's bijection. The count measures packet cardinality, not the sign or nonvanishing of their weighted sum.

## S14 — Niebur formula and valuation scope

B. K. Moriya and C. J. Smyth, *Index-dependent divisors of coefficients of modular forms*, [author manuscript dated 1 May 2013, accepted 28 April 2013](https://webhomes.maths.ed.ac.uk/~chris/papers/Moriya_Smyth_final.pdf). §7, printed pp.10–11, restates Niebur's identity for every $n\ge1$:

$$\tau(n)=n^4\sigma(n)-24\sum_{k=1}^{n-1}k^2(35k^2-52kn+18n^2)\sigma(k)\sigma(n-k).$$

The empty sum at $n=1$ is permitted. Douglas Niebur's original *A formula for Ramanujan's $\tau$-function*, Illinois Journal of Mathematics **19** (1975), 448–449, DOI 10.1215/ijm/1256050746, was blocked by the retrieval route; its original proof is not freshly checked. This is a verified primary-paper restatement. Moriya–Smyth §2.1 also explicitly allows $a(p)=0$ when extracting its size/divisibility condition from Deligne's bound. Neither this identity nor that alternative excludes zero.

## S15 — Differential relations and universal algebra

Tiago J. Fonseca, *Higher Ramanujan equations I: moduli stacks of abelian varieties and higher Ramanujan vector fields*, [arXiv:1612.05081v1](https://arxiv.org/abs/1612.05081v1). The inspected [35-page PDF](https://arxiv.org/pdf/1612.05081) carries header 15 December 2016 and internal date 5 November 2018. Introduction p.2 and Remark 6.4 p.29 give, for constant-one Eisenstein series and $D=q\,d/dq$,

$$DE_2=(E_2^2-E_4)/12,\quad DE_4=(E_2E_4-E_6)/3,\quad DE_6=(E_2E_6-E_4^2)/2.$$

Together with the normalized identity $\Delta=(E_4^3-E_6^2)/1728$ displayed in Stein's chapter, these supply exact classical inputs for the project's symbolic derivation of its universal $S_4(n)$ identity. The internal polynomial identity and coefficient extraction are audited separately. No novelty or historical-priority claim is made for these transformations.

## S16 — Balakrishnan–Craig–Ono classical leaves

Jennifer S. Balakrishnan, William Craig, and Ken Ono, *Variations of Lehmer's Conjecture for Ramanujan's tau-function*, [arXiv:2005.10345v1](https://arxiv.org/abs/2005.10345v1), 20 May 2020. The inspected [nine-page PDF](https://arxiv.org/pdf/2005.10345) carries that exact version header. Equation (1.2), printed p.1, records $\tau(n)\equiv n\sigma_1(n)\pmod5$ for positive integers, along with the mod9, mod7, and mod691 congruences. At a prime it yields $\tau(p)\equiv p(1+p)\pmod5$.

Theorem 2.2, printed p.4, states coprime multiplicativity, the prime-power recurrence for exponent $m\ge2$, the Frobenius-root formula, and Deligne's upper bound. The beginning of §3, printed p.7, proves the odd-square parity criterion directly from the Jacobi identity. These exact classical leaves support the publication's BCO citations. This targeted check does not audit the paper's higher-degree integral-point calculations or every omitted-value theorem. It does not claim that the checked classical facts originate in this paper.

## Search and access limits

The targeted search included the authorized historical project bibliographies, authenticated author copies, NUMDAM, arXiv version headers, and journal/publisher records. Exact inspected statements above are distinguished from primary-paper restatements and attributed inputs. Lehmer's original scan and Niebur's original proof have the explicit access limits stated above. No theorem is upgraded merely because its bibliography appears in an old project note. No priority or novelty verdict follows from this source check.
