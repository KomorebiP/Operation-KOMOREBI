# RRCT v0.52 dev3 Limited Nested-Workspace Pilot

## Result

- Status: `V052_LIMITED_NESTED_WORKSPACE_ENDPOINTS_MET`
- Endpoints: **18 / 18 passed**
- Holdout seeds: `392208712, 743448271, 793186123, 445719542`
- Exact deterministic replay: passed
- Flat full-access baseline: 100%

## Strongest justified conclusion

Within a finite two-level neural pilot, learned local bottlenecks can act as effective agents for a learned global bottleneck. Cutting or patching each level produces the predicted upward and downward causal effects, while unrelated private routines remain intact.

## What is new relative to the prior shared-workspace line

The experiment tests recursive composition rather than one workspace shared by peer agents:

```text
leaf processes → local workspaces → global workspace → top-down leaf control
```

The global workspace is not merely a decoder. It is separately necessary, and its output must be broadcast back down for correct leaf behavior.

## Boundary

A flat controller also solves. The hierarchy is therefore an existence proof and mechanistic decomposition, not a proof of unique optimality or a direct model of the brain.
