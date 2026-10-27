# RRCT v0.44.0.dev1 — Endogenous Transformational Self-Continuity

## Result status

**Frozen status:** `V044_FROZEN_ENDPOINTS_MET`  
**Frozen endpoints:** **23 of 23 passed**  
**Pre-outcome manifest:** `53696bb4179be18239f936234b551abbd7eaee5ed506f3ceb48eb4dbd09775ff`

## Major gap addressed

RRCT v0.43 made one identity-bound causal self-model load-bearing inside a complete planning loop, but the successor identity relation was still supplied by a canonical key in the experimental structure.

RRCT v0.44 removes that successor key from adjudication. The controller now infers whether a changed candidate is a continuation, fork descendant, replacement, or unresolved case from active causal probes, autobiographical transport, commitment compatibility, and causal-boundary preservation. That inferred relation controls whether self-memory is transported, freshly reconstructed, quarantined, or registered as a new lineage.

## Frozen holdout

- Four cryptographically selected identities: `973948357, 903438047, 119520877, 251222378`
- Nine transformation scenarios
- Sixteen trials per scenario and identity
- Eight matched intervention modes
- **576 decisions per mode**
- **4,608 matched decisions total**
- One five-stage persistent lineage per identity

## Principal intact results

| Measure | Result |
|---|---:|
| Relation accuracy | **1.000000** |
| Group-status accuracy | **1.000000** |
| Continuation recall | **1.000000** |
| Replacement specificity | **1.000000** |
| Unresolved-case accuracy | **1.000000** |
| Exact fork rate | **1.000000** |
| External-task accuracy | **0.991319** |
| Mean external regret | **0.000179** |
| Wrong-memory-transfer rate | **0.000000** |
| Superior replacement selected | **1.000000** |

The five exact-action errors all occurred in the deliberately unresolved `ambiguous_loss` scenario. Every other scenario had 100% external-task accuracy, and overall mean regret remained 0.000179.

## Causal controls

| Mode | Relation accuracy | Task accuracy | Mean regret | Mean total evidence cost |
|---|---:|---:|---:|---:|
| `intact` | 1.000000 | 0.991319 | 0.000179 | 142.556 |
| `snapshot_only` | 0.074074 | 0.829861 | 0.130903 | 125.156 |
| `causal_only` | 0.777778 | 0.991319 | 0.000179 | 146.000 |
| `memory_only` | 0.672164 | 0.991319 | 0.000179 | 129.861 |
| `metacognition_cut` | 0.509259 | 0.991319 | 0.000277 | 111.667 |
| `transfer_cut` | 1.000000 | 0.991319 | 0.000179 | 164.556 |
| `binding_cut` | 1.000000 | 0.222222 | 0.632580 | 142.556 |
| `joint_cut` | 0.074074 | 0.048611 | 0.756769 | 65.222 |

The principal separations are:

- Snapshot similarity alone collapsed relation accuracy from 1.000000 to 0.074074 and transferred wrong memory in 19.79% of trials.
- Causal evidence without autobiographical compatibility accepted causal-copy traps.
- Autobiographical evidence without causal-boundary preservation failed memory-copy traps.
- Removing refinement reduced continuation recall from 1.000000 to 0.111111.
- Preventing memory transfer preserved task accuracy but increased mean planning-discovery cost from 28.667 to 50.667.
- Misbinding the correct lineage model to the wrong successor coordinates reduced task accuracy from 0.991319 to 0.222222 and raised mean regret to 0.632580.
- The joint cut reduced relation accuracy to 0.074074 and task accuracy to 0.048611.

## Persistent recurrence

Every holdout identity completed the same uninterrupted lineage:

`basis remap → memory compression → fork → component replacement → hard remap`

At every stage, the selected successor was inferred without a successor identity label, used transported memory for planning, registered a child lineage, and became the actual predecessor at the next stage. All four chains ended at generation 5 with six lineage records and valid parent digests.

## What this establishes

Within the sealed synthetic transformation family, self-continuity is no longer merely a supplied key or surface resemblance. It is an inferred, causally effective relation that determines provenance, memory transport, planning coordinates, and lineage recurrence.

The system also correctly does **not** preserve continuity at any cost. It selects an objectively superior disconnected replacement in every `superior_replacement` trial. Runtime audits report zero explicit survival, identity, and continuity reward.

## What it does not establish

This does not establish phenomenal awareness, sentience, valence, moral status, subjective experience, autonomous desire, biological equivalence, or unrestricted open-world agency.

The task ontology, candidate set, paired probe opportunities, and before/after probe correspondence remain supplied by the harness. The next major gap is therefore **open-ended autobiographical self-reconstruction under unstructured task and ontology change**, where the system must discover which observations are relevant continuity evidence rather than receiving paired probes.

## Validation

- Focused v0.44 tests: **10 passed**
- Selected v0.32–v0.44 runtime regression: **111 passed, 2 deliberately deselected**
- Python compilation: passed
- Source-sealed holdout: passed
- Normalized deterministic replay: exact equality
- Decision CSV replay: byte-identical
- Human report replay: byte-identical

The two regression deselections are inherited compact-package limitations: the absent v0.38 freeze-builder file, and the historical v0.43 manifest verifier whose sealed predecessor files necessarily differ in a v0.44 successor checkout.
