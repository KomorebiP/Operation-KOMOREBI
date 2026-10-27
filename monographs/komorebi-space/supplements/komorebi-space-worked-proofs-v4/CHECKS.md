# Exact verification counts

Successful replay and additional audit.

| Group | Checks |
|---|---:|
| v3: `basis_dimension` | 4 |
| v3: `projector_idempotence` | 1,156 |
| v3: `transfer_naturality` | 1,156 |
| v3: `nested_projectors` | 4,624 |
| v3: `detail_in_projection_kernel` | 867 |
| v3: `split_reconstruction` | 867 |
| v3: `transfer_involution` | 289 |
| v3: `plotted_family_coherence` | 3 |
| v3: `plotted_full_reconstruction` | 1 |
| v3: `perturbed_family_residual` | 1 |
| v3: `protected_repair` | 1 |
| v4: `independent_model_matches_renderer` | 1 |
| v4: `reference_is_coherent` | 1 |
| v4: `two_signed_defects` | 1 |
| v4: `protected_obstruction_is_zero` | 1 |
| v4: `finest_repair_coherence` | 404 |
| v4: `finest_repair_protection` | 404 |
| v4: `finest_repair_idempotence` | 404 |
| v4: `exact_defect_decomposition` | 404 |
| v4: `least_squares_repair_coherence` | 404 |
| v4: `least_squares_repair_idempotence` | 404 |
| v4: `least_squares_error_orthogonal_to_kernel` | 404 |
| v4: `least_squares_pythagoras` | 404 |
| v4: `surjective_differential_right_inverse` | 115 |
| v4: `right_inverse_preserves_finest_view` | 115 |
| v4: `obstruction_normal_form` | 115 |
| v4: `obstruction_annihilates_allowed_changes` | 81 |
| v4: `component_energy` | 4 |
| v4: `orthogonal_scale_bands` | 6 |
| v4: `resolution_energy_telescope` | 4 |
| v4: `origin_worked_value` | 4 |
| v4: `displayed_protected_repair` | 1 |
| v4: `displayed_nearest_repair` | 1 |
| v4: `protected_cost` | 1 |
| v4: `nearest_cost` | 1 |
| v4: `residual_energy` | 1 |
| v4: `negative_control_omitted_finest_detail_detected` | 1 |
| v4: `negative_control_wrong_residual_sign_detected` | 1 |
| v4: `negative_control_pointwise_difference_not_compatibility_defect` | 1 |
| v4: `negative_control_asymmetric_cutoff_breaks_swap_naturality` | 1 |
| v4: `branching_nonzero_obstruction_independent_of_lift` | 6 |

**Total: 12,664 passing exact checks.**

Negative controls pass by detecting an intentionally false identity.
The count is a reproducibility record, not a measure of theorem novelty.
No Lean run or infinite exhaustive check is asserted.
