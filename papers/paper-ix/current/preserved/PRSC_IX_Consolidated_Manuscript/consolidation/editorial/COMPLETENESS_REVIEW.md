# Paper IX completeness review

**Primary verdict: proved as written. Status: PASS, within the available-source scope below.**

The edited manuscript accounts for each mathematical core statement in the preserved 28-page original and every subsequently completed block, within an explicitly bounded proved-results scope; historical-only and unrecovered material is identified rather than represented as newly proved.

Every mathematical core item enumerated from the preserved 28-page paper and every completed-block checklist entry is covered explicitly, by an identified specialization, or with an explicit evidence/scope acknowledgment. No missing completed mathematical block remains in this audited source set. This does not assert global completeness over unavailable historical files or completion of open research questions.

The audit covers 58 matrix rows, all 14 entries of the original arithmetic formula registry, all 31 completed-checklist entries and all 11 mathematical supplements. The rows comprise 25 original-paper entries, 21 completed-block entries, 4 native prose/external entries and 8 historical-scope entries. These are coverage records, not counts of independent theorems.

## Independent method and dependency chain

The source set was the preserved 28-page status-corrected paper, the 11 mathematical completion/supplement TeX files, the completed-results checklist, completed-block exposition files, the native progress note and the retrieved Annals text. Current statements and definitions were read directly; the preceding consolidation audit was not treated as sufficient evidence. For restored statements, the named raw Lean statements and critical proof interfaces were read. Six supporting source files were compared byte-for-byte to their preserved baseline ZIP members.

The evidence chain is: original claim or completed-block statement → current definitions and statement/proof → exact raw Lean declaration when present → preserved source member and its verification frontier. External and prose results are identified separately. No Lean rebuild or new primary-source authentication was performed in this review.

## What was corrected

- Concrete packet denominator product and its verified bound restored.
- Bernoulli boundary and sign convention restored as a classical derivation, with missing formal bridge explicitly disclosed.
- Lucas row reduction, integral common inverse and standard-window residue period restored from existing checked sources.
- Signed-zigzag inverse coefficient bridge restored.
- Exact normalization-loss counterexample restored from actual recursive-coefficient theorems.
- Joint affine lifting made explicit at depth zero.
- Historical intrinsic obstruction, polynomial CRT and rectangular-relation progress acknowledged with separate evidence labels.
- Affine Mahler kernel parameter domain made explicit.

The before snapshot omitted or left implicit these recoverable mathematical details. Several were consequences of broader theorems, but their source formulas, normalizations or boundary hypotheses were not explicit. Those omissions have now been repaired. The Bernoulli boundary remains a classical derivation without a located dedicated Lean bridge.

## Original paper and its core formulas

| ID | Source | Content | Current location | Status and evidence |
|---|---|---|---|---|
| O01 | Original PDF §1, Definition1.1; Theorem1.2, pp4–5 | Arithmetic seed vocabulary; residue selectors, orthogonality, reconstruction and refinement | 10_foundations.tex, opening and thm:residue-reconstruction | covered. Matched prior Lean source; no new compilation in this review. Seed tuple is descriptive; no undeclared category of arbitrary seed objects is inferred. |
| O02 | Original PDF §2, Theorem2.1, pp5–6 | Unit-EGF transport, inverse binomial convolution, conjugate projectors | thm:egf-coordinates | covered. Matched prior Lean source; no new compilation in this review. |
| O03 | Original PDF §2, Theorem2.2 and Boundary2.3, pp6–7 | Filtered triangular reconstruction and finite precision scope | thm:filtered-foundation; thm:triangular-foundation | covered. Matched prior Lean source; no new compilation in this review. Finite rows do not require infinite convergence. |
| O04 | Original PDF §3, Definition3.1 and Theorem3.2, pp7–8 | Original normalized section reciprocal; actual triangular recurrence | def:arith-euler; eq:arith-kernel; eq:arith-triangular | covered. Matched prior Lean source; no new compilation in this review. |
| O05 | Original PDF §3, Proposition3.3, p8 | Explicit product denominator D(N,j,n) | prop:arith-denominator | restored and inspected. Congruential.clearing_product and Congruential.universal_denominator_clearing Generic theorem present; explicit packet specialization omitted in before snapshot. |
| O06 | Original PDF §3, Example3.4, p8 | Euler boundary C(2,0,n)=E(2n), signed sech convention | 20_arithmetic.tex, Classical odd-length coordinates; lem:arith-reconstruction | covered. Matched prior Lean source; no new compilation in this review. |
| O07 | Original PDF §3, Example3.5, pp8–10 | Bernoulli boundary C(2,1,n)=(2−2^(2n))B(2n), n≥0 | ex:arith-bernoulli | restored and inspected. Original PDF explicit identity and derivation; no matching baseline Lean Bernoulli boundary found Use B(t)=t/(e^t−1), B1=−1/2. Mark classical explanatory identity, not newly formalized theorem. |
| O08 | Original PDF §4, Lemma4.1, p10 | Literal alternating odd-power source, full EGF, even part | def:arith-odd-source; proof of thm:arith-odd-reconstruction | covered. Matched prior Lean source; no new compilation in this review. Current theorem strengthens odd-prime assumption to every positive odd length. |
| O09 | Original PDF §4, Theorem4.2, p11; Second supplement §2 | Zigzag identification gamma_m=(−1)^m Z_(2m+1) | eq:arith-signed-zigzag | restored and inspected. Zigzag.inverse_is_signed_zigzag Gamma itself was defined correctly through sech², but source normalization bridge omitted. |
| O10 | Original PDF §4, Theorem4.2 and Corollary4.3, p11 | Exact odd Euler transform; explicit triangular row weights and p^(2M+2) truncation | thm:arith-odd-reconstruction; cor:arith-odd-ladder | covered. Matched prior Lean source; no new compilation in this review. |
| O11 | Original PDF §5, Lemmas5.1–5.2, pp13–14 | Actual dyadic source R(2n), reciprocal beta and 2-adic integrality | def:arith-truncation; lem:arith-reconstruction | covered. Matched prior Lean source; no new compilation in this review. Current source statement strengthens source integrality to nonzero unit. |
| O12 | Original PDF §5, Theorem5.3 and Corollary5.4, pp14–15 | Exact dyadic reconstruction and original 2^(2M+2) bound | lem:arith-reconstruction; thm:arith-sharp-tower | covered. Matched prior Lean source; no new compilation in this review. Current 2^(4M+3) bound is stronger and includes original weak bound. |
| O13 | Original PDF §6, Classical Input6.1 and Proposition6.2, pp15–17 | Odd and dyadic unit decomposition | thm:finite-unit-foundation | covered with finite formal scope. FiniteUnits; UnitRefinement; DyadicUnits Finite decompositions and compatibility are proved. Original infinite local-unit decomposition remains a classical input, not an added infinite theorem. |
| O14 | Original PDF §7, Classical Input7.1, Theorem7.2, Corollary7.3, pp17–18 | Finite Mahler reconstruction, coefficient shifts and weighted differences | thm:mahler-foundation; thm:weighted-mahler-foundation | covered with finite formal scope. Matched prior Lean source; no new compilation in this review. Full continuous Mahler expansion not claimed to follow from finite interpolation. |
| O15 | Original PDF §7, Theorem7.4, p18 | Geometric difference identity and finite unit-mode gain | thm:unit-modes-foundation | covered. Matched prior Lean source; no new compilation in this review. |
| O16 | Original PDF §7, Theorem7.5, p19; All-residue supplement | Unnormalized global differences; normalized factorial-loss bound | thm:arith-divisor-base; all-address proof | covered. Matched prior Lean source; no new compilation in this review. |
| O17 | Original PDF §8, Classical Input8.1 and Theorem8.2, pp19–20 | Lucas row reduction and diagonal unit | prop:arith-lucas-window | restored and inspected. StandardWindow.lucas_row_reduction; standard_diagonal_mod_one; factorial_unit_window All prime p, positive m, j<p, q≤n; source actually covers arbitrary natural q. |
| O18 | Original PDF §8, Corollary8.3, p20; Fifth supplement §1 | Integral standard-window coefficients, residue inverse and address independence | prop:arith-lucas-window | restored and inspected. WindowIndependence.coeffPadic_coe; standard_window_integral; reduced_row; residue_independence Must first establish p-integrality, then use actual residue map; no reduction homomorphism Q→Fp. |
| O19 | Original PDF §8, Corollary8.5, p21; Seventh supplement §2 | Uniform standard-window residual period h=(p−1)/m for n≥1 | cor:arith-window-period | restored and inspected. WindowPeriod.uniform_standard_window_period; standard_window_period_divisibility Implicit consequence of stronger current theorem, but defining residual sequence and explicit corollary missing before review. |
| O20 | Original PDF §9, Theorem9.1 and Corollary9.2, pp21–22 | Companion jumps, Cayley–Hamilton packet recurrence and Fibonacci/Lucas specialization | thm:companion-foundation | covered. Matched prior Lean source; no new compilation in this review. |
| O21 | Original PDF §10, Theorem10.1, p22 | Dyadic–odd finite CRT address and selector reconstruction | thm:crt-foundation | covered. Matched prior Lean source; no new compilation in this review. |
| O22 | Original PDF §13, Proposition13.1, pp25–26 | Exact counterexample to unrestricted normalized no-loss claim | ex:arith-normalization-loss | restored and inspected. Normalization.normalized_first; normalized_second; normalized_difference; difference_valuation; factorial_loss_is_sharp p=3,m=2,N=6,j=3,n=k=1: difference64/455, valuation0. Before snapshot had only corrected estimate, not counterexample. |
| O23 | Original PDF §13, Conjectures13.2–13.3 and Boundary13.4, p26 | Canonical obstruction and prime-independent spine questions | subsec:native132; subsec:native133 | explicitly open. Raw original statements and native progress note Fixed polynomial results and shared linear corrections do not settle unrestricted seed presentation/descent claims. |
| O24 | Original PDF §§11–12, §14, AppendixA/B, pp23–28 | Historical formula registry, finite numerical certificates, implementation map, selected rows and original proof ledger | sec:verification; subsec:historical-scope; preserved original PDF | preserved history, not all repeated. Original PDF available; old original plotting scripts and complete historical numerical package not recovered Original16figures, tables, example row data and code snippets are not all reprinted. Historical tests are not relabelled fresh tests. |
| O25 | Original PDF §15, p27 | Concluding operator-chain interpretation | 00_scope.tex and foundations opening | covered in prose. Expository interpretation Recast across opening paragraphs rather than retaining separate repetitive conclusion. |

## Subsequently completed blocks

| ID | Source | Content | Current location | Status and evidence |
|---|---|---|---|---|
| B01 | Nishibuchi_Conjecture_Completion.tex §§1–3 | Full stated external conjecture, coefficient matching, complete dyadic branch and n0=r | thm:arith-nishibuchi; thm:arith-dyadic-differences | covered. Matched prior Lean source; no new compilation in this review. |
| B02 | review/SHARP_DYADIC_README.md; strengthening formalization | All-row N=4 differences and multiplier valuation amplification | thm:arith-dyadic-differences; cor:arith-amplified | covered. Matched prior Lean source; no new compilation in this review. |
| B03 | review/EXACT_DYADIC_PERIODS_README.md | Exact nonzero N=4 displacements, d=(1,1,5,3), all positive periods and least period | 20_arithmetic.tex, Exact displacement valuations and least packet periods | covered. Matched prior Lean source; no new compilation in this review. |
| B04 | review/SHARP_DYADIC_README.md; DyadicSharpTower.lean | Exact classical kernel, optimal tail4M+3, first omitted sharpness and row-dependent summand weights | lem:arith-kappa; thm:arith-sharp-tower; prop:arith-row-weight | covered. Matched prior Lean source; no new compilation in this review. |
| B05 | isometry/INDEPENDENT_PROOF_AUDIT.md; DyadicFourIsometry.lean | Unique continuous isometric Z2 extensions, normalized and original exact affine images | 20_arithmetic.tex, Isometric continuation of the four dyadic packets | covered. Matched prior Lean source; no new compilation in this review. |
| B06 | native/Native_Conjectures_Progress.md; native/lean/IntegerFiniteCokernel.lean | Finite affine residual obstruction incl positive composite modulus, q=1 and depth 0 | prop:affine-obstruction; thm:finite-polynomial-obstruction | covered. Matched prior Lean source; no new compilation in this review. |
| B07 | shared_correction/INDEPENDENT_PROOF_AUDIT.md; SharedCorrection.lean | Shared correction quotient, surjective labels, joint fiber product, finiteness, paired universal factorization | thm:common-correction and following universal-property paragraph | covered. Matched prior Lean source; no new compilation in this review. |
| B08 | shared_correction/INDEPENDENT_PROOF_AUDIT.md | Actual joint affine lifting and choice-independent correction labels | 30_lifting.tex, affine specialization immediately after cor:shared-polynomial | restored explicitly and inspected. Komorebi.AffinePair.joint_lift_iff_class_eq and finite_affine_pair_compatibility, raw AffineSharedCorrection.lean:60 and:100 Positive composite q and q=1 included; L=0 retained. |
| B09 | polynomial_lifting/POLYNOMIAL_LIFTING.md | Actual Taylor bridge, fixed-presentation obstruction and representative independence | lem:polynomial-taylor; thm:finite-polynomial-obstruction; prop:representative-independence | covered. Matched prior Lean source; no new compilation in this review. |
| B10 | polynomial_lifting/POLYNOMIAL_LIFTING.md | Shared polynomial correction and unconditional solvability formulation | cor:shared-polynomial and proof | covered. Matched prior Lean source; no new compilation in this review. |
| B11 | polynomial_counts/POLYNOMIAL_LIFT_COUNTS.md | Actual residue-digit equivalence, torsors, kernel/cokernel rank counts | thm:lift-torsor-count | covered. Matched prior Lean source; no new compilation in this review. |
| B12 | polynomial_towers/PADIC_TOWERS.md | Single compatible tower, fixed Jacobian, p-adic limit, exact root and smooth branching | thm:smooth-tower; thm:smooth-padic-root | covered. Matched prior Lean source; no new compilation in this review. |
| B13 | polynomial_deformation/POLYNOMIAL_DEFORMATION.md | Uniqueness among all square roots in base ball; actual coefficient perturbations and nearby root stability | thm:smooth-padic-root; prop:smooth-coefficient-stability | covered. Matched prior Lean source; no new compilation in this review. |
| B14 | polynomial_charts/POLYNOMIAL_PARAMETER_CHARTS.md | Arbitrary target local surjectivity, square homeomorphism, selected-minor rectangular chart and precision equivalence | thm:continuous-parameter-chart; eq:polynomial-ball-image and proof | covered. Matched prior Lean source; no new compilation in this review. |
| B15 | polynomial_weighted/WEIGHTED_LIFTING.md | Arbitrary integral p-adic coefficient/center weighted lifting; exact inverse exponent and full-ball uniqueness | thm:weighted-lifting; ex:weighted-boundary | covered. Matched prior Lean source; no new compilation in this review. |
| B16 | polynomial_motion/FIRST_ORDER_ROOT_MOTION.md | Weighted coefficient deformation and first-order error depth2M−3s | thm:coefficient-motion | covered. Matched prior Lean source; no new compilation in this review. |
| B17 | polynomial_prescribed/PRESCRIBED_PARAMETER_LIFTING.md | Prescribed digit obstruction [r+Kv], actual fiber and rank counts | thm:prescribed-obstruction | covered. Matched prior Lean source; no new compilation in this review. |
| B18 | polynomial_parameter_towers/PRESCRIBED_PARAMETER_TOWERS.md | Every compatible integer parameter path, arbitrary p-adic endpoint, exact branching and square uniqueness | thm:prescribed-integer-tower; thm:prescribed-padic-tower | covered. Matched prior Lean source; no new compilation in this review. |
| B19 | polynomial_joint_motion/JOINT_DEFORMATION.md | Simultaneous coefficient+parameter movement with original Jacobian and sharp error depth | thm:joint-deformation | covered. Matched prior Lean source; no new compilation in this review. |
| B20 | polynomial_regularity/ANALYTIC_REGULARITY.md | Actual polynomial strict derivative; analytic local graph and derivative−JinvK | lem:actual-polynomial-derivative; thm:analytic-local-graph | covered. Matched prior Lean source; no new compilation in this review. |
| B21 | polynomial_regularity/ANALYTIC_REGULARITY.md | Every supplied continuous local selection, open-set regularity, integral specialization in ambient field | thm:selection-regularity; cor:selection-open-regularity; cor:integral-analytic-graph | covered. Matched prior Lean source; no new compilation in this review. |

## Native results with distinct evidence

| ID | Source | Content | Current location | Status and evidence |
|---|---|---|---|---|
| N01 | native/Native_Conjectures_Progress.md §3 | Intrinsic finite obstruction for finitely presented commutative Z-algebras via naive cotangent complex | subsec:native133, final paragraph before Arithmetic refinements | explicitly acknowledged with source pointer. Earlier live Stacks source review; no immutable primary source copy pinned; not Lean-formalized No claim that full seed category is covered. Full statements and proofs remain in the preserved native progress note; no new external-source authentication is claimed. |
| N02 | native/Native_Conjectures_Progress.md §4, A precise reconstruction that does hold | Finite CRT bijection for solution sets of the same integer polynomial list | subsec:native133, final paragraph before Arithmetic refinements | explicitly acknowledged with source pointer. Elementary prose proof in preserved note, not a new Lean-certified statement Current finite address CRT statement does not explicitly state this polynomial solution-set version. Full statements and proofs remain in the preserved native progress note; no new external-source authentication is claimed. |
| N03 | native/Native_Conjectures_Progress.md §4, A finite compatibility criterion | Rectangular relations iff equality-label representation; component quotient universal property | subsec:native133, final paragraph before Arithmetic refinements | explicitly acknowledged with source pointer. Prose proof in preserved note, not Lean-formalized Distinct from checked shared-linear-correction theorem; no undefined smallest-spine claim. Full statements and proofs remain in the preserved native progress note; no new external-source authentication is claimed. |
| N04 | native/Native_Conjectures_Progress.md §4 | Global integer diagonal cannot be continuous Hausdorff equality locus | subsec:native133 | covered as prose. Explicit CRT-density/properness/closed-diagonal proof, not claimed Lean-formalized |

## Recovered historical scope

| ID | Source | Content | Current location | Status and evidence |
|---|---|---|---|---|
| H01 | Annals §§2,4, labels thm:mode_group_algebra, thm:minimal_period, thm:standard_window_fourier | Finite-field mode algebra, subgroup inversion, Fourier invariance, minimal modal periods | subsec:historical-scope | preserved outside current proved-result scope. Retrieved textual Annals copy, not certified as exact original bytes; no blanket Lean coverage Related special cases appear in current text; preservation is not promotion to newly checked theorem. |
| H02 | Annals §5, thm:unified_local_euler, thm:unified_inverse_local_euler, cor:local_source_change, prop:odd_row_weight | Unified local source changes and odd exact row weights | subsec:historical-scope | preserved outside current proved-result scope. Retrieved textual Annals copy, not certified as exact original bytes; no blanket Lean coverage Related special cases appear in current text; preservation is not promotion to newly checked theorem. |
| H03 | Annals §6, thm:carmichael_mahler_scalar, thm:polynomial_exponential_mahler, thm:matrix_carmichael_mahler, thm:finite_adelic_transfer | Carmichael, polynomial exponential modes, matrix and finite adelic transfer | subsec:historical-scope | preserved outside current proved-result scope. Retrieved textual Annals copy, not certified as exact original bytes; no blanket Lean coverage Related special cases appear in current text; preservation is not promotion to newly checked theorem. |
| H04 | Annals §6, thm:amice_derivative_unified, thm:odd_analytic_branch, thm:direct_dyadic_interpolation | Amice analytic pullback, depleted odd Euler branches, direct dyadic analytic interpolation | subsec:historical-scope | preserved outside current proved-result scope. Retrieved textual Annals copy, not certified as exact original bytes; no blanket Lean coverage Related special cases appear in current text; preservation is not promotion to newly checked theorem. |
| H05 | Annals §7, thm:polyphase_shift_matrix through cor:euler_polyphase_refinement | Broader polyphase shift matrices, infinite branch reconstruction, kernel composition, sparsification, precision amplification | subsec:historical-scope | preserved outside current proved-result scope. Retrieved textual Annals copy, not certified as exact original bytes; no blanket Lean coverage Related special cases appear in current text; preservation is not promotion to newly checked theorem. |
| H06 | Annals §§8–9, thm:packet_lift_obstruction and following recurrence-spine results | Packetwise obstruction splitting and broader integral recurrence spine | subsec:historical-scope | preserved outside current proved-result scope. Retrieved textual Annals copy, not certified as exact original bytes; no blanket Lean coverage Related special cases appear in current text; preservation is not promotion to newly checked theorem. |
| H07 | Annals §7, thm:discrete_polyphase_reconstruction, thm:nested_discrete_polyphase, prop:polyphase_carry_convolution, affine-kernel displays | Finite polyphase synthesis, nesting, Cauchy carry law, affine kernel and binary example | subsec:polyphase-exposition | covered as prose. Finite algebraic derivations included; no new Lean certification claimed All affine-kernel indices now declared: M≥1 and s,r,k∈N. |
| H08 | strengthening/recovery/RECOVERED_EDGE_TOWERS.md; historical/recovered_source_windows | Older odd-prime edge formulas and binary digit-sum/carry forms | subsec:historical-scope | recovery/formalization remains open. Some exact source windows survive, but full historical derivations and matching formal coverage not all recovered Do not call these settled or absent from all storage. |

## Original formula registry

| Registry ID | Coverage rows |
|---|---|
| AR-01 | O01 |
| AR-02 | O02 |
| AR-03 | O04, O05 |
| AR-04 | O08, O09, O10 |
| AR-05 | O10 |
| AR-06 | O11, O12 |
| AR-07 | O11, B04 |
| AR-08 | O14 |
| AR-09 | O17, O18, O19 |
| AR-10 | O15 |
| AR-11 | O20 |
| AR-12 | O07 |
| AR-13 | O21 |
| AR-14 | O16, O22 |

## Completed checklist

| Completed item in source checklist | Coverage rows |
|---|---|
| Full stated Nishibuchi conjecture. | B01 |
| Amplification by the step valuation. | B02 |
| Exact dyadic displacements and all positive packet periods. | B03 |
| Optimal classical dyadic edge tower. | B04 |
| Finite affine obstruction. | B06 |
| Shared-correction quotient — completed in the preceding block. | B07 |
| Actual joint affine lifting criterion — completed in the preceding block. | B08 |
| Continuous dyadic isometric bijections — completed in the preceding isometry block. | B05 |
| Original coefficient extensions and their exact images — completed in the preceding isometry block. | B05 |
| Actual polynomial Taylor formula — completed in the preceding polynomial block. | B09 |
| Fixed-presentation finite polynomial obstruction — completed in the preceding polynomial block. | B09 |
| Polynomial representative independence — completed in the preceding polynomial block. | B09 |
| Actual shared polynomial corrections — completed in the preceding polynomial block. | B10 |
| Correction-digit torsors and exact polynomial lift counts — completed in the preceding count block. | B11 |
| Compatible smooth polynomial towers and exact p-adic roots — completed in the preceding tower block. | B12 |
| Square polynomial root uniqueness — completed in the perturbation block. | B13 |
| Actual coefficient perturbations — completed in the perturbation block. | B13 |
| Nearby perturbed roots — completed in the perturbation block. | B13 |
| Unique square-root stability — completed in the perturbation block. | B13 |
| Local polynomial surjectivity and square inverse — parameter-chart block. | B14 |
| Continuous rectangular parameter charts — parameter-chart block. | B14 |
| Weighted nonlinear lifting — preceding block. | B15 |
| Integral polynomial Taylor and contraction — preceding block. | B09/B15 |
| Weighted perturbation and first-order root motion — preceding block. | B16 |
| Prescribed-parameter polynomial obstruction and exact fibers — preceding block. | B17 |
| Compatible towers with prescribed parameter paths — preceding block. | B18 |
| Arbitrary prescribed p-adic endpoints and exact branching — preceding block. | B18 |
| Simultaneous coefficient and parameter deformation — preceding block. | B19 |
| Local analyticity and differentiability — current block, both parts complete. | B20 |
| Regularity of supplied continuous root selections — current block. | B21 |
| Manuscript consolidation — current edition. | editorial consolidation |

## Mathematical supplements

| Preserved supplement | Coverage rows |
|---|---|
| `Paper_IX_First_Lean_Block_Supplement.tex` | O01, O02, O03, O04, O05, O17, O22 |
| `Paper_IX_Second_Lean_Block_Supplement.tex` | O06, O08, O09, O10 |
| `Paper_IX_Third_Lean_Block_Supplement.tex` | O11, O12 |
| `Paper_IX_Fourth_Lean_Block_Supplement.tex` | O14, O15 |
| `Paper_IX_Fifth_Lean_Block_Supplement.tex` | O13, O18, O21 |
| `Paper_IX_Sixth_Lean_Block_Supplement.tex` | O20 |
| `Paper_IX_Seventh_Lean_Block_Supplement.tex` | O19 |
| `Paper_IX_Eighth_Lean_Block_Supplement.tex` | O16 |
| `Paper_IX_Singular_Amice_Supplement.tex` | O16 |
| `Paper_IX_All_Residue_Completion_Supplement.tex` | O16, O22 |
| `Nishibuchi_Conjecture_Completion.tex` | B01 |

## Definitions and scope obligations

| Obligation | Result |
|---|---|
| Original EGF, normalized C and unnormalized U, packet/degree shifts | Passed: explicitly defined and kept distinct. |
| Euler and Bernoulli boundary conventions | Passed: signed sech convention and B1=−1/2 supplied; Bernoulli evidence limitation explicit. |
| Odd source, gamma, signed zigzag normalization and weighted transfer | Passed: all defined with exact bridge. |
| Dyadic source, reciprocal beta, kernel weight and truncation | Passed: no conflation of classical N=2 and exceptional N=4 packets. |
| Lucas standard window, integral reduction and residual sequence | Passed: reduction follows integrality; the common sequence is defined. |
| Finite Mahler, CRT and polyphase symbols | Passed: finite versus infinite scope distinguished; affine-kernel indices now explicitly natural. |
| Actual polynomial residuals and partial Jacobians | Passed: derived from original equations and lower-root conditions. |
| Domains, positive-depth exceptions, composite moduli and zero dimensions | Passed within stated scopes; affine depth 0 now visible explicitly. |
| Analytic graph and supplied-selection regularity | Passed: open neighborhoods, actual strict derivative, base/root conditions and ambient field specified. |
| Native conjectures and wider historical results | Passed as scope accounting: not promoted to completed general theorems. |

## Final source snapshot

The final eight TeX files have 110 distinct labels and 79 local reference uses. The structural check found no duplicate labels and no unresolved local references. Source hashes follow; the companion JSON also records the source-document and baseline-module hashes.

| Manuscript source | SHA-256 |
|---|---|
| `Paper_IX_Consolidated.tex` | `09e03555b543df7965e226eea571f10ed5de27f3d4b4ce47e85da6c002f45f10` |
| `sections/00_scope.tex` | `ad58fc00a67677bd94d4d9b0b16ae145a33eb3f60f83554f27a7ff6a4e1ed301` |
| `sections/10_foundations.tex` | `2bb63ee8c53cc7c6646c0f6ae0eb39b7846debb42fc12065c73c07cd797cdc6b` |
| `sections/20_arithmetic.tex` | `664a905288558d4f8fcd6022f4e16971045946fc33935272ce8832fb575c322e` |
| `sections/30_lifting.tex` | `83defce02868187bd53ae9088a5b5046b2f05d05c9cfa0f88ab4cd7ce9e2d952` |
| `sections/40_regularity.tex` | `32f48dcc51d918d65be6dc827f31b05bc9870decb20dc596fed9276940244ffd` |
| `sections/50_open_questions.tex` | `3d8e7c89dd4fe318c099fa04d52c8de1f26143b82e33144d7a11745d3598be9f` |
| `sections/60_verification.tex` | `106c01682cc97570cbc714401e3171e10b88d8c9afa86d7436bd3715f1a92b9e` |

## Limits

- Old original TeX, figure-generation code and complete historical experiment package have not all been recovered. Their available PDF records are retained.
- Broader Annals-only results and incomplete historical edge/carry recovery remain identified outside the current Lean-certified theorem scope.
- The Bernoulli boundary is now explained but no dedicated formal bridge has been located.
- No fresh Lean rebuild or new external literature authentication was performed by this completeness review.
- No guarantee is made about files that were unavailable or about every historical conversation.
- The original figures, numerical tables and code examples remain in the preserved original PDF; they are not all reprinted or newly reproduced.
- The current manuscript is complete against the enumerated proved-results scope. General singular persistence, unrestricted Native 13.2/13.3, sharper arithmetic and historical/interface recovery remain open.
