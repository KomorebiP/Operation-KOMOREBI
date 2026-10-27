# RRCT v0.44 Continuation Capsule

## Model

`TransformationalSelfContinuityController` maintains a lineage anchor containing a causal boundary, intervention anchors, autobiographical memory anchors, commitments, calibration state, and an intentionally weak snapshot. It estimates source, sensory, and memory transports from paired probes. Causal-boundary preservation and autobiographical compatibility are conjunctive. The controller can refine evidence, represent forks, quarantine unresolved cases, transport memory into planning, and register a selected successor as the next predecessor.

## Frozen configuration

```json
{
  "accept_threshold": 0.45,
  "causal_residual_scale": 0.18,
  "fresh_discovery_cost": 24,
  "future_weight": 1.5,
  "maximum_route_strength": 1.5,
  "memory_residual_scale": 0.22,
  "minimum_causal_rank_fraction": 0.9,
  "minimum_memory_heldout_fraction": 0.2,
  "minimum_memory_rank_fraction": 0.6,
  "minimum_memory_rows": 6,
  "refinement_high": 0.9,
  "refinement_low": 0.06,
  "reject_threshold": 0.06,
  "snapshot_model_cost": 2,
  "transported_model_cost": 2
}
```

## Summary result

- 4 holdout identities
- 9 scenarios
- 16 trials per scenario
- 8 matched modes
- 4,608 decisions
- 23 of 23 endpoints passed
- Intact relation and group accuracy: 1.000000
- Intact external-task accuracy: 0.991319
- Intact mean regret: 0.000179
- Wrong-memory-transfer rate: 0
- All four five-generation lineages passed

## Conclusion

The frozen result supports bounded functional transformational self-continuity: continuity is inferred from causal and autobiographical transport evidence and is causally used for memory provenance, planning, and lineage recurrence. It is not evidence of subjective experience.

## Next gap

The next major gap is open-ended autobiographical self-reconstruction under unstructured task and ontology change. The system must learn what counts as a continuity probe, discover correspondence between observations, decide which invariants matter in a new domain, and recover after memory or model change without a predeclared transformation schema.
