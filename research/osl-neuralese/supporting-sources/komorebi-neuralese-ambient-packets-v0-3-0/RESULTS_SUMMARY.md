# Ambient packet diagnostics v0.3.0

## Bottom line

The diagnostic assay passed all eight validation gates, but the two frozen learned checkpoints failed the mechanism and capability reference gates.

The result is diagnostic rather than confirmatory:

> Finite-horizon continuation packets detect substantial latent fragility before ordinary answer accuracy fails. The learned projective models remain highly accurate on structured depth-128 trajectories, yet their D4 packet membership, null-loop retention, and projective tangent stability deteriorate at greater depth.

This was a developmental, posthoc analysis of retrospectively selected frozen checkpoints. No full developmental claim is made.

## Scope

- Two terminal-only projective checkpoints, seeds 0 and 1
- Training depth: 1–4
- Evaluation families: D4, C8, mixed cycle, and arbitrary permutation pairs
- 256 deterministic contexts per family
- Trajectory length: 256
- Audited prefixes: 0, 64, 128, and 256
- D4 packet horizon: 8
- Exhaustive suffixes per packet: 511
- Inequalities per packet: 3,577
- Null-loop contexts: 16 per seed
- Null-loop repeats: 1, 2, 4, 8, 16, and 32

## Assay validation

All assay controls passed.

| Control | Exact result |
|---|---:|
| Exact global positive-gauge residual | 0.0 |
| Exact statewise residual | 0.0 |
| Minimum corresponding global residual | 0.45856338038680733 |
| Leakage-control residual | 0.04334531515287677 |
| Leakage reconstruction error | 0.0 |
| Detected negative coefficients | 1 |
| Exact-chart packet membership | 1.0 at every prefix |
| Exact-chart switched accuracy | 1.0 |
| Exact-chart switched gain range | 1.0–1.0 |
| Nonnormal-control individual radii | 0.5, 0.5 |
| Nonnormal-control period radius | 1.4571067811865475 |
| Nonnormal-control projective amplification | 33.97056274847713 |

These controls show that the implementation distinguishes global scale, state-dependent scale, sign failure, leakage, exact packet transport, and switched nonnormal amplification.

## Behavioral depth

All structured-family accuracies were 1.0 at depth 64. At depth 128 they remained between 0.98828125 and 1.0. Degradation appeared by depth 256.

| Family | Seed 0, depth 128 | Seed 0, depth 256 | Seed 1, depth 128 | Seed 1, depth 256 |
|---|---:|---:|---:|---:|
| D4 | 1.0 | 0.859375 | 0.99609375 | 0.80859375 |
| C8 | 1.0 | 0.80859375 | 0.9921875 | 0.66796875 |
| Mixed cycle | 0.9921875 | 0.9375 | 0.98828125 | 0.78125 |
| Random permutation pairs | 0.23828125 | 0.23046875 | 0.26953125 | 0.23046875 |

The structured capability gate failed because the minimum depth-256 result was 0.66796875, below the 0.70 per-seed threshold. Random-family performance was descriptive and had no success threshold.

## D4 continuation-packet erosion

Packet membership measures whether the current hidden state supports every D4 continuation through horizon 8, not merely whether its current decoded answer is correct.

| Seed and metric | Prefix 0 | Prefix 64 | Prefix 128 | Prefix 256 |
|---|---:|---:|---:|---:|
| Seed 0 membership | 0.8515625 | 1.0 | 0.93359375 | 0.484375 |
| Seed 0 median margin | 0.3938455 | 0.0710858 | 0.0427151 | -0.0010917 |
| Seed 1 membership | 1.0 | 1.0 | 0.91796875 | 0.42578125 |
| Seed 1 median margin | 0.3107085 | 0.0772172 | 0.0421729 | -0.0064129 |

At prefix 128, immediate D4 accuracy remained 1.0 and 0.99609375 while packet membership had already fallen. At prefix 256, membership fell to 0.484375 and 0.42578125, with negative median continuation margins. The exhaustive packet gate therefore failed with a minimum membership of 0.42578125.

## Null-loop retention

The table reports the worst result across both seeds and all three D4 relation loops at each repeat count.

| Repeats | Minimum membership | Minimum current accuracy | Minimum median margin | Maximum median projective angle |
|---:|---:|---:|---:|---:|
| 1 | 1.0 | 1.0 | 0.0797144 | 0.0168193 |
| 2 | 1.0 | 1.0 | 0.0778113 | 0.0311165 |
| 4 | 1.0 | 1.0 | 0.0686249 | 0.0632187 |
| 8 | 0.9375 | 1.0 | 0.0415472 | 0.1450111 |
| 16 | 0.6875 | 0.9375 | 0.0213693 | 0.2360027 |
| 32 | 0.375 | 0.625 | -0.0242526 | 0.5761276 |

Packet retention begins degrading while current answers are still exact. At 32 repeats, minimum retention was 0.375, causing the null-loop gate to fail. Each condition used only 16 contexts per seed, so these are developmental estimates with coarse resolution.

## Ambient and switched diagnostics

Every one of the 128 audited D4 episodes had future-observability rank 8 through depth 4, and the maximum observed null dimension was zero. This provides no evidence for a fixed nonzero additive nuisance subspace in these episodes.

Statewise positive-scale fitting improved over one global scale for every audited operator and family, but neither fit was close:

- Median global residuals ranged from 0.9620675 to 0.9984152.
- Median statewise residuals ranged from 0.8897902 to 0.9586642.
- The strict projectively valid fraction was 0.0 in every seed-family condition.

The statewise-gauge result therefore shows a comparative advantage, not projective closure. Most residual error is genuine off-ray leakage.

For switched D4 words:

- All 256 length-8 words were behaviorally correct in all 32 contexts per seed.
- Maximum projective amplification reached 540.3713 for seed 0 and 89.4546 for seed 1.
- Mixed words exceeded constant-word amplification in 0.96875 of contexts for both seeds.
- No switched application was undefined.
- The minimum pre-normalization norm across all audited families was 0.0103951.

The failure was therefore not caused by zero states or nonfinite execution. Large word-dependent angular amplification was already present while current answers remained perfect.

## Interpretation

The results support three bounded conclusions.

1. **Packet membership is a stricter early-warning measure than current accuracy.** Ordinary trajectories and null loops lose continuation robustness before decoded endpoints fail.
2. **Radial normalization did not eliminate angular or switched instability.** The remaining failure is associated with packet-boundary approach, relation-loop drift, off-ray leakage, and large projective tangent gain.
3. **The learned action is not an exact semantic-chart action multiplied by one global or state-dependent positive scalar.** More general packet-preserving ambient structure is required.

The exact-chart control proves that globally stable packet transport is achievable in the benchmark. The learned checkpoints did not recover that property.

## Komorebi interpretation of the ambient space

For a context chart \(B_c\), write

\[
A_{c,g}=B_c^{-1}M_{c,g}B_c=P_{c,g}\Lambda_{c,g}+E_{c,g}.
\]

Here \(P_{c,g}\) is the intended semantic permutation, \(\Lambda_{c,g}\) is positive statewise gauge, and \(E_{c,g}\) is ambient leakage. Quotienting radial scale removes only \(\Lambda\). The pilot shows that products of the residual \(E\) terms can rotate reachable rays, shrink continuation margins, and create nontrivial holonomy around words whose abstract action is the identity.

Because the finite future-observability operator has full rank, there is no evidence for a fixed additive subspace that can simply be discarded. The useful object is instead a state-dependent cone or packet in oriented projective space, together with the semigroup action on those packets.

## Next design

The next experiment should train fresh preregistered checkpoints with four coupled but separately ablated ingredients:

1. **Projective recurrence:** normalize each update in a learned positive metric so radial magnitude cannot carry task state or explode.
2. **Anonymous multiscale composition consistency:** require words with the same demonstrated action to agree projectively across several lengths without naming D4 relations.
3. **Continuation-margin preservation:** optimize packet margins on a construction suffix bank and evaluate only on a relation-grouped held-out bank.
4. **Delayed-return control:** use a local observability or Feshbach-style split to penalize perturbations that are temporarily weak at the decoder but return under later operator products.

The loss should not force every state to one canonical ray. A useful bridge is

\[
M_g = B P_g B^{-1} R_g,
\]

where the first factor supplies exact quotient transport and the learned residual \(R_g\) is permitted only insofar as it preserves the target continuation packet and keeps switched tangent amplification bounded.

The primary frozen target for that block should be

\[
\boxed{
\text{positive held-out packet margin}
+\text{bounded switched amplification}
+\text{structured depth-256 accuracy}
}
\]

for every preregistered seed.

## Claim boundary

This run supports the usefulness of finite, task-relative ambient packet diagnostics on these frozen models. It does not establish an infinite continuation quotient, an exact ambient representation, stable learned packet transport, spontaneous Neuralese, architecture-independent emergence, transfer to pretrained language models, awareness, or consciousness.
