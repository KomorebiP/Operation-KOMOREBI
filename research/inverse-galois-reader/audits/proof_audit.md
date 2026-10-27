# Independent proof audit — Series09

Primary verdict: **proved as written within the exact reviewed scope, using explicitly verified external theorem inputs**.

Conjunction of the current closed elementary field examples, universal regular-operator statements, typed field/module translations, scoped conditional arithmetic implications, finite embedding and certificate results. This is not a verdict proving the unrestricted inverse or regular inverse Galois problem.

No unresolved failed implication was found in the frozen new source. External theorem inputs are accepted only in their checked primary-source forms. The audit does not prove those full external theorems again.

## The decisive boundary

Every finite group has a faithful rational regular module and a faithful field action on Q(x_g); Artin realizes it over the invariant base, and the subgroup calculus is exact in the regular realization. The five named groups are realized over Q. The stated rationality, regular-family, continuous proper-lift and explicit field-certificate inputs imply their scoped arithmetic conclusions.

The universal arithmetic existence implication remains open: Supply a verified arithmetic witness for every prescribed finite G: the certificate data or one of the declared conditional route inputs. The present sources do not supply that uniformly.

The exact S4 standard representation example shows why group-faithfulness cannot replace group-algebra-faithfulness. Its four-cycle average is zero although the subgroup is nonnormal and nonpermutable with the chosen transposition subgroup. The quadratic norm-loss and finite weak-lift examples likewise establish actual failures of the corresponding overstrong inference. These are precise boundaries, not arithmetic impossibility claims.

## Normalized claims and proof obligations

Each card in the JSON records its exact objects, hypotheses, coefficient domain, action/variance, source locator, proof check, dependency list and exceptional cases. The compact index below separates finite examples from universal statements.

| Card | Claim and exact conclusion | Evidence / dependencies |
|---|---|---|
| C01 | Polynomial formulation: Finite Galois realizations over Q are equivalent to separable-polynomial splitting-field realizations. | universal written argument; LC17, LC11, E01 |
| C02 | Regular module: Every finite G has an injective group-algebra action on its left regular module. | universal written argument; self-contained |
| C03 | Quadratic realization: Q(sqrt2)/Q has full group C2 and fixed field Q. | specific written field example; LC11 |
| C04 | Biquadratic realization: Q(sqrt2,sqrt3)/Q has group V4 and exactly the three named quadratic fixed fields. | specific written field example; C03, LC11 |
| C05 | Cyclic cubic realization: X^3+X^2-2X-1 has splitting field Q(alpha), degree3 and group C3. | specific written field example; LC11 |
| C06 | S3 realization: The splitting field of X^3-2 has degree6 and full group S3. | specific written field example; LC11 |
| C07 | S4 realization: X^4-X-1 has full splitting-field group S4. | specific written field example plus checked external bridge; LC08 |
| C08 | Variable action and fixed field: For every finite G, E=Q(x_g) over K=E^G is finite Galois with full group G and degree |G|. | universal written argument; LC10 |
| C09 | Primitive generic element and constants: E=K(x_1), trdeg_Q(K)=|G|, and Q is algebraically closed in Q(x_g). | universal written argument; C08 |
| C10 | Conditional Noether route: An actual rational presentation K=Q(t_1,...,t_d) for this invariant field implies a G realization over Q. | proved conditional implication; C08, C09, LC03, H01 |
| C11 | Two-variable invariant specialization: For the swap action, Q(x,y)^C2=Q(s,p), s=x+y,p=xy; the named three specializations have the stated outcomes. | specific written field and specialization example; LC10 |
| C12 | Subgroup projection and rank: E_H is the orthogonal projection onto V^H with rank [G:H]; H<=K gives E_HE_K=E_KE_H=E_K. | universal written argument; C02 |
| C13 | Exact compatibility: In the regular realization, E_HE_K=E_KE_H iff HK=KH iff HK is a subgroup; then product is E_HK=E_<H,K>. | universal written argument; C02, C12 |
| C14 | Normality and quotient: Normality of H, centrality of e_H, commutation of E_H with all lambda(g), and invariance of V^H are equivalent; the quotient action is faithful. | universal written argument; C02, C12 |
| C15 | S3 matrices: The declared six-by-six H12,H23 matrices and commutator are exact, with squared Hilbert-Schmidt norm3/4. | exact specific finite computation and written example; C12, C13 |
| C16 | Faithful S4 boundary: On the faithful sum-zero standard S4 module, a nonnormal four-cycle subgroup has zero average and commutes with a nonpermutable subgroup average. | specific exact representation counterexample; C02 |
| C17 | Fixed-field lattice: For a given finite Galois L/Q, fixed fields have reverse inclusions, expected degrees and normal quotients; intersection and compositum correspond to generated subgroup and subgroup intersection. | universal written argument; LC11 |
| C18 | Normal-basis translation: An existing finite Galois L/Q is equivariantly isomorphic to Q[G] as a module, and subgroup averages transport. | universal written argument; LC12, C02, C17 |
| C19 | Trace and norm: P_H=Tr_(L/L^H)/|H|, norm is product of H-conjugates, and trace/norm obey tower composition; the quadratic loss example is exact. | universal written argument; LC13, C17 |
| C20 | One-parameter Hilbert implication: A verified finite Galois F/Q(t), modeled outside nonzero constraints, has infinitely many rational specializations with full group G; a regular input therefore suffices. | checked external theorem and proved conditional implication; LC03, H02 |
| C21 | Nonregular cubic toy: X^3-t has generic S3 splitting field Q(u,zeta3), t=u^3, and specialized groups trivial,C2,S3 at0,1,2. | specific written generic-field and finite specialization example; C06 |
| C22 | Arithmetic quotient to field: A continuous finite-target lift of G_Q gives a finite Galois M/Q with group its image, containing the prescribed L; an onto lift gives E,N,G with the specified quotient. | universal written argument; LC16 |
| C23 | Finite C2/C4 obstruction: The identity of finite C2 has no homomorphic lift through C4 parity. | specific exact finite group proof; self-contained |
| C24 | Split and diagonal weak lifts: A continuous split section composed with onto rho is weak; for nontrivial N that particular lift is not proper. Onto coordinates need not give an onto paired map. | universal written implication with exact finite examples; self-contained |
| C25 | Kernel coverage: For any group Gamma and onto rho, a homomorphic lift is onto iff lift(ker rho)=N. | universal written argument; self-contained |
| C26 | Central correction equation: For central N and normalized section s, c(g,h)=s(g)s(h)s(gh)^-1 is normalized and satisfies the displayed cocycle law; u*s*rho is a homomorphism precisely by the stated correction equation. | universal written argument; C23 |
| C27 | Field certificate: For |G|=n, irreducible monic f degree n and n distinct compatible root substitutions in Q[X]/f imply full Galois group G over Q. | universal written argument; LC10 |
| C28 | Certificate examples and format: The quadratic certificate closes C2, and any existing characteristic-zero realization can be encoded in the certificate format. | specific exact certificate plus conditional encoding; C03, C27, LC17 |
| C29 | Product algebra boundary: Q^G with pointwise multiplication is equivariant, commutative, associative and unital with fixed constants Q, but is not a field for nontrivial G. | universal written argument; self-contained |
| C30 | Edition and appendix scope: The edition records closed examples and operator statements, conditional arithmetic routes, bounded computation and dated external context; it asserts no uniform inverse Galois proof. | scope and factual-source review; LC01, LC02, LC04, LC05, LC14 |

## Dependency graph

The graph in the JSON has an edge from each required input to its claim. Artin (LC10) feeds the actual variable action and certificate, rather than a bare module. Hilbert (LC03) feeds C10 only after the actual invariant-field rational presentation H01 and feeds C20 only after the actual family H02. Ordinary correspondence (LC11), normal basis (LC12), and trace/norm (LC13) all begin with an already supplied field. Continuous finite-quotient correspondence (LC16) begins with the continuous lift. Primitive elements (LC17) format an already existing realization. No conclusion constructs its own input through a circular dependency.

## Obligation matrix

| Obligation | Status | Evidence |
|---|---|---|
| O01 — Field versus vector space/product algebra | passed | C02,C08,C27,C29; actual multiplication and field input are retained. |
| O02 — Arithmetic base and full automorphism group | passed | C08 has invariant base K; C27 explicitly forces Q. Named five fields have full splitting-field groups. |
| O03 — Coefficient domain and normalized division | passed | Regular operator proofs use C; exact matrices Q; field arguments Q characteristic zero. No characteristic-dividing-order generalization. |
| O04 — Action law, composition and variance | passed | Left multiplication regular action, right cosets Hg, embeddings kH, and reverse certificate substitution all checked. |
| O05 — Group algebra versus group faithfulness | passed | Coefficient recovery proves needed algebra injectivity; C16 disproves the weaker converse and is explicitly scoped. |
| O06 — Compatibility support and multiplicity | passed | Uniform product multiplicity and positive exact support give both directions without assuming HK a subgroup first. |
| O07 — Normality and quotient kernel | passed | Conjugation supports, unitary invariant complements and regular quotient action give all equivalences and faithful quotient. |
| O08 — Fixed-field/module/multiplication translation | passed | LC11/12 start with an actual finite Galois field; normal basis is linear, transported multiplication separately typed. |
| O09 — Trace normalization, norm nonlinearity, towers | passed | LC13 is used only in separable range; degree/order and coset directions checked; concrete norm-loss example proves limitation. |
| O10 — Hilbert exact hypotheses and exceptional locus | passed | Full primitive extension, Q Hilbertian, r>=1 and nonzero constraints retained; one versus several parameters distinguished. |
| O11 — Regularity and constants | passed | Q rational-function constants proof works by evaluation; x^3-t generic splitting field explicitly nonregular; dummy-variable constants excluded. |
| O12 — Noether implication direction | passed | Actual rational invariant presentation is a hypothesis, not inferred from transcendence degree or assumed for all G. |
| O13 — Continuity, weak/proper distinction and field quotient | passed | Finite targets discrete, G_Q Krull, open normal kernel correspondence and image subgroup specified. Kernel coverage is separately proved. |
| O14 — Central defect sign and arithmetic obstruction scope | passed | Associativity proves normalized cocycle and corrected-section formula; no noncentral use or universal vanishing claimed. |
| O15 — Finite checks and exhaustive bounds | passed | Exact rerun byte-identical; independent all 64 subset enumeration yields six S3 subgroups, all 36 pair calculations and incidence matrices match. |
| O16 — Degenerate and trivial cases | passed | G=1, H=1/G, split nontrivial kernel, repeated roots, nonsquare d, singular t=0 and nonsingular group drop are all separated. |
| O17 — External dependency authenticity and application | passed at exact imported statement scope | Relevant pinned primary-source statements and their manuscript hypotheses checked; entire external proofs are not re-proved by this audit. |
| O18 — Source-attributed dated context | passed at attribution scope | Swan report and M23 preprint outside elementary dependencies; classical sectors named as external inputs and source presentation caveats retained. |
| O19 — Conservative mathematical proofreading | passed | All current new mathematical LaTeX, formulas/data and code reviewed; static references/citations and current TeX diagnostics pass. No auditor manuscript changes. |
| O20 — Universal arithmetic existence | open obligation, not claimed | For arbitrary G a field certificate, actual rational invariant presentation, regular Q(t) realization or continuous proper arithmetic lift remains to be constructed. |
| O21 — Final PDF page layout | separate review | This math/source report does not certify final reader-page layout; that review pins PDFs and individual page renders separately. |

## Exact source checks

Primary statements and applications were read in the retained pinned copies: Milne Corollary 3.11 pp.45–46; Theorem 3.17 pp.47–48; good-prime Theorem 4.28 pp.69–70; primitive-element Theorem 5.1 p.78; normal-basis Definition 5.17/Theorem 5.18 pp.86–90; trace/norm Remark 5.47/Proposition 5.48 pp.107–108; restriction Proposition 7.7 p.123 and infinite correspondence Theorem 7.13 pp.125–127. The root-embedding and finite splitting-field count are covered by Milne Proposition 2.4(b) and Proposition 3.2. The complete external proof of normal basis or Shafarevich existence is not reconstructed here.

Dèbes lecture Theorem 2.6.3(a),(d) p.85, localization Remark 2.6.5 p.87, Hilbert Definition 5.2.2/Theorem 5.2.4 p.206 and Proposition 5.2.14 pp.213–214 supply the exact one/several-parameter full-group specialization used. The notes are a pinned undated work-in-progress snapshot; unfinished cross-references are not evidence. The primitive polynomial generates the whole extension, its specialized irreducibility retains degree |G|, and the specialized group embeds into G outside the model locus. Zariski density avoids any prescribed finite collection of nonzero polynomial constraints by their product. Q being Hilbertian, rather than characteristic zero alone, is essential.

The source-attributed classical sectors use the corrected Schmidt–Wingberg Theorem 1 and Milne Example 4.32. The latter printed polynomial has leading coefficient 31; coefficientwise monic CRT or subtracting 30X^n preserves its modular factors and repairs the presentation. No uncorrected recipe is asserted in the manuscript. The cubic discriminant criterion is restricted to Q; the source’s characteristic two wording caveat is retained. Swan’s negative rationality example is Milne-reported context only. The October 2026 M23 v2 theorem statements and dates were checked as context, with no independent Belyi/Magma replay. These contextual claims are not elementary-proof dependencies.

Exact PDF/text snapshot hashes and source URLs are in the JSON and source registry. Only the relevant historical finite Galois/operator section and ledger were used for reconstruction; the larger recovered manuscript is outside the current audit.

## Finite evidence and all 22 figures

The exact example script was replayed and its serialized result was byte-identical to the frozen scientific JSON. A separate incidence construction uses entry(y,x)=1/|H| iff y*x^-1 lies in H. It enumerates all 64 subsets of S3, finds exactly six subgroups, checks all 36 ordered pairs and their uniform supported products, and independently matches both displayed averages and the commutator of squared Hilbert–Schmidt norm3/4. That fresh result is in `audits/finite_reconstruction.json`. The JSON-to-manuscript basis permutation is `[0,2,1,5,3,4]`.

Bounds: five scalar polynomials; six S3 subgroups and 36 ordered pairs; one faithful S4 boundary; two finite lift models; parameter values 0, 1, 2. Exact domains are Q,F2,F7 and finite permutations. The wrapper and version 2 manifest were inspected, including resource limits and hashes; the parent records validator success, and this agent did not rerun that validator. No random seed is used. Universal theorems rely on their proofs, not these bounds.

Every mathematical formula/data function for all 22 plates, all guide captions/carry-forward statements and the provenance facts were reviewed. All 44 figure PDF/PNG asset hashes and both pinned generator inputs match. Figure06 binary64 root positions are illustrative only. Figure02 inclusion directions, Figure07 cycle types, regular subgroup ranks/matrices, quadratic trace/norm, regular conditional specialization and finite embedding domains agree with the proof chain. Mathematical figure/data review does not certify final page layout.

## Resolved findings and conservative self-review

- F01: Figure02 inclusion arrows. Group arrows labelled subset pointed toward smaller subgroup. Visual author reversed group arrows to 1 subset H subset G; field arrows run K subset L^H subset L. Current formula/data rechecked.
- F02: Figure07 cycle labels. Specific (1234),(123) labels suggested unsupported common root numbering from finite factors. Visual author changed to cycle types4 and3+1 and guide explicitly disclaims shared labelling.
- F03: paper/chapters01_03.tex Figure02 caption. Caption did not describe actual fixed-field diagram. Author replaced with finite correspondence caption and exact source locator.
- F04: paper/chapters04_06.tex subgroup projector proof/caption. Left-action orbits Hg were called left cosets. Author changed both to right cosets, leaving formulas unchanged.
- F05: paper/chapters04_06.tex split-lift paragraph. Phrase both finite group maps described rho imprecisely; rho has profinite G_Q domain. Author states rho continuous by hypothesis, s continuous between finite discrete groups.
- F06: guide domain/source map. Profinite domain and published Pre-Galois source key/year needed precision. Guide names Pi profinite, DebesHarbater2021 and actual title/year; source map checked.
- F07: Noether negative contextual sentence. Negative source context required explicit attribution and audit boundary. Author now states Milne reports Swan and original counterexample not independently audited or used in conditional proof dependencies.
- F08: Appendix source map. New LC16/17 leaves omitted from the short table. Root added exact continuous quotient and primitive element rows.
- F09: Guide reproduction page command. TeX --only rendered as an en dash. Conservative source correction uses texttt{-{}-only}; mathematical content unchanged.

Review mode was conservative and read-only. This auditor made no manuscript edit, no mathematical token change and no routine copyedit. Authors made the identified local corrections; final changes were reread. The entire frozen reader and guide source, shared mathematical definitions, and all 22 formula/data functions are covered by the pins below and the complete JSON asset list. Current static checks passed 82 labels, 21 references and 5 distinct cited keys; current paper/guide TeX logs contain none of the selected unresolved-reference, overfull, missing-character, error or duplicate-destination diagnostics. These source checks are not a proof assistant certificate or visual layout verdict.

## Reviewed current bytes

| Path | Bytes | SHA-256 |
|---|---:|---|
| `paper/appendices.tex` | 6869 | `3a85727068fe4aa9fa53a6dab685b9f8fe2d47209e945b1215f6fd376e3842bb` |
| `paper/bibliography.tex` | 2337 | `9b22a0b1b874ddef94578aa29427a10dc75b33dfa558ed6b8deca3ca9b6f232e` |
| `paper/chapters01_03.tex` | 31414 | `fa3fdd8ba9ab7645ed227bda6c74fe47e4be309ec9d7308f8891b16df3b4e4f0` |
| `paper/chapters04_06.tex` | 41065 | `274d698c7fff19f60ff670a5c70209ac907fa95f0f7a046b05b9cc79743506e8` |
| `paper/chapters07_08.tex` | 14322 | `afca3df9640af01c6d4be7a8a7ce2074679a0746f78b7512779e6024ef7d8b71` |
| `paper/main.tex` | 1742 | `4f478581593e2227ab6f9e2bfb87f1718378aae69ea1a73f861a6285671319d3` |
| `paper/opening.tex` | 3013 | `a6cfb8499e143e27e71956e1fa0be6c1610171cb8029742e9c115ed9aa879a69` |
| `shared/guide_preamble.tex` | 2715 | `ef89a4061fa43f6b4284994b458155fa9d12d02ebd788e5d6a9fdb3450ba0071` |
| `shared/preamble.tex` | 3568 | `1b624e164db263a4d628f652315ded6909107a6c9a950260c92e0cde7bf86526` |
| `visual/main.tex` | 21279 | `9f2f93df8f2029fb009392729d665acd0e5210355b8a4c1133e47b29e91beb0a` |
| `visual/figures.py` | 29402 | `37c10a38cc024dd6fc03c3c40a67c7e6c9894c37de509f6873d568e4d2fddfdd` |
| `visual/figure_provenance.json` | 17858 | `466762596fb4eddc25ca4375a0e131cd1dc195b55ed7a14040e4b04a236e36ba` |
| `computations/exact_examples.py` | 7548 | `3da02eda8d0f04a3f1bc6eba82c9767a4fc3ae30f2aca7c22aaa1b09789f9d83` |
| `computations/run_examples.py` | 4327 | `7c8434bc38a158c1b18aceb0343c71ed7bc0c2c3746a821b8f1e7345bbf83233` |
| `computations/exact_examples.json` | 13466 | `041cb0aebc969d7eb18a0def147e0bf3a4fd24ae508d83e17c79aee4aba9cf63` |
| `literature/source_contracts.md` | 24561 | `fca0824c1d944b7e2668d9cf56dec37860f760a546b2530277eeeadc5f8f395f` |
| `literature/source_contracts.json` | 44647 | `afa4762522612f4c9ba33677f3f88252cba7a39d988954b6d115823f346f1407` |
| `literature/bibliography.tex` | 2337 | `9b22a0b1b874ddef94578aa29427a10dc75b33dfa558ed6b8deca3ca9b6f232e` |
| `README.md` | 4567 | `ecf3d8a9be598b167b5922c373b662229364cd4690ee57a3beecc362536da9e2` |
| `build.py` | 1728 | `0279f1fa0aaebac84e7a89e641b5fc7802fc30aaf63c5469bdcf09e329e949de` |
| `audits/finite_reconstruction.json` | 1007 | `8410de5c49ea33843834befc20c8bdf9f5f66770392867837b5a53f54bfd159e` |

All 44 figure asset hashes and the two historical source hashes with their exact partial/full read scopes are recorded in `proof_audit.json`; the asset list is also checked against `visual/figure_provenance.json`. Reader PDF hashes are deliberately left to the separate final layout review because a rebuild can change pagination without changing a mathematical source.

The cheapest next exact candidate check is: For any proposed individual field certificate, check irreducibility, all root/composition remainders in the stated reversed substitution order, and pairwise distinct residues. This audits a candidate; it does not assert candidate existence.

## Final layout-driven source delta review

The final opening, shorter chapter2 heading and condensed section7.4 were conservatively reread. The opening retains every claim boundary and historical/source qualification. Section7.4 retains exact root/composition remainders, reduced-residue distinctness, irreducibility evidence, rejection of collapsed actions or an incorrect fixed base, all stated finite counts, and the distinction between checking one candidate and finding fields uniformly. No theorem or proof changed.

Needspace before normality, FloatBarrier before section6.4, a contents-only page break before chapter5, package/metadata spacing and Figure7.1 width are layout changes. All 44 figure assets remain byte-identical. The table above now pins the final reviewed source bytes; prior and final hashes and each exact delta are preserved in the JSON. The mathematical verdict is unchanged. Final reader PDF layout remains covered by the separate page-QA records.

## Final three-block prose adjustment

The last chapter 7 delta condenses only its coordinate-obligation paragraph, Figure 7.1 caption and finite-laboratory sentence. The field multiplication, prescribed action, full group and rational base remain explicit. The counts remain five polynomials, all 36 pairs of six S3 subgroups, one faithful S4 boundary and two lift models. Their scope remains the named finite examples. All theorem/proof and displayed-equation environments are byte-identical to the prior reviewed source. The source table now pins the final chapter bytes, and the JSON retains the prior/final hashes. The mathematical verdict is unchanged.
