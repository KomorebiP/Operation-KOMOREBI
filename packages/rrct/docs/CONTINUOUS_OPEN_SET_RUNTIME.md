# Continuous open-set runtime

## Objective

The `continuous_open_set_runtime` family integrates previously isolated RRCT mechanisms into one persistent controller. It does not reset between ordinary tasks, task-structure changes, self changes, world changes, partner/sensor remaps, and memory conflicts.

## State

The persistent checkpointed state includes:

- current episode
- moving fuzzy packet membership matrix
- active packet count and packet lifecycle counters
- true and estimated world offsets
- true and estimated self coordinate maps
- true and estimated partner/sensor maps
- evidence budget
- autobiographical and quarantined record counts
- false-write count
- event state
- accumulated metrics and RNG state

## Synthetic event fabric

The evaluator can introduce:

- `none`
- `world_shift`
- `self_shift`
- `partner_change`
- `memory_corruption`

Task demand also changes among local, pair, overlapping, and global integration.

The controller is not given the correct event or repair action. It responds through prediction error, packet geometry, probes, provenance, and recurrence.

## Moving fuzzy packets

A noisy task-dependency matrix is decomposed into a positive low-rank fuzzy membership field. Packet creation and removal depend on:

- relative eigenvalue threshold
- formation cost
- birth and death patience
- minimum lifetime
- fuzzy update rate and temperature

The runtime measures membership entropy, idempotence defect, transport defect, packet-count accuracy, formation accuracy, and dissolution accuracy.

## Self/world repair

When a residual exceeds the change threshold, bounded probes compare self-side and world-side mismatch. The controller may:

- repair a self/partner coordinate mapping
- repair the world offset
- leave the source unresolved
- increase the next evidence budget

Memory corruption is handled separately through provenance quarantine. Removing provenance produces false autobiographical writes.

## Main interventions

- workspace cut
- self-model cut
- causal-boundary or self/world-attribution cut
- memory and provenance cuts
- change-detector cut
- adaptive-probe cut
- packet-birth and packet-death cuts
- repair cut
- planner-binding cut
- recurrence and feedback cuts

## Interpretation boundary

This is a bounded synthetic functional integration test. It does not establish subjective awareness, sentience, valence, welfare, or a general human cognitive architecture.
