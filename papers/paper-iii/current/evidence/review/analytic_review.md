# Paper III: independent Section 17 analytic audit

## Normalized claim and primary verdict

**Primary verdict: proved as written**, for the mathematical portion of the corrected analytic supplement and the corrected active Section 17 identified below. This verdict concerns the ordinary mathematical claims actually audited. It does not assert full-manuscript correctness, a complete Section 17 Lean formalization, a license decision, or external peer review.

The normalized claim is the following. Let the input, intermediate, and output spaces be Banach spaces over the same field, either the reals or the complexes. Use finite bounded, complete, pairwise annihilating idempotent families and inherited norms on their actual ranges. Then the range coordinates are bounded linear isomorphisms; continuous multilinear maps restrict to actual continuous range jets; the jets reconstruct each multilinear map and each available Fréchet derivative; the literal range norm is bounded by the output projector norm times the full multilinear norm; packet coordinates conjugate derivatives; the stated Taylor identity and factorial remainder bound hold on every included closed segment under the stated extra derivative; and the decorated partition chain rule, formal term count, and typed support inclusion hold in every positive order. In the complex case derivatives are complex Fréchet derivatives, while integration along the segment has a real parameter.

The separate finite multilinear reconstruction identity needs only the two finite resolutions of the identity. It does not need idempotence, annihilation, continuity of the multilinear map, Banach completeness, symmetry, or positive order. The nullary identity is included explicitly in the supplement and the formal source.

## Exact provenance and scope

Audit date: 20 October 2026. Reviewer: the isolated `analytic_audit` agent, delegated a focused raw-source audit by the release editor. No applicable `AGENTS.md` or project `.mathbox` ledger was present in the release root or its applicable ancestors at initial inspection. The proof-audit skill and its general-logic/external-source obligations were read, as were the literature-check skill and source-record/cache guidance. Previous audit verdicts were read only as provenance and known-failure searches; they were not accepted as evidence that a proof works.

All paths in this report are relative to `/workspace/scratch/9014da510e4f/paper3_release` unless a full path is shown.

| Artifact | Exact audited revision |
|---|---|
| Original supplement `docs/Paper_III_Section17_Analytic_Closeout.tex` | SHA-256 `5161f4eafa1fbc58d3349614ab8153fad443ddadec4fd21dcc50cf2009eb1a64` |
| Corrected supplement, all mathematics through the end of Section 4 | Full-file SHA-256 `7c11f68e6536ad5cd64f4f5468e8213563f9b4ff9155a75ff5476a3270e45688`; mathematical-scope SHA-256 `a9d082e83a434a69cba93ea319190772be52c13ae40e20de6cb6f133c78e2110` |
| Preserved `checkpoint_v0.3.0/baseline/editable/traditional/source/expanded.tex` | SHA-256 `84affcc82641bcd2b045bcd77b1c11205ee46fd7405b5dce5681b92f0b2ab6ab`; Sections 16–17 read directly, plus the identified later packet-jet dependent |
| Preserved `checkpoint_v0.3.0/baseline/editable/traditional/chapters/03_nonlinear_coordinates.tex` | SHA-256 `8be2ba36b891f9d86a99b0dc5ab4cde92a08811619580c1d7dd39c88e8d5d188`; the actual wrapper Section 17 was compared with the expanded source |
| Corrected active `manuscript/chapters/03_nonlinear_coordinates.tex` | Full-file SHA-256 `075b8d329d9f0518149a200d590efd8972460cb5f4ab8052211e9bd221179375`; Section-17-only SHA-256 `e564f9b71c07b334b1e0a3b62da949b5ae3d779a4b9d89fa0065e9513e96076d` |
| New formal `formal/KomorebiPaperIII/ContinuousPacketJets.lean` | SHA-256 `63f96e83190b694b27b00a9649fc87cac9a3b0a6d65830c2a2b5249e76cad924`; all definitions and proofs read for mathematical correspondence |

The supplement mathematical-scope hash is over the UTF-8 text starting with `\section{Two distinct contracts}` and ending immediately before `\section{Reproducibility and limitations}`. The active Section 17 hash is over the text starting with `\section{Packet jets and higher composition}` and ending immediately before `\section{Rooted tree expansions}`. These hashes separate mathematical review from subsequent updates to release status or other chapters.

The reviewer edited only the permitted supplement `.tex` file. The release editor integrated its arguments directly into the active manuscript, preserving the checkpoint original and existing result numbering. The reviewer subsequently read the integrated Section 17 in full and requested one correction to its partition-induction wording. The final corrected active scope above was read again and passed. The reviewer did not author or edit the active manuscript or the Lean module.

The initial mathematical reconstruction was independent of the supplement author. The supplement amendments are self-reviewed amendments. The later integration check is independent of the editor's inline implementation, but uses mathematical content the reviewer had just audited and clarified; it should not be advertised as a blind second mathematical derivation of every amended proof. The Lean correspondence check is independent of its author and separate from compilation. Different agents and matching conclusions do not, by themselves, prove mathematical correctness.

## Claim cards and obligation matrix

| Claim / locator | Quantified objects, hypotheses, exact conclusion | Verdict |
|---|---|---|
| `lem:closed` | Every projector range is closed. Analysis maps the ambient space into the finite product of actual ranges and synthesis is the finite sum. Under boundedness, idempotence, annihilation, and completeness, the two maps are inverse bounded linear maps. Empty-family convention is the zero norm on the zero coordinate space. | Passed |
| `thm:reconstruction` | Every finite-arity multilinear map between the declared spaces reconstructs by inserting both resolutions of identity. Arity zero is allowed; no projector independence or continuity of the multilinear map is used. | Passed |
| `prop:rangejet`; manuscript `def:packet_jet` | For each positive order and label tuple, restrict the inputs to the actual projector ranges, apply the full continuous multilinear map and the output projector, then regard the result in the actual output range with its inherited norm. | Passed |
| `prop:norm`; manuscript `prop:jet_norm_bound` | The restricted jet has norm at most `||Q_gamma|| ||B||`. Its ambient extension has norm at most that quantity times the selected input projector norms. The older restricted-jet product bound also follows, including redundant zero packets. | Passed |
| `cor:conj`; active coordinate-derivative paragraph | For each `1 <= r <= m`, bounded linear analysis/synthesis conjugate `D^r F` exactly. The coordinate domain is open. Single-slot direction evaluations give the literal range jet, even if a selected direction is zero. | Passed |
| `thm:taylor`; manuscript `cor:packet_taylor` | For `m >= 0`, `F` is `C^(m+1)` on an open neighborhood of the whole closed segment. The Taylor remainder is the stated Banach-valued integral divided by `m!`; the projected norm bound has denominator `(m+1)!`. | Passed |
| `thm:faa`; manuscript `thm:packet_faa` | For `n >= 1`, compatible `C^n` maps on the relevant open domains satisfy the set-partition formula. Increasing direction order and a canonical block order make tuples well typed; higher-derivative symmetry makes other block listings agree. | Passed |
| `cor:decorated`; manuscript `thm:packet_faa` | Insert the finite intermediate resolution in each outer derivative slot and then apply the actual output projector. Each intermediate argument belongs to exactly the required range. Mixed input labels remain present. | Passed |
| `prop:count`; manuscript `prop:faa_term_count` | For `n >= 1`, `M >= 0`, the number of formal terms is the sum of `S(n,k) M^k` for `1 <= k <= n`. It counts formal decorations, not distinct values or nonzero terms. | Passed |
| `prop:count`; manuscript `cor:structural_pruning` | The support is a set of external profiles. It is contained in the profiles admitting a partition and intermediate labels with all constituent jets nonzero. Both sides of the inclusion now belong to the same profile set. Equality is not asserted. | Passed after explicit typing repair |
| Manuscript `ex:second_order_composition` | The outermost projector acts on `Z`, so it is `R_delta`. The two ordinary second-order partition shapes have exactly the displayed terms and coefficients. | Passed after `Q_delta` to `R_delta` correction |

All nine result environments in the supplement's mathematical sections were audited, together with the manuscript's packet-jet definition, six Section 17 result environments, associated second-order example, and coordinate conventions. The scope is broader than a check of the two original Lean candidate files, and narrower than a whole-manuscript audit.

## Dependency graph

The proof dependencies are acyclic:

1. **Algebraic projector axioms** imply the range/fixed-set identity and the two analysis/synthesis inverse identities. These are internal proofs.
2. **Bounded projector continuity**, inherited subspace norms, finite products, and finite sums imply closed ranges and bounded coordinate maps. Closed subspaces of Banach spaces and their finite normed products are Banach. This is standard functional analysis; the specific range equality and coordinate formulas are proved internally.
3. **Multilinearity plus the two finite resolutions** imply the reconstruction identity. This internal proof is independent of the coordinate-equivalence argument, so it does not assume the theorem it is meant to establish.
4. **Isometric range inclusions, output projection, and a continuous multilinear map** give the literal continuous range jet and its strong norm estimate. Nonzero idempotents have norm at least one; zero domains make positive-order multilinear jets vanish. These internal steps imply the older product bound.
5. **The ordinary Fréchet chain rule and bounded linear coordinate maps** imply the coordinate derivative formula. Higher derivatives of those fixed coordinate maps vanish from order two onward.
6. **The chain rule along a real segment, continuity on a compact interval, Banach-valued fundamental theorem of calculus, and integration by parts** give the exact Taylor recurrence. Finite reconstruction and bounded projection then give the packet identity and its norm estimate.
7. **The first-order chain rule, the product rule for bounded multilinear evaluation, and derivative symmetry** give the partition formula by the explicit singleton-or-block-extension induction.
8. **The finite intermediate resolution** decorates the partition formula. The definition of Stirling numbers gives the term count. The contrapositive of the zero-constituent argument gives the typed support inclusion.

No finite numerical test is a leaf needed by a universal mathematical conclusion. No closed-range theorem for a general bounded operator is assumed: closedness here comes from idempotence. No arbitrary supplied coordinate equivalence is substituted for the actual projector construction.

## Decisive mathematical checks

### Actual ranges and their norms

For a bounded idempotent `P`, a vector belongs to its range exactly when `P x = x`. Thus the range equals `ker(id - P)`, a closed subspace. If `z_i` belongs to range `P_i`, idempotence fixes the `i`th component and annihilation kills all other projected components. This proves analysis after synthesis without an unproved direct-sum certificate. Synthesis after analysis uses the resolution of identity, not completeness of the Banach norm.

For the range jet, every input inclusion is isometric. For arbitrary allowed range inputs,

`||Q_gamma B(z_1,...,z_r)|| <= ||Q_gamma|| ||B|| product_a ||z_a||`.

The output subspace norm is exactly its ambient norm, so the same inequality proves continuity and the literal range operator norm estimate. There are no input projection factors in this argument. The ambient extension is a different map and introduces those factors by its definition.

This distinction can be strict. In Euclidean two-space, let `P_1(x,y)=(x+a y,0)` and `P_2(x,y)=(-a y,y)` for nonzero `a`. These are complementary nonzero idempotents of norm `sqrt(1+a^2)`. For `B=id` and a single identity output packet, the restricted first-order map is an isometric inclusion of its range and has norm one, while its ambient extension has the larger projector norm. This is a direct example, not an assertion of novelty for the bound.

If a selected input projector is zero, its range is the zero space; positive-order multilinearity forces the jet to be zero. If the output projector is zero, the jet is zero directly. This avoids incorrectly asserting that every projector, including zero, has norm at least one.

### Regularity, domains, and Taylor normalization

For `g(t)=F(x+t h)`, the inverse image of the open domain is an open subset of the real line containing `[0,1]`. Repeated differentiation gives `g^(r)(t)=D^r F(x+t h)[h,...,h]`. Continuity of the derivatives on the compact interval gives Bochner integrability even if the Banach codomain is not globally separable: the continuous image of the interval is compact and separable and is norm bounded.

The recurrence in the corrected proof is correct, including its sign:

`T_j = (1/j!) integral_0^1 (1-t)^j g^(j+1)(t) dt`,

`T_0 = g(1)-g(0)`, and, for `j >= 1`,

`T_j = T_(j-1) - g^(j)(0)/j!`.

The boundary contribution at `t=1` is zero for positive `j`, while at `t=0` it is `-g^(j)(0)`. Hence iterating the recurrence gives exactly the displayed Taylor polynomial and the remainder `T_m`. Integrating the nonnegative scalar weight gives `1/(m+1)`, so the norm denominator is `(m+1)!`.

Bounded linear maps commute with this integral by their action on simple functions and passage to the norm limit. Applying the output projector to the reconstructed derivative retains only its own component by annihilation and idempotence. No orthogonal-Hilbert-space assumption is used. The proof covers `m=0`, `h=0`, zero spaces, and zero projector ranges. No global convexity of the domain is required beyond inclusion of the stated segment.

For complex spaces, scalar restriction turns the complex derivative into its underlying real derivative along the segment without changing the norm or the displayed evaluations. The same real-parameter integral proof therefore applies.

### Partition induction and multiplicity

For fixed directions, the bounded multilinear evaluation map is differentiated with respect to its outer multilinear map and each one of its arguments. Differentiating the outer derivative produces the new singleton `{n+1}`. Differentiating the inner derivative corresponding to a block appends `n+1` to that block. A partition at order `n+1` has exactly one predecessor: delete `{n+1}` if that is itself a block, otherwise delete `n+1` from its unique containing block. Other singleton blocks are irrelevant to this inverse operation.

This is why the first integrated draft's wording “remove its singleton block if it has one” needed correction. A partition can have an unrelated singleton while `n+1` belongs to a nonsingleton block. The final integrated proof explicitly distinguishes the block `{n+1}`, so its bijection is correct.

No extra block-order factorial occurs. One uses each set partition once, chooses one intermediate label per block, and either uses a canonical block ordering or higher-derivative symmetry. The first three formal counts are `M`, `M+M^2`, and `M+3M^2+M^3`. At fourth order they are `M+7M^2+6M^3+M^4`. At `M=2`, the contributions are `2, 28, 48, 16`, totaling `94`, as stated in the figure caption. These identities follow from the combinatorial argument and were recomputed from the four block-count cases.

For `M=0`, completeness forces the intermediate space to be zero. A positive-order composite derivative and its decorated term count are both zero. Order zero is deliberately outside the term-count proposition; including it would require the unique empty-partition term one.

### Support typing and strict inclusion

The corrected support is a subset of `K x I^n`, the external output/input packet profiles. A decorated witness additionally contains a partition and a block-label function. The admissible profile set is the projection of those witnesses satisfying the nonzero-constituent conditions. Thus the two sides of the inclusion are finally of the same type.

If a profile has no admissible witness, every decorated term has either a zero outer jet or a zero inner jet. The latter supplies a zero argument to a positive-order multilinear map, so every term is zero for every direction tuple. This proves the support inclusion at the level of nonzero multilinear maps, not merely for one evaluation.

The reverse inclusion is false. With `G(t)=(t,t)` and `F(y_1,y_2)=y_1-y_2`, coordinate packets in the intermediate two-space give two nonzero first-order decorated terms whose sum is zero. There is also a separate obstruction without cancellation: with one identity intermediate packet, `G(t)=(t,0)` and `F(y_1,y_2)=y_2` have nonzero constituent linear maps but zero composite. The corrected text permits both phenomena.

## Exact repairs and downstream effects

| Original source locator | Finding | Correction / disposition |
|---|---|---|
| Preserved `expanded.tex:478`; preserved wrapper `03_nonlinear_coordinates.tex:359`; label `ex:second_order_composition` | The expression starts with `Q_delta D^2(F circ G)` although the composite takes values in `Z` and `Q` acts on `Y`. It is ill-typed under the established notation. | Active manuscript now uses `R_delta`; the checkpoint was preserved. This changes one forced symbol, not the theorem. |
| Preserved `expanded.tex:466`; preserved wrapper `:347`; label `cor:structural_pruning` | The support was said to be contained in a set of decorated partitions, mixing external profiles with decorated witnesses. | Both supplement and active manuscript define support on external profiles and project admissible decorated witnesses to those profiles. The intended full inclusion is proved. |
| Original supplement `lem:closed` and coordinate convention | The empty-family norm and the distinction between projector completeness and Banach completeness were implicit. | Empty coordinate product is explicitly the zero normed vector space; resolution of identity is named as the reason for synthesis after analysis. |
| Original supplement `cor:conj` | “Its nonzero coordinate” accidentally excluded a direction supported in one slot but equal to zero; derivative range was implicit. | “Possibly zero coordinate” and `1 <= r <= m` are explicit. |
| Original analytic setup and composition statement | The intended real/complex field and local open-domain compatibility were not uniformly explicit. | Common-field real/complex Banach scope is stated without reducing to real spaces. The supplement gives named open sets and `G(U) subset V`. |
| Active manuscript first integration, partition proof | Deleting an arbitrary singleton did not describe the actual predecessor bijection. | Corrected to delete exactly `{n+1}` when present; otherwise remove `n+1` from its containing block. Final integrated source re-read and passed. |

The original range product bound is true; its brief proof was not a counterexample or refutation. The supplement makes its relation to the stronger range bound and to the ambient extension explicit. The stronger bound is a substantive estimate added to the active manuscript, with no scope reduction.

References to Section 17 were searched directly. The later `cor:reduced_packet_jets` in `expanded.tex:1835` / `chapters/04_correction_transport.tex:604` uses only the restriction/projection construction of first and second derivatives. Its use of that construction remains valid after these corrections. The Schur identities on which that corollary also depends were not accepted as globally audited merely because their projection step is valid. Rooted-tree convergence, nonlinear correction, spectral sequences, transport, and the rest of the monograph are outside this focused audit.

## Formal source correspondence

The new `ContinuousPacketJets.lean` file was read in full, as were its relevant actual definitions in `PacketCoordinates.lean`, `MultilinearPacketJets.lean`, and `BoundedPacketJetNorm.lean`. These are actual source checks, not an inference from theorem names or a successful test count.

| Formal object | Mathematical correspondence | Assessment |
|---|---|---|
| `System.Coordinates` | Dependent finite product of `LinearMap.range (P.projector i)`; neither arbitrary surrogate spaces nor supplied inverse maps | Exact |
| `System.continuousCoordinateEquiv` | The existing projector-constructed analysis/synthesis linear equivalence, with continuity proved in both directions | Exact |
| `System.range_isClosed` | Closed fixed set of the actual continuous idempotent | Exact |
| `continuousPacketJet` | Compose the inherited-range `subtypeL` inclusions with `B`, apply the actual continuous output projector, and `codRestrict` to its actual submodule range | Exact |
| `continuousPacketJet_toMultilinearMap` | Forgetting continuity yields the earlier algebraic actual-range `packetJet` | Definitional equality in the displayed source |
| `continuousPacketJet_norm_le` | Operator norm of the actual range-valued continuous multilinear map, bounded by `||Q|| ||B||` | Exact restricted norm; not the ambient norm |
| `continuous_multilinear_packet_reconstruction` | Full finite sum over output labels and all input-label tuples, including mixed tuples | Exact |
| `iteratedPacketJet` | Direct application of `continuousPacketJet` to `iteratedFDeriv K n f x` | Exact object, with no substitute derivative |
| `iteratedFDeriv_packet_reconstruction`, `iteratedPacketJet_norm_le` | The reconstruction and strong norm bound for that chosen iterated derivative, including order zero | Exact stated specialization |

The formal file assumes a nontrivially normed field and normed spaces, which includes the manuscript's common real/complex Banach setting. It does not add finite-dimensionality, Hilbert orthogonality, orthonormal coordinates, or an inverse certificate. Omitting input-projector continuity from the range-jet definition and its norm theorem is correct: the inclusions of normed subspaces are continuous regardless of whether the projector used to name them is continuous. The separate coordinate-continuity theorem correctly requires continuity of every input projector.

The raw `iteratedFDeriv` is a total mathlib object. Its recursion uses `fderiv`; where a derivative does not exist, the latter is chosen as zero. Therefore the unconditional reconstruction theorem alone is not a differentiability theorem. This limitation is stated in the new file. Under the manuscript's `C^m` hypotheses, these chosen derivatives coincide with the genuine derivatives; the underlying mathlib `ContDiff.ftaylorSeries` and the recursive definitions supply the standard bridge. A local open-domain map can be represented by any ambient extension agreeing on that open set, because its derivatives there depend only on the germ.

The runtime auditor reported that **the exact `63f96e...` source hash checked here compiled successfully with pinned Lean 4.34.0-rc2**. That is separate compiler evidence supplied by the runtime audit, not a compiler run by this reviewer. At the time of that message, the combined cold closure build and final replay/census were still underway. This report does not replace those receipts or assert their later outcome.

The file does not contain a packet Taylor remainder theorem, the complete decorated `n`th chain rule, the Stirling-count theorem, or the support-pruning theorem. Their ordinary proofs passed above; they must not be counted as newly kernel-verified merely because the literal continuous-jet bridge now compiles.

## Source verification

The exact source question was whether the external calculus inputs have the required infinite-dimensional, bounded-multilinear, real/complex and Banach-valued scope. A local pinned mathlib checkout was available during the audit. `git rev-parse HEAD` returned `aeb72f1e9981b6d35b426b16dca7759be3e7ba06`, agreeing with the formal manifest. `git diff --exit-code HEAD --` on the four checked calculus files returned success with no differences. This authenticates the read source text to that exact checkout revision; the present audit does not independently replay its entire dependency closure.

| Exact primary source at that revision | Source extraction and application |
|---|---|
| `Mathlib/Analysis/Calculus/Taylor.lean`, `taylor_integral_remainder`, beginning at line 534; SHA-256 `fba037b49e06e1fe416f04f9682bfe924601cfaf0aa137ec54331a288c995160` | Statement and proof read. It assumes a real normed-space codomain with `CompleteSpace` and `ContDiffOn` of order `n+1` on the closed interval. Set the scalar interval to `[0,1]` and the function to the smooth curve `g`. This is the exact Banach-valued normalization used here. The supplement additionally proves its normalization directly by integration by parts. Application verified. |
| `Mathlib/Analysis/Calculus/FDeriv/Comp.lean`, `HasFDerivAt.comp`, line 107, and its filter-level proof; SHA-256 `b25791b5363ec250130d10d34fd77b9c2b24af63bfd89479b9b3c8443ebf74ed` | Statement and residual-estimate proof read. Bounded linear derivatives over a nontrivially normed field compose. The manuscript's real/complex derivatives and open-domain germs satisfy its hypotheses. Application verified. |
| `Mathlib/Analysis/Calculus/FDeriv/Symmetric.lean`, `second_derivative_symmetric`, line 483; SHA-256 `28288fa76deb17295433ed40b0037145583f96fa7d73674d555b715158eab2f3` | Real/complex normed-field restriction and the second-derivative symmetry statement read. Applying this to derivative-valued maps and using adjacent transpositions gives symmetry in every available `C^r` order. No symmetry over arbitrary non-Archimedean fields is inferred. Application verified. |
| `Mathlib/Analysis/Calculus/ContDiff/FaaDiBruno.lean`, Sébastien Gouëzel, 2024; `compAlongOrderedFinpartition` and `HasFTaylorSeriesUpToOn.comp`; SHA-256 `79b3216e965f032554197e51cb6d4dbcfb35e8a801b3dde1228f0eacbbb64aaf` | Partition objects, their composition evaluation, the norm bound and the principal induction proof read. It uses the same unique partition-extension mechanism. Its canonical ordering uses greatest elements; the manuscript may use least elements because its real/complex higher derivatives are symmetric. This checks the combinatorial overlap; the manuscript's own induction does not depend on an unproved substitution of formal Taylor coefficients. |
| `Mathlib/Analysis/Calculus/ContDiff/FTaylorSeries.lean`, `iteratedFDeriv`, line 804, and `iteratedFDeriv_zero_apply`; SHA-256 `f6ebee83905f13d5648f1a9bff39c15b6109f161fdf5d482af9c5f22176ba535`; `ContDiff/Defs.lean`, `ContDiff.ftaylorSeries`, line 1204 | Actual recursion, nullary value, currying convention and smoothness bridge read. They justify the literal chosen-derivative correspondence above. |

Stable repository source locator: `https://github.com/leanprover-community/mathlib4/tree/aeb72f1e9981b6d35b426b16dca7759be3e7ba06/Mathlib/Analysis/Calculus`. A web attempt to fetch the raw GitHub files was disabled; source authentication therefore rests on the read pinned checkout and its clean-file comparison, not on a claimed successful remote fetch.

The original manuscript's bibliography was also checked at discovery level. The official Springer page authenticates Abraham–Marsden–Ratiu, *Manifolds, Tensor Analysis, and Applications*, second edition, 1988, and its Banach-calculus chapter, DOI `10.1007/978-1-4612-1029-0_2`. The public publisher page does not expose the required full theorem text. The Constantine–Savits author page and AMS bibliographic record authenticate the multivariate paper, DOI `10.1090/S0002-9947-96-01501-2`, but full exact text was not authenticated in this session. They are background citations, not independent evidence that a particular infinite-dimensional theorem has been checked. No full-text verification of Deimling was performed.

The author-hosted Brian Conrad handout *Higher derivatives and Taylor's formula via multilinear maps* was opened and its finite-dimensional scope was explicitly observed. It was not promoted into a direct Banach-space source. No broad novelty claim is made. No retrieved full copyrighted text was added to the release or this report.

Primary bibliographic locators used:

- `https://link.springer.com/book/10.1007/978-1-4612-1029-0`
- `https://link.springer.com/chapter/10.1007/978-1-4612-1029-0_2`
- `https://sites.pitt.edu/~gmc/part.html`
- `https://doi.org/10.1090/S0002-9947-96-01501-2`
- `https://virtualmath1.stanford.edu/~conrad/diffgeomPage/handouts/taylor.pdf`

## Commands, checks, and remaining obligations

The source audit used bounded `rg` searches for exact result labels and dependencies, direct reads of the raw theorem/proof blocks, SHA-256 hashes, and clean pinned-source comparisons. The corrected supplement had 13 labels, no duplicate labels, and no undefined local `ref` or `eqref` targets in its source. Compilation and visual verification were assigned to the release editor; no PDF-layout pass is claimed here. No numerical suite was used as a substitute for the universal proofs.

Representative reproducible commands:

```sh
sha256sum docs/Paper_III_Section17_Analytic_Closeout.tex
sha256sum manuscript/chapters/03_nonlinear_coordinates.tex
sha256sum formal/KomorebiPaperIII/ContinuousPacketJets.lean
rg -n 'jet_reconstruction|jet_norm_bound|packet_taylor|packet_faa|faa_term_count|structural_pruning|reduced_packet_jets' checkpoint_v0.3.0/baseline/editable/traditional/source/expanded.tex
git -C formal/.lake/packages/mathlib rev-parse HEAD
git -C formal/.lake/packages/mathlib diff --exit-code HEAD -- Mathlib/Analysis/Calculus/Taylor.lean Mathlib/Analysis/Calculus/FDeriv/Comp.lean Mathlib/Analysis/Calculus/FDeriv/Symmetric.lean Mathlib/Analysis/Calculus/ContDiff/FaaDiBruno.lean
```

**Remaining ordinary mathematical gap in the exact reviewed Section 17 scope: none found.** The strongest safe statement is the full normalized real/complex Banach result at the top of this report, including arbitrary finite packet systems and every stated order. No arbitrary restriction of scope was used to obtain this verdict.

Remaining release tasks are outside this review: finish the compiler closure/replay/census for the newly accepted module; ensure all release records reflect its actual acceptance; retain distinct formal status for Taylor, decorated composition, counting and pruning unless separate exact proofs are accepted; build and visually inspect the integrated readers; and verify changes elsewhere in the manuscript through their own review. Later modifications to either mathematical-scope hash above require an impact check and, when they change a statement or proof, renewed audit.
