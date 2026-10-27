# Subtext Integration Boundary

## What is reused conceptually

Subtext shows that a fitted Jacobian lens can be applied continuously during both the input-reading pass and cached token generation. RRCT uses the same high-level measurement pattern:

1. attach bounded residual hooks at selected layers
2. collect every selected token position during reading
3. retain phase and token indices, including a true pre-sampling state for each generated token
4. transport through a pre-fitted lens
5. record ranked readouts without changing the frozen model

The v0.61 implementation is independent and does not copy Subtext's interface, media, prose, or source files.

## What is not inherited as evidence

A continuous display can reveal useful temporal structure, but the following remain qualitative until preregistered tests pass:

- a concept appearing before output
- a concept persisting while unrelated text is generated
- an intermediate concept appearing in a two-hop problem
- semantic-looking progression across layers

These phenomena can guide task construction. They do not establish native workspace geometry, limited capacity, broad causal reuse, binding, or formation.

## Temporal additions to RRCT

Every saved readout frame carries:

- prompt identifier
- reading or generation phase
- absolute token position
- source layer
- token IDs and decoded labels
- unnormalized and normalized strengths
- model and lens revisions

Primary statistics use the full recorded ledger, not the curated visual top words. Filtering may change display only and may never change probability normalization or scientific ranking. A generated-token frame must distinguish the state that selected token t from the post-consumption state that is disposed toward token t+1. These may not share one label.

## Hardware decision

Subtext's default Qwen3.5-4B path calls for roughly 10 GB VRAM and is not the first target for an 8 GB laptop GPU. RRCT keeps the current Qwen2.5-0.5B engineering model and later Qwen2.5-1.5B confirmation model. The temporal instrumentation is model agnostic.
