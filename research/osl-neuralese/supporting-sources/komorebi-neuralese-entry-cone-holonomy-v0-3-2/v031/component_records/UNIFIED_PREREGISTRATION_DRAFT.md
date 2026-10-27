# Neuralese v0.3.1: Entry, Cone, and Holonomy Factorization

Author: Komorebi P.  
Version: 0.3.1 draft  
Date: 2026-09-03  
Status: adaptive developmental follow-up, to be frozen before any v0.3.1 endpoint is inspected

## Study purpose

Version 0.3.0 localized three phenomena that must no longer be treated as one generic stability problem:

1. a checkpoint-seed-0 error at the unadvanced depth-zero anchor;
2. exact hard correctness after at least one learned transition over the registered ordinary-history window, despite nonzero probability and centered-logit microstate;
3. hard failures after sufficiently long paths, including repeated D4 identity words and nearly matched nonidentity words.

This study asks whether those observations factor into an **entry-interface defect**, a **finite recurrent decision-cone regime**, and **path-dependent projective drift**. It does not train, tune, select, or modify a checkpoint. Its primary scientific object is the frozen learned recurrence under the hard decoder interface. Soft outputs and matrix spectra are secondary mechanism measurements.

The study is not a test of spontaneous or universal Neuralese. It is a finite, task-local audit of two previously trained eight-state D4 workspaces.

## DESIGN_DISCLOSURE

This is an adaptive developmental study, not an outcome-independent confirmation.

Before this preregistration was frozen, the complete v0.3.0 results were known. In addition, a reviewer inspected relation-product spectroscopy on the old v0.3.0 coordinate episodes generated from seeds `930000` and `931000` while helping design this block. That inspection influenced the decision to measure positive-scalar identity residuals, projective angles, and margin-crossing sequences. Therefore, neither the selected spectral family nor the broad hypothesis that long relation products drift is confirmatory.

All registered v0.3.1 scientific endpoints will instead use fresh coordinate episodes generated only from seeds `940000` and `941000`. No learned-state, cone, margin, hard-error, soft-output, spectral, or control-word endpoint from those episodes may be inspected before the specification, runner, tests, and symbolic control-word banks are frozen and hashed. The symbolic banks may be checked before freeze only for word length, D4 endpoint, generator counts, uniqueness or multiplicity, and deterministic reproducibility. Learned matrices or decoder outcomes may not be used to admit, reject, order, or match a control word.

The fresh-episode endpoints are prospective relative to the exact frozen episode realizations. They are still adaptive-developmental evidence because the checkpoints, task family, relations, endpoint types, and mechanistic hypotheses were selected using earlier results. Fresh coordinate resampling remains inside the reconstructed D4 table-pair support and is not held-out task-family generalization.

If a scientific-code error is found after the first learned endpoint is exposed, the original output must be preserved. Any corrected analysis becomes a documented v0.3.2 adaptive revision. Thresholds, episode seeds, word banks, or domains may not be changed in place.

## Frozen scientific inputs

Only the following projective-terminal checkpoints are primary learned inputs:

| Checkpoint | SHA-256 |
|---|---|
| `projective_terminal_seed0.pt` | `b2d16d640dddc4f2f2ed69a4211f0d9948c71c3655901484238fa8ae11c1f702` |
| `projective_terminal_seed1.pt` | `a52dd3def596553c2880dfd00516bd1bb7492d1cbfab1634b570f27c1737d2d7` |

Weights must be read by the inherited restricted NumPy weights-only loader. The loader may admit only the already declared CPU float32 tensor representation and approved pickle globals. Diagnostic computation uses float64. The recurrence normalizes after every generator application. Any pre-normalization norm at or below `1e-12`, nonfinite value, malformed tensor, digest mismatch, count mismatch, or semantic endpoint mismatch fails execution. No clipping, imputation, retry with a different dtype, or replacement of a failed state is allowed.

Canonical generator symbols are `0 = R` and `1 = F`. Every canonical word must be converted through the episode-specific `canonical_to_slot` map before learned execution. Exact D4 semantics use the episode's integer permutation maps. All state comparisons, signatures, cone facets, and operator products are episode-local.

## Fresh episodes

For checkpoint seed `s` in `{0,1}`, construct exactly eight episodes by

```text
rng = np.random.default_rng(940000 + 1000*s)
sample_batch(rng, batch_size=8, length=0, family="d4")
```

Thus the only v0.3.1 episode seeds are `940000` and `941000`. The sampled `start` field is ignored and all eight visible start states are enumerated. Episode order is the order returned by `sample_batch`; it may not be sorted using learned outcomes.

The complete episode objects, or a canonical lossless serialization of `phi`, `canonical_to_slot`, integer maps, and tables, must be hashed into the execution freeze before learned endpoints are run.

## Known information allowed in design

The following v0.3.0 facts are explicitly treated as known:

- the cumulative hard rectangle failed because checkpoint seed 0's raw anchor for semantic state 2 decoded as 6 at the empty suffix;
- all 33,358,080 ordinary decisions after at least one transition were correct through history depth 8 and suffix horizon 8 on the old episodes;
- exact probability and centered-logit collapse failed once multiple histories were present;
- the earliest registered old-episode hard relator witness occurred at total observed history depth 38 and required a suffix of length 3;
- all four relation families failed somewhere by 64 inserted tokens;
- 19 of 20 hard-failing old relation configurations also had a failure in the prior final-token-toggle nonidentity control;
- old-episode relation-product spectra were inspected during design, as disclosed above.

These facts motivate the hypotheses. They are not v0.3.1 evidence and must be kept in a separate lineage table from the fresh endpoints.

## Mathematical setup

Let `D` be the `8 x 8` decoder, with row `d_q` for semantic class `q`. For episode `e`, let `A_R^e` and `A_F^e` be its learned operator matrices after table encoding. For a canonical word `w = (w_1,...,w_m)`, define

\[
A_w^e=A_{w_m}^e\cdots A_{w_1}^e.
\]

Per-step positive normalization changes the magnitude but not the positive ray of `A_w^e h`. Consequently, whenever no intermediate norm is invalid, every hard comparison after `w` has the same sign as

\[
\ell_{q,w,j}^e(h)
=
\left(d_{wq}-d_j\right)^\mathsf{T}A_w^e h,
\qquad j\ne wq,
\]

where `wq` is the exact episode D4 action on current semantic state `q`.

Define the finite hard safe cone

\[
K_{q,e}^{(H)}
=
\bigcap_{|w|\le H}\bigcap_{j\ne wq}
\left\{h:\ell_{q,w,j}^e(h)>0\right\}.
\]

These are open homogeneous polyhedral cones. They satisfy

\[
K_{q,e}^{(H+1)}\subseteq K_{q,e}^{(H)}
\]

and, where the recurrence is defined,

\[
A_a^e K_{q,e}^{(H+1)}\subseteq K_{aq,e}^{(H)}.
\]

The second relation follows from the declared suffix grammar. It is a finite facet-recursion identity, not evidence of infinite completion.

For a nonzero state and a nonzero pulled-back facet, define signed angular clearance

\[
c_{q,w,j}^e(h)
=
\frac{\ell_{q,w,j}^e(h)}
{\|d_{wq}^\mathsf{T}A_w^e-d_j^\mathsf{T}A_w^e\|_2\,\|h\|_2}.
\]

This dimensionless quantity lies in `[-1,1]`. Positive clearance is equivalent to membership in that decision half-space. A pulled-back facet norm at or below `1e-14` is an invalid geometric event and fails the relevant cone gate.

## Registered hypotheses

### H-E: entry localization and one-step absorption

The raw anchor representation and recurrent representation are typed interfaces. Any raw-anchor hard error is confined to the empty suffix, while one learned transition places every semantic state inside the finite recurrent safe cone.

This hypothesis does **not** predict that every raw anchor is decoded correctly. It predicts a location and an absorption property:

1. all nonempty suffixes of lengths 1 through 8 from every raw anchor are correct;
2. every one-step incoming representative is correct at its endpoint and under every suffix through horizon 8;
3. all one-step incoming representatives of the same current semantic state share one exact hard continuation signature through horizon 8.

### H-K: finite recurrent cone completion

Every state reached by an ordinary history of exact length 1 through 8 lies in the correct `K_q^(8)` with strictly positive angular clearance. This is a finite hard-interface claim. It permits history-dependent probabilities, logits, and rays inside the same cone.

### H-P: grouped-product sufficiency

For the registered relation paths, direct per-step normalized recurrence and grouped unnormalized matrix products followed by positive-ray normalization make identical predictions and agree in unit ray to numerical tolerance. Therefore hard failure times can be represented exactly as crossings of pulled-back decoder facets by `P_r^k h`, where `P_r=A_r` is the one-block relation product.

### H-H: long-path cone exit

At least one registered repeated identity path exits a correct finite cone by 64 inserted tokens on the fresh episodes. This is a prospective fresh-episode replication of an adaptively selected phenomenon, not a confirmatory discovery claim. Failure to find an exit would be reported as a failed replication on this domain, not as proof of stable closure.

### H-X: relation-specific excess is separable from generic drift

Repeated relation words may be less stable than deterministic words optimally matched on length, endpoint, generator exposure, directed bigrams, and run concentration. Equal-length nonidentity paths may also cause hard errors. Relation-specific excess and generic path fragility are separate finite comparisons. A result may support either, both, or neither. No word-population null model is assumed.

## Module 1: entry audit

For each checkpoint, fresh episode, target semantic state `q`, and canonical generator `a`, let `p_a(q)` be the unique exact predecessor satisfying `a p_a(q)=q`. Define

\[
h_q^{\mathrm{anchor}}=E_q,
\qquad
h_{q,a}^{\mathrm{in}}
=
\operatorname{norm}\left(A_a E_{p_a(q)}\right).
\]

For a prespecified wrong-semantic control, set `q_dagger = (q+1) mod 8` and define

\[
h_{q,a}^{\mathrm{decoy}}=h_{q_{\dagger},a}^{\mathrm{in}}.
\]

The exact entry domain contains:

- 8 raw anchors per episode;
- 16 one-step incoming representatives per episode, two for every current semantic state;
- 16 wrong-semantic incoming controls per episode;
- all canonical suffixes of every exact length `0,...,8` from each state.

The anchor vector is checkpoint-specific but episode-independent. Its suffix trajectory is episode-specific because the encoded operators differ. Every state and future is nevertheless retained per episode.

### Primary entry endpoints

- exact error set indexed by checkpoint, episode, anchor state, suffix word, and suffix length;
- raw-anchor accuracy separately at exact suffix length 0 and exact nonempty lengths 1 through 8;
- one-step incoming accuracy and minimum target margin through cumulative horizon 8;
- exact hard-signature multiplicity among the two incoming representatives for each semantic state;
- exact redirection of every decoy state toward `q_dagger`, rather than the declared original `q`;
- first revealing suffix for every pair consisting of a raw anchor and an incoming representative of the same current semantics;
- positive-ray angles and probability and centered-logit differences between the two incoming representatives.

The last two soft/geometric measurements are secondary and do not alter the hard entry verdict.

### Engineered entry replacements

Two diagnostic replacements are declared before outcomes:

```text
patch_R(q) = h_in[q,R]
patch_F(q) = h_in[q,F]
```

Each replaces the raw start anchor only, then uses the unchanged learned recurrence. Both are evaluated under every suffix through horizon 8. They are oracle-assisted mechanism interventions because they use the true visible state and exact predecessor table. Their success may localize the defect to entry, but it is not evidence that the original model learned or executes the patch.

No averaged, optimized, nearest-neighbor, learned, or endpoint-selected patch is permitted in v0.3.1.

The decoy gate requires the full hard continuation signature to equal the exact future of `q_dagger` and to differ from the exact future of `q`. Since every D4 action is bijective and `q_dagger != q`, the two exact semantic trajectories remain distinct under every common suffix. This is a causal specificity control against a generic norm or attractor explanation.

## Module 2: reachable cone audit

For every checkpoint and fresh episode, enumerate every exact canonical history of lengths `L=1,...,8` and all eight starts. The history counts per episode are

\[
n_L=8\,2^L.
\]

For every reached state, enumerate every canonical suffix of lengths `0,...,8`, all seven incorrect competitors at each suffix endpoint, and the corresponding normalized pulled-back facet. This is exact enumeration, not sampling.

### Primary cone endpoints

- membership of every state in `K_q^(H)` for each `H=0,...,8`;
- minimum signed angular clearance at every exact `(L,H)` shell;
- global minimum clearance, with checkpoint, episode, start, history, suffix, target, and competitor witness;
- fraction of states with positive clearance, separately by exact `L` and `H`;
- first horizon at which a state leaves the nested cone family, if any;
- observed-state action compatibility: for each generator, a state in `K_q^(H+1)` maps to `K_aq^(H)` for `H=0,...,7`.

### Secondary cone endpoints

- clearance quantiles `min`, `p01`, `p05`, `median`, and `p95` by checkpoint, episode, `L`, and `H`;
- within-semantic positive-ray diameter of the reached fiber;
- relation between ray diameter and minimum cone clearance, reported descriptively without a fitted cutoff;
- probability and centered-logit dispersion already used in v0.3.0, retained only to show that hard cone membership does not imply exact soft collapse.

The primary hard cone criterion is strict positivity. A separate numerical-robustness diagnostic reports whether every clearance exceeds `1e-10`. That threshold may not replace strict positivity, and failure of the robustness diagnostic does not turn a positive hard result into a hard failure.

## Module 3: relation path and margin-crossing audit

The four registered canonical identity blocks are:

| Relation | Word | Block length |
|---|---|---:|
| `f2` | `F,F` | 2 |
| `r4` | `R,R,R,R` | 4 |
| `frfr` | `F,R,F,R` | 4 |
| `rfrf` | `R,F,R,F` | 4 |

`frfr` and `rfrf` are distinct ordered learned paths but algebraically redundant D4 relations. They are not independent mathematical hypotheses.

The base-state domain is exact history depth 6:

- all 64 canonical base histories;
- all eight starts;
- all eight fresh episodes;
- both checkpoints.

This gives 512 base cases per episode. For `f2`, evaluate every integer repeat `k=0,...,32`, corresponding to inserted budgets `B=2k` through 64. For each length-four relation, evaluate every `k=0,...,16`, corresponding to `B=4k` through 64. At every repeat, evaluate all canonical suffixes of lengths `0,...,8`.

The exact D4 action of every relation power must be identity. A failure of that precondition is an execution failure.

### Primary path endpoints

- hard continuation survival and semantic accuracy at every repeat and suffix horizon;
- first repeat, inserted-token budget, and suffix horizon producing a hard error for every base case;
- global earliest observed-depth witness, where observed depth is `6 + B + suffix_length`;
- minimum target margin and signed angular cone clearance as functions of repeat;
- positive-ray endpoint angle and unit-ray L2 distance between baseline and repeated-relation state;
- count and fraction of failures requiring a nonempty revealing suffix;
- relation-product positive-scalar identity residual and conformal residual;
- exact agreement between direct recurrence and grouped-product predictions.

For a relation block product `P_r`, define the full repeated-word product `P_{r,B}=P_r^k`, where `B=k|r|`. All budget-level residuals and word-bank comparisons use `P_{r,B}`, not merely the one-block product. To avoid radial underflow or overflow, products may be rescaled by a positive scalar after each multiplication. The accumulated log scale is retained. Positive rescaling cannot alter rays, hard predictions, or the following scale-free residuals.

For any nonzero word product `P`, define

\[
\alpha_+(P)=\max\left(0,\frac{\operatorname{tr}P}{8}\right),
\]

\[
\delta_{\mathrm{scalar}}(P)
=
\frac{\|P-\alpha_+(P)I\|_F}{\|P\|_F},
\]

and, with `c=tr(P^T P)/8`,

\[
\delta_{\mathrm{conf}}(P)
=
\frac{\|P^\mathsf{T}P-cI\|_F}
{\|P^\mathsf{T}P\|_F}.
\]

A zero denominator or nonfinite quantity is invalid. `delta_scalar = 0` is positive-ray identity up to scalar. `delta_conf = 0` is conformality only and does not imply the correct relation.

### Secondary spectroscopy endpoints

- eigenvalue moduli and phases of each one-block `P_r`;
- largest-to-second-largest eigenvalue-modulus ratio;
- singular values, condition number where finite, and Henrici nonnormality;
- projective tangent singular values on the registered base states;
- direct margin sequences

\[
m_{r,k,v,j}(h)
=
\frac{(d_{vq}-d_j)^\mathsf{T}A_vP_r^k h}
{\|A_vP_r^k h\|_2};
\]

- eigendecomposition or real-Schur reconstructions of those sequences, only when their declared reconstruction residual is at most `1e-8`.

Spectral mode labels are descriptive. No dominant-mode causal claim is allowed merely from correlation with a failure time.

## Frozen symbolic controls

All word banks must be constructed and hashed before any fresh learned endpoint is evaluated. Selection uses canonical D4 algebra and symbolic word features only.

### A necessary parity restriction

Word-length parity is a D4 invariant under the declared generators. At every even relation budget, an exact-length binary word can reach only four of the eight D4 elements. In standard notation those endpoints are

```text
{e, R^2, FR, FR^3}.
```

These names are display labels only. The machine-readable bank must identify each endpoint by its exact eight-entry permutation tuple under the runner's declared left-to-right word execution. This prevents a notation convention from silently swapping `FR` with `RF`.

The odd endpoints `{R, R^3, F, FR^2}` are impossible at the same even length. A control design that claims exact length matching across all eight endpoints is invalid. v0.3.1 therefore separates exact-length controls from an explicitly non-length-matched parity sensitivity analysis.

### Bank M: globally optimal exact-length matched paths

The primary matched-path analysis uses only budgets `B in {16,32,64}`. For every relation template and budget, choose one deterministic word for each parity-feasible endpoint in `{e,R^2,FR,FR^3}`. The identity control must differ from the repeated relation template.

Controls are selected by an exact dynamic program over

```text
(position, D4 endpoint, first symbol, last symbol,
 F count, directed-transition counts, current-run length,
 differs-from-template)
```

where directed-transition counts are in fixed order `00,01,10,11`. For each dynamic-program state, retain the dominance-optimal accumulated sum of squared lengths of already closed runs. At termination, minimize the following objective lexicographically:

1. L1 difference in generator counts;
2. L1 difference in directed bigram counts in order `00,01,10,11`;
3. absolute difference in `sum(run_length^2)`;
4. Hamming distance from the repeated relation template;
5. binary lexical order, with `R=0` and `F=1`.

For constant `f2` or `r4` templates, the target run-square sum is `B^2` and the retained partial-run objective is maximized when earlier criteria tie. For alternating `frfr` or `rfrf` templates, the target is `B` and it is minimized when earlier criteria tie. This makes the dynamic program globally exact rather than a beam search. Exhaustive enumeration through at least length 8 must verify global optimality, endpoint constraints, target exclusion, and tie breaking.

The four selected paths per relation and budget are fixed conditions. Across 12 relation-budget references, Bank M therefore contains exactly 48 controls. They are not random samples from a word population.

### Bank S: parity-sandwich sensitivity

For each even `B in {16,32,64}`, select one matched path to each odd endpoint `{R,R^3,F,FR^2}` at length `B-1` and one at length `B+1`, using the same symbolic objective without an identity target-exclusion condition. For the shorter comparison, symbolic features and Hamming distance are computed against the relation template truncated to `B-1`. For the longer comparison, the periodic template is extended by its next symbol to length `B+1`. These eight paths bracket the target length but are **not length matched**. Across 12 references, Bank S contains exactly 96 controls. They are secondary evidence only and cannot establish an exact-length endpoint effect.

The complete frozen design therefore has exactly 12 repeated-relation reference words and 144 deterministic control words: 48 in Bank M and 96 in Bank S. No randomized or outcome-selected word bank is part of v0.3.1.

### Matched behavioral domain

For each of four relations, three budgets, sixteen fresh episodes, and every target or Bank-M control path, evaluate:

- all 64 exact base histories of depth 6;
- all eight starts;
- all suffixes through cumulative horizon 6, totaling 127 suffixes.

Thus each path has exactly `512 * 127 = 65,024` hard decisions per episode. The target plus four parity-feasible controls give exactly

```text
4 relations * 3 budgets * 16 episodes * 5 paths * 512 cases * 127 suffixes
= 62,423,040 decisions.
```

Bank S is a required secondary analysis. Its eight additional paths give a total target-plus-control workload of `162,299,904` decisions. These counts are execution assertions.

For path `w` in episode `e`, define hard risk

\[
R(w,e)=1-\frac{\#\{\text{base cases correct for every suffix through H6}\}}{512}.
\]

Decision-level error rate, first revealing horizon, minimum target margin, same-endpoint hard-signature disagreement, probability drift, centered-logit drift, and projective angle are also reported. They are secondary to `R(w,e)` for matched-path inference.

The three distinct questions are:

1. **same-endpoint path dependence:** does an identity word change the state or future signature relative to no insertion?
2. **identity-endpoint effect:** are identity-endpoint paths worse than equal-length paths reaching the other three parity-feasible endpoints?
3. **relator-specific excess:** is a repeated defining relation worse than its distinct, optimally exposure-matched identity control?

These questions must not be collapsed into a single use of the word “holonomy.”

### Operator comparison statistics

For every reference and control word, define

\[
T_{\mathrm{angle}}(w)
=
\max_{s,e,q,a}
\angle_+\left(h_{q,a}^{\mathrm{in}},
\operatorname{norm}(A_w^e h_{q,a}^{\mathrm{in}})\right)
\]

and

\[
T_{\mathrm{scalar}}(w)=\max_{s,e}\delta_{\mathrm{scalar}}(A_w^e).
\]

The checkpoint and episode maximum is taken before comparison, so every symbolic word contributes one scalar. These operator statistics are descriptive finite contrasts. They are not reference-distribution tail probabilities.

## Multiplicity and finite-family adjudication

No p-values, confidence intervals, permutation tests, or population-level inferential claims are registered. The words, checkpoints, and episode seeds are fixed conditions after the execution freeze. Base cases and suffixes are exhaustive nested decisions, not independent replicates.

Multiplicity is handled by declaring the whole finite family and refusing best-cell substitution:

- all 12 relation-budget references are reported;
- all 48 exact-length Bank-M controls and all 96 parity-sandwich Bank-S controls are reported;
- every contrast retains all 16 episode values, split by checkpoint;
- a universal statement requires conjunction over every named cell;
- an existential statement must say “at least one of the 12 registered cells” and identify every satisfying cell;
- no selected best relation, budget, checkpoint, episode, base case, suffix, spectrum, or control may be presented as if it were independently hypothesized;
- pooled decision accuracy cannot rescue a worst-case gate failure.

For each relation-budget cell and episode, define two primary deterministic contrasts:

\[
\Delta_{\mathrm{motif}}(e)
=R(\text{repeated relator},e)-R(\text{matched identity},e),
\]

\[
\Delta_{\mathrm{identity}}(e)
=\frac{R(\text{repeated relator},e)+R(\text{matched identity},e)}2
-\frac13\sum_{g\in\{R^2,FR,FR^3\}}R(\text{matched endpoint }g,e).
\]

A cell has **uniform motif dominance** only if `Delta_motif >= 0` in all 16 episodes, is strictly positive in at least one episode under each checkpoint, and has a positive mean separately under each checkpoint. A cell has **uniform identity-endpoint dominance** under the analogous rule for `Delta_identity`. Anything weaker is reported as mixed finite evidence, with the number and identities of positive, zero, and negative episode contrasts.

Margins, soft drift, ray angles, Bank-S parity sandwiches, spectra, and earliest witnesses are descriptive secondary families. No inferential label may be attached to them. The two checkpoint seeds and sixteen coordinate episodes do not support checkpoint-population, architecture-population, or task-population claims.

## Registered gates

| Gate | Exact pass rule | Meaning of a pass |
|---|---|---|
| `X0_execution_freeze` | exact checkpoint, episode, runner, test, preregistration, and word-bank hashes; restricted loader; exact counts and endpoints; no invalid numerics | the frozen audit executed as declared |
| `E0_anchor_lineage` | checkpoint seed 0 state-2 anchor decodes as 6, every other seed-0 anchor is correct, and all seed-1 anchors are correct, matching the deterministic v0.3.0 lineage | the inherited depth-zero observation was reproduced, not newly discovered |
| `E1_entry_localization` | every raw anchor is correct after every nonempty suffix of exact length 1 through 8, with positive margin and no invalid event | any inherited raw-anchor error is confined to the unadvanced interface on this domain |
| `E2_one_step_absorption` | all incoming representatives and both declared entry patches are correct through cumulative H8, have positive margins, and have exactly one hard H8 signature per current semantic state | one learned transition reaches a finite hard recurrent code and an oracle entry replacement repairs the interface |
| `E3_decoy_specificity` | every wrong-semantic incoming control follows the exact H8 signature of `q_dagger` and not `q` | the entry intervention carries specific semantic state rather than merely repairing norm or forcing a common attractor |
| `K0_recurrent_cone` | every ordinary exact-history state for L1 through L8 has positive clearance for every facet through H8 | finite reachable hard decision-cone completion on the registered rectangle |
| `K1_cone_recursion` | nesting and generator facet recursion are exact, and observed-state maps satisfy `K_q^(H+1) -> K_aq^(H)` for H0 through H7 | internal consistency of the finite cone construction |
| `K2_clearance_robustness` | every registered cone clearance exceeds `1e-10` | an additional numerical buffer on the registered states and facets |
| `P0_grouped_product_replay` | grouped products and direct per-step normalized recurrence have identical predictions and maximum unit-ray L2 error at most `1e-10` over the complete relation domain | the matrix-product margin-crossing representation is numerically valid |
| `H0_relation_hard_closure` | no repeated identity word through 64 inserted tokens produces an incorrect decision or nonpositive margin under any suffix through H8 | finite survival of the dense registered identity-path grid |
| `H1_relation_exit_replication` | at least one registered repeated relation has a hard cone exit by 64 tokens | prospective fresh-episode replication of the adaptively selected long-path failure phenomenon |
| `C0_control_integrity` | all 12 references, 48 Bank-M controls, and 96 Bank-S controls are present; every Bank-M path is a globally optimal symbolic match under the frozen objective; every endpoint obeys parity; every identity control differs from target; Bank-S lengths are exactly B-1/B+1; all digests match | the complete 12-reference/144-control design was constructed without learned outcomes and means what it claims |
| `Y0_same_endpoint_path_dependence` | at least one repeated identity path has unit-ray L2 difference greater than `1e-10`, probability-coordinate difference greater than `1e-10`, or centered-logit difference greater than `1e-10 * max(1,max_abs_centered_logit)` from baseline; behavioral holonomy is reported separately when a hard future signature changes | the learned realization is not numerically path flat for the registered identity words |
| `X1_relator_specific_excess` | at least one of the 12 cells meets the prespecified uniform motif-dominance rule over all 16 episodes | a repeated defining relator is uniformly no better, and sometimes worse under both checkpoints, than its distinct optimal same-endpoint symbolic match in at least one frozen cell |
| `X2_identity_endpoint_effect` | at least one of the 12 cells meets the prespecified uniform identity-endpoint-dominance rule over all 16 episodes | the two identity-endpoint paths are uniformly no better, and sometimes worse under both checkpoints, than the three parity-feasible nonidentity paths in at least one frozen cell |
| `G0_generic_path_fragility` | at least one exact-length Bank-M nonidentity control has positive H6 hard risk | path fragility is not exclusive to exact identity endpoints |

`H0_relation_hard_closure` and `H1_relation_exit_replication` are logical complements when execution passes. They are both displayed so that the report cannot frame either outcome as an omnibus success.

There is no single v0.3.1 success gate. The factorization is classified from the joint profile:

| Profile | Registered interpretation |
|---|---|
| `E1,E2,E3,K0` pass and `H1` passes | semantically specific entry-localized defect followed by a finite recurrent cone and later path-driven cone exit |
| `E1,E2,E3,K0` pass and `H0` passes | semantically specific entry-localized defect followed by relation survival only through the registered budget |
| `K0` fails | ordinary recurrent cone completion already fails inside L1-H8 |
| `H1` and `G0` pass, while `X1,X2` fail | observed long-path fragility is broader than a detected relator or identity-endpoint excess under these controls |
| `H1` and `X1` pass | long-path fragility includes a repeated-relator motif excess against the optimal same-endpoint control |
| `H1` and `X2` pass | long-path fragility includes an identity-endpoint effect among exact-length parity-feasible paths |
| `P0` fails | spectral and grouped-product attribution is invalid, regardless of hard outcomes |

## Primary and secondary endpoint hierarchy

The primary endpoints are:

1. exact raw-anchor nonempty-future correctness;
2. exact one-step incoming H8 hard-signature absorption;
3. worst signed angular clearance on the exact L1-L8, H8 recurrent cone domain;
4. first hard identity-path cone exit on the dense repeat grid through 64 tokens;
5. grouped-product replay agreement;
6. the 12 Bank-M relator-specific hard-risk contrasts;
7. the 12 Bank-M identity-endpoint hard-risk contrasts.

Secondary endpoints are soft-state differences, within-cone ray diameter, clearance quantiles, eigenvalues, singular values, nonnormality, projective tangent gains, Bank-S parity-sandwich sensitivity, finite operator residual contrasts, hard margin contrasts, and generic nonidentity-path behavior.

No secondary endpoint can override a failed primary exact gate. Any unregistered threshold, fitted projection, learned metric, chosen-after-outcome witness family, or alternative control matching is exploratory and must be placed in a separately labeled post-hoc output.

## Structural validation before fresh endpoints

The frozen tests must include at least:

1. exact regression of the two checkpoint digests and restricted-loader rejection cases;
2. canonical-word to slot-word parity under both slot assignments;
3. scalar versus vectorized recurrence parity;
4. positive normalization versus grouped-product ray parity on synthetic matrices;
5. exact inverse-predecessor construction for every D4 state and generator;
6. handcrafted entry-only, persistent-entry, and one-step-absorption cases;
7. pulled-back facet signs versus explicit suffix decoding through at least H3;
8. cone nesting and diagonal facet recursion on handcrafted systems;
9. positive and negative ray distinction;
10. a wrong-angle isometry that passes conformality and fails scalar identity;
11. a positive scalar identity that passes projective flatness;
12. a nonnormal product with delayed decision-facet crossing;
13. exact dense-repeat and suffix count formulas;
14. exact proof by enumeration that even lengths reach only `{e,R2,FR,FR3}` and odd lengths reach only `{R,R3,F,FR2}`;
15. exhaustive length-8 validation that the Bank-M dynamic program finds the global lexicographic optimum and obeys target exclusion;
16. exact frozen counts and hashes for all 12 references and 144 controls;
17. handcrafted verification of the uniform-dominance rules, including positive, zero, mixed, and checkpoint-conflicted profiles;
18. zero norm, vanishing pulled-back facet, nonfinite matrix, and tie failure cases;
19. separation of old `930000/931000` design data from fresh `940000/941000` endpoint data.

The execution freeze must record every scientific source hash, test count, test result, checkpoint hash, episode serialization hash, bank hash, and declared output path. The runner must refuse alternate episode seeds, alternate banks, missing freeze files, custom thresholds, and overwriting an existing registered result.

## Claim boundaries

A passing entry factorization supports only the claim that a deterministic, oracle-assisted one-step recurrent representative repairs the hard entry interface on the registered episodes and suffixes. It does not show that the original model autonomously corrects its start state.

A passing cone gate establishes only that the finite set of registered reachable states lies inside decoder-defined hard safe cones through H8. It does not establish:

- equality of probabilities, centered logits, rays, or full future laws;
- minimality of the quotient;
- positivity for every point in the full ambient cone;
- stabilization as `H` tends to infinity;
- an invariant metric or joint spectral bound;
- normally attracting nuisance fibers.

A hard relation failure is a valid finite counterexample to unconditional path closure at that witness. A hard relation pass certifies only the registered relations, budgets, base histories, suffixes, checkpoints, and episodes. It does not enumerate all ordinary words of the same total length.

Bank-M contrasts establish differences only among five deterministically selected paths per relation and budget. Although the symbolic objective matches generator counts, directed bigrams, and run concentration lexicographically, it does not match every higher-order motif. The fixed episode contrasts are finite comparisons, not population inference. They do not make the repeated relation exchangeable with its controls and do not by themselves distinguish training exposure from algebraic structure.

Fresh coordinate episodes do not establish held-out family generalization. Two checkpoints do not establish seed-population reliability. No v0.3.1 result establishes architecture independence, context transport, a global semantic atlas, spontaneous Neuralese in a frontier language model, recursive self-improvement, consciousness, or awareness.

## Explicitly deferred work

The following are outside the frozen v0.3.1 scientific analysis:

- retraining or fine-tuning;
- learning an arbitrary metric `G`;
- fitting a semantic projection or causal retraction;
- applying periodic fiber damping;
- architecture-to-architecture transport;
- extension beyond D4;
- using the fresh endpoints to choose a new relation, control feature, threshold, or episode seed.

Those interventions should be designed only after this factorization is complete. If pursued, they require a new preregistered version with calibration and evaluation episodes separated before fitting.

## Required outputs

The final package must include:

- this human-readable preregistration and an equivalent machine-readable specification;
- `DESIGN_DISCLOSURE` in both forms;
- checkpoint, source, test, episode, and word-bank hashes;
- frozen symbolic word banks or a byte-identical deterministic reconstruction certificate;
- per-checkpoint, per-episode entry records;
- exact cone-shell summaries and every minimum-clearance witness;
- dense repeat-grid hard-path records and earliest witnesses;
- operator residuals, grouped-product replay errors, and secondary spectra;
- all 24 deterministic hard-risk contrast vectors and their finite dominance classifications;
- all registered gate verdicts without an omnibus relaxation;
- old-design versus fresh-endpoint provenance labels on every table;
- limitations and claim boundary;
- a manifest and clean-extraction verification command.

## Freeze declaration template

The following fields must be populated before the first fresh endpoint run:

```text
PREREGISTRATION_SHA256=
SCIENTIFIC_SOURCE_SHA256=
TEST_SUITE_SHA256=
TEST_COUNT=
CHECKPOINT_SEED0_SHA256=b2d16d640dddc4f2f2ed69a4211f0d9948c71c3655901484238fa8ae11c1f702
CHECKPOINT_SEED1_SHA256=a52dd3def596553c2880dfd00516bd1bb7492d1cbfab1634b570f27c1737d2d7
EPISODE_SEED0=940000
EPISODE_SEED1=941000
EPISODE_SERIALIZATION_SHA256=
BANK_M_SHA256=
BANK_S_SHA256=
REFERENCE_WORDS_SHA256=
FRESH_ENDPOINTS_INSPECTED_BEFORE_FREEZE=false
OLD_930000_931000_SPECTROSCOPY_INSPECTED_DURING_DESIGN=true
```
