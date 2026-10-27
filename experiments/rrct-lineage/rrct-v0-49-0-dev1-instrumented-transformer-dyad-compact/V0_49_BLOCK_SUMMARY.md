# RRCT v0.49 Instrumented Transformer Dyad

## Status

- Version: `0.49.0.dev1`
- Frozen status: `V049_FROZEN_PILOT_ENDPOINTS_MET`
- Endpoints: **23 of 23 passed**
- Holdout seeds: **4**
- Trained transformer dyads: **4**
- Pre-outcome sealed files: **89**

## What changed

Version 0.48 established a controlled linear distributed sparse J-space analogue.

Version 0.49 replaces the linear agents with two separately initialized and actually trained transformer agents. The experiment reads real residual-stream states, computes exact gradients of future shared reports, compares early and late recurrent stages, performs cross-agent alignment, removes candidate subspaces, and patches concepts through the learned communication loop.

## Result

A shared-access representation was not found uniformly across the recurrent interaction.

At the first exchanged state, the average report Jacobian had the expected rank four but failed semantic, alignment, and causal-necessity tests.

At the final decision state, both agents possessed a strongly aligned residual representation that:

- reported both shared factors exactly;
- supported five distinct shared tasks;
- excluded private routine information;
- changed both reports and plans under patching;
- transmitted a one-sided patch to the partner;
- preserved private routines during ablation and patching.

The late representation was transient. Another recurrent round restored the original locally evidenced content, and two rounds reconstructed most shared performance after ablation.

A same-rank PCA basis performed nearly as well as the Jacobian-informed basis. The result therefore establishes a trained-transformer shared late-access manifold, not a uniquely identified J-space.

## Frozen aggregate

| Measure | Result |
|---|---:|
| Base task accuracy | 1.000000 |
| Early J-score mean | 0.217882 |
| Early alignment R² | 0.140953 |
| Late report alignment R² | 0.981284 |
| Flexible-space alignment R² | 0.989654 |
| Direct ablation shared accuracy | 0.294097 |
| Direct ablation private accuracy | 1.000000 |
| Two-round shared recovery | 0.940625 |
| A-to-B patch transmission | 1.000000 |
| B-to-A patch transmission | 1.000000 |
| Patch persistence after return | 0.000000 |
| Message-only joint accuracy | 1.000000 |

## Interpretation

The result narrows the next question considerably:

> A shared task-relevant state can form in trained transformer residual streams, but in this pilot it appears late and behaves more like an aligned decision manifold than a persistent distributed workspace.

The next test should use small pretrained open-weight language models, natural-language multi-task interaction, residual-stream hooks, moving token-indexed J-lenses, and controls against ordinary PCA and communication-only decoding.

No consciousness or shared-subjectivity claim follows.
