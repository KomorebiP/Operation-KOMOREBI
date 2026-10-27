# G1-D1 frozen-checkpoint diagnostic protocol

## Fixed source and integrity boundary

The source is exactly the canonical G1 v0.1.1 pilot at seed 711001. The bundled
run has 2,000 completed steps, config digest
`872349b749392924dab4b70eefe516751667d8d74ed91f73bb325b8277ce2a41`,
checkpoint SHA256
`ea0f9506334f6958c43e73596eb7404f785abd92be7668024b0c01efac1eae75`,
and source claim `G1_ENGINEERING_PASS`. D1 does not search seeds, checkpoints,
hyperparameters, splits, thresholds, or probe specifications.

Before analysis, the diagnostic validates the intact upstream package and the
complete cross-file run. It loads the checkpoint with `weights_only=True`,
retains only the 18 dense FP32 workspace tensors, and applies them strictly to a
freshly reconstructed frozen model. Optimizer, scaler, and RNG states are never
restored. Model and input hashes are checked again after intervention work.

## Fixed sampling and feature bank

Each compute problem is represented once rather than once per query. D1 uses a
seeded, stratified training subset of 80 problems per final state (480 total),
using the fixed sampler seed `711001 + 38117`,
all 240 validation problems, all 480 IID test problems, and all 480 depth-OOD
test problems. The sampled example identities are recorded so the subset can be
replayed exactly.

For both recurrent and compute-matched no-feedback execution, D1 captures
workspace states `z0` through `z4`, decoded answer-space injections
`decode(z0)` through `decode(z4)`, the source activation, the consumed
feedback's distance from the initial activation, and gate/update diagnostics.
No-feedback distances are zero by construction and are labeled accordingly.
The decoded injection is analyzed explicitly
because a signal can survive in the 96-dimensional state yet be discarded or
collapsed by the 896-dimensional output bridge.

## Probe and control contract

Every deterministic ridge probe uses the fixed training subset, chooses its
regularization on the fixed validation split, and reports IID and depth-OOD
results. The complete regularization-selection procedure is rerun for each of
127 seeded train-label permutations. All primary and secondary probes use 127
permutations. Nearest-centroid and five-nearest-neighbor results are reported as
nonparametric checks, not replacements for the registered ridge test.

The final-state probe families cover:

- source activation
- recurrent and no-feedback workspace states at each available step
- recurrent decoded injections at every step and the final no-feedback decoded
  injection

A structured raw-metadata final-state baseline one-hot encodes the start state,
transition-at-start, all six entries of the transition map, and application
depth from 1 through 10.
This provides method-matched baselines for signal extractable by the declared
ridge, centroid, and neighbor procedures from literal prompt fields; it is not
an exhaustive control for every nonlinear computation over those fields.
Secondary probes predict
`start_state` and `transition_at_start` from the source, `z0`, and `z4`; these
make common literal-copy or one-step heuristics visible rather than silently
crediting them as multi-step computation.

The primary signal label is based on IID performance and its lift over the
structured raw-metadata baseline. Depth-OOD performance is always reported
separately as transfer evidence: OOD success cannot turn a weak IID result into
strong detection, and OOD failure does not by itself show that the state lacks
IID information.

## Frozen interventions and replay

On both IID and depth-OOD queries, D1 evaluates:

- recurrent own states `z0` through `z4`
- compute-matched no-feedback `z4`
- a same-final-state donor and an answer-incompatible donor
- the mean training state and mean-centered own `z4`
- literal zero injection
- own `z4` through the leading rank-one component of the output projection
- own `z4` through the complementary residual projection

Projection replacements are temporary and the original tensor is restored
exactly. For every condition, D1 retains the full registered-label logits,
receiver-target log probability and family margin, top-one answer, and donor
target where defined. Recurrent, no-feedback, and literal-zero top-one outputs
are replayed against the saved pilot predictions.

For each incompatible donor query, semantic transport is the paired
difference-in-differences

\[
\bigl(\ell_{donor}-\ell_{receiver}\bigr)_{incompatible\ donor}
-
\bigl(\ell_{donor}-\ell_{receiver}\bigr)_{own\ z4}.
\]

Positive values mean that swapping the state shifted relative preference toward
the donor’s semantic answer. Means and 99% intervals are clustered by the
underlying compute-problem counter, preserving the dependence among its three
queries. This paired quantity is the transport diagnostic; a donor-versus-
receiver accuracy gap alone is not treated as transport evidence.

## Conservative interpretation boundary

| Registered observation | Permitted localization language |
| --- | --- |
| Source shows IID signal above metadata with OOD transfer, while `z0` does not | Consistent with initializer-stage signal loss under the tested probes |
| `z0` shows IID signal above metadata with OOD transfer, while `z4` does not | Consistent with recurrent-state signal erosion under this checkpoint |
| `z4` carries strong IID signal but decoded injection does not, alongside rank-one dominance | Consistent with an output-projection bottleneck localization |
| State and decoded injection carry signal but paired donor transport is weak | Consistent with downstream query-bridge nonuse; not proof of causal irrelevance |
| Neither final state nor decoded injection passes the registered detection rule | No robust final-state signal detected; not evidence that all such information is absent |
| Recurrent and no-feedback trajectories and answers nearly coincide | Feedback has little measured effect in this run; not a general architectural claim |

Rank-one/residual interventions, literal controls, IID lift, and OOD transfer
are reported alongside any localization; no single statistic is elevated into
a causal conclusion. All outputs carry `claim: DIAGNOSTIC_ONLY`. The registered
G1 result remains a scientific failure regardless of D1 outcomes.
