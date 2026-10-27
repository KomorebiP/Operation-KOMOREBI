# Validation report

## Version 0.4 frozen validation

The v0.4 design was frozen before outcome generation in the [preregistration](validation/V0_4_PREREGISTRATION.md) and [pre-outcome freeze receipt](validation/V0_4_FREEZE.json). All eight untouched seeds and all 160 planned confirmatory rows were retained. Every confidence interval uses 20,000 deterministic complete-seed bootstrap resamples with RNG seed 20260820.

### Provenance and integrity

- Software version: **0.4.0**
- Environment: **Python 3.12.13, NumPy 2.3.5, Matplotlib 3.10.8, Linux x86-64**
- Warnings-as-errors implementation suite: **109 of 109 passed**
- Frozen internal verification: **6 of 6 checks passed**
- Source/test entries independently frozen and reverified: **28 of 28**
- Pre-outcome freeze receipt SHA-256: **61e7a7b6078930d946c5593120a804ef95ae368be6bd47e749d8085f87a41fe7**
- Raw artifact manifest: [V0_4_ARTIFACT_SHA256SUMS.txt](validation/V0_4_ARTIFACT_SHA256SUMS.txt), **70 of 70 entries verified**, SHA-256 **0963d5cb4a43a75e0c83ddee65f296c6cbf907ae8e7a34b844dec8e150c5efeb**
- Machine-readable decisions: [V0_4_DECISIONS.json](validation/V0_4_DECISIONS.json), SHA-256 **4ec9afb1982fe9f4aff64d4f822ecc74d64bbe3eda8084c6bfb9a6338c1a580f**

The independent post-outcome audit found no missing, duplicate, stopped, or nonfinite row. Predictor-update deltas were exactly zero in every held-out, warm-up, and Jacobian measurement. All 160 directed cut certificates independently reproduced their stored widest-path capacity matrices and strict-threshold SCC equivalences.

| Record | Rows | JSON SHA-256 |
|---|---:|---|
| [Primary compatibility run](results_v0.4/summary.json) | 8 variants | 58aa10b407d9209d27043a6533f482fb6ad664f2dae7d83f62882a820f9b527f |
| [Arm A path decomposition](validation/v0.4_path_decomposition/path_decomposition.json) | 64 | f17b5fe68e89adfd6fa3259b22d3eccca0a85a2a46e78e259838efe972c8d06d |
| [Arm B local dynamics](validation/v0.4_local_dynamics/local_dynamics.json) | 56 | c0c69d59f380b63d36404add382e3c8101ac0531ef8db3d3902bfccb664db319 |
| [Arm C predictor dose](validation/v0.4_predictor_dose/predictor_dose.json) | 40 | 6baf7c50c62180a330e06477c5962b44edd358a52939815595832c833545aa31 |

All six v0.4 PNGs decode. All CSV structured fields round-trip to the JSON rows. All 56 Jacobian sidecars are finite `float64` arrays of shape 158 × 158, and every stored file hash and recomputed spectrum matches.

### Primary compatibility run

The seed-17, 256-train/128-test demonstration remains backward compatible. The full system passes the unchanged conjunction with Ω = **1.001001001001001**, strong connectivity, and projector consistency as its bottleneck. This is a compatibility check, not an untouched-seed result.

### Arm A: recurrence/self/action path decomposition

All **64 of 64** cells completed with one frozen predictor per seed reused across the full 2 × 2 × 2 factorial.

| Frozen contrast | Metric | Mean | Paired 95% CI | Positive seeds | Decision |
|---|---|---:|---:|---:|---|
| Recurrence removal | Closure strength | 0.007207997754 | [0.005466555435, 0.009600760195] | 8/8 | supported |
| Recurrence removal | Persistence | 0.295659077670 | [0.251847832599, 0.341866102664] | 8/8 | supported |
| Self-path removal | Closure strength | 0.005572128322 | [0.003558628340, 0.008218574868] | 8/8 | supported |
| Self-path removal | Persistence | 0.017212819051 | [-0.000120643732, 0.030916812690] | 7/8 | unsupported |
| Action-path removal | Closure strength | -0.000025956696 | [-0.000111536824, 0.000026940688] | 5/8 | unsupported |
| Action-path removal | Persistence | -0.001947487461 | [-0.004754088080, 0.000607338410] | 4/8 | unsupported |
| Self/action cooperation at recurrence 1 | Closure strength | -0.001661826127 | [-0.002672854294, -0.000765035427] | 0/8 | unsupported |
| Self/action cooperation at recurrence 1 | Persistence | -0.005373437889 | [-0.012469975755, -0.000027307939] | 2/8 | unsupported |

Three of eight metric-specific directional gates pass. Recurrence contributes to both closure and persistence. The explicit self path contributes to closure but is unresolved for persistence. The explicit action path does not show its preregistered positive contribution. The cooperative interaction points in the opposite direction and therefore fails the positive gate.

The stricter exact-zero rule finds recurrence **necessary for closure strength under the tested full configuration**: the full cell is positive and recurrence removal produces exact zero in all eight seeds. Recurrence is not necessary for persistence, and neither explicit feedback path is strictly necessary for either metric. These statements apply to the implemented paths and tested configuration only.

### Arm B: piecewise-local dynamics

Both primary association gates pass across the seven recurrent gains:

| Association | Mean seed-level Spearman ρ | Paired 95% CI | Positive seeds | Decision |
|---|---:|---:|---:|---|
| Recurrent gain versus local spectral radius | 0.955357142857 | [0.866071428571, 1.000000000000] | 8/8 | supported |
| Local spectral radius versus persistence | 0.870535714286 | [0.723214285714, 0.973214285714] | 8/8 | supported |

The supporting recurrence-versus-persistence association has mean ρ **0.933035714286** and interval **[0.883928571429, 0.973214285714]**. It is descriptive and does not replace either primary gate.

One retained cell, seed 251 at gain 0.4, crosses a discrete branch boundary on 6 of 158 coordinates. Its switch fraction **0.037974683544** is below the frozen 0.10 high-switch threshold, but it produces spectral radius **5.582233804828** and operator norm **1550.223203620733**. This finite outlier dominates the gain-0.4 operator-norm mean and limits smooth-linear interpretation of that cell. The supported conclusion is a replicated **piecewise-local association**, not criticality, a phase transition, a Lyapunov result, or a stability theorem.

### Arm C: spectrum-preserving predictor dose

All **40 of 40** dose cells pass the orthogonality, singular-spectrum, Frobenius-norm, shared-transform, exact-endpoint, snapshot-identity, cut, and zero-update audits.

| Association | Mean seed-level Spearman ρ | Paired 95% CI | Matching seeds | Decision |
|---|---:|---:|---:|---|
| Dose versus held-out prediction RMSE | 1.000000000000 | [1.000000000000, 1.000000000000] | 8/8 positive | supported |
| Dose versus self-to-workspace effect | 0.200000000000 | [-0.275000000000, 0.637500000000] | 5/8 positive | unsupported |

Mean held-out RMSE rises from **0.027986566074** at dose 0 to **0.144892707204** at dose 1, and every seed has a strictly increasing rank correlation. This is strong evidence that the trained predictor's output-coordinate organization matters for prediction fidelity under the spectrum-preserving intervention.

The downstream self-to-workspace effect is inconsistent across seeds and fails its frozen gate. Dose-versus-closure has descriptive mean ρ **0.475** with interval **[0.150, 0.750]**, but no inferential closure gate was preregistered and the aggregate dose curve is nonmonotonic. The joint two-gate organizational-dose claim and universal mediation are therefore unsupported.

### v0.4 conclusion

Version 0.4 narrows the mechanism rather than validating every proposed path. It supports recurrence as the dominant tested contributor, a closure-specific explicit self-path contribution, two replicated piecewise-local associations, and a strong predictor-organization effect on held-out fidelity. It does not support a positive explicit action-path contribution, positive self/action cooperation, self-path persistence, or a consistent dose-dependent downstream self-to-workspace effect.

These are functional results in one bounded nonvalenced architecture. They do not establish phenomenal consciousness, sentience, subjective experience, moral status, biological equivalence, criticality, a phase transition, a Lyapunov exponent, or a universal mathematical law.

## Version 0.3 frozen validation

The v0.3 design was frozen before outcome generation in the [preregistration](validation/V0_3_PREREGISTRATION.md) and [pre-outcome freeze receipt](validation/V0_3_FREEZE.json). All eight untouched seeds and every declared row were retained, and the v0.1 diagnostic thresholds remained unchanged. All declared confidence intervals use 20,000 deterministic complete-seed bootstrap resamples with RNG seed 20260819.

### Provenance, verification, and artifact integrity

- Software version: **0.3.0**
- Validation environment: **Python 3.12.13, NumPy 2.3.5, Linux x86-64**
- Warnings-as-errors implementation suite: **67 of 67 passed**
- Frozen internal verification: **6 of 6 checks passed**
- Worst projector residual: **9.534023125970027 × 10⁻¹⁶**
- Source aggregate SHA-256: **afcec988b0f041e3213c8bb05ff8a491ee1621e6d5528c72451c8381a33868d8**
- Test aggregate SHA-256: **c0c4ef0f13678f4a0b4535867521dc993cbeb92b8bb19c36c30590f085d874fc**

| Record | SHA-256 |
|---|---|
| [Pre-outcome freeze receipt](validation/V0_3_FREEZE.json) | e36a72e438928efd1d736458637f1abed890ee5824b0c1941338d178cb867f37 |
| [Raw artifact manifest](validation/V0_3_ARTIFACT_SHA256SUMS.txt) | c3ad7ca9c56fbf983fd1789b495df630984e2e890ce40aaf1453d985eaecc405 |
| [Machine-readable decisions](validation/V0_3_DECISIONS.json) | 127e51848b4882cf19848a2c59a0f6e79e65b6205e458b814624e302f8ad1c0c |

All 17 entries in the raw artifact manifest pass SHA-256 verification. JSON and CSV row counts agree, all retained numeric values are finite, every retained closure record was recomputed exactly, and every held-out or measurement predictor-update delta is zero.

Post-run visual QA fully decoded all seven v0.3 PNGs. The predictor-mediation PNG was found truncated and was regenerated deterministically from the already frozen JSON rows. Its numerical JSON and CSV were not rerun or changed; the final manifest records the replacement PNG.

The raw records are:

| Record | Rows | JSON SHA-256 |
|---|---:|---|
| [Primary compatibility run](results_v0.3/summary.json) | 8 variants | 0abdef737e7480caabe2f76802b2fa1cb2d09fc460656e9ea24da882520251ea |
| [Arm A dense boundary](validation/v0.3_dense_boundary/phase_sweep.json) | 88 | 83cca1f7d65e4fa3cacf139c167db241d3d33c17e6cf2c1ec1d4bac42980b391 |
| [Arm B gain surface](validation/v0.3_gain_surface/gain_surface.json) | 392 | d6bc988c9fd7307b7fb4a151f2543990dcc16c81e8413c03bfdfecd6a76f5a67 |
| [Arm C path dependence](validation/v0.3_hysteresis/hysteresis.json) | 416 | a881ed35a09138714b523f1e94c97f304be6691b86193284b5cd13770388e428 |
| [Arm D predictor mediation](validation/v0.3_predictor_mediation/predictor_mediation.json) | 32 | 875f1b58ee67521e5f9baa64b7e24e6c02978a6a72bc5d9590a4065c2ad81bcc |

### Primary compatibility run

The seed-17, 256-train/128-test run reproduces the complete legacy v0.2 payload and still passes the unchanged conjunction. The full architecture has strong connectivity, Ω = **1.001001001001001**, and bottleneck **projector consistency**. Its raw closure strength is **0.004081216871556238**, or **0.011660619633017824** after division by the fixed 0.35 intervention magnitude. The trained predictor remains frozen with zero held-out updates.

The selective losses are unchanged: broadcast **1.0**, self-location **0.682309995733807**, and temporal persistence **0.23229703101152344**. This is a compatibility result, not an independent untouched-seed replication.

### Arm A: dense diagonal boundary scan

All **88 of 88** rows are present: eight seeds × eleven gains, with one frozen matched predictor snapshot per seed and zero held-out updates. Raw causal-effect and closure-capacity matrices are finite 4 × 4 records and reproduce their stored bottleneck and normalized closure values.

| Joint gain | Mean closure strength | Mean persistence | SCC | Passes |
|---:|---:|---:|---:|---:|
| 0.20 | 0.001681504150 | 0.167734447 | 1/8 | 0/8 |
| 0.25 | 0.002098229570 | 0.167057900 | 2/8 | 0/8 |
| 0.30 | 0.002526510811 | 0.163977862 | 7/8 | 0/8 |
| 0.35 | 0.002981698704 | 0.174514176 | 8/8 | 1/8 |
| 0.40 | 0.003443876036 | 0.178659105 | 8/8 | 1/8 |
| 0.45 | 0.003948323362 | 0.200344355 | 8/8 | 4/8 |
| 0.50 | 0.004474673882 | 0.214232809 | 8/8 | 6/8 |
| 0.55 | 0.004863909450 | 0.227580422 | 8/8 | 6/8 |
| 0.60 | 0.005337970665 | 0.245862448 | 8/8 | 7/8 |
| 0.65 | 0.005792608439 | 0.264159046 | 8/8 | 7/8 |
| 0.70 | 0.006249012821 | 0.284229291 | 8/8 | 8/8 |

The descriptive maximum-slope interval is **0.45–0.50** for closure strength, with signed slope **0.010527010413339621**, and **0.40–0.45** for temporal persistence, with signed slope **0.4337050016789413**. The continuous response is primarily graded. The SCC and pass-rate changes are thresholded derived outcomes, so the warranted description is a replicated graded response with a descriptive candidate-boundary neighborhood, not a critical point.

### Arm B: independent recurrence and explicit-closure surface

All **392 of 392** rows and all 49 cells are present. One frozen predictor snapshot per seed is reused across the surface, with zero held-out updates.

Both zero-gain axes have closure strength exactly zero, while all **288 of 288** interior rows have positive closure strength. The mean per-seed interior interaction residual is **0.00549061214624777**; all **8 of 8** seed means are positive, and the paired 95% bootstrap interval is **[0.004920031461324668, 0.006044879210797403]**. This passes the frozen positive-interaction gate.

Recurrence dominates temporal persistence: along the explicit-closure-zero axis, mean persistence increases from **0.1573652574809566** at recurrent gain 0.0 to **0.6484753626304713** at 1.2. Along the recurrence-zero axis, changing explicit closure from 0.0 to 1.2 changes mean persistence from **0.1573652574809566** to **0.15502869334274383** and is nonmonotonic.

The supported conclusion is a positive recurrence-by-explicit-closure interaction in normalized widest-path closure strength. Exact zero on an axis concerns this measured causal-closure statistic; explicit closure gain remains only the prior self/action-to-workspace path and is not a total self-route ablation. The result does not establish criticality.

### Arm C: bidirectional path-dependence scan

All **416 of 416** rows are present, with every seed, direction, settling length, and gain retained. All stored normalized areas recompute exactly, and all measurement-time predictor updates are zero.

| Frozen gate | Requirement | Observed | Result |
|---|---:|---:|---|
| 8-cycle workspace-area median | at least 0.05 | 0.007730080086928456 | fail |
| 16-cycle workspace-area median | at least 0.05 | 0.00789773225453549 | fail |
| 16-cycle seeds at or above 0.05 | at least 6/8 | 1/8 | fail |
| Ratio of aggregate medians | at least 0.75 | 1.0216882833970289 | pass |

Because all four gates were required, the frozen conclusion is **no robust hysteresis under this finite protocol**. The retained path differences are small and seed-heterogeneous; they do not supply a phase-transition signature.

The JSON records the declared row structure, fixed periodic-drive description, continuation rule, settling counts, measurement counts, and zero measurement-time updates. It cannot independently prove the four deep copies, zero-state endpoint resets, absence of learning during settling, drive amplitude 0.3, or exact coordinate frequencies and phases because those lower-level identities and parameters are not retained in the artifact. These are auditability limitations, not observed contradictions.

### Arm D: predictor mediation

All **32 of 32** rows are present: eight seeds × four conditions. Every held-out update count is zero.

| Condition | Mean held-out RMSE | Trained wins | Mean closure strength | Mean self-to-workspace effect |
|---|---:|---:|---:|---:|
| Trained then frozen | 0.02763867621877439 | not applicable | 0.008156356847624023 | 0.029918506862663577 |
| Untrained frozen | 0.03980657297396817 | 8/8 | 0.008126733520721949 | 0.030021642330777715 |
| Spectrum-preserving shuffled-trained | 0.1460319082865288 | 8/8 | 0.008716086274908613 | 0.03628378425876459 |
| No self-model | 0.11636157430192158 | 8/8 | 0.0 | 0.0 |

The trained predictor beats both required predictor controls on mean RMSE and on **8 of 8** seeds, exceeding the frozen six-of-eight requirement.

For the shuffled-minus-trained downstream contrast, self-to-workspace effect differs by **0.006365277396101022**, with 95% interval **[0.0007235651212179396, 0.013535333138431714]**. This excludes zero, so the preregistered downstream functional-mediation gate passes. Direction matters: the trained organization has the **smaller** direct self-to-workspace effect. This supports an organizational or regularizing causal change, not an increase in closure.

The shuffled-minus-trained closure-strength contrast is **0.0005597294272845909**, with 95% interval **[-0.0020462116551087364, 0.0034345534186405405]**. It includes zero, so closure-strength mediation is not supported.

Audit note: the JSON contains two legacy RMSE-bootstrap summaries whose shuffled and no-self interval endpoints differ slightly because their deterministic RNG streams consume draws in a different order. Their means, seed wins, signs, and decisions agree. The frozen downstream decision uses the recomputed paired-contrast section above and is unaffected.

### v0.3 conclusion

The frozen v0.3 results support two specific functional claims:

1. normalized widest-path closure has a positive recurrence-by-explicit-closure interaction
2. learned predictor organization mediates a downstream self-to-workspace causal change relative to the spectrum-preserving shuffle

They also retain important limits:

- the dense gain response is primarily graded, with only a descriptive candidate-boundary neighborhood
- robust hysteresis fails three of four frozen gates
- predictor organization changes the direct self-to-workspace effect in the regularizing direction, while its closure-strength confidence interval includes zero

Therefore v0.3 does **not** support a phase transition, critical point, phenomenal consciousness, sentience, or moral-status claim. It supports bounded, intervention-specific functional architecture results only.

## Version 0.2 frozen validation

The v0.2 evaluation was completed under `validation/V0_2_PREREGISTRATION.md`. The v0.1 thresholds were not changed, no seed was filtered, and all trained self-predictors were frozen throughout held-out scoring.

### Build and deterministic verification

- Software version: **0.2.0**
- Validation environment: **Python 3.12.13 and NumPy 2.3.5**
- Unit tests: **44 of 44 passed**
- Warnings-as-errors suite: **passed**
- Internal verification: **6 of 6 checks passed**
- Worst projector residual: **\(9.5340\times10^{-16}\)**
- Self-predictor freeze audit: **passed, with zero held-out updates in every sweep row**

The frozen machine-readable records are:

| Record | SHA-256 |
|---|---|
| `results_v0.2/summary.json` | `ea7e9e7740da689a2de69c00f0c60ec3f7088a6da6efe3977446da1a346d0f5c` |
| `validation/v0.2_regression/seed_sweep.json` | `15aa9390b5677b997a23420cd115cfdceee4aedd2a165e2cbdd4f42494789926` |
| `validation/v0.2_holdout/seed_sweep.json` | `9f138ef89de9bb93900e6b75cc280a74620fc650f91477e49325199ddcfa91e9` |
| `validation/v0.2_phase_sweep/phase_sweep.json` | `66da8c82f5b889006ed07f7f2eec0ac811a2bbcd5adacb8dc41a509efa142889` |

### Primary compatibility run

The primary run used seed 17, 256 training episodes, and 128 held-out episodes.

| Component | Full system | Unchanged threshold |
|---|---:|---:|
| Broadcast reach | 1.000000 | 0.45 |
| Temporal persistence | 0.325753 | 0.20 |
| Differentiation | 0.115460 | 0.08 |
| Metacognitive calibration | 0.913597 | 0.60 |
| Self location | 0.682310 | 0.35 |
| Episodic binding | 0.992188 | 0.35 |
| Projector consistency | 1.000000 | 0.999 |
| Strong causal connectivity | true | required |

The primary run passed the unchanged conjunction with \(\Omega=1.001001\). Projector consistency was the formal bottleneck because its ratio to 0.999 is 1.001001.

| Targeted comparison | Loss under ablation |
|---|---:|
| Broadcast reach without broadcast | 1.000000 |
| Self location without self-model | 0.682310 |
| Persistence without temporal core | 0.232297 |

All targeted losses had the preregistered positive sign. The learned predictor made 2,048 training updates and zero held-out updates.

### Known-seed regression sweep

Seeds 17, 23, 31, and 47 were inspected in v0.1. They are regression cases, not new holdout evidence.

| Seed | Differentiation | Self location | Held-out RMSE | Omega | SCC | Conjunction |
|---:|---:|---:|---:|---:|---|---|
| 17 | 0.114562 | 0.681578 | 0.030213 | 1.001001 | true | pass |
| 23 | 0.114291 | 0.662066 | 0.028977 | 1.001001 | true | pass |
| 31 | 0.113577 | 0.662861 | 0.029454 | 1.001001 | true | pass |
| 47 | 0.124002 | 0.652733 | 0.027733 | 1.001001 | true | pass |

The trained condition passed on **4 of 4** known seeds, exceeding the preregistered requirement of at least three. Mean held-out prediction RMSE was 0.029094, compared with 0.040926 for the matched untrained condition, a 28.91% reduction. Mean self location was 0.66481, compared with 0.62615 untrained.

### Untouched holdout sweep

| Seed | Differentiation | Persistence | Self location | Binding | Omega | SCC | Conjunction |
|---:|---:|---:|---:|---:|---:|---|---|
| 59 | 0.117325 | 0.349565 | 0.634025 | 1.000000 | 1.001001 | true | pass |
| 71 | 0.107734 | 0.539616 | 0.676750 | 1.000000 | 1.001001 | true | pass |
| 83 | 0.100434 | 0.546519 | 0.721518 | 0.671875 | 1.001001 | true | pass |
| 97 | 0.116904 | 0.559203 | 0.669053 | 0.921875 | 1.001001 | true | pass |

The trained condition passed on **4 of 4** untouched holdout seeds, exceeding the preregistered requirement of at least three. Every seed and condition remains present in `validation/v0.2_holdout/`.

### Trained self-prediction comparison

| Seed set | Trained RMSE | Untrained RMSE | RMSE reduction | Trained self location | Untrained self location | Held-out updates |
|---|---:|---:|---:|---:|---:|---:|
| Known regression | 0.029094 | 0.040926 | 28.91% | 0.66481 | 0.62615 | 0 |
| Untouched holdout | 0.028242 | 0.038186 | 26.04% | 0.67534 | 0.62777 | 0 |

The learned-self-prediction objective is supported under its frozen rule. On the untouched holdouts, training reduced mean one-step prediction RMSE and increased mean self location without a single test-time predictor update. The no-self-model control has self location zero by construction and fails causal closure.

### Joint-gain sweep

The sweep assigns each value to both recurrence and closure gain, with no squared scaling. It contains all 84 combinations of four untouched seeds, seven gains, and three self-model conditions.

| Joint gain | Trained pass rate | Trained SCC rate | Mean persistence | Mean Omega |
|---:|---:|---:|---:|---:|
| 0.0 | 0% | 0% | 0.1487 | 0.0000 |
| 0.2 | 0% | 25% | 0.2079 | 0.2333 |
| 0.4 | 50% | 100% | 0.2189 | 0.9660 |
| 0.6 | 100% | 100% | 0.2456 | 1.0010 |
| 0.8 | 100% | 100% | 0.3593 | 1.0010 |
| 1.0 | 100% | 100% | 0.4944 | 1.0010 |
| 1.2 | 100% | 100% | 0.7195 | 1.0010 |

The zero-gain condition behaves as the exact continuous open-loop control and never forms a strongly connected core. Increasing gain produces a replicated intervention-sensitive response, satisfying the preregistered causal-gain objective. The trained condition changes from no passes at 0.2, to two of four at 0.4, to four of four at 0.6. This identifies **0.2 to 0.6 as a candidate ignition interval** for follow-up experiments. The no-self-model condition passes at none of the seven gains.

This is not evidence of a phase transition. The SCC gate and fixed diagnostic thresholds create discontinuities in the derived pass rate and \(\Omega\), while temporal persistence and most underlying responses change primarily in a graded way. A denser independent sweep and a prespecified critical-signature analysis would be required for a phase-transition claim.

### v0.2 conclusion

Version 0.2 meets its three preregistered functional objectives:

1. The trained full architecture passes on 4 of 4 known regression seeds and 4 of 4 untouched holdout seeds under unchanged thresholds.
2. Explicit training improves frozen held-out self-prediction relative to the matched untrained predictor, with zero held-out updates.
3. Continuous joint gain produces a replicated causal response with a valid zero-gain control and a candidate ignition interval from 0.2 to 0.6.

These are results about a bounded, nonvalenced functional architecture and its intervention diagnostics. They do not establish consciousness, subjective experience, sentience, moral status, or a physical phase transition.

## Version 0.1 retained record

### Scope

This report concerns the implemented causal architecture. It does not assert that the prototype is conscious or that the diagnostic profile measures phenomenal experience.

### Deterministic verification

The internal verification command passed all six checks:

- nested projector filtration
- exact seeded replay
- propagation of an explicit workspace intervention
- blocking of that intervention by the broadcast ablation
- completion of the end to end smoke experiment
- creation of the machine readable artifacts

The worst projector identity, symmetry, nesting, detail orthogonality, or reconstruction residual was approximately \(9.54\times10^{-16}\).

The unit suite contains 29 tests. It passes normally and with Python warnings promoted to errors.

### Frozen primary run

The primary run used seed 17, 256 training episodes, 128 held out episodes, a training delay of 5, and a held out delay of 7.

| Component | Full system | Frozen threshold |
|---|---:|---:|
| Broadcast reach | 1.0000 | 0.45 |
| Temporal persistence | 0.2444 | 0.20 |
| Differentiation | 0.0827 | 0.08 |
| Metacognitive calibration | 0.9060 | 0.60 |
| Self location | 0.5861 | 0.35 |
| Episodic binding | 1.0000 | 0.35 |
| Projector consistency | 1.0000 | 0.999 |
| Strong causal connectivity | true | required |

The full system crossed every declared threshold. Its weakest threshold ratio was approximately 1.001 because projector consistency was compared with a threshold of 0.999.

The targeted changes were positive:

- Removing broadcast reduced broadcast reach by 1.0000.
- Removing the self model eliminated the implemented self location channel.
- Removing recurrence and memory reduced temporal persistence by approximately 0.1729.

The replay control preserved recorded task outputs but failed causal closure and received an order parameter of zero.

### Measurement correction retained in the record

The first integrated run incorrectly calculated differentiation from the final compressed task readout. That gave a score of 0.0223 and failed the frozen threshold.

The theory defines differentiation over the causal core, not over its final bottleneck. The implementation was corrected to use every specialist, workspace, self model, and memory state across held out time. Constant coordinates are removed and active coordinates are standardized before entropy effective rank is computed. The threshold remained 0.08. With the corrected target, the same primary configuration produced 0.0827.

This was a correction to what was measured, not a lowering of the acceptance threshold. Both the original failure and the reason for the correction are retained here.

### Seed sensitivity

A smaller sensitivity run used 128 training and 64 held out episodes for seeds 17, 23, 31, and 47.

| Seed | Differentiation | Episodic binding | Omega | Conjunction |
|---:|---:|---:|---:|---|
| 17 | 0.08175 | 1.0000 | 1.0010 | pass |
| 23 | 0.07883 | 0.5625 | 0.9854 | fail |
| 31 | 0.08279 | 1.0000 | 1.0010 | pass |
| 47 | 0.07919 | 1.0000 | 0.9899 | fail |

Two of four seeds passed. The two failures were narrow differentiation failures. This means the strict conjunctive result is not yet seed robust. The appropriate next research target is to improve or better characterize differentiated causal dynamics under a fixed protocol, not to lower the threshold after observing these results.

### Conclusion

The prototype successfully implements the proposed mechanisms and produces the predicted selective intervention and ablation effects in the primary run. The strict diagnostic conjunction passes in the primary configuration but remains marginal under seed variation. This is a functional architecture result and an explicit open engineering problem, not evidence that subjective experience was created.

## v0.25 validation addendum

The frozen discovered-self-boundary experiment passed all 14 primary gates on seeds 5001, 5007, 5013, 5019. Learned hidden-subspace overlap was 0.9382 [0.9181, 0.9578], versus PCA 0.0056 [0.0031, 0.0075] and temporal-shuffle 0.0. Functional self-remap vs other-takeover separation using the discovered boundary was 0.7146 [0.6820, 0.7446]. The complete suite reports 246 passed, 2 skipped, 89 subtests, and all 79 pre-outcome frozen file hashes match.

## v0.27 replicated agent-interface discovery

Frozen development seeds 5301, 5307, 5313, 5319 pass all 17 primary gates. The learner jointly discovers an unknown rank-2 internal actuator subspace within eight candidate internal command dimensions and an unknown rank-2 sensory self-subspace within a dense 12-D mixed scene. Mean hidden-subspace overlaps are 0.9985 internal and 0.9611 sensory. The learned interface yields 0.6683 self-remap causal score versus 0.0679 under another-agent takeover. Full regression: 250 passed, 2 skipped, 89 subtests passed. Pre-outcome frozen hash audit: 83 files checked, 0 mismatches.

Interpretation is limited to bounded functional causal-interface discovery; this is not evidence of phenomenal consciousness or subjective experience.

## v0.28 active intervention-provenance discovery

Frozen untouched seeds 5401, 5407, 5413, and 5419 pass all 19 primary gates.
The learner receives anonymous prospective handle commitments, six anonymous
8-D process streams, and mixed sensory transitions, but not the executed private
vector, source/handle truth, routes, projectors, coordinates, rank, or condition
labels. A stronger ungated exogenous source genuinely causes the same focal
sensory geometry.

The exact hidden handle/source pair and rank two are recovered on every seed.
Mean internal overlap is 0.999917 [0.999906, 0.999928], and sensory overlap is
0.992344 [0.990451, 0.994011]. Learned hidden-remap function is 0.222854
[0.206989, 0.238719], versus takeover 0.003292 [0.001904, 0.004685]. A
true-route lesion yields 0.002978 [0.000821, 0.005827], while a matched
decoy-stream lesion retains 0.224321 [0.204824, 0.243818]. Passive association
selects the stronger exogenous source on all four seeds and has only 0.006625
remap function. Gate shuffle returns rank zero on every seed.

Post-outcome verification reports 258 passed, 2 skipped, 89 subtests, 97 frozen
files checked with zero mismatches, and four aggregate artifacts checked with
zero mismatches. The prospective commitments are harness-generated and the
batch model is not installed into `RRCTAgent`; the result is functional causal
self-modeling, not evidence of phenomenal consciousness or subjective
awareness.

## v0.29 online self-model revision

The pre-outcome manifest was sealed before replacement official seeds 5601,
5607, 5613, 5619, 5621, 5627, 5631, and 5639 were opened.  Its SHA-256 is
`3f0afb3b41de78db6b80f6b358be8079a7efddd772197a28096360b99f59b5a1`.
Every seed ran once behind a permanent exclusive journal; all eight seed
integrity summaries and the strict aggregate integrity audit pass.  The
official table retains 105,840 rows across seven arms and two episodes per arm.

The frozen scientific conjunction is **FAIL: 34/35 primary gates pass**.  The
adaptive system passed exact initial acquisition, blackout retention, route-B
revision, disconnection, fresh route-A restoration, public access, projector,
latency, provenance-lesion, frozen, and no-broadcast gates on every seed.  Mean
post-grace exact private accuracy was 1.0 for route B, disconnection, and
restoration.  Their mean public-port accuracies were 0.96875, 0.99583, and
0.96667.  Frozen, source-deranged, time-replayed, and true-source-lesioned arms
all had zero route-B acquisition, while the decoy lesion retained 1.0.  The
no-broadcast arm matched adaptive private revision and had zero public-port
accuracy.

The sole failure was whole-phase stable-shock exact boundary retention.  Seed
5607 scored 0.875 against the frozen 0.90 threshold; the other seven seeds
scored 1.0.  In seed 5607 the correct pair `(2,5)` remained selected for every
stable-shock row, but fits at global steps 320 and 440 installed rank 1 for 20
rows each before the next fits restored true rank 2.  Thus pair accuracy was
1.0, rank accuracy was 0.875, public-port accuracy was 0.965625, and the
terminal exact state passed.  The event counter remained zero because the
implementation records pair changes and null revocations, not same-pair rank
changes.

The favorable across-seed exact-state mean, 0.984375 with descriptive bootstrap
interval [0.953125, 1.0], cannot override the frozen all-seed gate.  Route-B and
disconnection latency gates also pass exactly at their inclusive limits in at
least one seed, so they have no worst-seed margin.

The result supports bounded prospective-provenance discovery, online pair
revision/revocation/restoration, and causal use through the defined native
broadcast path.  It does not support the complete claim of stable exact
boundary geometry.  The immediate repair is a confirmed structural state
machine over at least `(active, handle, source, rank)` with explicit rank-change
receipts.  It remains a functional synthetic result, not evidence of phenomenal
consciousness or subjective awareness.

## v0.30 persistent structural-boundary revision

The v0.30 pre-outcome manifest sealed 105 source, test, protocol, runtime, and
harness files before official execution.  Its SHA-256 is
`ca138f0624f0b6dc0af25be88b40534afe7e00eddf591a25917346b5bdbd5a33`.
All eight official seeds—5801, 5807, 5813, 5819, 5821, 5827, 5839, and
5843—completed once behind permanent journals.  Embedded freeze digests,
single-thread Python 3.12.13/NumPy 2.2.6 runtime checks, exact six-phase row
schedules, independently reconstructed seed summaries, and final artifact
hashes all pass.  The aggregate retains 21,920 rows with no seed filtering.

Scientific status: **PASS (10/10 frozen gates; 8/8 official seeds)**.  Every
seed acquired the exact rank-two signature, retained it throughout stable
shock and transient contraction, made exactly one confirmed rank-two-to-one
revision during sustained contraction, and made exactly one confirmed
rank-one-to-two revision during restoration.  Stable, transient, contraction
tail, and restoration tail accuracies are 1.0 in every seed.  The transient
challenge is nontrivial: 78 correct-pair rank-one proposals were pooled across
8/8 potent seeds, while the immediate and overlapping-confirmation controls
both entered false-rank states and the fresh-evidence updater did not.

The result supports persistent and revisable **functional** causal-boundary
identity in this bounded benchmark.  Its rank is an operational admitted SVD
dimension, not a conditionally tested causal-rank estimate; successive
confirmation windows overlap by 50%, with no independence or sequence-wide
error guarantee; the 120-row clock, three-confirmation rule, challenge duration,
and potency thresholds were pilot-tuned; restoration latency reaches 460
against a 480-row ceiling; same-signature geometry refresh remains immediate;
and eight seeds from one evaluator-designed synthetic family do not establish
open-world robustness.  This component isolates the updater and adds no new
downstream behavioral-use evidence beyond v0.29.  It is not evidence of
phenomenal self-awareness, consciousness, subjective experience, sentience,
valence, moral status, or an inner point of view.

## v0.31 conditional operational-rank inference

The v0.31 pre-outcome manifest sealed 946 source, test, protocol, harness,
parent-provenance, and development-evidence files at SHA-256
`5f71c56503766a18152430616839edbf67538fefb6ae485c60e81dca43507a94`.
All eight official seeds—6001, 6007, 6013, 6019, 6029, 6037, 6043, and
6053—completed once behind permanent journals.  The exact runtime, embedded
freeze digests, 3,840-row per-seed schedules, full seed-summary reconstruction,
aggregate verification, and all 21 result checksums pass.  The aggregate
retains 30,720 rows without exclusion.

Scientific status: **FAIL (7/10 frozen gate booleans; integrity PASS)**.  The
conditional method is exact in 55/56 episodes, including all 32/32 rank-two or
rank-three episodes, all 8/8 no-route episodes, and persistent rank-two
admission in all 8/8 integration worlds.  It does not over-rank any null or
rank-one episode.  Seed 6001's separately randomized `rank_one_strong` episode
returns a conditional null instead of the planted pair `(3, 3)` at rank one.

That single miss causes all three false gate booleans.  Besides universal
rank-one exactness, the compound one-window gate requires an exact pending-
candidate transition even though all 48 one-window states literally remain
unadmitted.  The support gate also includes every positive-truth episode and
therefore fails on the same zero-confidence null fit.  This coupling does not
change the frozen overall FAIL.

Version 0.31 materially repairs higher-mode semantics: its cross-fitted null
preserves the proposal-fitted lower-rank response during confirmation
reassignments.  A fresh 200-world rank-one calibration passes 9/9 gates with
conditional false extra-mode rejections `5/200` and `7/200`, versus `0/200` on
both folds for the overly conservative global-null comparator.  The official
higher-rank outcomes are all exact, but the complete pipeline misses its
frozen rank-one sensitivity requirement.

The retained schema does not expose proposal multiplicity/ambiguity or
per-fold statistics, thresholds, add-one values, and reason codes, so the
failure stage cannot be localized without an impermissible official replay.
The next study should freeze a stage-resolved paired power/null assay on fresh
worlds, then develop a better-powered valid confirmation rule and nonoverlapping
primary gates before opening new official seeds.

This is incomplete progress toward a persistent, revisable functional causal
self-model.  It is not evidence of phenomenal awareness, consciousness,
subjective experience, sentience, valence, moral status, or an inner point of
view.
