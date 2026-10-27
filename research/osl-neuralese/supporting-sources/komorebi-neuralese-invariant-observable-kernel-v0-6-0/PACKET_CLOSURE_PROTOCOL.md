# Packet Closure Protocol — v0.4.0

**Author:** Komorebi P.  
**Study class:** prospective developmental fresh-seed paired pilot  
**Parent diagnosis:** v0.3.0 ambient-packet and switched-projective audit

## Scientific question

Can exact control of the ambient operator geometry prevent the v0.3 angular
leakage, packet erosion, null-loop holonomy, and switched amplification without
destroying exact recurrent execution? Separately, does a construction-only
closure objective improve continuation safety beyond endpoint supervision?

The target is not a small raw hidden norm. Positive radial scale is a
behavioral gauge in this model class. The target is **finite-horizon projective
packet closure**: a recurrent state remains in a region supporting the correct
held-out continuations, the induced projective dynamics stay defined and
controlled under switching, and causal interventions retain their predicted
effects.

## Why the ambient space must be explicit

The eight learned state anchors in the v0.3 model generically span its entire
eight-dimensional hidden space. An exact semantic/ambient split there has

\[
\operatorname{rank}P=8,\qquad Q=I-P=0,
\]

so an exact delayed-return penalty is identically vacuous. Every official v0.4
arm instead uses

\[
H\cong\mathbb R^{12},\qquad
\operatorname{rank}P=8,\qquad
\operatorname{rank}Q=4.
\]

Let the eight learned anchors be the columns of
\(B\in\mathbb R^{12\times8}\). The official experiment fixes the Euclidean
gauge \(G=I\) and computes

\[
P=B(B^{\mathsf T}B)^{-1}B^{\mathsf T},
\qquad Q=I-P.
\]

Rank, idempotence, and self-adjointness are audited numerically. Here \(Q\) is
the exact orthogonal complement of the learned anchor plane. It is an ambient
complement, not an asserted observational nullspace and not presumed to be
unused.

## Fixed Euclidean gauge and hard-polar control

All four official arms share the same parameterization and identical
initialized tensors within each seed: twelve-dimensional anchors, homogeneous
decoder, bias-free table encoder, and fixed Euclidean metric coordinates. They
also share the accepted episode stream and projective state normalization.
Their learned anchors and weights may diverge after training. The arms differ
only along the two preregistered axes below.

### Raw Euclidean-normalized operator

The table encoder emits an unconstrained matrix \(A_g\in\mathbb R^{12\times
12}\), and recurrence applies

\[
F_g(h)=\frac{A_g h}{\lVert A_g h\rVert_2}.
\]

This removes radial explosion but does not constrain angular or switched
projective gain. The metric is exactly \(I\); no learned chart can absorb or
conceal instability.

### Hard \(O(12)\) polar operator

For the polar arms, the same encoder first emits the same kind of raw matrix.
With a full singular-value decomposition

\[
A_g=U_g\Sigma_gV_g^{\mathsf T},
\]

the recurrent operator is retracted to

\[
M_g=U_gV_g^{\mathsf T}\in O(12).
\]

No determinant correction is applied, so both connected components of
\(O(12)\) remain available. The recurrent matrix is a Euclidean isometry by
construction, up to audited floating-point error, even though the pre-polar
matrix remains learned and unconstrained. This is an architectural stability
control, not an exact task compiler or a hard-coded permutation
representation. The runner audits both the post-polar isometry and the
conditioning of the raw pre-polar parameterization. Fixing \(G=I\) retains
orthogonal-coordinate invariance, not arbitrary \(GL(12)\) reparameterization
invariance.

## Developmental failure that preceded the official panel

The original seed-71 development screen remains part of the audit lineage, but
it is not part of the official paired pilot. It contained eleven arms:

- fixed-Euclidean supervision;
- learned-metric supervision;
- a fixed-Euclidean full-objective diagnostic; and
- the eight learned-\(G\) cells of the \(2^3\) composition \(C\), packet-margin
  \(M\), and Feshbach-return \(R\) factorial, with conformal and switched-gain
  terms common to those cells.

That screen was a developmental failure of the tested learned-\(G\)
formulation, not a general impossibility result for learned metrics. It
motivated replacing the moving learned chart with the exact
raw-versus-polar architectural comparison. It also did not justify carrying
the packet-margin loss into the next block, so margin is omitted from the
official training objectives. The archived eleven-arm screen is not pooled
with the four-arm results and cannot satisfy any official pilot gate.

The official screen and pilot training budget freezes the exact completed
corrected-screen workload: 1,600 steps, batch 128, and 200 warmup steps. An
attempted larger-budget seed-71 calibration was interrupted before it produced
any result, so it was discarded and did not inform this choice. The use of a
developmental screen workload is recorded before the pilot and is one reason
the pilot is not called confirmatory. Every pilot arm runs for exactly the
frozen number of steps; there is no early stopping, best-checkpoint selection,
or per-seed budget change.

## Official paired \(2\times2\) panel

The primary experiment crosses operator architecture with objective. In the
table, **CR** means demonstration-aligned composition plus finite-path
complement-return regularization; it does not include packet margin, conformal
loss, or a learned switched-gain penalty.

| Arm | Operator architecture | Extra closure objective |
|---|---|---|
| `euclidean_supervised` | Raw, fixed \(G=I\) | None |
| `euclidean_cr` | Raw, fixed \(G=I\) | Composition + return |
| `polar_supervised` | Hard \(O(12)\) polar, fixed \(G=I\) | None |
| `polar_cr` | Hard \(O(12)\) polar, fixed \(G=I\) | Composition + return |

Every arm receives terminal D4 cross-entropy, construction-suffix endpoint
cross-entropy, and anchor-frame conditioning. The CR arms additionally receive:

1. **Demonstration-aligned multiscale composition.** Construction words are
   grouped by transition maps derived from the episode tables. No group name,
   family label, conjugating permutation, or named D4 relation is supplied,
   but the auxiliary path does receive the episode's
   canonical-generator-to-visible-slot alignment. This is an explicit
   scaffold, so the objective is not fully anonymous operator discovery. The
   loss compares composed latent action at scales one through four on the
   complete semantic anchor set.

2. **Finite-path complement return.** With scale-normalized operators, the
   exactly computed departure, ambient propagation, and return blocks are

   \[
   V_h=QM_hP,\qquad D_v=QM_vQ,\qquad U_g=PM_gQ.
   \]

   The optimized quantity is the direct energy of the scheduled three-block
   path

   \[
   U_gD_vV_h,
   \]

   divided by the ambient dimension. This is a finite Feshbach-style return
   diagnostic, not a full resolvent, exact closure constraint, or return
   certificate. A ratio to total product energy is recorded only as a
   diagnostic, because optimizing that ratio would permit manipulation of its
   denominator.

   The return-only schedule contains six deterministic construction-side paths:
   two each at lengths 2, 4, and 8. Every nonempty prefix and complete action of
   every scheduled path remains outside the reserved identity and \(r^2\)
   endpoint-action groups. These paths receive no endpoint label, packet margin,
   or held-out suffix content; they are used only inside the three-block return
   penalty. Consequently, terminal supervision, construction endpoint
   supervision, and composition scales stop at length four, but the CR arms do
   receive structural rollout exposure at length eight. The horizon-eight packet
   assay is an endpoint-action holdout, not a wholly length-unseen assay.

The paired design reports the polar-architecture effect, the CR-objective
effect, the CR effect within each architecture, and their interaction for each
metric whose four finite cells are all defined. A legitimately undefined
metric is marked unavailable without suppressing the other contrasts. A
failure of `polar_cr` to outperform its matched controls is retained rather
than explained away after inspection.

State- and operator-patch specificity are not used as cross-architecture
factorial estimands. State-patch rates are conditioned on arm-specific native-
correct eligible sets, so their risk sets are not common across cells. The raw
arms also cannot receive the hard-orthogonal relative-conjugacy operator
control, so an operator-specificity contrast would confound architecture with
control definition. Per-arm intervention outcomes remain visible, and the
registered causal-specificity gates apply to `polar_cr`.

## Strict endpoint and audit firewall

Training uses only D4 episodes of lengths one through four. For every proposed
terminal episode, the complete induced canonical action is computed before the
episode is admitted. Proposals whose endpoint action is either

\[
e \quad\text{or}\quad r^2
\]

are rejected and deterministically resampled. Accepted, rejected, identity,
and \(r^2\) counts and proposal-stream digests must close exactly and must
match across paired arms.

The construction-only auxiliary bank contains exactly 20 nonempty words
through horizon four, all outside the two reserved endpoint-action groups.
Training code receives that construction bank and its digest only. This is an
endpoint firewall: a recurrent trajectory may internally pass through the same
abstract action, but no loss-bearing terminal or construction endpoint belongs
to either reserved group. Every checkpoint and the pre-evaluation seal must
match the canonical construction word list and digest exactly.

Only after every available checkpoint has been serialized and hashed is the
evaluation bank materialized. It contains the empty identity continuation and
all 170 nonempty binary words through length eight whose complete D4 action is
identity or \(r^2\). The empty continuation makes correct decoding of the
captured prefix itself part of packet membership. The checkpoint contains
neither those words nor evaluation-bank content.

The state-intervention, operator-intervention, operator-control, ambient, and
switched-word banks are also materialized only after the checkpoint seal. Each
bank carries a deterministic receipt and contract fixing its family, canonical
conjugated action, context count, depth, tensor geometry, targets,
intermediates, and visible-slot map. Every evaluation result
binds the source digest, preregistration-contract hash, checkpoint-seal hash,
and evaluation-bank hash. This ordering prevents evaluation cases from entering
training artifacts while still allowing exact replay and integrity checks.

## Primary closure and secondary transfer

The primary scientific target is D4 closure. Held-out packet membership,
margin, null closure, switched-word behavior, and the deep accuracy
curve are evaluated on the firewalled D4 problem.

C8 and mixed-cycle episodes are never used for training. Their deep curves are
reported separately as **zero-shot cross-family transfer**. They are not
combined with D4 into a minimum-family primary endpoint, and failure on either
secondary family does not by itself negate a D4 packet-closure result.

For the fresh-seed pilot, the primary `polar_cr` D4 accuracy targets are

\[
0.98\text{ at depth }128,\qquad
0.90\text{ at depth }256,\qquad
0.75\text{ at depth }512.
\]

The same thresholds are displayed for C8 and mixed-cycle transfer, but their
status remains secondary and descriptive.

## Exact ambient-complement causality

Ambient energy is not evidence of ambient computation. For each D4, C8, and
mixed-cycle causal batch, the runner compares:

1. the native rollout;
2. confinement to \(P\) after every recurrent step;
3. one-time removal of \(Qh\) at the midpoint, followed by native continuation;
4. a deterministic random rank-four projector ablation at the same midpoint.

The random projector is conditioned only on the native midpoint state and its
\(Q\)-energy; behavioral outcomes do not enter its construction. The ideal
float64 construction has rank four and geometry/energy-match error at most
\(10^{-8}\). The assay separately measures the exact float32-cast projectors and
the two removed vectors actually used before normalization: applied \(P\),
\(Q\), and random-projector ranks must remain 8, 4, and 4, with projector and
removed-energy-match error at most \(10^{-6}\). Specific ambient attribution
also requires every native and intervened rollout to remain finite and defined,
then requires a native-accuracy drop of
at least 0.05 after \(Q\) removal and an excess drop of at least 0.05 over the
matched random control.

This attribution is deliberately separate from the closure claim. A finding
that \(Q\) is unused, or no more important than an energy-matched random
subspace, is scientifically meaningful and does not invalidate an otherwise
successful projective-closure result.

Ambient attribution is eligible only when the model's native accuracy on that
causal bank is at least 0.75. Below that floor, a change under ablation cannot be
cleanly attributed to loss of a successfully used mechanism. The report
therefore separates breakage among natively correct cases from correction among
natively wrong cases instead of compressing both transitions into a single
accuracy difference.

## Hardened state and operator interventions

State transplantation inserts a donor midpoint state into a matched recipient
trajectory and tests the exact donor-implied continuation. Operator replacement
likewise tests the exact alternate-operator continuation. Both assays require
the unedited rollout to be correct on the same example, require original and
counterfactual targets to differ, and score the intervention conditionally on
those eligible cases. Every relevant native, patch, and control output must be
finite. State transplantation is compared with
two distinct controls: an exactly norm- and recipient-angle-matched unit-sphere
state, and a wrong but reachable state from the same prefix context. Degenerate
angle cases are counted explicitly rather than silently discarded.

Operator replacement substitutes the independently emitted hard-polar operator
for an alternate visible table. Its geometric control applies an orthogonal
conjugation to the relative replacement \(A O^{\mathsf T}\), preserving relative
spectrum, determinant component, and operator chord while breaking the intended
semantic replacement whenever that construction is noncentral. A second control
uses an independently emitted operator from another episode context. Its
base visible slot alternates deterministically by frozen bank-row index. If
that slot's concrete permutation table exactly equals either the original or
the main alternate table, the other slot is used; a row with no admissible
slot fails closed. This exclusion consults table equality but never a learned
code distance or behavioral outcome. The post-seal bank contract requires
zero selected collisions against both primary tables. The conjugacy control
matches operator geometry, not the induced hidden-state displacement, and the
cross-context control lies on the encoder image but is not distance matched.
Those limitations are reported.

In every profile the state transplant occurs after the frozen midpoint split
(4 of 8, 16 of 32, or 32 of 64 operators). Operator replacement occurs at
zero-indexed step 3—the fourth operator—in every profile.

For the primary hard-polar arm, native accuracy and eligible-case fraction must
each be at least 0.90, target distinctness must be 1.0, and conditional state and
operator replacement success must each be at least 0.90. Both state controls
and both operator controls must each remain at or below 0.40; all four controls
enter the registered causal-specificity gates.

## Descriptive CR-objective effect

The three-seed paired panel reports whether adding CR changes the worst packet
membership, tenth-percentile continuation margin, and worst null closure
over the complete registered grid. The three preregistered direction checks
are specifically the hard-polar-stratum simple effect
`polar_cr - polar_supervised`; they are not the CR main effect averaged across
raw and polar cells. The complete paired table also reports the raw-stratum
simple effect, both factor main effects, and the interaction descriptively.
The preregistered developmental direction checks are:

1. the mean tenth-percentile-margin difference is positive and at least two of
   three seedwise differences are positive;
2. the mean packet-membership difference is nonnegative; and
3. the mean null-closure difference is nonnegative. Here null closure is the
   minimum of baseline packet membership, conditional retention of baseline
   members, and absolute post-loop membership over every registered relation and
   repeat. This prevents membership turnover from masquerading as retention.

These hard-polar-stratum comparisons are descriptive paired sign/direction
rules at \(n=3\), not confidence
intervals, hypothesis tests, or population-level evidence. Their status is kept
separate from the primary `polar_cr` closure result because the chosen primary
cell can succeed even if CR adds no benefit over `polar_supervised`.

## Seed firewall

- Seed 53 is engineering smoke only.
- Seed 71 is development only, including the archived eleven-arm learned-\(G\)
  failure screen and the official-panel implementation screen.
- Seeds 101, 211, and 307 have no registered model-training or evaluation
  outcomes inspected before the paired pilot. Synthetic unit fixtures may use
  profile keys but do not train or evaluate those registered runs.
- Any later confirmatory seeds must be selected and frozen after this
  developmental package; they cannot be retroactively labeled confirmatory.

There is no seed retry, seed replacement, held-out-based early stopping, or
pilot-weight adjustment.

## Frozen training configuration

All profiles use twelve hidden dimensions, D4 terminal and endpoint-supervised
train lengths one through four,
AdamW, learning rate \(2\times10^{-3}\), weight decay \(10^{-6}\), gradient
clip 5, construction horizon four, one construction context, four construction
words per step, episode-seed base 40,000, and 11 trajectory records. The fixed
CR return-only rollout depths are 2, 4, and 8. The fixed loss coefficients are:

Every registered profile is sealed to CPU execution, one PyTorch intra-op
thread, and deterministic algorithms. A non-CPU `--device` is rejected before
any registered seed is consumed.

The official pilot additionally requires the exact frozen runtime receipt:
CPython 3.12.13, PyTorch 2.14.0+cu130, NumPy 2.3.5, the recorded Linux/glibc
platform string, and the recorded PyTorch and NumPy numerical-build hashes.
Later replays on other environments may be useful diagnostics but are not
promised to be byte-identical and cannot become replacement evidence.

| Component | Weight | Official use |
|---|---:|---|
| Terminal endpoint cross-entropy | 1.00 | All arms |
| Construction endpoint cross-entropy | 0.25 | All arms |
| Anchor conditioning | 0.01 | All arms |
| Demonstration-aligned composition | 0.10 | CR arms only |
| Packet margin | 0.10 | Inactive compatibility field |
| Conformal defect | 0.00 | Inactive compatibility field |
| Switched-gain hinge | 0.00 | Inactive compatibility field |
| Finite-path complement return | 0.05 | CR arms only |

The serialized metric-learning-rate scale remains 0.10 for schema continuity,
but every official metric parameter is zeroed and frozen. The retained margin
target 0.10, margin temperature 0.05, and switched-gain target 2.0 are likewise
diagnostic/configuration fields, not active official losses.

| Profile | Seeds | Steps | Batch | Warmup | Deep examples / intervention chunk | Packet examples | Packet prefixes | Deep depths |
|---|---|---:|---:|---:|---|---:|---|---|
| smoke | 53 | 20 | 32 | 5 | 32 / 32 | 16 | 0, 64, 128, 256 | 32, 64 |
| screen | 71 | 1600 | 128 | 200 | 128 / 128 | 64 | 0, 64, 128, 256 | 64, 128, 256 |
| pilot | 101, 211, 307 | 1600 | 128 | 200 | 512 / 256 | 128 | 0, 64, 128, 256 | 128, 256, 512 |

| Profile | Null examples / repeats | Switched word bank / contexts | Feshbach contexts | Causal interventions | Ambient causality | Eval-seed base |
|---|---|---|---:|---|---|---:|
| smoke | 8 / 1, 2 | 16 words at length 4 / 2 | 4 | 32 at length 8 | 32 at length 8 | 510,000 |
| screen | 32 / 1, 4, 8, 16 | 64 words at length 8 / 8 | 16 | 128 at length 32 | 128 at length 32 | 520,000 |
| pilot | 64 / 1, 2, 4, 8, 16, 32 | all 256 words at length 8 / 16 | 32 | 512 at length 64 | 512 at length 64 | 530,000 |

Smoke and screen are engineering/developmental profiles only. Screen and pilot
use the same training workload; the pilot changes only the untouched seeds and
the evaluation workload. The pilot is run once after the code, contract,
source digest, weights, gates, and seeds are sealed.

The official invocation is restricted to the canonical
`results/packet_closure_pilot/` path and refuses any pre-existing output directory.
After retention, a second official invocation therefore fails closed. A run at
another path must opt into `--replay`; replay results are labeled
`non_evidentiary_pilot_replay`, do not receive prospective pilot gate
adjudication, and cannot be selected as replacement fresh-seed evidence.

## Outcome hierarchy

1. **Execution integrity:** paired initialization and accepted/proposal streams,
   endpoint rejection, bank separation, finite gradients, and checkpoint/source
   receipts are exact. Source-tree and contract hashes must equal their startup
   values before checkpoint sealing and again after evaluation.
2. **Assay calibration:** construction/held-out split, post-seal materialization,
   ideal rank-eight/rank-four projectors plus their applied float32 ranks,
   hard-polar isometry, deterministic switched banks, and energy/rank-matched
   ambient controls behave within their separately registered tolerances.
3. **Primary mechanism (`polar_cr`, D4):** held-out membership is at least 0.90
   at every audited prefix and in both reserved groups; the tenth-percentile
   margin is positive; null-bank baseline membership, conditional retention,
   and post-loop membership are each at least 0.90 through 32 repeats;
   exhaustive length-eight switched gain lies in
   \([0.999,1.001]\), all updates are defined, and switched-word accuracy is at
   least 0.95.
4. **Primary capability (`polar_cr`, D4):** the frozen depth-128/256/512 curve
   is fully finite and meets the 0.98/0.90/0.75 targets.
5. **Attribution:** all four paired cells are present; on natively correct cases
   with distinct counterfactual targets and finite outputs, causal state and
   operator patches reach at least 0.90 while both registered controls remain
   at or below 0.40.
6. **Secondary transfer:** C8 and mixed-cycle depth curves are reported apart
   from the primary D4 result.
7. **Ambient attribution:** exact \(Q\) ablation is compared with the
   rank/energy-matched random control and reported separately from closure.
8. **Objective effect:** the paired three-seed hard-polar-stratum
   `polar_cr - polar_supervised` direction
   checks are reported separately from the success of the selected `polar_cr`
   cell.

Mechanism or capability gate failures are preserved as scientific results.
Integrity or assay-calibration failure invalidates interpretation. Secondary
transfer, ambient-attribution, and objective-effect status do not enter the full
developmental closure claim. The report exposes execution, assay, primary
mechanism, primary capability, causal attribution, secondary transfer, ambient
attribution, and objective-effect statuses independently; no omnibus label is
allowed to conceal a failed component.

## Claim boundary

Even a complete pass would establish only that an explicit, small,
table-conditioned recurrent architecture can be trained for finite-depth D4
projective packet closure in a fixed Euclidean gauge, and that the effects of
hard isometry and construction/return pressure can be separated in a paired
design. It would not establish spontaneous Neuralese, infinite-horizon or
universal stability, an exact hidden group representation, architecture-
independent emergence, the same mechanism in a pretrained language model, or
awareness or consciousness.
