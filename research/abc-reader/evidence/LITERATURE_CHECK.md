# ABC literature and source-dependency check

Checked 8 October 2026. This check applies to the ABC publication set assembled in `abc_set`, including the recovered prime-contact/coherence chapters. It authenticates named sources, extracts the relevant statements, translates notation, and checks whether those statements supply the manuscript's claimed inputs. It is not a referee report on every cited proof, an independent verification of IUT, or a global novelty certificate. The mathematical proof audit and bounded computation audit are separate evidence files. The final split-Tate scalarity leaf, Faltings endomorphism leaf, and fresh October repository-status check are recorded in `LITERATURE_APPENDIX_TATE_FALTINGS.md`.

The governing workflow was the current **mathbox:literature-check** skill, including its source-record and source-cache instructions. Primary author copies and publisher pages were preferred. Sources are privately retained in `evidence/literature`; their original content must be excluded from the distributed source/evidence ZIP. `LITERATURE_SOURCE_MANIFEST.json` records URLs, versions, SHA-256 hashes where acquisition succeeded, extraction limitations, and failed attempts. The local source-cache helper rejected insertion because it could not verify Git ignore coverage; the private retention here is a direct acquisition record, not a claim that the helper's managed cache was installed.

## Outcome for the manuscript

The integer ABC conjecture remains the external target of this project. Established results support the definitions, polynomial comparison, modularity of its Frey curves, classical polylogarithm identities, and the contextual arithmetic-derivative/Hecke/motivic frameworks. The checked sources do **not** establish the proposed bounded integral realization, coherence transfer, nondegeneracy certificate, or uniform height/radical estimate. Those are manuscript hypotheses or open bridge obligations. A finite computation or a formal theorem about an abstract certificate does not furnish the missing arithmetic witness.

No assertion about acceptance by all or most mathematicians is required. The defensible current status is more precise: Mochizuki's IUT proof claim was published; Scholze and Stix documented an objection to the passage to IUT III Corollary 3.12; Mochizuki disputes their simplifications; the July 2026 LANA interim report has not reconstructed its specified compatibility and expressly withholds a final verdict. These statements describe identifiable primary documents.

## Exact ABC target and notation

For positive integers `a+b=c` with `gcd(a,b)=1`, put

\[
R=\operatorname{rad}(abc)=\prod_{p\mid abc}p.
\]

The target is

\[
\forall\varepsilon>0\ \exists K_\varepsilon>0\ \forall(a,b,c),\qquad
c\le K_\varepsilon R^{1+\varepsilon}.
\]

The constant depends only on the chosen epsilon, uniformly over all primitive triples. Pairwise coprimality follows from the sum relation. For positive triples `c=max(a,b,c)`. Allowing signed nonzero triples gives the equivalent maximum-height form after sign/order changes. Vojta's author course PDF, §2, Conjecture 2.4 and equations (2.4.1)–(2.5), printed pp. 6–7, supplies this formulation and its translation to a three-point divisor on the projective line. Oesterlé 1988, §3, Conjecture 3, printed p. 169, is an earlier primary formulation.

Equivalently, for every epsilon, the quantity `log c−(1+epsilon)log R` is bounded above. This is stronger than one fixed power bound `c<=C R^M`, and far stronger than a bounded census. Quality `q=log c/log R` is a diagnostic, not the conjecture's quantifier. For each fixed epsilon, ABC implies finitely many triples with `q>1+epsilon`; conversely those finiteness statements imply the displayed uniform constants by taking the maximum over finitely many exceptional triples.

The endpoint epsilon zero is false. A self-contained family is

\[
(a_n,b_n,c_n)=(1,3^{2^n}-1,3^{2^n}),\quad n\ge1.
\]

Here `v_2(b_n)=n+2` by the elementary lifting calculation, so

\[
\operatorname{rad}(b_n)\le b_n/2^{n+1},\qquad
R_n\le3b_n/2^{n+1},\qquad
c_n/R_n\ge2^{n+1}/3\longrightarrow\infty.
\]

Thus no universal `c<=K R` holds. This is an elementary exposition leaf, not a novelty claim or a counterexample to positive-epsilon ABC.

## Established unconditional and conditional results

| Source leaf | Exact usable statement | Application and limit |
|---|---|---|
| Stewart–Yu 2001, Theorem 1, printed p. 170 | For coprime positive `a+b=c`, an effectively computable absolute constant `C>0` satisfies `c<exp(C R^(1/3)(log R)^3)`. | An established unconditional benchmark. This check does not certify that it is the latest optimal bound as of 2026. It does not have the ABC power-law scale. |
| Same theorem, direct corollary | For a fixed finite set `S` of allowed primes, `R<=product(S)` gives an effective finite upper bound on `c` and hence finitely many triples. | Fixed prime support is already finite unconditionally. Finiteness on a fixed support is not the universal ABC gap. |
| Snyder 2000, Mason theorem, printed p. 94 | Over an algebraically closed field `k`, nonzero pairwise coprime `A+B=C` with derivatives not all zero satisfy `deg C<=n_0(ABC)−1`. Permuting yields the maximum-degree bound. | Complete two-page proof read. In characteristic zero the derivative hypothesis is equivalent to at least one polynomial being nonconstant. In positive characteristic the derivative condition must be retained. This polynomial theorem does not imply integer ABC. |
| Oesterlé 1988, §3, Conjecture 4 and immediately following equivalence, pp. 169–170 | Full ABC is equivalent to the modified Szpiro estimate `max(|c_4|^3,c_6^2)<=C_epsilon N^(6+epsilon)` for minimal integral elliptic-curve invariants and conductor. The source states the equivalence also with a semistable restriction. | The maximum-invariant form is essential. The ordinary discriminant inequality `|Delta|<=C_epsilon N^(6+epsilon)` must not be silently identified with this full height estimate. Printed formulas were visually checked because OCR was unreliable. |
| Vojta 1998, Conjectures 2.1 and 2.3, Theorem 3.1 | The general height/counting conjecture implies its truncated-counting version; the ABC case is `X=P^1`, three-point `D`, rational points. | The theorem is a conditional implication between conjectures. It is not an unconditional ABC theorem. |
| Elementary Fermat consequence of ABC | From `x^n+y^n=z^n` with coprime positive bases, `R=rad(xyz)<z^3`; fixing, for example, epsilon 1 gives `z^(n−6)<K_1`. Since `z>=2`, no such solutions exist for all sufficiently large `n`. | ABC by itself in this simple argument gives asymptotic Fermat, with an ineffective cutoff unless a constant is supplied. Full Fermat is already unconditional by Wiles and Taylor–Wiles; do not credit full Fermat solely to this argument. |
| Evertse–Győry–Stewart–Tijdeman 1988, Theorem 1 and introduction | A source on two-variable `S`-unit equations, including finiteness arguments and exceptional coefficient classes. | Its main uniform coefficient-class result uses the subspace theorem and is ineffective. The manuscript's effective fixed-support consequence should instead be attributed directly to Stewart–Yu, avoiding an unsupported effective interpretation of this theorem. |

Mason/Stothers attribution is historical orientation. Snyder's actual theorem and proof were consulted; the original Mason book and Stothers paper were not fully acquired/read in this check. The surviving uncertainty does not affect the self-contained characteristic-zero proof in the manuscript.

## Arithmetic-derivative route: exact source translation

The checked source is Pasten, *Arithmetic derivatives through geometry of numbers*, arXiv:2106.16165**v3** (11 December 2021), published in Canadian Mathematical Bulletin 65(4) (2022), 906–923, DOI `10.4153/S0008439521000990`. The version matters: v3 corrects an omission in Lemma 4.4.

Pasten's universal arithmetic differential has prime coordinate `n v_p(n)/p`; composition with a bounded scalar functional `psi` gives an arithmetic derivative. The manuscript's prime-contact coordinate and scalar functional are the same established construction after notation translation. Filtered shell organization and its subsequent modules are a project presentation/construction; this check does not establish global novelty of that packaging.

| Pasten leaf | Checked statement | Required qualification |
|---|---|---|
| Theorem 3.3, pp. 6–7 of v3 | For primitive positive `a+b=c`, `(a,b)!=(1,1)`, an additive-on-this-triple functional `psi in T(a,b)` with nonzero arithmetic Wronskian gives `c/log c <= R ||psi||/log 2`. | Additivity alone is insufficient: the Wronskian must be nonzero. The norm must be bounded at the appropriate uniform scale before an ABC estimate follows. |
| Lemma 3.5, p. 7 | An independent derivative exists with norm bounded at approximately `omega(abc)c log c/(2 log 2)`. | This size is too large to prove full ABC via the preceding inequality. Existence of an arbitrary nonzero functional does not close the gap. |
| Conjecture 3.9, p. 8 | The Small Derivatives Conjecture asserts the existence of **one** exponent `eta in (0,1)` giving an independent derivative of norm `<c^eta` for all but finitely many admissible triples, excluding `(1,N,q)` with `q` prime up to permutation. | Preserve the excluded family and finite exceptions. One exponent is not a statement for every positive epsilon. |
| Theorem 4.5 and Corollary 4.6, p. 11 | Full ABC implies Small Derivatives. Conversely Small Derivatives implies a weak Oesterlé power bound `c<R^M` for some `M`, with finite exceptions. For `1<M<2`, Theorem 4.5 yields a derivative for each `eta>1−(2−M)/(4M)`. | Do not call the single-exponent conjecture equivalent to full epsilon-uniform ABC. The abstract's broad equivalence wording is qualified by the exact corollary. |

The manuscript's stronger uniform certificate condition must be stated on its own, then proved to imply the exact target. Pasten supplies the arithmetic framework and comparison theorem, not the project's missing uniformly small, nondegenerate witness.

## Published IUT claim and documented current status

The publisher authenticates Mochizuki's IUT IV as PRIMS 57(1/2) (2021), 627–723, published 5 March 2021, DOI `10.4171/PRIMS/57-1-4`. The cached author PDF is dated **April 2020**; it is not falsely labeled the publisher's final file.

IUT IV Theorem A (author PDF p. 3) / Corollary 2.3 (pp. 54–55) claims a Diophantine inequality for a smooth proper geometrically connected curve `X` over a number field, a reduced divisor `D`, hyperbolic `X\D`, fixed degree bound `d`, and every positive epsilon. In the source's normalized height/different/conductor notation it has the form

\[
h_{\omega_X(D)}(P)\le(1+\varepsilon)
\bigl(\log\operatorname{diff}_X(P)+\log\operatorname{cond}_D(P)\bigr)+O_{X,D,d,\varepsilon}(1).
\]

The stated ABC specialization is a **published proof claim**. This audit authenticates that statement and the following primary positions; it does not independently verify its proof or resolve the dispute.

The original IUT III author PDF (May 2020) was also retained. Theorem 3.11 begins on printed p. 153 with initial Theta-data and distinct Hodge theaters in an LGP-Gaussian log-theta-lattice. Corollary 3.12, printed pp. 173–174, asserts finite `−|log(Theta)|>=−|log(q)|`: the Theta term is the procession-normalized mono-analytic log-volume of the holomorphic hull of the union of possible pilot images, subject to Ind1/2/3; the q term is the corresponding q-pilot image without those indeterminacies. These are specialized source quantities. An abstract order/certificate theorem, including a Boolean example, is not an instantiation of this source theorem without the arithmetic object, observable, normalization, and witness map.

- **Scholze–Stix, August 2018:** the 10-page manuscript specifically criticizes the passage from IUT III Theorem 3.11 to Corollary 3.12, focusing on scale-changing identifications of ordered real lines and the asserted log-volume inequality. See §1.3 and §2.2, particularly pp. 9–10. Their title is their conclusion, not a substitute for an independent audit.
- **Mochizuki, September 2018 comments:** disputes the simplification/identification of structures in that criticism. The October 2025 *Report on the current situation surrounding IUT* continues this position, especially §§2.1–2.2. These are the author's responses, not neutral consensus measures.
- **Project LANA, interim report, last updated 20 July 2026:** its abstract says the team has not reconstructed the required compatibility and offers no final verdict. In §9.2, equation (9-1), printed p. 46, the specified goal is compatibility `eta^q=eta_S^anab` for a suitable `S` between the q-pilot construction and the anabelian construction in a common target. Section 10 accepts the displayed Scholze–Stix hexagon's noncommutativity but says that alone does not establish a defect in the intended comparison; the report distinguishes that cross-link identification from the same-side comparison. The source therefore does **not** support either “LANA verified IUT” or “LANA conclusively confirmed Scholze–Stix's rejection.”
- **Mochizuki, April 2026 formalization talk:** outlines stages of a prospective formalization. These slides are not a completed formal proof of ABC.

The initial current-status search included recency-filtered primary web searches for ABC/IUT/LANA and the official author/project/publisher pages. It found the July 2026 LANA report and official ZEN announcement (17 July). A follow-up checked the October 2026 `lana-agents/iut` README, which expressly disclaims verification of IUT and retains an unproved Corollary 3.12 variant; see the appendix for its exact scope. A failed search or silence is not evidence of universal agreement. The report should be cited by its corporate byline **LANA Project**, not an invented list of individual authors.

## Modularity, Hecke, Fermat-motive, and regulator context

| Manuscript context / citation | Exact authenticated leaf | Dependency classification |
|---|---|---|
| Frey curve and modular parametrization; `BCDT` | Breuil–Conrad–Diamond–Taylor 2001, Theorem A, author final PDF p. 1: every elliptic curve over `Q` is modular. | Established external input. For a nonsingular rational Frey curve this supplies modularity. It supplies no bound on modular degree, congruence module, or the proposed projector/prime-contact realization. The displayed differential-area identity is an internal pullback calculation once parametrization and normalization are fixed. |
| `Wiles`, `TaylorWiles` | Official Annals publication metadata authenticated: 141(3) (1995), 443–551 and 553–572 respectively. | Historical/theoretical background to modularity and unconditional Fermat. The precise semistable-modularity theorem was not separately re-audited; use BCDT Theorem A for the all-curve input. |
| `CesnaviciusManin` | Author v3, Theorem 1.1: `c_phi | deg(phi)` for surjections from `X_1(N)`; Theorem 1.2: `c_phi | 6 deg(phi)` for `Gamma_1(N)<=Gamma<=Gamma_0(N)`, improved to divisibility by `deg(phi)` for cube-free `N`, with detailed 2/3 refinements. | This is not a general theorem `c_phi=1`. The manuscript must retain a Manin coefficient or justify any semistable/optimal specialization separately. Definitions/background suffice for the packet bookkeeping. |
| `Agashe` | Author v2 (5 October 2025), Theorem 1.2: prime-adic equality between modular number and the **square** of congruence number assumes multiplicity one for every maximal ideal of that residue characteristic containing `I_f`. | No unconditional generic equality. Modular number/degree/exponent and congruence number/exponent are distinct. The paper itself distinguishes them. This source does not identify the project's toy congruence ideal with an actual global modular module. |
| `BKM1` | v3, Theorem 1.1 restates the Wiles–Lenstra criterion for a surjective map of complete Noetherian local `O`-algebras, `T` finite flat, nonzero congruence ideal; equality of cotangent/congruence sizes characterizes an isomorphism of complete intersections. | Structural context. Hypotheses include local coefficient/deformation data. A toy ring calculation is not automatically a Galois/Hecke deformation theorem. |
| `BKM2` | v2, Theorem 1.1, pp. 3–4: relatively prime squarefree `N,Q`, `p>2` not dividing `NQ`, weight-2 newform, irreducible residual representation and `N | N(rho_bar)`; prescribed Steinberg/finite-flat/minimal deformation conditions. The ring and module defects equal `sum_(q|Q) 2n_q/e`. | These hypotheses and source objects are essential. This local-global defect formula does not construct the manuscript's integral transfer or furnish its ABC bound. |
| `AokiFermat`, `ColemanMcCallum` | Inherited bibliography retained as orientation; Coleman–McCallum publisher metadata independently confirmed. Original theorem leaves were not fully read in this audit. | No source-dependent classification or conductor formula from these papers should be used as a proved project input without a further exact leaf check. Elementary finite character/slope identities in the chapter stand on their internal proofs. |
| `OtsuboYamazaki` | v3, Theorem 1.1(i) and Theorem 1.2: motivic Gauss/Jacobi relations over finite `kappa`, `d | (q−1)`, with nontrivial character conditions and cyclotomic coefficients. The multiplication relation extends in Theorem 7.2 to arbitrary `kappa` with all `d`th roots of unity and coefficient field containing `Q(zeta_d)`. | Avoid describing all relations as finite-field-only. These are rational/cyclotomic-coefficient Chow-motive statements, not the bounded **integral** norm/coherence realization the project needs. Some generation/classification discussion later is conditional on Beilinson/Tate. |
| `Goncharov`, `ZagierPolylog` | Authenticated author copies: Goncharov arXiv:math/0103059v4; Zagier chapter in *Arithmetic Algebraic Geometry*, author list dated 1990, pp. 391–430. | Motivic orientation. This check does not transfer every complex analytic identity into a specified integral motivic group. Zagier's scanned PDF lacks useful extracted text; no exact theorem was certified from OCR. |
| `Borel` | Original 1974 paper, Proposition 12.2, printed p. 271, visually verified: for `i>=2`, ranks over `R` are `0,r_1+r_2,0,r_2` for `i=0,1,2,3 mod 4`; bottom of p. 271 extends from an order to the number field. | For `Q`, `K_3(Q)` has rational rank 0 and `K_5(Q)` rank 1. This supports only the rational pure-K/regulator direction discussed. It does not say all dilogarithms or all mixed weight-2 logarithmic expressions vanish. |

### Bibliographic corrections

The inherited bibliography had incorrect or outdated metadata. Corrected entries are supplied in `BIBLIOGRAPHY_ADDITIONS.tex`:

- BKM1: **Compositio 157(9) (2021), 2046–2088**, DOI `10.1112/S0010437X21007454`; inherited pages 1908–1954 were wrong.
- BKM2: **JIMJ 23(6) (2024), 2461–2541**, DOI `10.1017/S1474748024000021`; inherited year/volume/pages were wrong.
- Česnavičius–Neururer–Saha: **JEMS 26(2) (2024), 573–637**, DOI `10.4171/JEMS/1367`.
- Otsubo–Yamazaki: **AFST series 6, 35(1) (2026), 95–135**, DOI `10.5802/afst.1842`.
- Pasten derivative paper: published CMB entry above, with consulted v3 specified.
- Agashe: latest consulted version **v2, 5 October 2025**, rather than silently presenting its 2008 first version as current.
- Zagier: **1990** follows the author's publication list; an electronic edition can show a later date. The consulted chapter/page range is unambiguous.

## Polylogarithm identities and branch conditions

The primary source is NIST DLMF §§25.12 and 25.11, retrieved through the web tool on 8 October 2026. Direct HTTP downloads of the pages and equation TeX files all returned 403, so no original local-source hash is asserted for these web-only records.

- Equation **25.12.10** defines `Li_s(z)=sum_(n>=1) z^n/n^s`, analytic for `|z|<1` for fixed complex `s`; on `|z|=1` the series converges if `Re(s)>1`. Termwise differentiation inside the disk yields `z dLi_s/dz=Li_(s−1)`; the derivative statement is a direct analytic consequence, not a separate novel theorem.
- Equation **25.12.6** gives the classical complement identity on `0<x<1`: `Li_2(x)+Li_2(1−x)=pi^2/6−log x log(1−x)`.
- Equation **25.12.4** gives `Li_2(z)+Li_2(1/z)=−pi^2/6−(1/2)Log(−z)^2` with principal branches on the cut plane `C\[0,infinity)`.
- Equation **25.12.13**, together with **25.11.14**, gives a safe integer-order negative-real specialization, for `x>0` and positive integer `n`:

\[
\operatorname{Li}_n(-x)+(-1)^n\operatorname{Li}_n(-1/x)
=-\frac{(2\pi i)^n}{n!}
B_n\!\left(\frac12+\frac{\log x}{2\pi i}\right).
\]

The Bernoulli expression follows by substituting the Hurwitz-zeta special value. Extending such identities across cuts requires explicit continuation/branch choices. A formal power-series identity near zero, a real-variable identity, and a principal-branch complex identity must not be used interchangeably without those choices. No source theorem supplies the manuscript's arithmetic realization solely from these functional equations.

## Search scope, authenticity, and limitations

Searches were by exact title, author, DOI, arXiv identifier, theorem terms, and status terms, using both web search engines (separate calls) and direct primary URLs. Current IUT/status queries used the stronger engine with recency. Primary publishers consulted included EMS, Cambridge, Annals, AFST/Centre Mersenne, and OUP; primary author repositories included RIMS, Bonn, Waterloo, Stanford, arXiv, MPIM, and the LANA project repository. NUMDAM supplied authenticated journal/seminar archives. Secondary news, crowdsourced summaries, and broad search snippets were not used to certify mathematical statements.

Not every context citation has a full proof audit. The records distinguish publication metadata, source authentication, exact statement reading, proof reading (Snyder), and applicability. Finite-range negative searches do not prove novelty. Arithmetic derivatives and classical polylogarithm identities are established; modularity does not settle the project's integral realization. The remaining manuscript hypotheses must remain visible in both the monograph and visual guide.

### Acquisition failures and repairs retained

1. The first Stewart–Yu response was rejected by a PDF-header-at-byte-zero validator. Its official author-host file had a **128-byte MacBinary prefix**. The raw download is preserved and hashed; removing only that wrapper produced the valid PDF body, separately hashed. No mathematical content was altered.
2. The cache helper failed its Git-ignore-coverage precondition. Direct private source retention was used and declared.
3. Six direct DLMF HTTP requests returned 403. Official web retrieval supplied the named equation statements; original download hashes are unavailable.
4. Oesterlé and Borel OCR had formula/character corruption. Crucial formulas were checked against rendered original pages; Zagier's extraction contained only page breaks, so it is metadata/context only.
5. Web-tool retrieval of some arXiv/PDF endpoints failed or was disabled; direct authorized primary downloads succeeded and are individually recorded. Alternate Mason/Stothers endpoints failed or gave metadata only; Snyder supplied the exact proved analogue.
6. A mistaken link while navigating the Stewart publication list led to an unrelated paper. It was neither retained as evidence nor used.

No inaccessible source is marked theorem-verified. The source manifest and theorem-leaf manifest make these limits reviewable.
