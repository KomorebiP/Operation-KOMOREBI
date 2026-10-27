# V0.3 research specification

## Stage A question

Can a recurrent operator model with exact, hard noncontractive dynamics retain
the learned execution, anonymous-composition, and causal-patching performance
of a soft isometry-penalty model while remaining stable at much greater depth?

Stage A is a controlled table-execution assay. Every episode supplies two full
eight-state permutation tables, a start state, and an anonymous operator word.
The recurrent channel is explicitly an 8x8 matrix. An exact solution is
available by transposing each row-coded table and representing the state as a
one-hot vector. This design tests whether training reaches a useful solution
under a strong inductive bias; it does not test spontaneous operator discovery.

## Hard operator mechanism

The primary hard arm maps the table encoder's raw matrix (R(T)) to a
sign-canonical orthogonal QR factor:

\[
Q(T)=\operatorname{canonicalQR}(R(T)), \qquad Q(T)^\top Q(T)\approx I.
\]

Its recurrent update is

\[
h_{t+1}=Q(T_t)h_t.
\]

The primary uses fixed (G=I), not a learned invariant metric. Matrix
exponential, Cayley, polar, and learned-diagonal-metric variants exist as
developmental ablations but were not primary arms.

## Primary treatments

The sealed 4 x 12 grid used seeds 300--311 and four whole-package treatments:

| Arm | Recurrent constraint | Composition target |
|---|---|---|
| `hard_correct` | Sign-canonical QR, fixed (G=I) | Correct anonymous composite |
| `hard_shuffled` | Sign-canonical QR, fixed (G=I) | Matched shuffled composite |
| `soft_correct` | Learned full SPD metric, soft isometry penalty | Correct anonymous composite |
| `soft_shuffled` | Learned full SPD metric, soft isometry penalty | Matched shuffled composite |

Hard and soft models receive bit-identical raw initialization tensors, but the
QR projection changes the effective operators and adds different computation.
Their contrast is therefore not a one-factor causal estimate and is not a
formal compute-matched noninferiority design.

## Split discipline

All 40,320 permutation maps are SHA-ranked into disjoint train/dev/test
partitions of 24,192/8,064/8,064 maps. For each sampled training word of length
1--4, every nonempty contiguous subword action must hash to train. The exact
direct sampler draws uniformly with replacement from valid joint
coordinate/word supports:

| Length | Valid pairs / candidates | Support SHA-256 |
|---:|---:|---|
| 1 | 25,008 / 25,008 | `265cc1737ac80cf2afcfd2261a16b5d5d8770286511c3e1b6a7bac9bb3f326cb` |
| 2 | 32,120 / 50,016 | `c1074929f34aadefb48ad52de8882afe29e388e07cb6be66ed7b71d1d343be3b` |
| 3 | 37,936 / 100,032 | `7f5ab4a82c43e918f8485e0768cd6d1dd11c7fa37ac732ccf2d3644032ecae3d` |
| 4 | 45,680 / 200,064 | `7759e2320e3f3a8992f7d5654a1f1688d5cd15bd599dc09b0cdcccdce4ee5813` |

The primary consumed 49,152,000 directly conditioned examples with zero split
violations. Broad deep-stability metrics hold out primitive tables. A separate
split-conditioned assay also requires the complete finite action of each scored
word to hash to test.

These restrictions do not establish globally novel abstract group elements.
The finite D4 action set is algebraically regenerable from training actions.

## Frozen hypothesis families

### H1: stability and execution

The hard arm was required to preserve finite nonvanishing trajectories through
depth 2,048, satisfy orthogonality and minimum-singular-value checks, execute
D4/C8/random families across seeds, retain performance on split-conditioned
terminal actions, and remain within a frozen behavioral margin of the soft arm.

### H2: anonymous closure

Correct composition pressure was required to produce high substitution and
sequential/direct agreement, low intrinsic closure residual, high native
two-step accuracy, and seed-consistent advantages over shuffled targets.

### H3: cross-context causal state semantics

Recipient-native execution and donor-state patches had to exceed absolute
accuracy and margin thresholds while the on-manifold wrong-state control
remained low.

All 26 gate definitions are frozen in
`protocols/V0_3_STAGE_A_PRIMARY.json` (SHA-256
`ecd48865c7327b39b5d0b2679f2e6fc3e9509a01bce343cfe94b9b237482acaf`).

## Stage A outcome

The conjunctive primary failed with 8/26 gates passing:

- H1: 7/16 passed. All exact QR integrity checks passed, including norm
  preservation through depth 2,048. All positive learned execution criteria
  failed their required seed fraction, and the hard-versus-soft behavior
  margin failed.
- H2: 0/6 passed. Correct composition pressure improved hard-arm depth-64
  behavior on average, but did not produce reliable direct latent closure.
- H3: 1/4 passed. The wrong-state control stayed low; recipient-native,
  cross-context patch, and patch-margin gates failed.

Hard correct achieved mean D4 accuracy 0.4840 at depth 64 and 0.3576 at depth
128, versus 0.9054 and 0.5521 for soft correct. At depth 2,048, the hard norm
ratio was 1.00001 while the soft-correct ratio was approximately
\(7.06\times10^{-19}\). Exact stability and medium-depth trainability were not
jointly achieved.

## Calibration and primary status

Qualification used development coordinates only. A disclosed 4,000-step
attempt failed its short-horizon criterion; subsequent 8,000-step calibration
and architecture scans selected fixed-identity hard QR with composition weight
0.3. The final four-seed qualification passed 8/8 development gates. These
steps calibrated the engineering protocol and are not confirmatory evidence.

The primary seal records that test coordinates were unopened when the protocol
was frozen. The run was later resumed in deterministic bounded chunks after an
execution-supervisor interruption; all existing outputs were validated, and
the final receipt records 48/48 cells and six transport pairs.

The primary processed 49,152,000 directly conditioned examples with zero
split violations and passed the independent exact oracle. Recovery provenance
is recorded at
`results/v0.3.0/stage_a_primary_v3/RECOVERY_EVENTS.json`; the authoritative
scientific decision is in
`results/v0.3.0/stage_a_primary_v3/GATES.json`.

## Statistical unit

The independent training seed is the primary unit (n=12). Evaluation examples
reduce within-model measurement noise but do not increase the model-level
sample size. Six disjoint seed pairs form the Stage A transport sample.
Post-hoc 100,000-resample paired-bootstrap intervals are descriptive only and
do not change frozen gate decisions.

## Stage B developmental scaffold

The sparse GF(5)^4 task removes dense primitive tables and length-1 terminal
targets. Five affine-frame demonstrations uniquely identify each anonymous
primitive; model inputs exclude context IDs, operator truth, masks, and targets.
The monomial family is the bounded representability control, while shear is an
out-of-representation diagnostic. The functional transport module tests
within-codebook residual structure, bidirectional cycles, operator transport,
commuting squares, and component-specific counterfactuals.

No trained Stage B primary was run in v0.3. Its code and exact audits establish
benchmark integrity only.

## Next-block specification

V0.3 rejects the hypothesis that the tested QR treatment jointly solves
stability and trainability. The canonical next block should separate the two
problems with a **developmental sparse factor-inference bridge**:

1. Give the learner only five affine-frame demonstrations per anonymous
   primitive, a start state, and a length-2--4 word.
2. Train it to infer signed-monomial permutation, sign, and translation factors
   from terminal composition loss.
3. Compile inferred factors into the exact eight-dimensional orthogonal torus
   action. Stability is verified separately; factor identification is learned.
4. Compare against the exact finite-field oracle, exact factor compiler,
   matched soft recurrence, and generic hard QR; retain correct/shuffled
   composition targets.
5. Require held-out-context execution, depth-2,048 stability, causal factor
   edits, and specificity to pass jointly within each seed.
6. Run transport only after native execution is strong, requiring
   residual-within-codebook prediction, cycles, commuting squares, and
   protected-attribute invariance against centroid, shuffle, random-map, and
   full-state decode/re-embed baselines.

This remains developmental. A later Stage B primary must be sealed before test
contexts open. Monomial supports only the bounded same-context length-2--4
claim; shear remains an out-of-representation diagnostic, and pooled-generator
witnesses forbid an unbounded novelty claim.

A small development-only Stage A sidecar may compare smooth orthogonal
parameterizations and staged soft-to-hard optimization from matched *effective*
initial operators with compute accounting. It diagnoses the QR basin failure;
it is not the flagship.
