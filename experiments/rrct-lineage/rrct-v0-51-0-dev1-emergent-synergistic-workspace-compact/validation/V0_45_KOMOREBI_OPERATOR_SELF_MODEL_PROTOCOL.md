# RRCT v0.45 Komorebi Operator Self-Model Protocol

## Scientific question

Can the public finite operator APIs in Komorebi Math provide measurable computational leverage for RRCT self-modeling, rather than merely serving as alternative terminology?

The block tests four concrete claims:

1. A causal self packet can be discovered from controllability without evaluator identity labels.
2. The packet can be transported through an unknown coordinate change while preserving the self/world decomposition.
3. Transfer-block residuals can localize whether a hidden model change occurred primarily in the controllable self packet, the uncontrollable world packet, both, or neither.
4. Packet-wise low-rank recompression can preserve a low-energy self-memory mode that a matched global rank budget discards.

A second, retrospective compatibility arm routes existing v0.44 transformational-continuity cases through the new operator bridge and checks that the bridge does not reduce relation, group, or task performance while emitting a linked Komorebi receipt chain.

## Exact Komorebi dependency

The release vendors the exact public wheel:

```text
komorebi-math 1.0.0b4
SHA-256 7d51e3040aea84f6d540936c2427376205ef8660d44b6841c2848c542e628adb
```

The integration uses:

- `PacketSystem`
- `AnalysisSynthesisSystem`
- `recompress_core`
- `BayesianUpdate`

The original wheel is retained unchanged and verified before import.

## Synthetic operator world

Each world contains a ten-dimensional stable linear system with a hidden three-dimensional controllable subspace and a seven-dimensional uncontrollable subspace. A random basis hides this decomposition. The controller receives only the dynamics matrix, actuation matrix, and paired anonymous state probes.

The self packet is discovered as the numerical range of the finite controllability matrix

\[
[B,AB,\ldots,A^{n-1}B].
\]

No coordinate mask or identity label is supplied.

An unknown orthogonal coordinate change is then applied. One of four hidden conditions is introduced:

- no functional change
- self-packet change
- world-packet change
- mixed change

The controller estimates the coordinate transport, transports its discovered packet system, decomposes the model residual into packet blocks, and makes a Bayesian change-source judgment before the evaluator reveals the condition.

## Matched modes

| Mode | Description |
|---|---|
| `komorebi_packets` | Discovered packet system, Bayesian packet attribution, packet-wise memory compression |
| `coordinate_split` | Fixed first-coordinate split after random basis hiding |
| `global_residual` | Scalar global residual with no packet attribution |
| `resolution_cut` | Correct packet attribution but global low-rank memory compression |

The controls are intentionally narrow. They answer whether the packet representation adds value over the specific non-packet alternatives tested. They do not establish superiority over every possible causal-subspace or structured-compression method.

## Frozen holdout

The final holdout uses four deterministic seeds selected before holdout execution:

```text
116221458
458425147
129992909
292534192
```

Each seed contains 16 trials per scenario, four scenarios, and four matched modes:

- 64 unique worlds per seed
- 256 unique worlds overall
- 1,024 matched mode decisions

The final source, protocol, seed receipt, focused tests, runners, and vendored wheel are sealed before the holdout is executed.

## Frozen endpoints

1. Komorebi change-source accuracy is at least 0.95.
2. Komorebi change detection accuracy is at least 0.98.
3. Every Komorebi projector construction is certified.
4. Mean transported-projector residual is at most 0.02.
5. Komorebi accuracy exceeds fixed-coordinate splitting by at least 0.20.
6. Komorebi accuracy exceeds the scalar global residual by at least 0.30.
7. Packet-wise compression has mean self-memory error at most 0.05.
8. Global compression increases self-memory error by at least 0.50.
9. Packet compression improves self-memory error in every matched world.
10. Runtime rows report no evaluator-label use.
11. Row digests are unique.
12. The v0.44 bridge preserves relation accuracy.
13. The v0.44 bridge preserves group accuracy.
14. The v0.44 bridge preserves task accuracy within 0.01.
15. The v0.44 bridge does not increase mean regret by more than 0.005.
16. All inherited RRCT receipt chains validate.
17. All Komorebi operator receipt chains validate.
18. The bridge emits operator receipts for every evaluated transition.

## Interpretation boundary

A positive result means that Komorebi's packet, transfer, Bayesian, and recompression APIs provide measurable leverage in this bounded synthetic comparison and can be causally integrated into RRCT's existing self-continuity controller.

It does not establish:

- open-world self-boundary discovery
- general superiority of Komorebi Math over all alternatives
- subjective awareness
- sentience or valence
- moral status
- intrinsic self-preservation
- biological equivalence
