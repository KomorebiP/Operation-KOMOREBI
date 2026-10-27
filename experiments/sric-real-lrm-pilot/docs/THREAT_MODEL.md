# Threat Model

## Accidental intervention mismatch

The intervention path could alter prompt format, position IDs, attention masks, or answer-token scoring. The adapter constructs one complete teacher-forced sequence and changes only the latent vectors.

## Invalid replay

A trace capture from a descriptive hook may not equal the state actually reinjected. The audit targets the reinjected vector itself and requires logit-level replay.

## Cache artifacts

Incorrect key/value cache slicing can make replay or transplantation appear causal. The trace engine follows the pinned runtime's cache ranges and fails closed on unsupported cache types.

## Final-answer confound

Different-answer transplantation is weak evidence. The primary donor shares the answer and differs in proof signature.

## Proof-depth confound

A different number of reasoning stages can make transplantation fail for timing reasons. The donor rule first matches proof depth and records fallbacks.

## Surface confound

A trace may encode exact premise ordering. The semantic twin tests premise-order stability. Other surface transformations remain unclaimed.

## Gold-label circularity

Proof steps may assist donor construction but may not both construct and certify an inferred ontology. The current pilot stops before semantic naming.

## Adaptive thresholding

Inspecting final effects before setting thresholds invalidates the claim. The seal commits thresholds and donors before final execution.

## Group leakage

Semantic twins or shared proof templates can produce falsely narrow intervals. Group-aware resampling must use the strongest available proof-family identifier.

## Checkpoint substitution

A filename is not a model identity. The complete checkpoint hash is required.

## High-capacity post-hoc decoding

A decoder may memorize audit labels. Pilot 0.1 uses no semantic decoder. Pilot 0.2 must separate construction and witness supports.

## Negative-result suppression

A latent-unused or adapter-invalid result is informative. The chronology requires preserving every final status and runtime failure.
