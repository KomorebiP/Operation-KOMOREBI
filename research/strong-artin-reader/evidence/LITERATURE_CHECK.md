# Strong Artin literature verification

Checked on 8 October 2026. This report verifies external statements used by the monograph and visual guide. It does not referee every cited proof, establish novelty, or supply the missing automorphy theorem.

## Questions and conventions

The checked arrows are cyclic cuspidal descent, the quotient character fibre, cyclic automorphic induction, compatibility with local parameters, the scope of regular automorphy lifting, abstract pseudocharacter realization, and highly ramified epsilon stability. Frobenius characteristic polynomials use one consistent arithmetic convention throughout the project. The source notation `rec` is translated to the normalized local Langlands correspondence used in the manuscript. A normalization shift or contragredient must be accounted for rather than silently omitted.

The archived manuscript and bibliography were read before searching. Sources were found using both web search engines and primary author, journal, arXiv, IAS, IMJ, and Numdam pages. Queries included “strong Artin conjecture cyclic base change descent ambiguity”, “solvable base change”, “automorphic induction monomial solvable”, “potential automorphy and change of weight”, and “nonregular symplectic representations”. Source acquisition and theorem extraction are separate checks. Local hashes and exact versions are recorded in `LITERATURE_SOURCE_MANIFEST.json`.

## AC89: definition, induction, and the solvable boundary

- James Arthur and Laurent Clozel, *Simple Algebras, Base Change, and the Advanced Theory of the Trace Formula*, Annals of Mathematics Studies 120, Princeton University Press, 1989. Author-hosted scan: <https://www.math.toronto.edu/arthur/pdf/30.pdf>.
- Read Chapter 3, Theorem 4.2, Theorem 6.2, Lemma 6.4, Theorem 7.1 and Proposition 7.2, printed pages 202, 215–218, 220–221.
- For a cyclic prime extension, invariant cuspidal representations descend and a full orbit of distinct cuspidal conjugates induces cuspidally. The local unramified operation is restriction or induction of Weil parameters.
- Theorem 7.1 establishes the nilpotent-image sector. Proposition 7.2 uses a character in the integral span of linear characters induced through subnormal cyclic-factor towers. It is not a theorem that every irreducible representation of every solvable group is automorphic.
- Classification: known external input. The general cyclic descent argument in the book has a historical gap. Use CR18 below for the repaired fibre statement rather than relying on Lemma 6.3 alone.

## CR18: cyclic descent and its free fibre

- Laurent Clozel and C. S. Rajan, *Solvable base change*, arXiv:1806.02513v1, 7 June 2018. <https://arxiv.org/pdf/1806.02513v1>. Published in *Journal für die reine und angewandte Mathematik* 772 (2021), 147–174, DOI <https://doi.org/10.1515/crelle-2020-0023>. Online publication occurred in 2020.
- Read Theorem 3 and its following remarks, preprint page 3, and the fibre proof in Section 3.
- Hypotheses: solvable Galois extension `E/F`, unitary cuspidal `Π` over `E`, and cuspidal descents `π,π′` with the same cuspidal base change. The descents differ by a Hecke character from `Gal(E/F)`. Nontrivial such twists remain distinct.
- For cyclic `E/F`, an invariant unitary cuspidal `Π` descends without an extra twist. For general solvable extensions the image statement includes an invariant character twist over `E`.
- Implication: the cyclic fibre is a free transitive quotient-character action. The source does not choose the descent attached to a specified Artin representation.

## RT02: an existing attachment difficulty

- Dinakar Ramakrishnan, *Modularity of solvable Artin representations of GO(4)-type*, *International Mathematics Research Notices* 2002, no. 1, 1–54, DOI <https://doi.org/10.1155/S1073792802000016>. Author manuscript: <https://www.its.caltech.edu/~dinakar/papers/go1.pdf>. Its 40-page author layout differs from the published pagination.
- Read Theorem A and the introduction, author pages 1–4.
- Theorem A treats solvable finite-image four-dimensional representations valued in `GO(4,C)`, with cuspidality exactly for irreducible representations.
- The introduction explicitly discusses the ambiguity between two quadratic descents and the need to attach the correct one to the Asai representation. This supports the relevance of the project’s attachment question, not its universal solution.
- Monomial Artin holomorphy is classical. Strong automorphy through arbitrary inducing extensions is a separate assertion. The source’s historical list of known cases is not used as a complete 2026 classification.

## HT99: local compatibility with explicit normalization

- Michael Harris and Richard Taylor, *On the geometry and cohomology of some simple Shimura varieties*, author preprint dated 30 August 1999, IMJ preprint 227. <https://www.imj-prg.fr/preprints/227.pdf>. Published book: *The Geometry and Cohomology of Some Simple Shimura Varieties*, Annals of Mathematics Studies 151, 2001.
- Read Lemma 12.7(4–6), author pages 162–163, after the normalization `rec_l(π)=r_l(π^∨⊗|det|^{(1-g)/2})`.
- For a cyclic prime extension of p-adic fields, the normalized local correspondence respects character twists, base change as restriction, and automorphic induction as induction, for irreducible admissible representations.
- Classification: known after translating the normalization. The published numbering differs. This verification cites the checked preprint lemma, not an assumed book number.
- This theorem alone does not promote arbitrary almost-everywhere Artin matching to attachment at every ramified and archimedean place. Keep those contracts distinct unless a further argument is supplied.

## BLGGT14: regular lifting does not supply the Artin gate

- Thomas Barnet-Lamb, Toby Gee, David Geraghty and Richard Taylor, *Potential automorphy and change of weight*, arXiv:1010.2561v4, 9 December 2013. <https://arxiv.org/pdf/1010.2561v4>. *Annals of Mathematics* 179 (2014), 501–609, DOI <https://doi.org/10.4007/annals.2014.179.2.3>.
- Read introductory Theorem B, the definitions in Section 2.1, and Theorem 4.2.1, preprint page 53. Version 4 adds a missing exclusion of `ζ_l∈F` in several statements.
- Theorem 4.2.1 assumes an imaginary CM field, a regular algebraic irreducible polarized representation, potential diagonalizability above `l`, irreducibility after restriction to `F(ζ_l)`, the stated prime bound, `ζ_l∉F`, and residual ordinary or potentially diagonalizable automorphy.
- Regularity means distinct Hodge–Tate numbers. A finite-image representation becomes trivial over a finite extension, hence has only Hodge–Tate weight zero. For rank greater than one it fails that regularity condition. This last observation is an application, not a quotation from the paper.
- Do not confuse automorphic coefficient weight zero with all Galois Hodge–Tate weights zero. Twists and conventional shifts must be stated.

## CG20: special nonregular theorems do exist

- Frank Calegari and David Geraghty, *Minimal modularity lifting for nonregular symplectic representations*, *Duke Mathematical Journal* 169, no. 5 (2020), 801–896, DOI <https://doi.org/10.1215/00127094-2019-0044>. Checked 2019 advance-publication copy: <https://www.math.uchicago.edu/~fcale/papers/Siegel.pdf>.
- Read Theorem 1.1 and Section 1.1. Its example is ordinary `GSp4` over `Q`, Hodge–Tate weights `[0,0,j−1,j−1]`, `p−1>j≥4`, distinguished Frobenius eigenvalues, large residual image, minimal ramification and residual modularity of weight `(j,2)`.
- This is a genuine nonregular result. Its hypotheses do not supply arbitrary rank, finite-image, all-zero-weight Artin lifting. The accurate statement is that the cited regular theorem is inapplicable and special nonregular results require their own checks, not that no nonregular lifting theorem exists.

## KY16: conditional construction and finite-group lifting

- Henry H. Kim and Takuya Yamauchi, arXiv:1403.5535v3, 7 April 2016. Actual manuscript title: *A uniform structure on subgroups of GL_n(F_q) and its application to a conditional construction of Artin representations of GL_n*. <https://arxiv.org/pdf/1403.5535v3>. Published in *Journal of the Ramanujan Mathematical Society* 32, no. 1 (2017), 75–99. The arXiv abstract retains an older short title.
- Read Theorem 1.1, Conjecture 5.1 and Section 6. Required inputs include finite Hecke field, bounded denominators, cuspidal Galois conjugates, residual realizations at sufficiently large coefficient primes and Rankin–Selberg coefficient bounds.
- The residual existence assertion is an assumption, not proved from finite Satake data. Section 6 lifts prime-to-`l` finite matrix images via a profinite Schur–Zassenhaus complement, then uses reduction injectivity on a finite polynomial alphabet for exact recovery.
- These provide a checked nearby precedent for the project’s finite-group reconstruction. No assertion of universal novelty follows.
- The checked lifting construction in Section 6, pages 15–16, can serve as the primary leaf for a finite prime-to-`l` matrix group: take its inverse image in `GL_n(O_lambda)`; the congruence kernel is pro-`l`, and a profinite Schur–Zassenhaus complement maps isomorphically to the residual group. This supplies a finite characteristic-zero lift without claiming that the precise inherited Serre or Curtis–Reiner editions have been read.

## DS74: uniqueness from Frobenius data

- Pierre Deligne and Jean-Pierre Serre, *Formes modulaires de poids 1*, *Annales scientifiques de l’École Normale Supérieure*, series 4, 7, no. 4 (1974), 507–530, DOI <https://doi.org/10.24033/asens.1277>. <https://www.numdam.org/item/ASENS_1974_4_7_4_507_0.pdf>.
- Read Lemma 3.2, printed page 513. Two continuous semisimple representations with matching characteristic polynomials on a density-one set of unramified primes are isomorphic. In characteristic zero equality of traces suffices. Its immediate context is `G_Q`.
- The number-field use is the same Chebotarev and character argument. Semisimplicity is essential. In modular characteristic keep characteristic polynomials rather than relying on bare traces without a suitable characteristic bound.

## Ch13/14: abstract realization and the continuity boundary

- Gaëtan Chenevier, *The p-adic analytic space of pseudocharacters of a profinite group and pseudorepresentations over arbitrary rings*, arXiv:0809.0415v2, final version 18 July 2013, 56 pages. <https://arxiv.org/pdf/0809.0415v2>. Published chapter 7, *Automorphic Forms and Galois Representations*, volume 1, LMS Lecture Note Series 414 (2014), 221–285; DOI <https://doi.org/10.1017/CBO9781107446335.008>. The checked preprint numbering differs from the print version.
- Proposition 1.27, preprint page 20: over a `Q`-algebra, determinants and pseudocharacters correspond. Theorem 2.12, page 28: for an algebraically closed field `k`, any dimension-`d` determinant on a `k`-algebra `R` has a semisimple realization `R→M_d(k)`, unique up to isomorphism, with the same kernel. Corollary 2.13 gives the group version. Theorem 2.16, page 31, gives a finite-dimensional semisimple quotient over perfect fields.
- This is abstract realization. Example 2.34, page 39, proves continuity only for **discrete** `GL_d(k)`. Complex or `l`-adic continuity needs a separate argument, such as the manuscript’s finite-dimensional image-algebra trace coordinates. Section 4.1, page 50, takes a **closed** rigid point with residue field finite over `Q_p`; the family gate must retain finite-valued specialization and coefficient-field conditions.

## Ch13: modular Brauer–Nesbitt, with full characteristic polynomials

- Additional leaf in the same checked primary work, arXiv:0809.0415v2: Theorem A, page 4; Lemma 1.12(ii) and its Amitsur formula proof, pages 12–14; Theorem 2.12 and Corollary 2.13, pages 28–29; explicit Brauer–Nesbitt uniqueness sentence in the proof, page 31.
- For **any algebraically closed field**, including characteristic `p` with no bound on `p`, a group determinant has a unique semisimple realization with its prescribed characteristic polynomials on group elements. Amitsur’s formula identifies the determinant on the group algebra from those polynomials. Hence two same-dimensional semisimple representations of a finite group over an algebraically closed characteristic-`p` field with identical characteristic polynomials at **every** group element are isomorphic. Finiteness of the group is more than this checked statement needs; no prime-to-`p` order assumption is imposed.
- This is the imported external uniqueness leaf used by `semisimple_label_collapse`. It is distinct from characteristic-zero trace uniqueness, from determinant/pseudocharacter equivalence over `Q`-algebras, and from cross-characteristic finite-group lifting. In modular characteristic do not substitute bare traces or assume values lie in the prime field. It has no fresh Lean coverage here.

## DH81: exact epsilon stability

- Pierre Deligne and Guy Henniart, *Sur la variation, par torsion, des constantes locales d’équations fonctionnelles de fonctions L*, *Inventiones Mathematicae* 64 (1981), 89–118. Author/IAS scan: <https://publications.ias.edu/sites/default/files/Number43.pdf>.
- Read definitions 0.5–0.7, pages 92–93, Theorem 4.6 and Lemma 4.7, page 110. Representations are continuous finite-dimensional complex Weil representations; inertia has finite image. Write `alpha(A)` for the minimum and `beta(A)` for the maximum constituent ramification slope. For a virtual representation `A` without tame constituents, there is `gamma∈K^×` such that every dimension-zero virtual `B` with `beta(B)<alpha(A)/2` satisfies `epsilon(B⊗A,psi)=det B(gamma)`.
- Application: take `A=eta`, `B=U−U'` for equal-dimensional representations with equal determinant. For sufficiently ramified `eta`, the epsilon quotient is one. Alternatively `B=U−(dim U)·1` gives the determinant formula. The source writes `det U(gamma)`; an inverse determinant formula requires defining `c=gamma^−1`. The equal-determinant conclusion is independent of this naming convention. This application is translated from the checked theorem, not a quotation.

## Sch15: a torsion cohomology occurrence gate

- Peter Scholze, *On torsion in the cohomology of locally symmetric varieties*, *Annals of Mathematics* 182, no. 3 (2015), 945–1066, DOI <https://doi.org/10.4007/annals.2015.182.3.3>. Checked published PDF: <https://annals.math.princeton.edu/wp-content/uploads/annals-v182-n3-p03-p.pdf>.
- Read Section 5.4, Theorem 5.4.1, page 1058, Corollary 5.4.3, page 1060, and Remark 5.4.6, page 1061. A nonzero field-valued Hecke eigenspace in the specified cohomology supplies a continuous semisimple residual representation with complete normalized unramified characteristic polynomials. The cohomological Hecke image itself carries a determinant modulo a bounded nilpotent ideal; field specialization kills that ideal.
- The checked 2015 version records historical Arthur/Mok stabilization dependencies for the general field range. Its explicit unconditional subrange is CM fields containing an imaginary quadratic field with the prescribed set of places pulled back from rational primes. Later resolution of those historical dependencies was not checked here. Actual eigensystem occurrence and exact Satake/Tate normalization remain premises of the project gate.
- The detailed setup and normalization are in `ADDITIONAL_LITERATURE_LEAVES.md`.

## GS14: unitary holomorphic-limit realization

- Wushi Goldring, with appendix by Sug Woo Shin, *Galois representations associated to holomorphic limits of discrete series*, *Compositio Mathematica* 150, no. 2 (2014), 191–228, DOI <https://doi.org/10.1112/S0010437X13007355>. Checked published copy openly linked from <https://sites.google.com/site/wushijig/home/publications>.
- Read Theorem 1.2.1, page 194, its Kottwitz/holomorphic/good-reduction setup, and proof pages 218–219. Inputs include the specified PEL unitary similitude datum, cuspidality, an `X`-holomorphic limit archimedean component, a good-reduction prime `l`, and a degree-one reflex-field prime above `l`. Output is a semisimple `l`-adic representation with normalized Weil–Deligne matching at the prescribed primes split over the totally real subfield.
- The proof uses a density-one set of split primes. Applying finite-trace rigidity requires an explicit finite alphabet for these **normalized** parameters, including the source’s `(1−n)/2` twist. Finite image is a separate project conclusion. The theorem does not cover arbitrary `GL_n` forms, universal all-place compatibility, or a family determinant at every singular point.
- Detailed assumptions, normalization and authorship metadata are in `ADDITIONAL_LITERATURE_LEAVES.md`.

## GK12/13: parallel weight-one companion forms

- Toby Gee and Payman Kassaei, *Companion Forms in Parallel Weight One*, arXiv:1206.6631v1, 28 June 2012, 12 pages. <https://arxiv.org/pdf/1206.6631v1>. Published in *Compositio Mathematica* 149 (2013), 903–913, DOI <https://doi.org/10.1112/S0010437X12000875>.
- Read Theorems A and B, page 2, Theorems 2.1.1, 3.1.1 and 4.1.3. The companion theorem assumes `p>2`, a totally real field unramified at `p`, an irreducible modular residual representation that remains irreducible over `F(zeta_p)`, the stated projective-image exclusions for `p=3,5`, and unramified, distinct Frobenius eigenvalues at every place over `p`. It produces a prime-to-`p`-level parallel weight-one form. Section 2 constructs parallel weight-`p` companions; Section 3 uses the Hasse invariant to obtain weight one.
- Theorem B assumes modularity of **every** irreducible continuous totally odd two-dimensional residual representation over `F` for **every** prime `p`, and concludes modularity of all irreducible continuous totally odd two-dimensional complex representations over `F`. This is a conditional rank-two implication. It does not supply residual realizations or weight raising in arbitrary rank.

## DW17/20: weight-one residual realization

- Mladen Dimitrov and Gabor Wiese, *Unramifiedness of Galois representations attached to weight one Hilbert modular eigenforms mod p*, arXiv:1508.07722v4, 28 November 2017, 24 pages. <https://arxiv.org/pdf/1508.07722v4>. Published title: *Unramifiedness of Galois representations attached to Hilbert modular forms mod p of weight 1*, *Journal of the Institute of Mathematics of Jussieu* 19, no. 2 (2020), 281–306, DOI <https://doi.org/10.1017/S1474748018000026>; online publication 23 April 2018.
- Read Theorem 1.1, page 1, Sections 4.2–4.4, pages 20–21. A parallel weight-one Hilbert modular form over an algebraic closure of `F_p`, level prime to `p`, and common `T_q`-eigenvector away from a finite set containing the level has an attached continuous semisimple two-dimensional residual representation, unramified outside the level, matching the stated Hecke traces. No `p`-distinguished condition is imposed, and any prime `p` is allowed.
- Section 4.4 records `det rho_f=epsilon` for a diamond-character eigenform. An application demanding complete characteristic polynomials must retain this determinant/diamond-character normalization, not silently replace it with bare traces in modular characteristic. Sections 4.2–4.3 use Hasse weight raising, lifting and partial Frobenius/ordinary companions; these are specific rank-two geometric methods.

## W26: a recent solvable sector

- Junwu Wang, *Strong Artin Conjecture for Generalized Octahedral Representations in GL_3*, arXiv:2609.38231v1, 28 September 2026. <https://arxiv.org/pdf/2609.38231v1>.
- Read the introduction, Theorem 1.1 on page 2, and Corollary 5.4 on page 17. Theorem 1.1 treats a number field and a three-dimensional generalized octahedral Artin representation with projective image `H_216=C_3^2⋊SL(2,3)`. Corollary 5.4 treats all primitive solvable six-dimensional Artin representations.
- The introduction says the result, combined with prior cases, completes the solvable three-dimensional sector. It does not establish arbitrary solvable rank.
- Status: primary source authenticated and statements extracted. This newly posted preprint’s entire proof and its preceding Gan adjoint-lift input were not independently audited here. Cite it as an external preprint result with that scope rather than a project proof.

## Source failures and corrections

The web PDF reader rejected the Arthur–Clozel scan as too large. It also failed direct PDF reads for several arXiv pages and timed out on an NSF manuscript mirror. Ordinary authorized downloads of the precise primary PDFs succeeded and `pdftotext -layout` supplied local text. One Poppler font-type warning occurred on the Wang PDF. Mathematical statements remained readable.

The Chenevier author-hosted PDF returned HTTP 502. The exact arXiv version and an alternative Durham manuscript downloaded successfully; the theorem check uses arXiv:0809.0415v2, whose title, version and date were verified against the arXiv landing page. The Durham copy was acquired as fallback and was not used to authenticate theorem numbering. The Deligne–Henniart scan has imperfect OCR; page 110 was rendered and visually read to check the slope inequality and determinant formula.

The institutional Dimitrov–Wiese PDF link returned HTTP 502. The precise arXiv version 4 downloaded successfully. A Gee–Kassaei author-hosted copy also downloaded, but the checked theorem locators use the authenticated arXiv version 1 explicitly. These fallback source copies are not additional checked works.

The skill cache helper was invoked for three source ingests, but each failed with “cannot verify Git ignore coverage for the literature cache”. `git rev-parse` reported no usable repository. Consequently this report does not claim a valid helper-managed cache. Authenticated local source copies and their hashes are recorded separately. Full third-party PDFs and extracted text are to be omitted from distributed deliverables unless redistribution is separately authorized.

An early message gave Kim–Yamauchi’s page range as 75–95 before publisher verification. The publisher page established 75–99, and the author agent was sent the correction immediately. The local preprint PDF has 26 pages rather than the preliminary message’s 24. A final check of actual PDF page headers corrected three preliminary page locators: BLGGT Theorem 4.2.1 is page 53, Deligne–Serre Lemma 3.2 is page 513, and Wang Corollary 5.4 is page 17. Clozel–Rajan’s inherited bibliography recorded 2020 without volume or pages. The journal issue is 772 (2021), 147–174, with online publication in 2020.

Clozel–Rajan version 1 has an evident domain typo in Theorem 3(1): the descending representation is printed as living over `E`, immediately before applying base change from `F` to `E`. The definition and proof use the representation over `F`. This report translates that domain to `F`. The inherited Langlands *Base change for GL(2)* bibliography entry should also be typed as a book rather than an article.

No global novelty search was performed. No failed search is evidence of novelty or nonexistence. The applicable classifications here are known external input, translated known input, adjacent conditional construction, and currently unresolved project implication.

The manifest records **fifteen checked primary works**, not every entry in the inherited bibliography. Other inherited citations remain outside this verification scope. Source authentication and exact statement extraction do not constitute an independent audit of every external proof.
