# V0.3 functional transport assay design

## Scope and interpretation

`transport_assays.py` is an additive layer over the verified v0.2
`transport.py`. It does not alter legacy receipts or gates.

- Stage A (the hard-stability eight-state confirmation) continues to use the
  verified legacy v0.2 cross-seed transport diagnostic. Its result remains
  bounded by the eight-state decode/re-embed ceiling and cannot add a
  confirmatory beyond-codebook claim.
- Stage B (the developmental sparse GF(5)^4 task) can call this module. Its
  focal contrast is transport beyond a *declared* codebook, normally attribute
  0 (pose), while attributes 1–3 are payload. Since a full 625-state decoder can
  reconstruct the complete state, success over the pose baseline is not success
  over every possible discrete codebook. The full-state decode/re-embed ceiling
  must therefore be reported too.
- Stage B findings are developmental evidence for a later preregistration, not
  a new confirmatory v0.3 claim.

## Why this rejects a label-only explanation

Endpoint accuracy alone cannot distinguish a coordinate map from decoding one
of eight labels and inserting the corresponding target embedding. The stronger
assay requires all of the following:

1. Fit and evaluation contexts (and any declared attribute values) are disjoint.
2. The affine map preserves variation within the chosen codebook label.
3. It beats a target-label centroid and a within-label shuffled-pair fit.
4. The explicit source-decode → target-reembed ceiling is reported.
5. State maps work in both directions and survive both round trips.
6. Independently fitted operator-code maps work on held-out contexts, survive
   both round trips, and close a functional stepping square.
7. Component-specific counterfactuals change the written/dependent attributes
   while preserving audit-declared invariant attributes.
8. Fidelity is reported on all examples and conditionally on preregistered masks
   such as both-native-correct and behaviorally distinguishing trials.

`conditional_residual_r2` is the central geometric diagnostic. It subtracts a
separate prediction and target centroid inside every declared codebook label.
A label prototype therefore scores exactly zero whenever within-label target
variance is nonzero; a richer map must predict the remaining payload/context
variation.

## Integration locations

Copy the staged files to:

- `src/komorebi_neuralese/transport_assays.py`
- `tests/test_transport_v3.py`

Keep Stage B records under a schema-specific directory such as
`results/.../residual_transport/`; do not flatten them into legacy `transport`
records. The module emits schema
`komorebi.neuralese.functional_transport.v3`.

Each record includes source/target model identifiers, distinct anchor/evaluation
seeds, named fit/evaluation partitions, exact holdout counts and membership,
the declared codebook columns, and float64-SVD design rank/condition diagnostics.

## Runner sketch

Create one `PairedRepresentations` for anchors and one for evaluation. Rows must
pair the same semantic endpoint and anonymous context across independently
trained models. `source_operators` and `target_operators` use shape
`[examples, slots, ...]`; matrix and vector codes are both accepted.

```python
assay = fit_transport_assay_from_datasets(
    anchors,
    evaluation,
    metadata=AssayMetadata(
        source_id=source_run_id,
        target_id=target_run_id,
        anchor_seed=anchor_seed,
        evaluation_seed=evaluation_seed,
        anchor_partition="train",
        evaluation_partition="test",
    ),
    codebook_columns=(0,),       # pose-only codebook
    ridge=1e-5,
    shuffle_seed=control_seed,
)

latent_metrics = assay.evaluate_latents(
    evaluation,
    source_decode=decode_all_source_attributes,
    target_reembed=reembed_all_target_attributes,
    target_decode=decode_all_target_attributes,
    source_reembed=reembed_all_source_attributes,
)
```

For the sparse intervention batches, feed `write_masks` or dependency-derived
affected masks as `patched_components`, and `preserved_masks` as
`invariant_components`:

```python
patch_metrics = score_component_patches(
    {
        "affine": affine_prediction,
        "pose_centroid": pose_baseline_prediction,
        "full_state_decode_reembed": full_state_baseline_prediction,
    },
    counterfactual_attributes,
    factual_attributes,
    patched_components=write_masks,
    invariant_components=preserved_masks,
    condition_mask=protocol_eligible,
    native_prediction=native_prediction,
    native_target=native_target,
    baseline="pose_centroid",
)
```

Use `transport_operator_patch` for direct operator substitution and
`operator_intertwining_metrics` for the commuting square. For square
matrix-valued codes, `StateInducedOperatorTransport` additionally tests the
conjugation implied by the state map; nonzero affine-bias incompatibility is
still exposed by the functional commuting-square residual.

## Stable metric paths

Recommended gate/report paths (developmental until a later freeze):

- `state.forward.conditional_residual_r2`
- `state.forward_codebook_contrast.conditional_residual_r2_minus_centroid`
- `state.forward_codebook_contrast.conditional_residual_r2_minus_within_codebook_shuffle`
- `state.forward_decode_reembed_baseline.conditional_residual_r2`
- `state.cycle.source_cycle.r2` and `state.cycle.target_cycle.r2`
- `operator.forward.r2`, `operator.reverse.r2`
- `operator.cycle.source_cycle.r2`, `operator.cycle.target_cycle.r2`
- `operator.forward_shuffled_control.r2`, `operator.forward_random_map.r2`
- `commuting_square.r2` from `operator_intertwining_metrics`
- `joint_component_fidelity`, `invariant_row_accuracy`,
  `joint_fidelity_on_native_success`, and
  `joint_fidelity_on_native_distinguishing` from component patch scoring

The verifier should require the exact prespecified source/target pair set and
schema, reject missing baselines or masks, and fail closed on zero-sized
conditional strata rather than treating `None` as a pass.
