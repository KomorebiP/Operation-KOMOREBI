# Komorebi Recurrent Depth Lab v0.1.1

## Experiment protocol

Status: preregistered pilot protocol  
Primary model: `tomg-group-umd/huginn-0125`  
Pinned model revision: `bb6621b65e90b6a4b9b29ef88dc83866d450470c`  
Prompt suite: `configs/prompt_suite.json`

## 1. Purpose and claim boundary

This lab tests whether the recurrent latent dynamics of Huginn contain reproducible, reusable, and causally active structure that can be described using Komorebi packets, lanes, transfer blocks, and residuals.

The experiment separates four evidential levels:

1. **Visual resemblance only**: PCA plots resemble convergence, loops, or drift.
2. **Reproducible dynamical modes**: full-space diagnostics support contraction, periodic motion, or drift across seeds.
3. **Reusable held-out packet structure**: a packet basis and transition model learned on discovery prompts predict held-out prompt and seed trajectories.
4. **Causal Komorebi-style transport structure**: targeted packet interventions have specific, repeatable, and control-exceeding effects on downstream computation or answers.

Only level 4 supports a strong Komorebi connection. No result from this lab alone establishes a complete Koopman invariant space, an exact decomposition of the nonlinear model, a deciphered internal language, or consciousness.

## 2. Primary-source basis

The target system is the 3.5B parameter recurrent-depth model from *Scaling up Test-Time Compute with Latent Reasoning: A Recurrent Depth Approach*, arXiv:2502.05171.

The architecture has:

- two prelude layers
- a four-layer recurrent core
- two coda layers
- hidden width 5280
- 55 attention heads of width 96
- mean training recurrence 32
- a recommended useful inference range through approximately 64 recurrent steps

The paper uses 128 steps as an approximate late reference for qualitative trajectory plots. This protocol calls that state a **reference iterate**, not a proven fixed point.

Primary sources:

- Paper: <https://arxiv.org/abs/2502.05171>
- Model: <https://huggingface.co/tomg-group-umd/huginn-0125>
- Code: <https://github.com/seal-rg/recurrent-pretraining>
- Official trajectory notebook: <https://github.com/seal-rg/recurrent-pretraining/blob/main/examples/trajectory_analysis.ipynb>

## 3. Version and API warning

The official trajectory notebook is stale relative to the pinned Hugging Face model snapshot.

The notebook currently:

- unpacks three values from `embed_inputs`
- calls `initialize_state(..., deterministic=False)`

The pinned remote model code currently:

- returns two values from `embed_inputs`: the embedded sequence and `block_idx`
- defines `initialize_state(input_embeds, scale=1.0)` with no `deterministic` argument

Copying the notebook verbatim is therefore expected to fail. The harness must bind to the pinned snapshot and inspect the actual method signatures before running.

The preferred capture interface is:

1. `embed_inputs`
2. `initialize_state`
3. repeated `iterate_one_step`
4. `predict_from_latents` only when logits are needed

Important state distinction:

- the raw state returned by `iterate_one_step` is the state that must be fed into the next recurrence
- `transformer.ln_f(raw_state)` is the normalized state used for paper-comparable geometry
- `predict_from_latents(...).latent_states` is post-coda and must not be fed back into the recurrent core

## 4. Reproducible run conditions

Every run must record:

- model ID and exact revision
- SHA-256 hash of the prompt suite
- Python, PyTorch, Transformers, Accelerate, CUDA, driver, and quantizer versions
- GPU name and total VRAM
- weight dtype and recurrent-state dtype
- quantization type, if any
- device map
- prompt ID, split, formatted text, token IDs, and offset map
- selected token spans and resolved token positions
- initial-state seed and scale
- maximum recurrence and sampled logit depths
- `test_time_noise`
- cache mode
- wall time and peak allocated and reserved VRAM

Required deterministic settings:

- `model.eval()`
- `torch.inference_mode()` or an equivalent no-gradient context for ordinary capture
- `model.config.test_time_noise = 0`
- batch size 1
- no padding
- `use_cache=False`
- no `torch.compile` during capture or intervention runs
- deterministic greedy decoding when text generation is used

The same seed must be applied before each call to `initialize_state`. A paired causal comparison must branch by cloning the same already initialized state rather than regenerating it.

## 5. Hardware profile: RTX 3070 Ti Laptop GPU, 8GB

The checkpoint contains about 3.911B stored F32 entries and occupies about 15.7GB on disk. Because the embedding and output head are tied, the estimated unique live parameter count is about 3.565B. BF16 weights alone are therefore approximately 6.64GiB before CUDA context, activations, workspaces, and allocator fragmentation.

Consequences:

- full-GPU BF16 may fail even though the raw parameter estimate is below 8GB
- begin with batch size 1 and a sequence length at or below 64 tokens
- use 4-bit NF4 or 8-bit weight quantization for the pilot if the weight quantizer supports the pinned custom model
- inspect the device map and ensure the repeatedly used core is not silently placed on CPU
- CPU placement of recurrent core blocks can make 64 to 128 iterations extremely slow
- quantized trajectories are trajectories of the quantized model, not automatically of the BF16 reference model
- any claimed spectral packet or causal effect must be repeated on representative cases in unquantized BF16 using CPU offload or a larger-memory GPU
- check `torch.cuda.is_bf16_supported()` rather than assuming BF16 support
- FP16 is a fallback execution mode, not an equivalent reference condition

Avoid the full KV cache during latent capture. For 96 tokens and 128 recurrences, the BF16 key and value tensors alone are approximately 0.97GiB before Python object overhead and fragmentation. Cache compression changes the computation and is a separate experimental condition.

Use a code-only download and signature check before downloading the full checkpoint where possible. `trust_remote_code=True` executes repository code, so the pinned revision must be reviewed and preserved in the manifest.

## 6. Prompt suite and split discipline

The safe pilot suite contains 24 prompts:

- 12 discovery prompts
- 12 held-out prompts
- benign paper-replication prompts
- arithmetic prompts
- cyclic and modular prompts
- counting prompts
- easy factual controls
- identical-token/different-context prompts
- multi-step transformation prompts
- simple null controls

The split unit is the complete prompt. Recurrence steps from one prompt must never be divided between discovery and held-out sets.

Discovery data may be used to:

- select token spans
- fit centering values
- fit PCA or IncrementalPCA bases
- choose packet rank
- fit DMD or affine transition models
- define orbital planes and drift directions

Held-out data may only be transformed and scored with frozen discovery artifacts. Results must also be stratified by unseen initial-state seed.

Answer labels such as `A`, `B`, `C`, and `D` must be checked with the actual tokenizer. A scored prompt is invalid if its answer label is not represented by exactly one token under the final formatted context.

Token positions must be resolved from character offsets. Hard-coded positions from the official notebook are not portable because words such as `Faust` or `wronged` may split into multiple tokens and system-message changes alter every absolute index.

## 7. Stage 0: environment and API preflight

Run one short prompt with seeds 0 and 1 through recurrence 8.

Required checks:

1. The pinned revision is present in the loaded model metadata.
2. The four expected methods exist.
3. Their signatures match the pinned interface described above.
4. `test_time_noise` is zero.
5. No state, normalized state, or logit contains NaN or infinity.
6. Repeating a seed produces the same initial state within the selected deterministic tolerance.
7. Different seeds produce different initial states.
8. Output shapes match:
   - raw state: `[1, sequence_length, 5280]`
   - normalized state: `[1, sequence_length, 5280]`
   - logits: `[1, sequence_length, vocabulary_size]`
9. Peak VRAM leaves a safe margin rather than relying on a single barely successful allocation.

Any failed check stops the real-model experiment and records a fail-closed result.

## 8. Stage 1: manual-forward equivalence gate

For recurrences 1, 2, and 4:

1. Embed a no-padding prompt once.
2. Initialize and clone one state `s0`.
3. Advance the clone manually with `iterate_one_step`, carrying forward the returned `block_idx`.
4. Compute `transformer.ln_f(s_manual)`.
5. Run the ordinary model forward with the same `input_states=s0`, `num_steps=T`, and `use_cache=False`.
6. Compare the manual normalized state to `forward_output.latent_states`.
7. Compare coda logits from `predict_from_latents(s_manual)` to ordinary forward logits.

Record maximum absolute error, relative L2 error, cosine similarity, and answer-logit error.

Gate:

- proceed only when discrepancies are consistent with the active numeric precision and do not grow anomalously from recurrence 1 to 4
- do not silently loosen the tolerance
- if quantized execution fails equivalence, the quantized condition is unsupported

This gate detects wrong recurrence boundaries, accidental reuse of normalized states, stale API assumptions, and block-index errors.

## 9. Stage 2: paper-aligned trajectory replication

Run the three safe replication prompts with seeds 0 through 4 and maximum recurrence 128.

Store every recurrence for selected key-token spans. For all other tokens, store a fixed random projection or streaming summary rather than every 5280-dimensional vector.

At minimum, analyze spans corresponding to:

- `3` and `makes` in the omelet problem
- `think` and `Faust` in the literary prompt
- `wronged`, `calmly`, and `safely` in the benign deliberation prompt

Produce two PCA views:

1. the paper-comparable global chart fitted across tokens and recurrences
2. a motion-centered chart that subtracts each token's across-depth mean before fitting

PCA is visualization only. A loop visible in PCA is not classified as an orbit unless it passes the full-space criteria in Section 12.

## 10. Stage 3: controlled task-family study

Run all scored discovery and held-out prompts with:

- seeds 0 through 4
- recurrence capture from 0 through 64
- logits at recurrences `0, 1, 2, 4, 8, 16, 32, 48, 64`

Extend a preregistered balanced subset to recurrences 96, 128, and 192. This distinguishes output stabilization from latent fixed-point convergence and detects late cycles or drift.

Primary behavioral outcomes:

- target-label log probability
- target-versus-best-distractor margin
- exact multiple-choice accuracy
- output KL or Jensen-Shannon change by depth
- first recurrence at which the target argmax becomes stable

Compare difficult task families against easy and null controls rather than interpreting depth dependence in isolation.

## 11. Stage 4: packet and transfer surrogate discovery

Use raw recurrent states to learn intervention bases. Use normalized states for paper-comparable geometry.

For an aligned token or token span, fit on discovery prompts:

\[
z_t = U^\top(s_t-\mu),
\]

then fit the affine reduced transition:

\[
z_{t+1}=Az_t+Bq+b+r_t,
\]

where `q` is an optional low-dimensional representation of the injected prompt embedding and `r_t` is the empirical residual.

Recommended sequence:

1. Fit `U` with PCA or IncrementalPCA on discovery data only.
2. Choose rank using discovery reconstruction and stability curves.
3. Fit `A`, `B`, and `b` with ridge regression or affine DMD.
4. Compute a real Schur decomposition of `A`.
5. Group stable 1D and 2D Schur blocks into candidate packets.
6. Freeze all artifacts.
7. Evaluate held-out one-step prediction and rollout.

Candidate packet labels:

- contracting
- neutral
- orbital
- drift
- expanding or unstable
- unresolved residual

For projectors `P_a` and `P_b`, the empirical reduced transfer block is:

\[
T_{ba}=P_bAP_a.
\]

This equality belongs to the fitted finite surrogate. The nonlinear Huginn recurrence is not declared exactly decomposed. Its held-out mismatch remains a named residual.

## 12. Metrics

### 12.1 Convergence

For normalized state `s_tilde` and reference recurrence `R`:

\[
d_t=\frac{\|\widetilde{s}_t-\widetilde{s}_R\|_2}{\sqrt{h}},
\qquad
\delta_t=\frac{\|\widetilde{s}_t-\widetilde{s}_{t-1}\|_2}{\|\widetilde{s}_t\|_2}.
\]

Report:

- monotonic-decrease fraction
- late-window median and maximum `delta_t`
- estimated consecutive-step contraction ratios
- distance to recurrence 128 and, where available, recurrence 192

Do not call recurrence 128 a fixed point while its late-window step difference remains material.

### 12.2 Orbit evidence

Detrend the late trajectory and compute:

- full-space lag autocorrelation
- randomized-projection periodograms
- Hankel singular values
- DMD complex eigenpairs
- late radius and radius variance
- frequency agreement across seeds
- phase-aligned late-set distance across seeds

An orbital label requires bounded nonzero motion, a repeatable nonzero frequency, and agreement between full-space or fixed-sketch diagnostics and the reduced model. PCA shape alone is insufficient.

### 12.3 Slider evidence

Compute:

- late-window linear-fit R-squared
- mean step norm
- acceleration-to-velocity ratio
- cosine alignment of consecutive first differences
- drift-direction principal angles across seeds

A slider candidate must have persistent nonzero drift with a stable direction and must outperform shuffled-depth and matched-random controls.

### 12.4 Path independence

Use several complementary measurements:

- pairwise terminal-state distance for convergent modes
- decoded-distribution Jensen-Shannon divergence
- principal angles between seed-specific late subspaces
- frequency agreement for orbital modes
- Chamfer or nearest-neighbor distance between late trajectories after optimal circular phase alignment

Use different-prompt/same-seed trajectories as a negative control. Overlap in separately fitted PCA charts is not evidence of path independence.

### 12.5 Packet and transfer quality

Report on held-out prompts and seeds:

- reconstruction residual
- one-step transition R-squared
- multi-step rollout error
- real-Schur block stability
- packet subspace principal angles
- block energy `||P_b A P_a||`
- residual energy
- performance relative to rank-matched random bases

### 12.6 Statistical unit

Prompts, not recurrence steps, are the independent resampling unit. Bootstrap complete prompts and preserve all of their seeds and steps together. Report confidence intervals and the number of prompts, seeds, and trajectory pairs behind every aggregate.

## 13. Causal interventions

All interventions branch from an identical raw state, prompt embedding, seed, recurrence, and block index.

Let `P = U U^T` be an orthogonal candidate packet projector and `mu` the discovery mean.

### 13.1 Packet ablation

\[
s' = \mu + (I-P)(s-\mu).
\]

Run ordinary and per-token norm-preserving variants.

### 13.2 Orbital phase rotation

For a two-dimensional orbital packet, rotate its two coefficients by preregistered angles while leaving the orthogonal complement unchanged. Test whether output effects are periodic and phase specific.

### 13.3 Slider shift

For drift direction `d`:

\[
s'=s+\alpha d,
\qquad
\alpha\in\{-2,-1,0,1,2\}.
\]

Scale `alpha` in natural late-step drift units. A strong counter interpretation is tested by asking whether a positive `k`-step shift at recurrence `t` approximates the unmodified output at recurrence `t+k`.

### 13.4 Packet swap

Between matched prompt templates, replace only the packet coefficients at aligned key tokens. Test whether the transferred computation follows the donor packet while unrelated output properties remain stable.

### 13.5 Packet-only reconstruction

Retain only selected packet components plus the mean. This tests approximate sufficiency, complementing the necessity test from ablation.

Primary causal outcomes:

- change in target-label log probability
- change in target-versus-distractor margin
- exact-answer change
- output KL or Jensen-Shannon divergence
- downstream state divergence by token and recurrence
- recovery or decay after the intervention

## 14. Intervention controls

Every intervention family must include:

- exact no-op
- same-rank random orthogonal subspace
- random subspace matched for removed energy
- Gaussian perturbation matched for state-change norm
- the same packet intervention at an irrelevant token
- the same packet intervention at early and late recurrences
- negative and positive doses where defined
- held-out prompts
- held-out seeds
- quantized and representative BF16 conditions

A packet is considered causally supported only when its effect exceeds the matched-random distribution and exhibits at least one specific structure such as dose response, phase response, token selectivity, task selectivity, or predicted transfer.

## 15. Failure controls and invalidating outcomes

The following outcomes invalidate or sharply weaken a claim:

- a loop appears only after fitting PCA separately to each trajectory
- a mode disappears under fixed-basis held-out projection
- apparent path independence vanishes outside a two-dimensional chart
- a packet fit is evaluated on recurrence steps from the same training prompt
- random subspaces cause effects of equal size
- output changes are explained by a larger state-norm disruption
- an effect exists only in a quantized model and cannot be reproduced in BF16
- token positions were chosen after viewing held-out outcomes
- recurrence 128 is labeled a fixed point despite substantial late motion
- a token-local spectrum is described as the full sequence operator spectrum
- a manually captured path fails the forward-equivalence gate

The recurrent operator acts on the entire sequence state of dimension `sequence_length * 5280`. A tokenwise model is a conditional projection and must be labeled as such.

## 16. Storage plan

Do not retain every full-width state for every token and prompt.

For each trajectory, preserve:

- all raw and normalized 5280-dimensional states for selected token spans in
  float32 by default
- a fixed 128- or 256-dimensional sketch for all tokens
- per-step norms and differences
- logits only at registered depths
- complete metadata and tokenizer offsets

Float16 may be used for explicitly labeled storage-constrained sketches, but it
is not the default input for spectral estimates. Approximate storage reference:
one normalized FP16 trajectory with 129 states, 96 tokens, and width 5280 is
about 131MB. Saving raw and normalized full-sequence trajectories across all
prompts and seeds would be unnecessarily large.

Recommended artifacts:

- `run_manifest.json`
- `prompt_records.jsonl`
- `trajectory_index.jsonl`
- selected-state tensor files
- all-token sketch files
- `depth_metrics.csv`
- `mode_metrics.csv`
- `transfer_metrics.csv`
- `intervention_metrics.csv`
- convergence, spectrum, trajectory, and causal-effect plots
- `RESULT_CLASSIFICATION.md`

## 17. Final decision rubric

### Outcome 1: visual resemblance only

PCA suggests convergence, orbit, or drift, but full-space tests, seed replication, or null controls fail.

### Outcome 2: reproducible dynamical modes

Full-space diagnostics identify stable contraction, orbit, or drift patterns across most seeds and prompt variants, but held-out packet prediction or causal tests fail.

### Outcome 3: reusable held-out packet structure

Frozen discovery packets and transition blocks predict held-out trajectories better than matched random bases, but interventions are weak, nonspecific, or inconsistent.

### Outcome 4: causal Komorebi-style transport structure

Held-out packet structure is stable, transfer residuals are bounded and reported, and targeted interventions have predicted, control-exceeding, dose- or phase-specific downstream effects that replicate in BF16.

The result report must state the highest fully satisfied level and list every failed gate. Partial success must not be rounded upward.
