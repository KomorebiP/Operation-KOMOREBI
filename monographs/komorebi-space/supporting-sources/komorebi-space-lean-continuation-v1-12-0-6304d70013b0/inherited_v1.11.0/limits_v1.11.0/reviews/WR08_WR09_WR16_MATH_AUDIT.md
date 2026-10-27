# WR08 / WR09 / WR16 independent mathematical and statement audit

Primary verdict: **proved as written**. The printed WR08, WR09, and WR16 claims pass mathematical review, and every principal clause has a matching complete formal counterpart in the frozen `clean_limits_01` compiler exports. This final review binds the accepted run receipt, terminal postflight, full declaration export, axiom report, and all three new production-module hashes below. No extra closed-range, dimension, or separability hypothesis was found.

Reviewer: independent `limits_math_audit` agent, assigned the raw statements and accepted base without an author's proposed verdict. Skills used: `mathbox:proof-audit`, and `mathbox:proofread-math` in review-only mode. No manuscript, author formal source, status ledger, or verification script was edited by this reviewer.

## Authoritative source and exact claim cards

Accepted inherited formal checkpoint: `KS-v1.10.0-WR03-WR05-complete`; inherited source directory `budget_v1.10.0/integration/runs/clean_budget_01/source/KomorebiSpace`.

| Source | Exact locator | SHA-256 at printed review |
| --- | --- | --- |
| `monograph_v1.10.0/source/chapters/05h_regularized_repair.tex` | WR08 at lines 140–190; WR09 at lines 209–250 | `9c5e9253ba9f1e0f179f60082531708cb6c00047d06bcbcb8459fc0a7534ce51` |
| `monograph_v1.10.0/source/chapters/05k_stopping_rules.tex` | WR16 and its preceding data/certificate bounds, lines 78–131 | `c808f84874650d1c08fb5ddee1e42bc6c59b82f3a7449a316135edf0442af85f` |
| `monograph_v1.10.0/source/chapters/05f_bounded_realization.tex` | Hilbert/protected conventions; weak-subsequence lemma; WR01 | `d074e02a50fe9f08e94dad513f59d90168d1b100102f4f65b1512935c7301f33` |

Shared quantifiers: arbitrary real Hilbert spaces H and Y, a bounded real-linear operator T:H→Y, and a fixed intended datum r∈Y. No compactness of T, finite dimension, separability of either space, or closedness of ran T is assumed. Let C=closure(ran T), b=P_C r, q=‖r−b‖, and a_α=(T* T+αI)⁻¹T*r for every real α>0. Norms are the actual Hilbert norms. The protected specialization is H=ker p with its inherited Hilbert metric, T=d|H; every correction then preserves the protected data exactly.

**WR08.** Along the entire positive-real-parameter family as α↓0: (08.1) T a_α→b in norm; (08.2) ‖r−T a_α‖→q; (08.3) α‖a_α‖²→0. If b∈ran T, there is a unique minimum-norm preimage a†, and (08.4) a_α→a† in norm along the same entire family. If b∉ran T, (08.5) ‖a_α‖→+∞. A theorem only along α_n=1/n, only for a chosen sequence, or only asserting unboundedness would leave a clause incomplete. A positive-subtype filter or an eventually equal extension to nonpositive real parameters is acceptable only with an explicit identification of its limit with the right-hand real filter at zero.

**WR09.** For each positive α and two data with ‖r−r̃‖≤δ, (09.1) ‖a_α(r)−a_α(r̃)‖≤δ/(2√α) and (09.2) ‖T(a_α(r)−a_α(r̃))‖≤δ. These hypotheses imply δ≥0; no separate strict positivity is needed for the pointwise bounds. (09.3) The coefficient 1/(2√α) is worst-case sharp across bounded linear Hilbert operators at each fixed positive α. (09.4) For the same fixed T, H, Y and r, and any measured family r̃(δ) with noise bound ‖r̃(δ)−r‖≤δ, if b∈ran T, α(δ)>0, α(δ)→0 and δ/√α(δ)→0 as δ↓0, then a_{α(δ)}(r̃(δ))→a† in norm. This is a full positive-real δ-family statement, not only a sequence statement. The theorem allows q>0 and concludes least-squares convergence then.

**WR16.** For each n∈ℕ let α_n>0, measured datum r̃_n, proposed correction a_n∈H, and bounds ‖r̃_n−r‖≤δ_n and ‖T*(T a_n−r̃_n)+α_n a_n‖≤ε_n. Assume b∈ran T, α_n→0, δ_n/√α_n→0, and ε_n/α_n→0. Then (16.1), at every n,

\[
\|a_n-a^\dagger\|\leq\varepsilon_n/\alpha_n+\delta_n/(2\sqrt{\alpha_n})+\|a_{\alpha_n}(r)-a^\dagger\|,
\]

and (16.2) a_n→a† in norm. The certificate must use the measured datum r̃_n, the Hilbert adjoint into H, and the Hilbert normal-residual norm. A coordinate covector norm or an objective residual is not the same hypothesis. No changing operators, kernels, or metrics are covered.

## Independent derivation and dependency graph

The review reconstructed the following implications from the definitions before examining new formal proof implementations.

1. Orthogonal projection gives r−b⊥ran T. Consequently T*(r−b)=0 and ‖r−T a‖²=q²+‖b−T a‖² for every a∈H. The normal equations therefore select the same correction from r and b.
2. Closure membership of b gives, for every η>0, a single fixed competitor a with ‖r−T a‖²<q²+η. Global minimality yields q²≤‖r−T a_α‖²≤J_α(a_α)≤q²+η+α‖a‖². Choose a first and then α small. Thus residual square and objective both tend to q²; subtracting gives the weighted-penalty limit, and orthogonal decomposition gives image convergence. This proves the full right-hand limit without selecting a diagonal sequence.
3. If b is attained, the fiber T⁻¹{b} is nonempty, closed and affine, hence has a unique closest point a† to zero. Comparison with a† gives ‖T a_α−b‖²+α‖a_α‖²≤α‖a†‖², hence ‖a_α‖≤‖a†‖. Every positive sequence of parameters tending to zero has a weakly convergent correction subsequence. Its image is b, and weak lower semicontinuity plus minimality identifies its limit as a†; the uniform upper bound and lower semicontinuity give norm convergence on that subsequence. The Hilbert square identity upgrades weak convergence and convergence of norms to strong convergence. A sequence selected from any failure of the full right-hand limit contradicts this subsequence conclusion.
4. If b is unattained and correction norms do not tend to +∞, select α_n>0 tending to zero with norms bounded by one finite M. Image convergence and WR01 imply an actual preimage of b, contradiction. This proves eventual escape above every finite threshold.
5. Subtract the two normal equations at the same α. For h=a_α(r̃)−a_α(r), e=r̃−r, and t=‖T h‖, obtain t²+α‖h‖²=⟨e,T h⟩≤δt. Thus t≤δ, including t=0; completing the square gives α‖h‖²≤δ²/4. The scalar model H=Y=ℝ, T=√α I has solution map 1/(2√α) I and attains the correction bound for nonzero noise. The witness operator may depend on the fixed α, as the printed sharpness assertion requires.
6. Insert a_{α(δ)}(r) in the noisy error triangle. The noise term is at most δ/(2√α(δ)) and tends to zero; the bias term tends to zero by the full attained WR08 limit and the selected parameter limit. No limit of the datum component orthogonal to the range is needed.
7. For WR16 first compare the proposal with the exact measured-data optimizer using coercivity of T*T+αI: correction error≤ε/α. Next compare measured and intended exact optimizers by WR09, then insert the minimum-norm target. The three terms give the stated per-index inequality and each tends to zero.

Dependency leaves: Hilbert orthogonal projection and nearest-point geometry; bounded weak-subsequence extraction and norm lower semicontinuity; adjoint identities; normal-operator invertibility/global minimality (WR06); bounded approximate realization (WR01); and fixed-parameter normal-residual error bound (WR13). The weak-subsequence argument in the printed WR01 context reduces the given sequence to its separable closed linear span, so it does not impose ambient separability. All central implications above are proved internally in the manuscript, without relying on the background citation to Clason. No new external literature assertion was required for this review.

## Final obligation matrix

| Obligation | Printed proof | Exact frozen formal counterpart |
| --- | --- | --- |
| Correct projection onto closure of actual range | Passed | Passed |
| WR08 image norm limit | Passed | Passed |
| WR08 residual norm and weighted-penalty limits | Passed | Passed |
| Existence and uniqueness of actual minimum-norm preimage | Passed | Passed |
| WR08 strong attained limit over every positive parameter | Passed | Passed |
| WR08 divergence to +∞ in unattained case | Passed | Passed |
| WR09 correction and fitted-data constants | Passed | Passed |
| WR09 worst-case sharpness | Passed | Passed |
| WR09 full positive-real noise-parameter limit | Passed | Passed |
| WR16 measured normal certificate and pointwise bound | Passed | Passed |
| WR16 norm convergence | Passed | Passed |
| No closed range/dimension/separability restriction | Passed | Passed: complete exported binders inspected |
| Zero correction space, T=0, zero datum, δ=0, positive floor | Passed | Passed: universal types admit the stated specializations |

Boundary reconstruction: T=0 gives b=0, a_α=0 and constant floor ‖r‖; all limits hold. An attained projected datum may coexist with q>0, and the argument still selects the least-squares minimum-norm preimage. Nontrivial ker T does not break uniqueness because only the minimum-norm fiber element is selected. Nonattainment of b rules out b=0 and is incompatible with finite-dimensional range, but those facts are consequences, not hypotheses. A weighted penalty tending to zero is never used as a uniform bound on the unweighted corrections.

## Formal definition/dependency checks

The accepted base defines `BudgetProfile.rangeClosure T` as `T.range.topologicalClosure` and `projectedDatum` as its `starProjection`. Thus it projects onto the closure of the actual image, without a closed-range assumption. `RegularizedHilbertRepair.correction` is the inverse of the coercive normal operator applied to `T.adjoint r`; `normal T α a = T.adjoint (T a) + α • a`; `objective` uses ‖T a−r‖²+α‖a‖². Its `gradient` is exactly T*(T a−r)+αa, not a factor-two derivative or a coordinate residual. The base pointwise `data_noise_bound` and `data_fitted_bound` have the printed constants and actual Hilbert norms. `BoundedApproximateRealization.exists_solution_of_frequently_bounded` works over any nontrivial filter and preserves the finite norm budget, so it can support a full real-parameter escape result.

These are source checks of accepted inherited dependencies. They do not substitute for exact-type inspection of the new frozen exports or for the separate clean-run verifier.

### Development source pass: basic limits module

`limits_v1.11.0/formal/KomorebiSpace/RegularizationLimits.lean` was independently read in full at SHA-256 `9a9bc073f605faa13dae5d42fa3a66f390cdf95c71241e2b25d6b3d07cc09cfd`, matching `development/basic/attempt_003/receipt.json`. That receipt records a strict compiler exit of 0 and an empty diagnostic log; this reviewer has not substituted that development receipt for the final clean-run verifier.

Source correspondence passes for 08.1, 08.2, 08.3 and 08.5. The total `path` is the accepted `RegularizedHilbertRepair.correction` whenever α>0 and zero elsewhere; `path_of_pos` proves the required bridge. Every public limit uses `𝓝[>] 0` on ℝ, and the proof explicitly uses eventual positivity. The closure competitor is selected before shrinking α, so the combined projected-error/penalty squeeze is valid over the full filter. The residual limit is norm continuity applied to image convergence. The unattained theorem concludes `Tendsto (fun α => ‖path T r α‖) (𝓝[>] 0) atTop`; its frequently-bounded contradiction uses the same parameter filter and projected image limit. No sampled parameter path, closed-range restriction, finite-dimensional restriction, ambient separability assumption, or correction-space change occurs in this source. This development source pass is confirmed by the final compiler-type review below.

### Development source pass: attained strong-limit module

`limits_v1.11.0/formal/KomorebiSpace/RegularizationStrongLimit.lean` was independently read in full at SHA-256 `f2960594f8112fb3f5f443b4059313c63642794c07fd3ad2ad3b2e9ccdb795cc`, matching the successful strict development attempt `development/strong/attempts/strong_003`. Source correspondence passes for 08.4, including construction and uniqueness of the minimum-norm preimage from actual range membership. `exists_unique_minimum_preimage` applies the inherited closed-convex nearest-point theorem to the actual fiber T⁻¹{b}; its `IsMinimum` predicate is membership and global minimum of the original Hilbert norm.

The formal route differs validly from the printed weak-subsequence route. For any preimage a of b and u=a_α, independently simplifying the exact objective identity and the orthogonal residual decomposition gives

\[
\alpha(\|a\|^2-\|u\|^2)=2\|b-Tu\|^2+\alpha\|a-u\|^2.
\]

Dropping the fitting error and dividing by positive α proves `correction_distance_sq_le`; it also supplies the required uniform norm bound. If norms of the approximate preimages were frequently at most c<‖a†‖, the inherited filter form of WR01 would give a preimage with norm≤c, contradicting minimum norm. Thus their norms tend to ‖a†‖. The preceding distance-energy bound then forces convergence in the original norm topology. `exists_unique_minimum_and_limit` concludes actual existence/uniqueness and convergence over `𝓝[>] (0 : ℝ)`, with only projected-datum range membership beyond the ordinary Hilbert/operator hypotheses. No minimum-norm selector, weak topology, assumed convergence, or extra geometric restriction is hidden in this source. This development source pass is confirmed by the final compiler-type review below.

### Development source pass: noise and inexact limits module

`limits_v1.11.0/formal/KomorebiSpace/RegularizationNoiseLimits.lean` was independently read in full, then its only later change was checked against the frozen file: replacement of an order-addition proof invocation by the equivalent `add_le_add ... le_rfl`, with no statement or definition change. Final source SHA-256 is `8e5045c83611637d9212b9f2f3563b9bd2073c3f11fa3da67b1b7b053f5dab03`, matching successful strict attempt `development/noise/attempt_004`.

Source correspondence passes for 09.1–09.4 and 16.1–16.2. `scalarSharpOperator α` is exactly multiplication by √α on ℝ, and `data_noise_coefficient_attained` gives equality for every pair of scalar data. Together with the global bound and the nonzero pair (1,0), `data_noise_coefficient_le_of_uniform_bound` rules out a smaller universal coefficient at any fixed positive α. `noise_path_bound` and `noise_fitted_path_bound` retain the two printed constants. The right-hand real-noise theorem `noisy_parameter_choice_nhdsWithin` quantifies a measured family `s : ℝ → Y` and parameter function `α : ℝ → ℝ`, assumes positivity only for positive noise levels, uses the actual noise-level variable as δ, and concludes the norm-topology limit on `𝓝[>] (0 : ℝ)`.

`stopping_rule_sequence` assumes positivity and the data/measured-gradient bounds at every natural-number index, plus the three printed vanishing schedules. Its conclusion is the conjunction of norm convergence and the displayed three-term error estimate at every index. It specializes a more general filtered theorem, but the printed sequence theorem does not lose the per-index certificate. The common `aMin` hypotheses are precisely actual preimage membership and global minimum norm; their existence/uniqueness follows from the strong-limit module rather than an extra external assumption. The fixed T, H, Y and all norm instances remain the same throughout. This development source pass is confirmed by the final compiler-type review below.

A fresh narrow subagent, given only the raw WR09/WR16 targets and source paths, independently reconstructed the noise/certificate semantics and checked their quantifiers. It also found no discrepancy in the sharpness witness, full real-noise family, normal-residual norm, positivity, or every-index stopping bound. Its source-only verdict was conditional on the named exact-data strong-limit input; it made no compiler or full dependency certification. This supplementary agreement is not a substitute for the derivations or compiler-export review.

## Final clause-to-export correspondence

The clause-to-declaration map below has been checked against the frozen compiler types as well as the source. Every name has prefix `KomorebiSpace.`. All rows pass.

| Printed clause | Declaration or required combination |
| --- | --- |
| 08.1 image→projection | `RegularizationLimits.fitted_tendsto_projectedDatum` |
| 08.2 residual norm→floor | `RegularizationLimits.residual_norm_tendsto_floor` |
| 08.3 weighted penalty→0 | `RegularizationLimits.weighted_penalty_tendsto_zero` |
| 08.4 unique minimum-norm preimage and strong limit | `RegularizationStrongLimit.exists_unique_minimum_preimage`, `path_tendsto_of_minimum`, and combined `exists_unique_minimum_and_limit` |
| 08.5 norms→+∞ when unattained | `RegularizationLimits.norm_tendsto_atTop_of_not_mem_range` |
| 09.1 correction stability | `RegularizationNoiseLimits.noise_path_bound` and `RegularizationLimits.path_of_pos` |
| 09.2 fitted-data stability | `RegularizationNoiseLimits.noise_fitted_path_bound` and `RegularizationLimits.path_of_pos` |
| 09.3 worst-case coefficient sharpness | `RegularizationNoiseLimits.scalarSharpOperator`, `scalar_correction_formula`, `data_noise_coefficient_attained`, and `data_noise_coefficient_le_of_uniform_bound` together with 09.1 |
| 09.4 entire positive-real noise-family convergence | `RegularizationNoiseLimits.noisy_parameter_choice_nhdsWithin`, with minimum-norm existence from 08.4 |
| 16.1 all-index three-term certificate | `RegularizationNoiseLimits.stopping_rule_sequence` second conjunct; its general pointwise form is `stopping_three_term_bound` |
| 16.2 norm convergence of proposals | `RegularizationNoiseLimits.stopping_rule_sequence` first conjunct, with minimum-norm existence from 08.4 |

## Frozen compiler-type and definition review

The final catalogue contains 47 new declarations: 31 explicitly written theorems, two explicitly written definitions, and 14 compiler-generated helpers. Every new row has a nonempty full type without an ellipsis. The review inspected all 47 complete types through an independent readable compiler display of the same `ci.type` expressions, paired with the frozen full export. Explicit full expansions were additionally inspected for the core right-hand limits, norm/topology instances, scalar sharpness, and energy helper. The independent display preserves all quantified binders and uses full names/universes; its name set was checked to equal the 47-name frozen catalogue exactly. This makes the display a reading aid for the actual compiled statements, rather than a hand-transcribed replacement.

The two compiled definition values were inspected directly: `path` is the accepted correction at α>0 and zero otherwise; `scalarSharpOperator` is √α times the continuous linear identity on ℝ. No new minimum-preimage selector or noise-schedule definition is hidden behind the theorem interfaces. The actual sequence certificate uses `RegularizedHilbertRepair.gradient T (α n) (s n) (a n)`, so its datum is measured, and the inherited definition has exactly the printed normal-residual meaning. Its norm instance is the original correction-space norm. Limit target topologies in the explicit expansion are the topologies induced by the declared normed groups, not weak topologies.

All quantified ordinary Hilbert types remain unrestricted. The only additional geometric assumption in the attained conclusions is actual range membership, or its explicit chosen-minimum equivalent with existence proved in the same module. In particular, the public theorem hypotheses contain no `FiniteDimensional`, `SeparableSpace`, `SecondCountableTopology`, closed-range, or operator-compactness condition. The auxiliary arbitrary-filter norm lemma has the necessary `NeBot` assumption; the right-hand real and natural-number specializations discharge this and do not export an additional assumption. Generated helpers have ordinary congruence, arithmetic simplification, or scalar-instance statements and do not add a new mathematical input.

`reviews/math/ReviewTypes.lean` generated the independent reading display from the final clean object directory, with the same strict compiler flags and no `-o` argument. Its only explicit output was in `reviews/math/`; the clean run's source and build trees were read-only. The terminal receipt confirms the compiled objects remained unchanged. `reviews/math/review_types_receipt.json` records the exact invocation and environment; `reviews/math/type_comparison.json` records declaration-name equality, full-type completeness, allowed axioms, and terminal evidence binding.

## Final evidence identity

Paths in this table are relative to `limits_v1.11.0/integration/runs/clean_limits_01/`.

| Artifact | SHA-256 |
| --- | --- |
| `source/KomorebiSpace/RegularizationLimits.lean` | `9a9bc073f605faa13dae5d42fa3a66f390cdf95c71241e2b25d6b3d07cc09cfd` |
| `source/KomorebiSpace/RegularizationStrongLimit.lean` | `f2960594f8112fb3f5f443b4059313c63642794c07fd3ad2ad3b2e9ccdb795cc` |
| `source/KomorebiSpace/RegularizationNoiseLimits.lean` | `8e5045c83611637d9212b9f2f3563b9bd2073c3f11fa3da67b1b7b053f5dab03` |
| `receipt.json` | `1fbbed1df05f74aa0c6b967cd3828b3985c7b3c4bb533027636719640978bdd0` |
| `postflight.json` | `37e7f09b13c7db2a9cb979f64402199d1a377a19f58ec698a605d7b78765bb9d` |
| `axioms.json` | `b6806e522fa0a562e91adfa3fcc3347401de7ffd7d21d7e0e5a90888d955b1f8` |
| `new_declarations.json` | `2e4d1172858215855b559348a7885bdc95ad39a6c7589a959787013f63247abb` |

The three source snapshot hashes were rechecked against the corresponding frozen files under `limits_v1.11.0/formal/KomorebiSpace/`, byte for byte. The independent readable export is `limits_v1.11.0/reviews/math/review_types.json`, SHA-256 `f60d4b29d7697132a4b30d1da1053880278f1dcdf3aa814ffddc8041de3b49e4`; its source is `ReviewTypes.lean`, SHA-256 `e0c3658f769de771cee573a0b971e50312f5e4b781a2409901c6adfa98777d04`.

The final clean receipt and postflight both report PASS. The clean run compiled 154 targets with warnings as errors and automatic implicit variables disabled, checked 39 controls, and exported 4,982 declarations, preserving all 4,935 inherited declaration identities/axiom dependencies. The new 47 declarations use only the permitted `propext`, `Classical.choice`, and `Quot.sound` axioms, with no unsafe declaration or unapproved axiom. These machine-evidence results are recorded by the separate verifier; this review's independent contribution is the printed argument and exact statement/definition correspondence.

## Remaining gap and scope limits

There is no remaining mathematical or statement-correspondence gap for the audited WR08/WR09/WR16 clauses. The strongest safe conclusion is their complete formal coverage at the stated generality, with full positive-real regularization/noise limits where printed and the every-index inexact certificate. The formal trust boundary remains Lean's compiler/kernel, the permitted standard axioms, and pinned external compiled dependencies; this review does not rebuild all external dependencies or perform an independent kernel check. Publication and archive integrity are separate reviews. No novelty claim is made for these classical Hilbert-space results.

Review commands included targeted `rg`, `sed`, and `sha256sum` of the authoritative sources and accepted base modules. Proofreading was review-only: no routine edits, no mathematical-token edits, and no unresolved printed mathematical or typographical issue within this target scope. No claim is made here about all illustrations, executable finite models, or the rest of the monograph.
