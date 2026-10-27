# Incubator: incomplete implementation entries

These entries are removed from the main reading lists until the return criteria below are met. Their original files remain available for development and inspection. Placement here is a readiness decision, not a conclusion that every mathematical idea in them is false. Lean is not required for return; appropriate written, computational, or implementation evidence is.

See the [first focused review](SOUNDNESS_REVIEW_2026-10-27.md) and [SRIC admission audit](SRIC_ADMISSION_AUDIT_2026-10-27.md) for the inspected sources, findings, and limits. No whole-collection soundness certification is implied for entries outside this list.

<a id="research-rrct-multispace-protocol"></a>

## RRCT multispace convergence protocol

Only synthetic estimator execution is recorded; the actual Qwen and primary causal runs are absent.

**Return gate:** Run the frozen-model smoke with authenticated inputs and report its descriptive scope; any workspace claim additionally requires the full primary causal, mediation, and replication gates.

[Preserved source](../research/rrct-multispace-protocol) · [Completion and evidence record](STATUS_CATALOG.md#research-rrct-multispace-protocol) · [Review and findings](SOUNDNESS_REVIEW_2026-10-27.md)

<a id="research-sric-external-admission"></a>

## SRIC: external semantic admission

A bounded audit reproduced admission with empty replay logits, order-dependent handling of a NaN replay error, and an unsupported real-checkpoint flag for an absent fingerprint. The normal engineered fixture remains explicitly synthetic.

**Return gate:** Publish a separately identified corrected edition with rejection tests for empty/non-finite logits and absent or invalid provenance, plus the existing positive fixture and finite-mismatch control. Qualify any real-model run separately with pinned checkpoint evidence.

[Preserved source](../research/sric-external-admission) · [Completion and evidence record](STATUS_CATALOG.md#research-sric-external-admission) · [Review and findings](SRIC_ADMISSION_AUDIT_2026-10-27.md)

<a id="research-prism-1r"></a>

## PRISM-1R

Hardware is an uncompiled boundary skeleton with success tie-offs; no executed hardware qualification.

**Return gate:** Replace success tie-offs with real generation, certificate, dependency and fault inputs; compile/simulate the RTL and retain meaningful rejection controls. Hardware performance requires separate measured evidence.

[Preserved source](../research/prism-1r) · [Completion and evidence record](STATUS_CATALOG.md#research-prism-1r) · [Review and findings](SOUNDNESS_REVIEW_2026-10-27.md)

[Research reading list](../research/README.md) · [Complete inventory](COMPONENT_INDEX.md) · [Finalization queue](FINALIZATION_QUEUE.md)
