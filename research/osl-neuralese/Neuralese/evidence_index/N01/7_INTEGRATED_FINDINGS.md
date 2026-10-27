# Komorebi Neuralese Operator Workspace v0.3.0: integrated findings

## Decision

The sealed Stage A primary **failed**. Only **8 of 26 frozen gates passed**.

V0.3 answered one engineering question decisively: sign-canonical QR can make
the recurrent operator channel noncontractive and norm-preserving through
2,048 steps. It did not answer the scientific question positively. The hard
model did not learn reliable operator execution across seeds, did not acquire
the preregistered anonymous-closure behavior, and did not support the required
cross-context causal state patches. The soft model was much more accurate at
depths 8--128, but its recurrent state collapsed by depth 2,048.

The correct conclusion is therefore:

> Exact orthogonal recurrence repairs numerical norm collapse by construction,
> but the tested QR parameterization does not jointly deliver stable dynamics
> and reliable learned operator semantics. V0.3 exposes a stability--trainability
> tradeoff; it does not establish a stable Neuralese substrate.

This negative result is informative because it was obtained with a complete
48-cell test grid, an immutable pre-test seal, strict path-level train splitting,
a fail-closed exact oracle, matched shuffled controls, six transport pairs, and
an exact single-cell replay.

## What Stage A tested

Each episode supplied two complete eight-state permutation tables, a start
state, and an anonymous operator word. The latent state had dimension eight and
the operator channel was explicitly matrix-shaped. An exact solution exists:
transpose the row-coded transition table and recurrently apply it to a one-hot
state. Stage A is consequently a strongly structured table-execution assay,
not an operator-discovery task.

The four primary treatments were:

| Arm | Recurrent dynamics | Anonymous composition target |
|---|---|---|
| `hard_correct` | Sign-canonical orthogonal QR, fixed \(G=I\) | Correct |
| `hard_shuffled` | Sign-canonical orthogonal QR, fixed \(G=I\) | Matched shuffled |
| `soft_correct` | Learned full SPD metric with soft isometry pressure | Correct |
| `soft_shuffled` | Learned full SPD metric with soft isometry pressure | Matched shuffled |

Hard and soft arms began from bit-identical raw parameter tensors, but QR
immediately changes the hard arm's effective operators and adds different
computation. Their comparison is a whole-treatment engineering comparison,
not a one-factor causal estimate, a compute-matched comparison, or a formal
noninferiority test.

## Protocol and execution integrity

Development-only qualification used four seeds and dev coordinates. It passed
all **8/8 qualification gates** across a complete **16/16-cell** grid after a
disclosed failed 4,000-step attempt, an 8,000-step calibration, and developmental
architecture scans. Qualification therefore justified opening the frozen
primary; it was not confirmatory evidence.

The primary protocol was then sealed at `2026-09-02T21:20:29Z`, while the
primary output was absent and test coordinates were recorded as unopened. The
primary ran all four arms on seeds 300--311: **48/48 cells**, plus **six**
disjoint hard-arm transport pairs. The parameter-free exact table oracle passed
its orientation, composition, closure, split, and stability checks. A later
execution-supervisor interruption was handled by deterministic bounded
recovery; existing cells were validated before the remaining cells and
transport pairs were completed, with recovery events retained in the result.

| Integrity object | SHA-256 |
|---|---|
| Primary protocol | `ecd48865c7327b39b5d0b2679f2e6fc3e9509a01bce343cfe94b9b237482acaf` |
| Scientific code at seal, 29 files | `814ea6f2301523965bf8d94dd9da8bbb598451f03e0200cae1cde2ab8de53624` |
| Coordinate split | `3aceaac6852f88360de0851eefc43bf46331d3b4efe3a04d0f2b9dfeff455340` |
| Qualification protocol | `0bca42f89400904180f36872aaa4fb8040c2cb848b86e50dc084eb90a47634a0` |
| Qualification receipt | `511d706bd82f910d1817e21e99aa58823e86707b5652736fd74281e2d75e7f55` |

## Primary results

| Test-split metric | Hard correct | Hard shuffled | Soft correct | Soft shuffled |
|---|---:|---:|---:|---:|
| D4 endpoint accuracy, depth 8 | 0.8757 | 0.8913 | **1.0000** | 0.9990 |
| D4 endpoint accuracy, depth 64 | 0.4840 | 0.1955 | **0.9054** | 0.1466 |
| D4 endpoint accuracy, depth 128 | 0.3576 | 0.1401 | **0.5521** | 0.1361 |
| C8 endpoint accuracy, depth 64 | 0.3960 | 0.1401 | **0.7869** | 0.1489 |
| Random-family accuracy, depth 64 | 0.1800 | 0.1292 | **0.2796** | 0.1403 |
| Split-conditioned D4, depth 64 | 0.4880 | 0.1862 | **0.9157** | 0.1165 |
| Split-conditioned D4, depth 128 | 0.3464 | 0.1436 | **0.5342** | 0.1133 |
| Median endpoint/start norm, depth 2,048 | **1.00001** | 1.00000 | \(7.06\times10^{-19}\) | \(3.56\times10^{-8}\) |
| Composition substitution | 0.8636 | 0.8621 | 0.8822 | 0.8854 |
| Sequential/direct agreement | 0.5951 | 0.5915 | 0.6697 | 0.6725 |
| Median closure residual, lower is better | 1.1575 | 1.1714 | 0.8589 | 0.9228 |
| Recipient-native accuracy | 0.3333 | 0.3524 | 0.5853 | 0.5618 |
| Cross-context state-patch accuracy | 0.2189 | 0.2150 | 0.4429 | 0.3853 |

The gate decision was conjunctive and seed-based:

| Hypothesis family | Passed | What passed |
|---|---:|---|
| H1: stability and execution | 7/16 | Hard-QR integrity, depth-2,048 norm checks, and avoidance of soft contraction |
| H2: anonymous closure | 0/6 | Nothing |
| H3: cross-context causal semantics | 1/4 | The low wrong-state control only |
| **Total** | **8/26** | **No positive learned-semantic gate passed** |

Several hard-arm means exceeded their absolute thresholds, but the required
fraction of independent training seeds did not. For example, hard-correct D4
depth-64 accuracy averaged 0.4840 against a 0.25 mean threshold, yet only 6/12
seeds passed the per-seed threshold where 9/12 were required. At depth 8,
8/12 seeds passed where 9/12 were required. The hard model was sharply bimodal:
some seeds were near perfect at long depth while others remained near chance.
The preregistered seed-fraction rule correctly prevented a few strong runs from
hiding this unreliability.

## Stability was solved architecturally, not semantically

For `hard_correct`, the depth-2,048 endpoint/start norm ratio was 1.00001, the
minimum stepwise norm ratio was 1.00000, the P95 transient gain was 1.00009,
the P95 orthogonality defect was \(3.11\times10^{-7}\), and the minimum singular
value was 1.00000. Every hard seed had finite depth-2,048 trajectories.

These are integrity properties of the QR projection. They demonstrate that the
implementation maintained the promised orthogonal dynamics; they are not
evidence that training discovered an invariant metric, an exact group
representation, or meaningful operators.

The soft arm shows why norm stability still matters. `soft_correct` attained
0.9054 D4 accuracy at depth 64 and 0.5521 at depth 128, but its median
depth-2,048 norm ratio was approximately \(7.06\times10^{-19}\). The hard arm
avoided that collapse but was worse than soft by **0.4214** at D4 depth 64,
failing the frozen behavior-margin gate in 8 of 12 paired seeds. Exact
noncontraction alone did not make the optimization problem easier; in this
parameterization it made the useful solution markedly less reliable.

## Correct composition pressure improved behavior without producing closure

The hard-correct arm beat hard-shuffled on average at D4 depth 64 by 0.2886,
at D4 depth 128 by 0.2174, and at C8 depth 64 by 0.2559. This is evidence that
the correct anonymous target changed learned long-horizon behavior.

It is not evidence of a learned operator algebra. Correct and shuffled arms
were almost indistinguishable on the direct closure measurements:

- composition substitution: 0.8636 versus 0.8621;
- sequential/direct agreement: 0.5951 versus 0.5915;
- native two-step accuracy: 0.6927 versus 0.6960;
- closure residual: 1.1575 versus 1.1714.

All six H2 gates failed. In particular, high substitution accuracy was not
specific to correct composition, and the small residual advantage did not
approach the absolute residual threshold. The learned system found behaviorally
useful regularities, but the assay did not identify a faithful, directly
composable latent representation.

## Cross-context causal semantics did not materialize

For the hard-correct arm, recipient-native accuracy was 0.3333,
cross-context patch accuracy was 0.2189, the on-manifold wrong-state control was
0.1074, and the patch margin was only 0.1115. The wrong-state control passed,
but recipient-native execution, patch accuracy, and the required 0.4 margin all
failed. Correct versus shuffled hard training produced essentially no patch
advantage: 0.2189 versus 0.2150.

The soft model was better but still not a successful causal-semantic result:
its patch accuracy was 0.4429 and recipient-native accuracy 0.5853, both below
the frozen hard-arm targets used to define success. V0.3 therefore does not
support context-independent causal state meaning.

## Cross-seed transport remained codebook-compatible

Six affine maps were fitted on short, train-split D4 trajectories and evaluated
on test-split terminal actions. On D4, mean aligned state-patch accuracy was
0.8495, versus 0.1218 for shuffled-pair fitting and 0.1069 for a random map.
Operator-intertwining behavioral agreement was 0.8608. These are real alignment
signals.

However, a discrete decode-to-state-label followed by target re-embedding
reached **0.9088**, above the learned affine transport. The mean normalized
metric-compatibility defect was 0.5204. The transport result is therefore
consistent with aligning the known eight-state codebook and does not establish
shared within-codebook structure, richer latent semantics, or a coordinate-free
Neuralese.

## Post-hoc uncertainty does not change the gate decision

The completed 12-seed grid was summarized with 100,000 paired PCG64 bootstrap
resamples per metric and contrast. The analysis was explicitly labeled
`posthoc_descriptive_not_preregistered_not_a_frozen_gate`; its immutable input
SHA-256 was
`25f6a802b01c74ca1f90bc787a5d39899c92ac53800b6cbe1148a77fcf3185d8`.

Selected hard-correct minus hard-shuffled descriptive intervals were:

| Metric | Mean difference | 95% percentile interval |
|---|---:|---:|
| D4 depth 64 | +0.2886 | [0.1143, 0.4744] |
| D4 depth 128 | +0.2174 | [0.0791, 0.3688] |
| C8 depth 64 | +0.2559 | [0.0850, 0.4408] |
| Random family, depth 64 | +0.0508 | [0.0228, 0.0794] |
| Closure residual, lower is better | -0.0139 | [-0.0214, -0.0069] |
| Cross-context patch accuracy | +0.0039 | [-0.0212, 0.0277] |

The hard-correct minus soft-correct D4 depth-64 difference was -0.4214 with a
descriptive interval of [-0.6017, -0.2297]. These summaries clarify effect
size and seed variability. They do not retroactively alter thresholds, replace
the frozen seed-fraction rules, supply p-values, or rescue a failed primary.

## Exact replay

`hard_correct`, seed 300 was retrained and reevaluated under a separately
identified replay protocol. Metric JSON and the semantic arm record were
recursively exact; all state keys, dtypes, shapes, layouts, auxiliary values,
and tensor bytes matched; and the maximum parameter difference was 0.0. The
canonical checkpoint SHA-256 matched exactly:
`c978a00a11cad971657eaeb2df4be0acd2c1582362568810e8a617b4904e4eef`.
The canonical tensor-state digest was
`6aa9eacaabb325f6d2f0052c2305075490ff56424405bb2c3085c5cb7d7d006e`,
and the metric digest was
`2cae84505fa04e6908ad0ad82c39197e3b66af07ca75c662bdc75a93d26992eb`.

The raw `torch.save` file hashes differed because the replay carried a new
protocol identifier and protocol digest. That informational difference is not
a state mismatch; the declared provenance-normalized checkpoint and every
model tensor were exact.

## Strict split discipline and its limit

All 40,320 permutation maps were SHA-ranked into disjoint partitions: 24,192
train, 8,064 dev, and 8,064 test, with zero pairwise intersections. Every
nonempty contiguous subword action in every sampled training word was required
to hash to train. The exact cached sampler drew uniformly with replacement
from the valid joint coordinate/word support, rather than reporting fictional
rejections:

| Word length | Valid pairs / candidates | Support SHA-256 |
|---:|---:|---|
| 1 | 25,008 / 25,008 | `265cc1737ac80cf2afcfd2261a16b5d5d8770286511c3e1b6a7bac9bb3f326cb` |
| 2 | 32,120 / 50,016 | `c1074929f34aadefb48ad52de8882afe29e388e07cb6be66ed7b71d1d343be3b` |
| 3 | 37,936 / 100,032 | `7f5ab4a82c43e918f8485e0768cd6d1dd11c7fa37ac732ccf2d3644032ecae3d` |
| 4 | 45,680 / 200,064 | `7759e2320e3f3a8992f7d5654a1f1688d5cd15bd599dc09b0cdcccdce4ee5813` |

The primary consumed **49,152,000** directly conditioned training examples
with **zero** split violations. The separate split-conditioned final-action
assay additionally required each complete scored word action to hash to test;
only accepted examples were evaluated, with exact candidate and stream
receipts.

This is still not globally novel group-element evaluation. The broad depth
assay holds out primitive tables. The split-conditioned assay additionally
holds out the realized terminal finite-state action, but D4 group elements can
be regenerated algebraically from train actions. Neither assay proves novelty
of the abstract word-equivalence class.

## What Stage A supports

Stage A supports the following bounded claims:

- Sign-canonical QR maintained the promised fixed-\(G=I\) norm geometry to
  depth 2,048 on every primary seed.
- Correct anonymous-composition pressure improved average long-depth behavior
  relative to shuffled targets, despite substantial seed bimodality.
- Soft isometry pressure retained far better medium-depth execution while
  failing catastrophically on nonvanishing state norm at depth 2,048.
- Cross-seed affine alignment was far above shuffled and random maps, but did
  not beat the discrete decode--re-embed ceiling.
- The strict sampler removed the earlier path-level train/test leakage for all
  sampled contiguous training actions.
- The full result is deterministically reproducible for the audited replayed
  cell.

Stage A does **not** establish reliable hard-stable execution, anonymous latent
closure, exact hidden algebra, learned metric geometry, cross-context causal
semantics, transport beyond the eight-state codebook, globally novel group
elements, spontaneous Neuralese, a mechanism in language models, awareness,
or consciousness.

## Stage B sparse scaffold

V0.3 also implemented, but did not train in a primary, a sparse operator-
inference task over \(\mathbb F_5^4\), a 625-state product space. Each context
contains two anonymous affine primitives. The learner receives five
affine-independent demonstrations per primitive, a start state, and a word of
length at least two. Thus it sees only 10 of 1,250 possible primitive-table rows
(0.8%). It receives no dense table, intermediate target, context or operator
truth identifier, intervention mask, provenance label, or audit-only semantic
metadata. The exact visible-input oracle proves that the demonstrations suffice
to recover each affine map, while direct observed-row lookup cannot take the
first query step.

The frozen catalog contains 120 contexts per family: 72 train, 24 dev, and 24
test, corresponding to 144/48/48 primitive maps. Context and primitive
fingerprints are literally disjoint across splits.

| Family | Catalog SHA-256 | Same-context length-2--4 held-out collisions | Bounded witness SHA-256 |
|---|---|---:|---|
| Signed monomial | `77d8d985a569420e1bcfdd230a6d7b36e2496498028ece9ade77a61d67fa4334` | **0/96** | `4f53cda18c2baa0c0354bb5f9a3ecbe5ed12ab4d8e11ba873c2f11161202b945` |
| Shear | `87a40820648367a6c6fc6b03a51ce8335bed71e0dded4b3b39160563c92fa05a` | **86/96** | `e24de9b50a3b06c3d958f8b19d31216d81410cd9847d23eeb04a526be9af4190` |

The monomial family therefore permits one narrow novelty statement: none of
its 96 held-out primitives equals a word of length 2--4 formed from the two
slots of any single train context. The shear family does not permit that
statement: 43 dev and 43 test primitives have exact bounded witnesses.

Pooling all 144 train primitives across contexts destroys any unbounded
novelty claim for both families. All 96 held-out shear primitives are reachable
by depth 3 (95 at depth 2, one at depth 3; witness digest
`a8f57ab80177320b97ed9736deb1c85b523b74cf6f0efd947f40f22923bc52f3`).
All 96 held-out monomial primitives are also reachable by depth 3 (12 at depth
2, 84 at depth 3; witness digest
`d72912af618d48c6517bf4913d0099b49e7f22191a8a644a935e1d21a6c7da18`).
The audit does not claim to exhaust either generated group; positive witnesses
already suffice to reject unbounded operator novelty.

The signed-monomial family additionally admits an exact, numerically orthogonal
eight-dimensional torus action: four GF(5) attributes are encoded as four
cosine/sine pairs, while coordinate permutations, signs, and translations
compile to block permutations and planar rotations/reflections. The functional
transport module can audit within-codebook residuals, forward and reverse
cycles, operator transport, commuting squares, and component-specific
counterfactuals. These are tested scaffold capabilities, not trained Stage B
results.

## Recommended next block: sparse factor inference into an exact stable executor

The next block should be a **developmental Stage B bridge**, not another sealed
primary and not a larger repetition of hard QR.

The central experiment should ask:

> Can a model infer anonymous signed-monomial affine factors from five sparse
> demonstrations and compile them into the exact orthogonal torus action, using
> terminal composition loss, while preserving both long-horizon accuracy and
> causal specificity on held-out contexts?

This separates the two failures that Stage A entangled. Operator identification
is learned from sparse evidence; recurrent stability is supplied by a known
faithful executor. The model must still discover the episode-specific
permutation, sign, and translation factors, but it no longer has to find a
trainable point through a discontinuous generic QR map at the same time. It
also removes the complete-table shortcut.

The first developmental matrix should contain:

1. An exact finite-field inference/execution oracle and an exact factor-to-torus
   compiler as separate ceilings.
2. A terminal-only sparse factor-inference model compiled into the orthogonal
   torus executor, trained on monomial words of lengths 2--4.
3. Matched soft-recurrent and generic hard-QR learners receiving the identical
   sparse model-input projection.
4. Correct versus shuffled anonymous-composition targets for every learned
   architecture.
5. Shear as an explicitly out-of-representation diagnostic, never pooled with
   the monomial bounded-novelty claim.

Evaluation should make success conjunctive within each seed. A seed should
count as successful only if it simultaneously achieves held-out-context
terminal accuracy at extrapolated depths, retains nonvanishing bounded state
geometry at depth 2,048, passes exact factor/operator replacement tests, and
beats on-manifold wrong-state and norm-matched perturbation controls. Separate
stability and accuracy means would repeat the central ambiguity exposed by
Stage A.

Transport should be evaluated only after native execution is strong. The v0.3
functional assay should require transport to preserve within-codebook residual
variation, close bidirectional state and operator cycles, commute with held-out
operators, and produce the exact attribute-specific counterfactual while
leaving protected attributes invariant. It must beat centroid/decode--re-embed,
within-codebook shuffled, and random-map baselines. Codebook-level endpoint
accuracy alone should not count.

Finally, use dev coordinates to calibrate the model and joint gates, retain all
negative runs, and seal a new multi-seed test protocol before opening Stage B
test contexts. The monomial claim must remain explicitly bounded to the
same-context length-2--4 training support; the pooled-generator witnesses forbid
calling the held-out primitives globally novel.

If this bridge succeeds, the next relaxation is clear: replace the explicit
factor compiler with a learned continuous operator while preserving the same
joint behavioral, stability, causal, closure, and transport gates. If it fails,
the failure localizes the bottleneck to sparse operator inference rather than
recurrent norm control. Either outcome advances the research more than another
unmodified QR sweep.
