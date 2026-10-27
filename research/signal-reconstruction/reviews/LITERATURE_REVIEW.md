# Signal Reconstruction: bounded literature verification

Checked 2026-10-07 UTC for the 2026-10-06 edition. This is a targeted check of two external theorem leaves and selected historical attributions. It is not a global novelty search, a full bibliography audit, a Lean check, or an audit of every cited paper.

The singular-value perturbation and Rouché applications are valid under the printed hypotheses. The exact shifted-sample de-aliasing identity is established prior work after translation of notation. One upstream bibliography entry requires correction: **VEXPA is Signal Processing 177 (2020), article 107722**, not volume 147 (2018), pages 207–220.

## Project sources and locators

The two immutable upstream TeX sources are:

- `Universal_Unknown_Edge_Recovery_Release/Universal_Unknown_Edge_Recovery_Release/Universal_Unknown_Edge_Recovery.tex`, SHA-256 `25715c0955a0dc2714f0e794e26894a10b1d0e22bbc78ae33f942d5c46bb17f0`.
- `Self_Calibrating_Polyphase_Gibbs_Reconstruction_Release/Self_Calibrating_Polyphase_Gibbs_Reconstruction_Release/Self_Calibrating_Polyphase_Gibbs_Reconstruction.tex`, SHA-256 `7f5c632de2961c5765f3c21416b18937898a17834202c4160014a187c7404f71`.

Project theorem dependencies checked: Universal lines 479–515 (residualized sparse uniqueness), 792–804 and 904–959 (moment and annihilator conventions), 1263–1332 (Weyl and Rouché); Self-Calibrating lines 205–267 (normalization and polyphase coefficients), 276–330 (Hankel rank gap), 500–618 (branch lifting and conditional rates), 950–982 (leading confluent coefficient), and the bibliographies. These locators refer to the hashes above, not an evolving final document.

## LIT-01: singular-value perturbation

**Primary source:** G. W. Stewart, *Perturbation Theory for the Singular Value Decomposition*, UMIACS-TR-90-124 / CS-TR-2539, September 1990, §2, Theorem 1, printed p.3. [Institutional record](https://drum.lib.umd.edu/items/04248b40-1958-4077-b011-543af55c128f/full), [institutional PDF](https://drum.lib.umd.edu/bitstreams/a38cc6db-9bb7-4f3b-ae43-55b5827bb9d4/download). Authentication and exact theorem extraction succeeded. This checked copy is the 1990 technical report, not an assumed identical numbering in the 1991 book chapter.

For equally sized matrices, with singular values in decreasing order and the Euclidean induced matrix norm, the result is

\[
|\sigma_k(A+E)-\sigma_k(A)|\le\|E\|_2.
\]

No smallness, randomness, Hankel structure, or simple-singular-value assumption is needed for this inequality. Project translation is $A=H_0$ and $E=H-H_0$. The constant is exactly one. This is **known after translation of notation**.

The project-specific consequence is valid: if $\operatorname{rank}H_0=L\ge1$ and $\varepsilon=\|E\|_2<\sigma_L(H_0)/2$, then every supplied threshold

\[
\varepsilon<t<\sigma_L(H_0)-\varepsilon
\]

counts exactly $L$ singular values of $H$. When $L=\min(R,C)$, the proof has no $\sigma_{L+1}$ to reference; it simply puts every available singular value above $t$. The separate $L=0$ case uses $t>\varepsilon$ and counts zero. Largest adjacent singular-value ratio is an estimator, not a consequence of this theorem.

An internal proof for complex rectangular matrices is available directly from the singular-value minimax formula: the triangle inequality bounds each restricted maximum for $A+E$ by that for $A$ plus $\|E\|_2$. Minimize over subspaces, then interchange $A$ and $A+E$. This avoids any implicit real-to-complex source extension. An independently inspected research-paper restatement is O'Rourke, Vu, Wang, arXiv:1311.2657v7 (2 January 2023), Theorem 7, p.3; its introduction uses real matrices.

## LIT-02: root localization

**Primary author textbook:** Jiří Lebl, *Guide to Cultivating Complex Analysis: Working the Complex Field*, version 1.9, 11 July 2026, §5.4.2, Theorem 5.4.2, Corollary 5.4.3 and the classical specialization, printed pp.139–140. [Author PDF](https://www.jirka.org/ca/ca.pdf). Title, version, date, theorem and proof context were extracted successfully.

The classical strict gate $|f-g|<|f|$ on a positively oriented circle guarantees equal zero counts inside, with multiplicity, for functions holomorphic on a neighborhood of the closed disk. Polynomials satisfy that domain requirement. Translate $f=Q$, $g=\widetilde Q=Q+E_Q$ and the circle to $|z-z_j|=\rho$. This is a **formal corollary** of the checked result.

The project's separation gate $0<\rho<\Delta/2$ places one simple true root in each disk and makes the disks disjoint. Therefore the strict perturbation gate gives one perturbed root in each disk, counted with multiplicity. Equal degree then leaves no additional roots. For a single root, no pairwise-separation minimum is required; one may treat this case separately.

The coefficient normalization is correct: both polynomials are monic of the same degree, so $E_Q(z)=\sum_{k=0}^{L-1}\delta q_kz^k$. Since $|z_j|=1$, on the relevant boundary $|z|\le1+\rho$, giving the stated sufficient bound $\sum_k|\delta q_k|(1+\rho)^k<m_j(\rho)$. The two factors of $2\pi$ from Fourier normalization do not enter this polynomial bound.

This is a conditional deterministic stability statement. Its true centers, true coefficient errors and boundary minima are not automatically available from measured data. Calling it a data-only certificate requires additional verified enclosures. Sampled boundary minima alone need an interpolation or interval bound. A useful purely geometric lower bound is $m_j(\rho)\ge\rho\prod_{k\ne j}(|z_j-z_k|-\rho)$.

## LIT-03: spark and finite dictionaries

**Primary paper:** D. L. Donoho and M. Elad, *Optimally sparse representation in general (nonorthogonal) dictionaries via $\ell^1$ minimization*, PNAS 100(5) (2003), 2197–2202, DOI [10.1073/pnas.0437847100](https://doi.org/10.1073/pnas.0437847100). The published paper was read in the [author-hosted PDF](https://elad.cs.technion.ac.il/wp-content/uploads/2018/02/15_New_Sparseness_IT.pdf). Definition 1 is on p.2198; Theorem 3 and Corollary 1 are on p.2199. Authentication and extraction succeeded.

The paper defines spark by the smallest dependent column subset. Its theorem bounds the combined sparsity of two distinct representations from below by spark; the corollary gives uniqueness below half the spark. Project translation uses the residualized dictionary $A=(I-P_{\mathcal S})D$. Thus the universal $s$-sparse injectivity gate is **known after translation of notation**.

The project's converse is supplied by its direct support-splitting proof. Column normalization is unnecessary for that proof. If the residualized dictionary has no dependent subset, define spark as infinity or handle the full-column-rank case explicitly. Spark does not by itself guarantee recovery by $\ell^1$ minimization; the project uses finite support search/$\ell^0$ uniqueness.

## LIT-04: exact polyphase identity and de-aliasing

**Primary paper:** M. Briani, A. Cuyt, F. Knaepkens and W.-s. Lee, *VEXPA: Validated EXPonential Analysis through regular sub-sampling*, Signal Processing **177 (2020), 107722**, DOI [10.1016/j.sigpro.2020.107722](https://doi.org/10.1016/j.sigpro.2020.107722). Read the [author-hosted accepted journal pre-proof](https://medialibrary.uantwerpen.be/oldcontent/container2652/files/papers/Br_Cu_ea_vex_20.pdf), accepted 14 July 2020, manuscript dated 16 July 2020. Final volume/year/article number confirmed by the [coauthor's institutional record](https://www.stir.ac.uk/research/hub/publication/1650288).

In §3.1–3.2, equations (9)–(12), decimation yields $\lambda_i^u$, shifted coefficient solves yield $\alpha_i\lambda_i^s$, and their ratio gives $\lambda_i^s$. Further offsets form a one-term exponential progression. Translation is $\lambda_i=z_\ell$, decimation $u=N$, shift $s=1$, and effective amplitude $\alpha_i=a_\ell u_\ell^{q_0}$. Consequently $b_{\ell,r}=b_{\ell,0}z_\ell^r$ is **known after translation of notation**; additional-offset stabilization is also closely related prior material.

This prior result does not supply the project's whole Fourier-tail, branch-margin and native edge-synthesis contract. Conversely, it prevents attributing shifted-sample de-aliasing itself to this edition. The upstream bibliography entry at Self-Calibrating lines 1279–1283 is incorrect and should be corrected in the final edition while the immutable upstream source is retained.

## LIT-05: decimated Fourier reconstruction

**Primary paper:** D. Batenkov, *Complete algebraic reconstruction of piecewise-smooth functions from Fourier data*, Mathematics of Computation 84(295) (2015), 2329–2350, DOI [10.1090/S0025-5718-2015-02948-2](https://doi.org/10.1090/S0025-5718-2015-02948-2). Read the [institutionally hosted published PDF](https://math.umd.edu/~tadmor/references/files/Batenkov%20MathComp2015.pdf). Algorithm 2, p.2335; Theorems 12–13, p.2336. The browsed copy carries redistribution restrictions and was not added to the release.

The paper uses decimated Fourier equations and selects an $N$th-root branch using a previously obtained jump estimate. Algorithm 2 assumes an initial location accuracy $o(N^{-1})$. Theorem 12 supplies a $N^{-d-2}$ location rate under its magnitude/tail assumptions; Theorem 13 gives the full reconstruction rates. This is **adjacent prior material**, rather than the exact same multi-edge polyphase algorithm.

It supports the need for correct branch selection and the extra inverse-decimation factor. Its constants and rates cannot be imported merely by equating its smoothness index $d$ with the project's tail index $p$. The project's separate hypotheses on local inverse bounds and branch margin must remain explicit, especially when $p=0$.

## LIT-06: finite-rate-of-innovation attribution

M. Vetterli, P. Marziliano and T. Blu, *Sampling Signals with Finite Rate of Innovation*, IEEE Transactions on Signal Processing 50(6) (2002), 1417–1428, DOI [10.1109/TSP.2002.1003065](https://doi.org/10.1109/TSP.2002.1003065).

The bibliographic record and historical class attribution were confirmed through the indexed [author-hosted article](https://bigwww.epfl.ch/publications/vetterli0201.pdf) and publisher metadata. Direct full-PDF retrieval from EPFL and alternative academic hosts failed, and IEEE metadata retrieval returned HTTP 418. Therefore no exact theorem-number, sampling-kernel hypothesis, or normalization translation from this paper is certified here. It is suitable as historical attribution only. The edition's consecutive-moment reconstruction should carry its own direct Vandermonde/annihilator proof.

## Search boundary and source availability

The search used two web search engines, primarily exact titles, DOI strings, theorem names, and the terms “singular value perturbation”, “Rouché”, “Prony”, “spark”, “finite rate of innovation”, “decimation”, and “shifted samples”. It inspected primary author/institutional PDFs and records, followed VEXPA's backward references to Cuyt–Lee and Batenkov's branch-selection algorithm, and verified the strongest relevant statements. Cuyt–Lee's full paper was not audited here. There was no exhaustive forward-citation, multilingual, patent, or adjacent-field search and no independent second novelty review. The date horizon is the checked sources available on 2026-10-07; no claim of historical first or global novelty follows.

No third-party PDF was copied into the deliverable or local literature cache in this pass. Local PDF hashes and retained extraction files are therefore unavailable. Source identity rests on the authenticated bibliographic records and exact browsed versions above; project-source hashes are recorded separately. Several alternative web retrievals failed with HTTP 502, 403, 418, timeout, or an internal retrieval error; these failures are not evidence that a theorem or prior result does not exist.

The corresponding JSON records verdicts, project locators and stable URLs. Final-document attribution must preserve the distinction between checked external leaves, direct project proofs, and historical sources whose complete theorem contracts were not extracted.
