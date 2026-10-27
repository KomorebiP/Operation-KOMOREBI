# PR-LASM integration boundary

Version 0.3.0 replaces the posterior-like ranking used in 0.2.0 with an actual
finite Bayesian PR-LASM inference layer.

## Implemented

- exact spatial, color, Fourier, Haar, polyphase, and object-relational atlases
- exact reconstruction checks for invertible atlases
- deterministic macro, meso, and micro signal states
- typed program-family portfolio
- hierarchical Bayesian family and route priors
- Bayesian ridge reliability calibration with predictive variance
- program, family, atlas, resolution, and output posteriors
- posterior entropy and disagreement
- residual classification and typed residual refinement
- posterior-diverse two-attempt selection

## Intentionally omitted for ARC-AGI-2

- persistent cross-task episodic memory
- state-action transition graphs
- replay probes
- active environment exploration
- action planning

Those mechanisms belong to the interactive PR-LASM and are relevant to
ARC-AGI-3. Importing them into a static input-output benchmark would add code
without adding a valid source of evidence.

## Reused mathematical contract

The broader PR-LASM repository is not vendored. The ARC implementation retains
its central separation:

```text
exact multi-atlas archive
+ compressed statistical states
+ typed operator posterior
+ explicit residual refinement
+ exact synthesis contract
```

The standalone entry remains small enough for offline Kaggle execution and
independent MIT licensing.
