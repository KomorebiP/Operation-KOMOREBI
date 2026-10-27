# Architectural provenance

The offline agent is an executable transfer of the Projector Calculus program into interactive local environments.

The runtime object is a finite posterior over pairs

```text
(resolution, operator program)
```

rather than one fixed transition map. The implemented operator vocabulary includes direct transfer, pairwise interaction, finite delay, power-law memory, exponential memory, phase-conditioned dynamics, and a nonlinear hybrid. Coarse and fine packet states provide a small resolution atlas. Exact replay supplies interventions when the local game is deterministic. Posterior disagreement and residual structure guide subsequent probes.

This release deliberately uses a finite, auditable operator library. It does not claim unrestricted synthesis over the full free operad, and it does not load the older synthetic proposal checkpoint at runtime.
