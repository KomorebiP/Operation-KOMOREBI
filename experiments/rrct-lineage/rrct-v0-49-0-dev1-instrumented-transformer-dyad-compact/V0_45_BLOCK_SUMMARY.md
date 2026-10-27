# RRCT v0.45 Komorebi Operator Self-Model

## Status

- Version: `0.45.0.dev1`
- Frozen scientific status: `V045_FROZEN_ENDPOINTS_MET`
- Deterministic replay status: `V045_RELEASE_VERIFIED`
- Frozen endpoints: **18 of 18 passed**
- Pre-outcome sealed files: **82**

## Question

Version 0.45 tests whether Komorebi Math supplies actual computational leverage for RRCT self-modeling, rather than serving only as a conceptual analogy.

The implementation directly uses the exact public Komorebi Math `1.0.0b4` wheel through four APIs:

- `PacketSystem`
- `AnalysisSynthesisSystem`
- `BayesianUpdate`
- `recompress_core`

The original Komorebi wheel is vendored unchanged and verified before import.

```text
Komorebi wheel SHA-256
7d51e3040aea84f6d540936c2427376205ef8660d44b6841c2848c542e628adb
```

## What was implemented

The new RRCT bridge:

1. Discovers a candidate self packet from the finite controllability range
   \([B,AB,\ldots,A^{n-1}B]\), without receiving a self-coordinate mask.
2. Constructs certified complementary self/world projectors through Komorebi packet systems.
3. Builds an analysis-synthesis atlas and checks its reconstruction certificate.
4. Transports the packet system through an unknown coordinate transformation.
5. Resolves a successor-model residual into self-from-self, self-from-world, world-from-self, and world-from-world transfer blocks.
6. Uses a finite Bayesian update to classify no change, self change, world change, or mixed change.
7. Recompresses autobiographical memory packet by packet, preserving a deliberately low-energy self component under a matched rank budget.
8. Binds the operator assessment to RRCT v0.44 continuity, adjudication, planning, task, and outcome receipts.

The inherited v0.44 controller remains available as the comparison baseline.

## Frozen holdout

The source, exact Komorebi dependency, protocol, thresholds, seeds, tests, runners, and implementation were sealed before holdout execution.

Holdout seeds:

```text
116221458
458425147
129992909
292534192
```

Design:

| Dimension | Value |
|---|---:|
| Stable linear state dimension | 10 |
| Hidden controllable self dimension | 3 |
| Hidden world dimension | 7 |
| Change scenarios | 4 |
| Trials per scenario and seed | 16 |
| Unique synthetic worlds | 256 |
| Matched operator decisions | 1,024 |
| v0.44 bridge decisions | 144 |

The four hidden conditions were no functional change, self-packet change, world-packet change, and mixed change.

## Principal operator results

| Mode | Change-source accuracy | Change detection | Projector certificate rate | Mean transported-projector residual | Mean self-memory error |
|---|---:|---:|---:|---:|---:|
| **Komorebi packets** | **1.000000** | **1.000000** | **1.000000** | **0.000807** | **1.82e-15** |
| Fixed coordinate split | 0.492188 | 1.000000 | 0.000000 | 1.191385 | 1.82e-15 |
| Scalar global residual | 0.500000 | 1.000000 | 0.000000 | 1.000000 | 1.82e-15 |
| Resolution cut | 1.000000 | 1.000000 | 1.000000 | 0.000807 | 1.000000 |

Komorebi packet attribution exceeded:

- fixed-coordinate splitting by **50.78 percentage points**
- scalar global-residual attribution by **50.00 percentage points**

The resolution-cut control retained the correct causal packets, so it still localized change correctly. However, replacing packet-wise recompression with global low-rank truncation increased the protected self-memory error from approximately zero to approximately one.

Packet-wise compression improved the protected self-memory error in every matched holdout world.

## Existing RRCT compatibility

The Komorebi bridge was also applied retrospectively to the existing v0.44 transformation cases.

| Engine | Cases | Relation accuracy | Group accuracy | Task accuracy | Mean regret | Complete chain validity |
|---|---:|---:|---:|---:|---:|---:|
| v0.44 baseline | 72 | 1.000000 | 1.000000 | 1.000000 | 0.000000 | 1.000000 |
| Komorebi bridge | 72 | 1.000000 | 1.000000 | 1.000000 | 0.000000 | 1.000000 |

The bridge emitted an average of **3.278 operator receipts per evaluated v0.44 case**. All inherited and operator-extended receipt chains validated.

This compatibility arm is retrospective successor validation, not a newly frozen v0.44 scientific cohort.

## Validation

| Layer | Result |
|---|---:|
| Focused v0.45 tests | **9 passed** |
| v0.43-v0.45 successor line | **26 passed, 2 predecessor-freeze tests deselected** |
| v0.36-v0.40 runtime line | **64 passed, 1 historical freeze-builder test deselected** |
| v0.41-v0.45 runtime line | **47 passed, 2 predecessor-freeze tests deselected** |
| Python AST parsing | **168 files passed** |
| Exact frozen replay | Passed |
| Built RRCT wheel | Passed |
| Exact embedded Komorebi wheel | Present and SHA-256 verified |
| Clean installed-wheel import | Passed |
| Installed-wheel operator smoke test | Passed |

The first clean-install probe invoked helper names that do not exist in the sealed API. The package itself had built correctly. The corrected probe loaded the vendored wheel through the actual sealed bridge and passed. No scientific source or holdout output was changed.

## What the result establishes

Within the frozen synthetic comparison, Komorebi’s packet and transfer representation provides measurable value for two RRCT operations:

1. **Causal localization:** it recovers a hidden controllable self subspace, transports it through an unknown coordinate change, and distinguishes self-side from world-side model changes.
2. **Resolution-aware autobiography:** packet-wise recompression preserves a low-energy self-memory component that a global truncation with the same total rank budget discards.

The result also establishes that these operator records can be attached to RRCT’s existing transformational-continuity receipt chain without reducing v0.44 performance.

This is the first implemented, measured bridge between the two projects. It moves the connection from mathematical analogy to executable integration.

## What the result does not establish

The controls are intentionally narrow. The result does not establish that Komorebi Math is superior to every possible:

- controllability-subspace algorithm
- causal representation learner
- graph-based self-boundary method
- structured low-rank compressor
- Bayesian change detector

The benchmark is linear, low dimensional, synthetic, and supplied with anonymous paired state probes. The actuation interface still provides a route for defining controllability, and the transformation episode is still externally delimited.

It does not establish:

- open-world self-boundary discovery
- unannounced self-change detection
- endogenous ontology construction
- general autobiographical self-reconstruction
- functional self-awareness in arbitrary environments
- subjective awareness, sentience, valence, or moral status

## Next gap

The next major experiment should use the Komorebi packet machinery inside an **anonymous continuous event fabric**. RRCT should have to detect an unannounced mismatch, decide whether it is self-side or world-side, discover a new packet decomposition or transfer map, reconstruct a minimal provenance-aware autobiography, and bind the repaired model back to planning.

That would test whether Komorebi operators help with open-set self-model repair rather than only a prepared linear change-localization task.
