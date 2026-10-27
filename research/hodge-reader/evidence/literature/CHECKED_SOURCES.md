# Hodge source contracts — 9 October 2026

Prepared for *Conjecture Series 06: Hodge*, Komorebi P. This report checks selected external inputs to the recovered research packages. “Extracted” means that the exact primary statement and its hypotheses were read; it does not mean that every proof in the cited paper was independently reconstructed. Project proofs, computations, regularity hypotheses and correspondence constructions require their own audit. No global proof of the rational Hodge conjecture is asserted.

No third-party paper is copied into this publication bundle. The files here contain bibliographic records, limited paraphrases and source contracts. Primary documents were consulted through public source retrieval. No persistent source cache was requested or initialized; consequently there are no local-paper hashes to report. Search and access boundaries are recorded below.

## Release-relevant outcomes

| Input | Outcome for this edition |
|---|---|
| General rational Hodge conjecture | Official formulation extracted; Clay still labels it unsolved |
| Lowest-weight image; pure semisimplicity | Exact leaves in **Deligne II**, not the inherited citation to III |
| Uniruled fourfolds | Rational HC extracted from Arapura’s independent primary reproof |
| Fermat transfer | Concatenation and complementary-pair removal extracted; no arbitrary tensor cancellation |
| Five-phase complete intersection | Its defining equations are already Aoki’s (p=5) cycle; present determinant/period recomputation separately |
| Villaflor determinant and period | Exact hypotheses extracted; smoothness of the cycle is not required |
| Half twists | Hodge structures and Hodge inclusions extracted; no automatic algebraic correspondence |
| Kang, arbitrary-degree Fermat fourfolds | Published citation authenticated and later primary corroboration found; original exact theorem/proof extraction unavailable |
| Markman | Exact fourfold/split-sixfold scope authenticated; published corollary also covers abelian varieties of dimension at most five |
| Brosnan | Version and abstract authenticated; exact Proposition 4 remains inaccessible here |
| Secant preprint identification | Version 5, §4.3 Proposition 2 authenticated; a narrow eigencharacter mismatch is identified |
| Odd primitive Dirichlet value | Nonvanishing follows from exact numbered primary statements; application to the project lattice remains separate |

## 1. Official statement and live status

**Pierre Deligne, “The Hodge Conjecture,” Clay Mathematics Institute official problem description**, §1, p.2; §2, pp.2–3. [Primary PDF](https://www.claymath.org/wp-content/uploads/2022/06/hodge.pdf). [Current official problem page](https://www.claymath.org/millennium/hodge-conjecture/), checked 2026-10-09.

For a smooth projective complex variety, every rational cohomology class of type $(p,p)$ in degree $2p$ is conjectured to be a rational linear combination of classes of codimension-$p$ algebraic subvarieties. The coefficients are rational; an individual effective cycle is not required. Deligne’s remarks explain that the integral version is false and that replacing projectivity by a general Kähler hypothesis changes the problem. Clay’s current page explicitly marks the problem “Unsolved.” These statements do not prevent particular families from already satisfying HC.

**Status:** exact primary formulation and official current status extracted.

## 2. Deligne’s lowest-weight image and semisimplicity

**Pierre Deligne, “Théorie de Hodge II,” Publications Mathématiques de l’IHÉS 40 (1971), 5–57**, DOI [10.1007/BF02684692](https://doi.org/10.1007/BF02684692). [Primary scanned article](https://www.numdam.org/article/PMIHES_1971__40__5_0.pdf).

**Corollary 3.2.17, printed p.39** (PDF page index 35) gives, for smooth separated $U$ and a smooth compactification $\bar X$,

$$
\operatorname{im}\bigl(H^n(\bar X,\mathbf Q)\to H^n(U,\mathbf Q)\bigr)=W_nH^n(U,\mathbf Q).
$$

**Lemma 4.2.3, printed p.44** (PDF index 40) establishes semisimplicity for the specified rational Hodge families closed under the listed operations and admitting homogeneous polarizations. Its point case supplies splitting of polarizable pure rational Hodge structures. It does not split arbitrary mixed Hodge structures.

**Correction:** both locators belong to *Hodge II*. The recovered Carrier70 citation “Hodge III, Lemma 4.2.3” is incorrect: III’s sections begin at 5 and refer backward to II. The project must establish the relevant smooth compactification and purity before applying these results.

**Status:** exact primary leaves extracted.

## 3. Uniruled fourfolds

**Donu Arapura, “Varieties with very little transcendental cohomology,” arXiv:0706.2506v1**, 17 June 2007. [Primary PDF](https://arxiv.org/pdf/0706.2506).

**Corollary 4.2, printed p.11**, states rational HC for uniruled fourfolds and generalized HC for uniruled threefolds. The ambient convention is smooth projective varieties over $\mathbf C$, with rational coefficients. Arapura independently proves the fourfold result using the motivic-dimension bound for uniruled varieties and Proposition 4.1. This supplies a primary reproof of the input attributed historically to **A. Conte and J. P. Murre, “The Hodge conjecture for fourfolds admitting a covering by rational curves,” Math. Ann. 238 (1978), 79–88**.

The original Conte–Murre proof was not separately extracted. The reviewed carrier’s smooth projective resolution must first be shown uniruled; the result does not itself show that the proposed singular carrier or its resolution is uniruled.

**Status:** exact theorem extracted via independent primary reproof; original historical source not independently audited.

## 4. Non-pseudoeffective canonical class

**S. Boucksom, J.-P. Demailly, M. Păun and T. Peternell, “The pseudo-effective cone of a compact Kähler manifold and varieties of negative Kodaira dimension,” arXiv:math/0405285v1**, 14 May 2004. [Primary PDF](https://arxiv.org/pdf/math/0405285).

**Theorem 2.6, printed p.7**: a smooth projective manifold that is not uniruled has pseudoeffective canonical class. Its contrapositive supplies the uniruledness conclusion once non-pseudoeffectivity of the resolution’s canonical class is proved. It does not transfer a canonical-class calculation from a singular model to an arbitrary resolution. The project’s covering curves and their avoidance of exceptional divisors are load-bearing local hypotheses.

**Status:** exact primary theorem extracted; project application remains a separate geometric implication.

## 5. Fermat character criterion and rational packets

**T. Shioda and T. Katsura, “On Fermat varieties,” Tohoku Math. J. (2) 31(1) (1979), 97–115**, DOI [10.2748/tmj/1178229881](https://doi.org/10.2748/tmj/1178229881). [Primary PDF](https://www.jstage.jst.go.jp/article/tmj1949/31/1/31_1_97/_pdf/-char/en).

The original article and its Proposition 2.4, pp.103–104, were inspected for the inductive cohomological construction. The character criterion was crosschecked in da Silva’s Theorem 2.1, cited below. For full-support characters of an even-dimensional degree-$m$ Fermat variety, the primitive complex eigenspaces have dimension one. Rational Hodge classes complexify into the eigenspaces whose residue sum is $(n/2+1)m$ after multiplication by every unit modulo $m$. A single complex character line is not itself a rational class: rational packets require the unit/Galois orbit.

**Genival da Silva Jr., “Notes on the Hodge conjecture for Fermat varieties,” arXiv:2101.04739v2**, 8 May 2021, [PDF](https://arxiv.org/pdf/2101.04739), Theorems 2.1–2.2 and Corollary 2.3, was also inspected. Published: *Experimental Results* 2:e22 (2021), DOI 10.1017/exp.2021.14. Its finite computations were not replayed in this source check.

**Status:** criterion and specified construction/restatement extracted; no audit of every theorem in these papers.

## 6. Aoki, transfer operations and historical cycles

**Noboru Aoki, “Some new algebraic cycles on Fermat varieties,” J. Math. Soc. Japan 39(3) (1987), 385–396**, DOI [10.2969/jmsj/03930385](https://doi.org/10.2969/jmsj/03930385). [Primary PDF](https://www.jstage.jst.go.jp/article/jmath1948/39/3/39_3_385/_pdf/-char/ja).

**Theorem 1-4, p.388**, attributes to Shioda and Ran two operations: concatenation of algebraic characters is algebraic; removal is valid for an appended character made of complementary pairs. It supplies no cancellation of an arbitrary tensor factor. **Theorem 2-1, p.388**, constructs the cycle representing an odd-prime standard character, with $m=pd$ and $\gcd(a,d)=1$. The standard-character definition on p.387 also requires $d/\gcd(i,d)>2$.

At $p=5,d=q$, Aoki’s equations, together with the elementary-symmetric reformulation in §3, give exactly

$$
e_1(x_0^q,\ldots,x_4^q)=e_2(x_0^q,\ldots,x_4^q)=0,
\qquad x_0\cdots x_4=\kappa x_5^5,
\qquad\kappa^q=-1/5.
$$

Attribute the defining cycle to Aoki and separately report this edition’s determinant/period computation. The Transfer210 standard blocks $(p,i)=(5,5),(7,2)$ at degree 35 satisfy the listed coprimality conditions.

**Status:** exact statements and equations extracted and key pages visually inspected; no general sixfold HC conclusion.

## 7. Half twists

**Bert van Geemen, “Half twists of Hodge structures of CM-type,” J. Math. Soc. Japan 53(4) (2001), 813–833**, DOI [10.2969/jmsj/05340813](https://doi.org/10.2969/jmsj/05340813). [Published primary PDF](https://www.jstage.jst.go.jp/article/jmath1948/53/4/53_4_813/_pdf/-char/en).

**§1.4, pp.814–815:** the negative half twist is an effective structure of weight $k+1$. The positive half twist of weight $k-1$ requires $V^{k,0}_{\bar\Sigma}=0$. **Proposition 2.8, p.818**, describes the corresponding matching or conjugate-matching $K$-action subspaces inside tensor products, including $V\subset V_{1/2}\otimes K_{-1/2}$ when the positive half twist exists. **§2.9, p.819**, gives a Hodge-theoretic cohomological inclusion involving the CM abelian variety $A_K$.

These statements concern Hodge structures. They do not automatically provide a Chow correspondence, an algebraic projector or an algebraic adjoint realizing every proposed inclusion. A half twist also changes weights differently from an ordinary Tate twist. The project must verify existence of the selected half twist and separately construct any required algebraic kernel.

**Status:** exact published statements extracted, including the conjugate CM-type condition.

## 8. Complete-intersection class and period

**Roberto Villaflor Loyola, “Periods of complete intersection algebraic cycles,” arXiv:1812.03964v5**, 30 March 2021. [Primary PDF](https://arxiv.org/pdf/1812.03964).

**Theorems 1.1–1.2, pp.1–2:** $X\subset\mathbf P^{n+1}$ is a smooth degree-$d$ hypersurface, $n$ is even, $Z$ is a middle-dimensional complete intersection with ideal $(f_1,\ldots,f_{n/2+1})$, and $F=\sum f_i g_i$. The ordered tuple $H=(f_1,g_1,\ldots)$ fixes the determinant sign. The primitive class is represented by the specified multiple of the residue with numerator $\det\operatorname{Jac}(H)$. If $P\det\operatorname{Jac}(H)\equiv c\det\operatorname{Hess}(F)\pmod {J_F}$, with the required numerator degree, the period is the stated nonzero normalization times $c$.

The paragraph after Theorem 1.2 expressly permits singular $Z$, using deformation to a smooth pair. It does not dispense with the complete-intersection ideal, dimensional or ambient smoothness requirements. The project must establish those and compute $c\ne0$, retaining its row order.

**Status:** exact primary hypotheses extracted; singularity of $Z$ alone is not an obstacle.

## 9. Kang: existence statement and source-access boundary

**Su-Jeong Kang, “Refined motivic dimension of some Fermat varieties,” Bull. Austral. Math. Soc. 93(2) (2016), 223–230**, DOI [10.1017/S0004972715001379](https://doi.org/10.1017/S0004972715001379), online 25 November 2015. [Publisher record](https://www.cambridge.org/core/journals/bulletin-of-the-australian-mathematical-society/article/refined-motivic-dimension-of-some-fermat-varieties/EEBE2D9F98935C50BED5E3AD71DAEF59).

The publisher metadata and abstract were authenticated. The original full PDF could not be retrieved through the attempted publisher paths. Exact extraction of its theorem hypotheses and proof is therefore **unavailable in this audit**. A later primary paper, Miranda–Movasati–Rufino–Villaflor, §3.4, explicitly attributes the all-degree Fermat-fourfold HC/GHC result to Kang’s Corollary 3.2. The inherited description of a published existence result is therefore bibliographically supported; it must not be called a newly proved project theorem or an independently audited original proof.

**Status:** citation and published-result attribution authenticated; original exact theorem/proof audit conditional on obtaining its full text. Indexed search snippets were not treated as proof.

## 10. September 2026 Fermat context

**Maximiliano Miranda, Hossein Movasati, Lucas Rufino and Roberto Villaflor, “Lengths of Hodge characters in Fermat varieties,” arXiv:2609.27301v2**, 26 September 2026. [Primary PDF](https://arxiv.org/pdf/2609.27301).

**Theorem 1.1 (=4.4)** claims HC for all-dimensional Fermat varieties of degree below 65, except 44, 51 and 52, and the corresponding weighted cases by lcm degree. **Theorem 2.3, pp.16–17**, gives the weighted-character criterion and Galois interpretation. **§3.4, p.26**, cites Kang’s Corollary 3.2 for arbitrary-degree Fermat fourfolds.

This is current preprint context. Its integer-program computations and complete proof were not independently replayed here. The project should avoid outdated blanket claims about still-open small degrees, but should explicitly distinguish this source’s theorem claims from its own verified computations and constructions.

**Status:** exact source statement/version authenticated; cited theorem claim, not a new project validation.

## 11. Markman: precise completed scope

**Eyal Markman, “Cycles on abelian 2n-folds of Weil type from secant sheaves on abelian n-folds,” arXiv:2502.03415v2**, 8 June 2025. [Primary PDF](https://arxiv.org/pdf/2502.03415). **Theorem 1.5.1, p.9**, treats Hodge–Weil classes of polarized abelian sixfolds of Weil type for an imaginary quadratic field with discriminant $-1$; **Corollary 1.6.1, p.9**, treats HC for abelian fourfolds.

Published current account: **“Secant Sheaves and Weil Classes on Abelian Varieties,” Proceedings of the International Congress of Mathematicians 2026, vol.3, 586–602**, DOI [10.1137/25M1803796](https://doi.org/10.1137/25M1803796), [primary publisher text](https://epubs.siam.org/doi/10.1137/25M1803796). **Theorem 1.2** establishes algebraicity of Weil classes for fourfolds and split sixfolds with imaginary quadratic $K$. **Corollary 1.3** gives HC for abelian varieties of dimension at most five.

These sources do not establish all nonsplit sixfolds, arbitrary-dimensional Weil-type varieties or every CM field. The broader discussion of a strategy is not a completed theorem in that scope.

**Status:** exact versions and theorem scope extracted; no independent reconstruction of the entire long proof.

## 12. Brosnan: limited authentication

**Patrick Brosnan, “Discriminants of Hermitian forms, maximal degenerations and Kontsevich’s tropical approach to the Hodge conjecture,” arXiv:2609.14169v1**, 12 September 2026. [Primary record](https://arxiv.org/abs/2609.14169).

The primary record and abstract authenticate the title, author, version and degeneration/discriminant topic. The full text at the attempted arXiv PDF/HTML/export routes was unavailable in this audit. The project attributes to **Proposition 4** the implication from maximal degeneration to split discriminant, represented by $(-1)^n$ for dimension $2n$. That exact proposition and its hypotheses were **not extracted here**. A search-visible third-party mirror was not substituted for an authenticated primary copy.

**Status:** metadata/abstract authenticated; exact load-bearing proposition conditional. A discriminant obstruction to this degeneration route would not itself imply nonalgebraicity of Weil classes.

## 13. Narrow secant-preprint source audit

**Deep Bhattacharjee and Ushashi Bhattacharya, “Relative Secant Cycles and Hodge Classes,” Preprints.org 202602.0462, version 5**, submitted 2 August and posted 5 August 2026. [Primary version URL](https://www.preprints.org/manuscript/202602.0462/v5) redirects to the presently indexed version 5. It is identified by the publisher as not peer reviewed.

**§4.2 and §4.3 Proposition 2** were read directly. The latter proof identifies a $\mathrm{Norm}_{K/\mathbf Q}^{\,n}$ eigenspace with the Weil space and treats $\eta^n$ as invariant under $K^\times$. Under the ordinary endomorphism pullback on a polarized Weil-type $2n$-fold, $\eta^n$ has eigencharacter $\mathrm{Norm}^n$, whereas the two complex Weil lines have characters $a^{2n}$ and $\bar a^{2n}$. For $n=3,a=2+i$, these are $125$ versus $-117\pm44i$. Thus the stated identification is incompatible with that action.

This is a local failure of the cited identification under the stated action. It is not a verdict on every result, construction or possible corrected formulation of the manuscript. The project’s exact arithmetic replay is separately recorded.

**Status:** exact source/version/claim authenticated; narrow representation comparison only.

## 14. Odd primitive Dirichlet nonvanishing

**Romyar Sharifi, “Iwasawa Theory,” Chapter 4, Cyclotomic fields**, [author’s primary notes](https://www.math.ucla.edu/~sharifi/notes/iwasawa-ch04.html), accessed 2026-10-09. **Lemma 4.1.18** gives the nonzero primitive Gauss sum; **Corollary 4.1.22** gives nonvanishing at 1; **Theorem 4.2.14** relates the odd primitive value at 1 to $B_{1,\bar\chi}$; **Proposition 4.2.13** gives $L(0,\chi)=-B_{1,\chi}$. Therefore, as a formal corollary, $L(0,\chi)\ne0$ for every primitive odd Dirichlet character.

The [NIST DLMF §25.15](https://dlmf.nist.gov/25.15), equations 25.15.5 and 25.15.9, independently supplies the functional equation and nonvanishing at 1. Primitivity and oddness matter. An imprimitive value at zero can acquire vanishing Euler factors. The dyadic proof must establish its primitive-conductor reduction and distinguish rational span from integral generation; neither conclusion is supplied by this analytic leaf.

The inherited Washington book citation was not directly extracted. Add the checked Sharifi locator rather than marking Washington independently audited.

**Status:** exact numbered inputs extracted; nonvanishing is an explicitly stated formal deduction.

## Historical references outside this check

The retained citations **VoisinHodge, CDK, BeauvilleDonagi, DebarreKuznetsov, AtiyahHirzebruch, CharbonneauStern, VanGeemenIzadi, OtsuboYamazaki**, Washington’s book, and internal **Seed I–III** were not freshly theorem-audited here. Their inclusion does not upgrade every recovered claim about cubic fourfolds, Gushel–Mukai varieties, K-theory or coniveau to checked status. The official Deligne description independently confirms failure of the integral HC. The general carrier/half-twist correspondence pipeline remains conditional wherever algebraic kernels or projectors are only Hodge-theoretically specified.

## Provenance and search boundary

Checked 2026-10-09 using the mathbox literature-check workflow. Searches prioritized Clay, author pages, publisher/J-STAGE scans, Numdam and exact arXiv records. Source-access failures are distinguished from false mathematics. This is a theorem-dependency check, not a comprehensive novelty survey. No claim of newness follows from a search gap; the historical identity of the Aoki cycle is affirmatively recorded. Source URLs and exact versions are machine-readable in `source_contracts.json`; optional bibliography blocks are in `bibliography_additions.tex`.
