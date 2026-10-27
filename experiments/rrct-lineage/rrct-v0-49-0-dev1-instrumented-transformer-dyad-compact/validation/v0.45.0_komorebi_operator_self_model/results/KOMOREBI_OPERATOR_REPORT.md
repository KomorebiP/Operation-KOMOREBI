# Frozen RRCT-Komorebi Operator Integration Report

## Result

`V045_FROZEN_ENDPOINTS_MET`

All 18 declared endpoints passed after verification of the 82-file pre-outcome source seal.

RRCT directly loaded the unchanged Komorebi Math `1.0.0b4` wheel and used its finite packet, analysis-synthesis, Bayesian-update, and low-rank-recompression APIs. This report concerns executable use of those APIs, not a terminological reinterpretation of existing RRCT variables.

## Causal packet benchmark

A ten-dimensional stable linear system contained a hidden three-dimensional controllable subspace and a seven-dimensional uncontrollable complement. Random basis changes hid the coordinate partition. The runtime received the dynamics matrix, actuation matrix, and anonymous paired probes, but no self mask or change label.

The discovered controllability range defined a candidate self packet. Komorebi supplied the certified complementary packet system and analysis-synthesis representation. After an unknown orthogonal coordinate transformation, the runtime transported the packets and decomposed the dynamics residual by source and destination packet.

Across 256 unique frozen worlds and 1,024 matched mode decisions:

| Mode | Correct change source | Mean packet-transport residual |
|---|---:|---:|
| Komorebi packet model | 256/256 | 0.0008073815 |
| Fixed coordinate split | 126/256 | 1.1913850696 |
| Scalar global residual | 128/256 | 1.0000000000 |

The scalar residual detected that a change occurred, but could not distinguish whether the changed operator component belonged primarily to the self packet or the world packet. The fixed coordinate split failed because the relevant subspace was randomly rotated away from the declared coordinates.

## Resolution benchmark

Each synthetic autobiography contained a low-energy component supported in the self packet and a higher-energy world component. Under a matched total rank budget:

- packet-wise recompression preserved the self-memory task with mean error `1.82e-15`
- global low-rank truncation produced mean self-memory error `0.999999999997`
- packet recompression improved the self-memory result in every matched world

This supports a narrow but concrete resolution-theory claim: global energy ranking can discard a low-energy packet that is functionally important, while a declared packet budget can preserve it.

## RRCT transformational-continuity bridge

The new controller subclasses the v0.44 transformational-continuity controller. For each candidate assessment it produces a linked Komorebi operator receipt containing:

- discovered-projector receipt digest
- packet transfer metrics
- packet residual energies
- Bayesian change posterior
- autobiographical packet-compression metrics
- inherited continuity-assessment digest

The bridge was evaluated on 72 inherited v0.44 cases and compared with 72 baseline decisions. Both achieved exact relation, group, and task accuracy with zero regret. Every inherited and extended chain validated.

## Integrity

```text
Komorebi version:       1.0.0b4
Komorebi wheel SHA-256: 7d51e3040aea84f6d540936c2427376205ef8660d44b6841c2848c542e628adb
Pre-outcome freeze:     6b95cc321bf412a74bb250bf1ed8b92e25bd5d3ca74af7a390c265f9579ef334
Operator analysis:      15cb2a2e892700e052aff65f9d08d58e6496bd5aac996fd647a5ae88703e4f1a
Frozen summary:         85e1af6f378c7cd36f7ac2404bdd3a77bbe49100222ced9f3619d6fedb04b0f7
Bridge compatibility:   61e235fd48d3e892d6eb8be644cee01b087e794c231b7ac5899c7f7a3a1fd198
```

The deterministic replay reproduced both the operator analysis and bridge compatibility object exactly.

## Interpretation boundary

The positive finding is bounded to this synthetic comparison. It demonstrates computational leverage over the included coordinate, scalar-residual, and resolution controls. It does not establish universal optimality, open-world self-awareness, or subjective experience.
