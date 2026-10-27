# Structural and figure-text review

Review date: 12 October 2026. Method: `mathbox:proofread-math`, review-only mode. No manuscript source was edited by this reviewer. No Lean compilation, fresh numerical experiment, or external novelty search was run for this review.

## Result and limits

**PASS for the bounded source-structure and figure-text scope after the figure 24 caption correction.** All 40 numbered figure `.tex` sources were read, together with their captions, the text extracted from linked PDF assets, and the nearby mathematical models where necessary. The main monograph uses 38 of these figures. Figures 13 and 14 belong to the separate Visual Guide and were reviewed separately; that guide and the Lean Guide were not mixed into the monograph reference graph.

This review checks whether figure formulas, labels, captions, and stated models agree. It is not a new theorem-by-theorem referee audit, independent reproduction of the plotted numerical data, or rendered-page inspection. The compiler build and visual layout review have separate evidence. In particular, legibility, clipping, glyph rendering, page placement, and collision freedom are not conclusions of this report.

The only definite mathematical wording defect found in the 40 figure captions was the zero-vector exception in figure 24. The original caption said that “all vectors on its fixed line define nonzero coherent families.” The zero vector defines the zero family. The coordinator corrected this to “all **nonzero** vectors on its fixed line define nonzero coherent families.” The correction is present in `source/chapters/06_cases.tex:115`. It does not change the theorem or diagram.

## Structural evidence

Run from the release directory:

```sh
python scripts/check_manuscript.py
```

The checker writes `reviews/STRUCTURAL_CHECK.json`, including its own SHA-256, every included source hash, all 40 figure source hashes, linked graphic hashes, captions, and the actual inclusion edges. Rerun it after final manuscript edits: its result applies to the recorded hashes, not to later source changes.

| Check | Recorded result |
|---|---:|
| Recursive monograph closure, including the local publication package | 73 files |
| Input occurrences | 73 |
| Main monograph plates | 38 |
| Complete numbered figure source inventory | 40 |
| Unique labels | 317 |
| Reference occurrences | 105 |
| KS hypertargets / hyperlinks | 80 / 80 |
| Bibliography keys / citation occurrences | 10 / 12 |
| Referenced PDF graphic assets | 30 |
| Missing inputs or graphics | 0 |
| Duplicate labels, targets, or bibliography keys | 0 |
| Unresolved references, hyperlinks, or citations | 0 |
| Unbalanced braces, explicit math delimiters, or environments | 0 |

The recursive input edges explicitly include `chapters/03_towers.tex` → `chapters/03a_observation.tex` and `chapters/03_towers.tex` → `chapters/03b_repair_transport.tex`, plus `chapters/07_concordance.tex` → `claim_table.tex`. The preamble's `edition_stats.tex` and `written_status.tex` inputs and local `komorebi-publication.sty` are included. The project's `plate`, `fixedplate`, and `source` macros are recognized, so labels introduced through those macros and their figure inputs are counted. Macro definition placeholders containing `#` are not treated as real filenames or references.

The checker is a conservative lexical checker, not a TeX interpreter. It recognizes literal inputs and the project's specific macros; it does not execute arbitrary macros or conditionals. It checks per-file environment nesting, braces, and explicit dollar/parenthesis/bracket math delimiters. Successful LaTeX compilation remains the authoritative syntax/expansion check.

## Figure-by-figure record

The figure numbers below are source inventory numbers, not a claim that the main monograph contains 40 plates. “Consistent” means no mismatch was found within the stated review scope.

| Source | Model and caption check | Result |
|---|---|---|
| `01_views.tex` | Contravariant evaluation arrows and `(g ∘ f)* = f* g*` have the stated directions. | Consistent |
| `02_extension.tex` | The lift satisfies the prescribed restriction; the defect is taken modulo `δ ker p_U`; subtracting an invisible correction with the same defect gives an exact lift. | Consistent |
| `03_tower.tex` | The square residual is `ρ_Y,n f_(n+1) − f_n ρ_X,n`, with the displayed source and target levels. | Consistent |
| `04_split.tex` | The semantic/residual coordinates, inverse `P s + A r`, and zero-residual repair agree. | Consistent |
| `05_cascade.tex` | The displayed finite telescope includes the correct lifted packet terms and final `Q_3 x` remainder. | Consistent |
| `06_groupoid.tex` | Homomorphisms from `C₂` to `S₃` give the identity and transposition orbits; the displayed stabilizers are `S₃` and `C₂`. | Consistent |
| `07_cover.tex` | The three-view pair patches miss a composable pair; proper three-view patches in the four-view example cover every composable pair. | Consistent |
| `08_marked.tex` | The marked fiber equation and equivalence square preserve the identified boundary as stated. | Consistent |
| `09_holonomy.tex` | Anchoring maps have direction `H_i → H_o`; `T_i τ_ij T_j⁻¹` acts at the anchor; the reflection preserves the displayed fixed line. | Consistent |
| `10_closed_range.tex` | For basis vectors, distance to the kernel remains one while the displayed diagonal residual is `1/n`; the horizontal axis is the basis index. | Consistent |
| `11_descent.tex` | The displayed increments `(0,0,3)` and `(0,2,0)` are orthogonal and their squared lengths sum to 13. | Consistent |
| `12_moving_line.tex` | The chosen repair operator and orthogonal projector are distinguished; the projector gap `t/√(1+t²)` and its bound by `t` are valid on the stated nonnegative parameter range. | Consistent |
| `13_parity.tex` | In the Visual Guide, an integer coarse value extends exactly when even, with unique finer value equal to half of it. | Consistent; outside main graph |
| `14_tail.tex` | In the Visual Guide, each fixed coordinate of the tail remainder eventually vanishes while its supremum norm remains one. | Consistent; outside main graph |
| `15_protected_geometry.tex` | Raw `(2,0)`, nearest exact `(1,1)`, and protected exact `(2,2)` are distinguished; the caption explains the suppressed fixed third coordinate. | Consistent |
| `16_dyadic_support.tex` | Possible surviving support is described by divisibility of `k+1` by `2^N`; the caption does not assert that every allowed coordinate is nonzero. | Consistent |
| `17_amplification.tex` | The flat scalar transport model has bounded directed-edge residuals and root-preserving repair error `2^n−1`; the comparison with graph length is correctly scoped. | Consistent |
| `18_rank_loss.tex` | Equal-size operator perturbations are separated from their projector effects: continuous moving-line gap versus unit gap under rank loss. | Consistent |
| `19_branches.tex` | The protected seed and intermediate choices are separated; finer lifting is the stated integer parity condition `m = 2n`. | Consistent |
| `20_schedule.tex` | The running-maximum schedule is monotone and meets the required stages; no efficiency bound is inferred. | Consistent |
| `21_mismatch.tex` | The shear sends `(0,1)` to `(2,1)`; the two repair orders give `(2,0)` and `(0,0)`, so the displayed mismatch is exact-valued. | Consistent |
| `22_gain_budget.tex` | Gain `(1−t)⁻¹` is plotted on `0 ≤ t < 1`; the endpoint changes the kernel and is not included in the stable regime. | Consistent |
| `23_cycle_primitive.tex` | Anchor-zero and mean-zero primitives differ by a constant; vertex four repeats vertex zero; the caption correctly calls the horizontal labels vertices. | Consistent |
| `24_reflection_cycle.tex` | Identity tree transports and closing reflection retain precisely the fixed line; the nonzero-family statement now excludes the zero anchor. | Corrected and consistent |
| `25_summable_path.tex` | Residual `1/(n+1)` is nonsummable, successive steps `1/((n+1)(n+2))` are summable, and the tail equals the displayed residual. | Consistent |
| `26_residual_bursts.tex` | Residuals can double within each pair while the two-step product is `1/4`; the displayed even-step product is `4⁻ᵏ`. | Consistent |
| `27_path_limits.tex` | A common residual path and protected value allow different unprotected limits; the displayed alternatives do not assert uniqueness without its hypothesis. | Consistent |
| `28_escaping_repair.tex` | Squared finite repair size is `N`; squared residual lies between `1/(N+1)` and `1/N` for the stated positive indices. The caption identifies a proved bound, not a finite truncation as the infinite value. | Consistent |
| `29_transport_cost.tex` | The free path category allows zero cost for a nonidentity two-arrow path; the isolated object and directed costs agree with the model. The nearby text distinguishes arrow count from total cost. | Consistent |
| `30_phase.tex` | The phase `c(x,y)=x₂y₁` over `F₂` has the displayed asymmetric table entries; coherent associativity is distinguished from removal of the phase. | Consistent |
| `31_nested_energy.tex` | Escaping minimal squared energy is `N`; the attainable comparison is a partial sum of `n⁻²` below two. | Consistent |
| `32_budget_certificate.tex` | With `T=diag(1,1/2)`, `r=(1,1)`, and correction `(1/2,2/5)`, residual `(1/2,4/5)` has norm `√89/10`; correction budget is `√41/10`, and the displayed dual equality is valid. | Consistent |
| `33_budget_uncertainty.tex` | Nominal `max(1−M,0)` and perturbation band `δ+ηM` use the stated `δ=1/20`, `η=1/10`. | Consistent |
| `34_noise_filter.tex` | The filter `σ/(σ²+α)` peaks at `σ=√α` with value `1/(2√α)` for positive `α`. | Consistent |
| `35_regularized_escape.tex` | Soft coordinates `m²/(m²+n²)` converge pointwise to one; each sequence has finite squared norm while those norms are unbounded as the parameter grows. | Consistent |
| `36_budget_product.tex` | Optimized and hard-prefix curves use different budgets; the horizontal scale is explicitly not a common budget. The stated limiting constants are `π/4` and one. | Consistent |
| `37_solver_amplification.tex` | Displayed `ε/α` and `ε/(2√α)` are universal error bounds at the stated tolerance, not measured errors. | Consistent |
| `38_objective_certificate.tex` | For `3t²−2t+1`, proposal `t=1/4` gives `11/16`, optimum is `2/3`, dual bound is `21/32`, gap is `1/32`, and actual excess is `1/48`. | Consistent |
| `39_covector_metric.tex` | Positive scalar reparameterizations give raw covector norm `s/4` and Gram value `2s²`, leaving intrinsic norm `1/√32` unchanged. | Consistent |
| `40_stopping_schedule.tex` | The stated positive-noise parameter range, ceiling choice `m=⌈δ⁻²ᐟ³⌉`, bias bound, data-amplification bound, and solver tolerance agree; the curves are bounds, not empirical measurements. | Consistent |

## Disposition

No unresolved mathematical-text discrepancy was found in the figure inventory after the single caption correction. No source edit or new numerical calculation was necessary for the other figures. The static reference and balance checks pass on their recorded source snapshot. Any later source or figure changes require a checker rerun and, where the mathematical content changes, a targeted review of the affected row.
