# Block 10 declaration index

Every entry is included in Audit.lean. Theorems and constructors are distinguished.

## KomorebiPhysics.BoundedSpectral

| Kind | Name | Source line |
|---|---|---:|
| abbrev | `KomorebiPhysics.BoundedSpectral.Symbol` | 16 |
| abbrev | `KomorebiPhysics.BoundedSpectral.Space` | 17 |
| def | `KomorebiPhysics.BoundedSpectral.ofBound` | 20 |
| theorem | `KomorebiPhysics.BoundedSpectral.ofBound_apply` | 23 |
| def | `KomorebiPhysics.BoundedSpectral.multiply` | 27 |
| theorem | `KomorebiPhysics.BoundedSpectral.multiply_apply` | 33 |
| theorem | `KomorebiPhysics.BoundedSpectral.multiply_norm_le` | 36 |
| def | `KomorebiPhysics.BoundedSpectral.diagonal` | 47 |
| theorem | `KomorebiPhysics.BoundedSpectral.diagonal_apply` | 54 |
| theorem | `KomorebiPhysics.BoundedSpectral.diagonal_single` | 57 |
| theorem | `KomorebiPhysics.BoundedSpectral.norm_diagonal_le` | 65 |
| theorem | `KomorebiPhysics.BoundedSpectral.symbol_le_norm` | 69 |
| theorem | `KomorebiPhysics.BoundedSpectral.norm_diagonal` | 74 |
| theorem | `KomorebiPhysics.BoundedSpectral.diagonal_congr` | 78 |
| theorem | `KomorebiPhysics.BoundedSpectral.diagonal_zero` | 81 |
| theorem | `KomorebiPhysics.BoundedSpectral.diagonal_one` | 85 |
| theorem | `KomorebiPhysics.BoundedSpectral.diagonal_add` | 89 |
| theorem | `KomorebiPhysics.BoundedSpectral.diagonal_sub` | 94 |
| theorem | `KomorebiPhysics.BoundedSpectral.diagonal_mul` | 99 |
| theorem | `KomorebiPhysics.BoundedSpectral.diagonal_smul` | 103 |
| theorem | `KomorebiPhysics.BoundedSpectral.diagonal_norm_sub` | 107 |
| theorem | `KomorebiPhysics.BoundedSpectral.diagonal_adjoint` | 110 |

## KomorebiPhysics.SpectralTruncation

| Kind | Name | Source line |
|---|---|---:|
| def | `KomorebiPhysics.SpectralTruncation.truncate` | 15 |
| theorem | `KomorebiPhysics.SpectralTruncation.truncate_apply` | 21 |
| def | `KomorebiPhysics.SpectralTruncation.anchored` | 25 |
| theorem | `KomorebiPhysics.SpectralTruncation.anchored_apply` | 28 |
| theorem | `KomorebiPhysics.SpectralTruncation.anchored_zero` | 33 |
| def | `KomorebiPhysics.SpectralTruncation.cutoff` | 37 |
| theorem | `KomorebiPhysics.SpectralTruncation.cutoff_apply` | 39 |
| theorem | `KomorebiPhysics.SpectralTruncation.cutoff_idempotent` | 43 |
| theorem | `KomorebiPhysics.SpectralTruncation.truncate_sandwich` | 48 |
| theorem | `KomorebiPhysics.SpectralTruncation.anchored_sandwich` | 54 |
| theorem | `KomorebiPhysics.SpectralTruncation.truncate_vector_sum` | 60 |
| theorem | `KomorebiPhysics.SpectralTruncation.truncate_strong` | 69 |
| theorem | `KomorebiPhysics.SpectralTruncation.cutoff_strong` | 74 |
| theorem | `KomorebiPhysics.SpectralTruncation.anchored_strong` | 77 |
| theorem | `KomorebiPhysics.SpectralTruncation.error_coordinate` | 85 |
| theorem | `KomorebiPhysics.SpectralTruncation.error_norm_le` | 92 |
| theorem | `KomorebiPhysics.SpectralTruncation.tail_le_error_norm` | 103 |
| theorem | `KomorebiPhysics.SpectralTruncation.error_norm_eq_sup` | 110 |
| theorem | `KomorebiPhysics.SpectralTruncation.anchored_norm_tendsto` | 128 |
| theorem | `KomorebiPhysics.SpectralTruncation.anchored_norm_iff` | 141 |
| theorem | `KomorebiPhysics.SpectralTruncation.unit_modulus_error` | 155 |
| theorem | `KomorebiPhysics.SpectralTruncation.unit_modulus_not_norm` | 164 |

## KomorebiPhysics.HarmonicSurrogates

| Kind | Name | Source line |
|---|---|---:|
| def | `KomorebiPhysics.HarmonicSurrogates.denominator` | 18 |
| theorem | `KomorebiPhysics.HarmonicSurrogates.eigenvalue_mono` | 20 |
| theorem | `KomorebiPhysics.HarmonicSurrogates.eigenvalue_half_le` | 24 |
| theorem | `KomorebiPhysics.HarmonicSurrogates.denominator_re` | 28 |
| theorem | `KomorebiPhysics.HarmonicSurrogates.denominator_ne_zero` | 31 |
| theorem | `KomorebiPhysics.HarmonicSurrogates.denominator_norm_lower` | 37 |
| theorem | `KomorebiPhysics.HarmonicSurrogates.denominator_norm` | 40 |
| theorem | `KomorebiPhysics.HarmonicSurrogates.resolvent_coefficient_bound` | 46 |
| def | `KomorebiPhysics.HarmonicSurrogates.resolventSymbol` | 51 |
| theorem | `KomorebiPhysics.HarmonicSurrogates.resolventSymbol_apply` | 57 |
| theorem | `KomorebiPhysics.HarmonicSurrogates.resolventSymbol_norm` | 60 |
| theorem | `KomorebiPhysics.HarmonicSurrogates.resolvent_tail` | 64 |
| theorem | `KomorebiPhysics.HarmonicSurrogates.resolvent_truncation_norm` | 70 |
| theorem | `KomorebiPhysics.HarmonicSurrogates.resolvent_truncation_tendsto` | 76 |
| theorem | `KomorebiPhysics.HarmonicSurrogates.resolvent_mem_domain` | 82 |
| def | `KomorebiPhysics.HarmonicSurrogates.resolventDomain` | 100 |
| theorem | `KomorebiPhysics.HarmonicSurrogates.resolvent_right_inverse` | 103 |
| theorem | `KomorebiPhysics.HarmonicSurrogates.resolvent_left_inverse` | 114 |
| def | `KomorebiPhysics.HarmonicSurrogates.heatSymbol` | 126 |
| theorem | `KomorebiPhysics.HarmonicSurrogates.heatSymbol_apply` | 132 |
| theorem | `KomorebiPhysics.HarmonicSurrogates.heatSymbol_norm` | 135 |
| theorem | `KomorebiPhysics.HarmonicSurrogates.heat_zero` | 139 |
| theorem | `KomorebiPhysics.HarmonicSurrogates.heat_add` | 144 |
| theorem | `KomorebiPhysics.HarmonicSurrogates.heat_truncation_exact` | 156 |
| theorem | `KomorebiPhysics.HarmonicSurrogates.heat_truncation_tendsto` | 167 |
| def | `KomorebiPhysics.HarmonicSurrogates.phaseSymbol` | 176 |
| theorem | `KomorebiPhysics.HarmonicSurrogates.phaseSymbol_apply` | 180 |
| theorem | `KomorebiPhysics.HarmonicSurrogates.phaseSymbol_norm` | 183 |
| theorem | `KomorebiPhysics.HarmonicSurrogates.phase_zero` | 186 |
| theorem | `KomorebiPhysics.HarmonicSurrogates.phase_add` | 192 |
| theorem | `KomorebiPhysics.HarmonicSurrogates.phase_inverse` | 205 |
| theorem | `KomorebiPhysics.HarmonicSurrogates.phase_preserves_norm` | 210 |
| theorem | `KomorebiPhysics.HarmonicSurrogates.phase_truncation_exact` | 220 |
| theorem | `KomorebiPhysics.HarmonicSurrogates.phase_truncation_not_norm` | 224 |
| theorem | `KomorebiPhysics.HarmonicSurrogates.phase_truncation_strong` | 229 |
| theorem | `KomorebiPhysics.HarmonicSurrogates.cutoff_eq_old_partial` | 233 |

## KomorebiPhysics.AnchoredSurrogates

| Kind | Name | Source line |
|---|---|---:|
| def | `KomorebiPhysics.AnchoredSurrogates.root` | 14 |
| theorem | `KomorebiPhysics.AnchoredSurrogates.root_pos` | 16 |
| theorem | `KomorebiPhysics.AnchoredSurrogates.root_sq` | 18 |
| theorem | `KomorebiPhysics.AnchoredSurrogates.root_ge_eigenvalue` | 21 |
| theorem | `KomorebiPhysics.AnchoredSurrogates.root_ge_one` | 26 |
| def | `KomorebiPhysics.AnchoredSurrogates.boundedSymbol` | 31 |
| theorem | `KomorebiPhysics.AnchoredSurrogates.boundedSymbol_apply` | 35 |
| theorem | `KomorebiPhysics.AnchoredSurrogates.boundedSymbol_norm_le` | 37 |
| theorem | `KomorebiPhysics.AnchoredSurrogates.root_normalized` | 43 |
| theorem | `KomorebiPhysics.AnchoredSurrogates.bounded_normalized` | 56 |
| theorem | `KomorebiPhysics.AnchoredSurrogates.bounded_tail` | 61 |
| theorem | `KomorebiPhysics.AnchoredSurrogates.bounded_anchored_exact` | 71 |
| theorem | `KomorebiPhysics.AnchoredSurrogates.bounded_anchored_tendsto` | 80 |
| theorem | `KomorebiPhysics.AnchoredSurrogates.bounded_zero_padded_exact` | 85 |
| def | `KomorebiPhysics.AnchoredSurrogates.regularizerSymbol` | 99 |
| theorem | `KomorebiPhysics.AnchoredSurrogates.regularizer_apply` | 103 |
| theorem | `KomorebiPhysics.AnchoredSurrogates.regularizer_mem_domain` | 105 |
| def | `KomorebiPhysics.AnchoredSurrogates.regularizerDomain` | 118 |
| theorem | `KomorebiPhysics.AnchoredSurrogates.bounded_transform_action` | 121 |
| def | `KomorebiPhysics.AnchoredSurrogates.cayleyCoeff` | 130 |
| theorem | `KomorebiPhysics.AnchoredSurrogates.denominator_norm_pm` | 132 |
| theorem | `KomorebiPhysics.AnchoredSurrogates.cayleyCoeff_norm` | 136 |
| def | `KomorebiPhysics.AnchoredSurrogates.cayleySymbol` | 140 |
| theorem | `KomorebiPhysics.AnchoredSurrogates.cayleySymbol_apply` | 142 |
| theorem | `KomorebiPhysics.AnchoredSurrogates.cayley_difference` | 144 |
| theorem | `KomorebiPhysics.AnchoredSurrogates.cayley_difference_norm` | 150 |
| theorem | `KomorebiPhysics.AnchoredSurrogates.cayley_tail` | 155 |
| theorem | `KomorebiPhysics.AnchoredSurrogates.cayley_anchored_exact` | 165 |
| theorem | `KomorebiPhysics.AnchoredSurrogates.cayley_anchored_tendsto` | 170 |
| theorem | `KomorebiPhysics.AnchoredSurrogates.cayley_zero_padded_exact` | 174 |
| theorem | `KomorebiPhysics.AnchoredSurrogates.cayley_transform_action` | 180 |
| theorem | `KomorebiPhysics.AnchoredSurrogates.cayley_preserves_norm` | 192 |

## KomorebiPhysics.SpectralErrorBounds

| Kind | Name | Source line |
|---|---|---:|
| theorem | `KomorebiPhysics.SpectralErrorBounds.denominator_norm_mono` | 14 |
| theorem | `KomorebiPhysics.SpectralErrorBounds.resolvent_error_endpoint` | 23 |
| theorem | `KomorebiPhysics.SpectralErrorBounds.resolvent_error_bound` | 36 |
| theorem | `KomorebiPhysics.SpectralErrorBounds.bounded_coefficient_mono` | 42 |
| theorem | `KomorebiPhysics.SpectralErrorBounds.bounded_error_endpoint` | 52 |
| theorem | `KomorebiPhysics.SpectralErrorBounds.bounded_error_rationalized` | 72 |
| theorem | `KomorebiPhysics.SpectralErrorBounds.bounded_error_bound` | 83 |
| theorem | `KomorebiPhysics.SpectralErrorBounds.cayley_error_endpoint` | 92 |
| theorem | `KomorebiPhysics.SpectralErrorBounds.cayley_error_bound` | 108 |
| theorem | `KomorebiPhysics.SpectralErrorBounds.wrong_anchor_not_norm` | 115 |
| theorem | `KomorebiPhysics.SpectralErrorBounds.bounded_wrong_anchor` | 121 |
| theorem | `KomorebiPhysics.SpectralErrorBounds.cayley_wrong_anchor` | 125 |
| theorem | `KomorebiPhysics.SpectralErrorBounds.heat_zero_error` | 129 |
| theorem | `KomorebiPhysics.SpectralErrorBounds.heat_zero_not_norm` | 134 |
| theorem | `KomorebiPhysics.SpectralErrorBounds.backward_heat_unbounded` | 143 |
| theorem | `KomorebiPhysics.SpectralErrorBounds.zero_parameter_resolvent_error` | 152 |
| theorem | `KomorebiPhysics.SpectralErrorBounds.resolvent_error_at_ten` | 158 |
| theorem | `KomorebiPhysics.SpectralErrorBounds.phase_tail_eigenvector` | 163 |
| theorem | `KomorebiPhysics.SpectralErrorBounds.identity_cutoff_strong` | 169 |
| theorem | `KomorebiPhysics.SpectralErrorBounds.identity_cutoff_norm_error` | 172 |

