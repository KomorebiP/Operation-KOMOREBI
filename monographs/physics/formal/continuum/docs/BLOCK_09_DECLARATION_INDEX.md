# Block 09 declaration index

144 new inventoried names: 113 theorem declarations, 29 definitions and two structures.

## KomorebiPhysics.GraphDomain

| Name | Kind | Source line |
|---|---|---:|
| `KomorebiPhysics.GraphDomain.graphMap` | def | 24 |
| `KomorebiPhysics.GraphDomain.graphNorm` | def | 29 |
| `KomorebiPhysics.GraphDomain.graphMap_fst` | theorem | 31 |
| `KomorebiPhysics.GraphDomain.graphMap_snd` | theorem | 33 |
| `KomorebiPhysics.GraphDomain.graphMap_injective` | theorem | 35 |
| `KomorebiPhysics.GraphDomain.graphNorm_sq` | theorem | 41 |
| `KomorebiPhysics.GraphDomain.graphNorm_nonneg` | theorem | 45 |
| `KomorebiPhysics.GraphDomain.graphNorm_zero` | theorem | 47 |
| `KomorebiPhysics.GraphDomain.graphNorm_eq_zero` | theorem | 49 |
| `KomorebiPhysics.GraphDomain.graphNorm_add_le` | theorem | 53 |
| `KomorebiPhysics.GraphDomain.graphNorm_smul` | theorem | 57 |
| `KomorebiPhysics.GraphDomain.graphNorm_neg` | theorem | 61 |
| `KomorebiPhysics.GraphDomain.norm_le_graphNorm` | theorem | 64 |
| `KomorebiPhysics.GraphDomain.action_norm_le_graphNorm` | theorem | 67 |
| `KomorebiPhysics.GraphDomain.graph_convergence_iff` | theorem | 71 |
| `KomorebiPhysics.GraphDomain.squared_graph_convergence_iff` | theorem | 90 |
| `KomorebiPhysics.GraphDomain.IsSymmetric` | def | 110 |
| `KomorebiPhysics.GraphDomain.symmetric_self_im_zero` | theorem | 112 |
| `KomorebiPhysics.GraphDomain.ofBounded` | def | 123 |
| `KomorebiPhysics.GraphDomain.ofBounded_apply` | theorem | 127 |

## KomorebiPhysics.CountableAtlas

| Name | Kind | Source line |
|---|---|---:|
| `KomorebiPhysics.StrongAtlas` | structure | 20 |
| `KomorebiPhysics.StrongAtlas.partialSum` | def | 31 |
| `KomorebiPhysics.StrongAtlas.energy` | def | 33 |
| `KomorebiPhysics.StrongAtlas.partial_tendsto` | theorem | 35 |
| `KomorebiPhysics.StrongAtlas.projected_inner` | theorem | 38 |
| `KomorebiPhysics.StrongAtlas.packets_orthogonal` | theorem | 42 |
| `KomorebiPhysics.StrongAtlas.partial_inner` | theorem | 46 |
| `KomorebiPhysics.StrongAtlas.partial_norm_sq` | theorem | 58 |
| `KomorebiPhysics.StrongAtlas.energy_hasSum` | theorem | 65 |
| `KomorebiPhysics.StrongAtlas.energy_summable` | theorem | 70 |
| `KomorebiPhysics.StrongAtlas.energy_tsum` | theorem | 72 |
| `KomorebiPhysics.StrongAtlas.finite_energy_le` | theorem | 75 |
| `KomorebiPhysics.StrongAtlas.partial_norm_le` | theorem | 80 |
| `KomorebiPhysics.StrongAtlas.ofFinite` | def | 86 |
| `KomorebiPhysics.DomainAtlas` | structure | 100 |
| `KomorebiPhysics.DomainAtlas.project` | def | 110 |
| `KomorebiPhysics.DomainAtlas.partialSum` | def | 115 |
| `KomorebiPhysics.DomainAtlas.project_coe` | theorem | 117 |
| `KomorebiPhysics.DomainAtlas.partial_coe` | theorem | 120 |
| `KomorebiPhysics.DomainAtlas.action_partial` | theorem | 124 |
| `KomorebiPhysics.DomainAtlas.GraphCompatible` | def | 128 |
| `KomorebiPhysics.DomainAtlas.graph_components` | theorem | 131 |
| `KomorebiPhysics.DomainAtlas.action_hasSum` | theorem | 136 |
| `KomorebiPhysics.DomainAtlas.graph_iff_action` | theorem | 141 |
| `KomorebiPhysics.DomainAtlas.graph_of_bounded_action` | theorem | 154 |

## KomorebiPhysics.CountableContinuity

| Name | Kind | Source line |
|---|---|---:|
| `KomorebiPhysics.DomainAtlas.amplitude` | def | 22 |
| `KomorebiPhysics.DomainAtlas.current` | def | 25 |
| `KomorebiPhysics.DomainAtlas.rate` | def | 27 |
| `KomorebiPhysics.DomainAtlas.amplitude_reverse` | theorem | 30 |
| `KomorebiPhysics.DomainAtlas.current_antisymm` | theorem | 36 |
| `KomorebiPhysics.DomainAtlas.current_self` | theorem | 42 |
| `KomorebiPhysics.DomainAtlas.internal_current_zero` | theorem | 47 |
| `KomorebiPhysics.DomainAtlas.partial_current` | theorem | 52 |
| `KomorebiPhysics.DomainAtlas.amplitude_hasSum_graph` | theorem | 58 |
| `KomorebiPhysics.DomainAtlas.current_hasSum_graph` | theorem | 63 |
| `KomorebiPhysics.DomainAtlas.amplitude_hasSum_strong` | theorem | 70 |
| `KomorebiPhysics.DomainAtlas.current_hasSum` | theorem | 82 |
| `KomorebiPhysics.DomainAtlas.current_row_abs_summable` | theorem | 88 |
| `KomorebiPhysics.DomainAtlas.current_row_tsum` | theorem | 91 |
| `KomorebiPhysics.DomainAtlas.current_tail_graph_bound` | theorem | 95 |
| `KomorebiPhysics.DomainAtlas.current_tail_strong_bound` | theorem | 108 |
| `KomorebiPhysics.DomainAtlas.hasDerivAt_energy` | theorem | 125 |
| `KomorebiPhysics.DomainAtlas.energy_derivative_graph_limit` | theorem | 140 |
| `KomorebiPhysics.DomainAtlas.hasDerivAt_energy_tsum` | theorem | 148 |
| `KomorebiPhysics.DomainAtlas.boundary_identity` | theorem | 156 |
| `KomorebiPhysics.DomainAtlas.boundary_tendsto` | theorem | 169 |
| `KomorebiPhysics.DomainAtlas.hasDerivAt_region` | theorem | 180 |
| `KomorebiPhysics.DomainAtlas.region_derivative_boundary_limit` | theorem | 187 |
| `KomorebiPhysics.GraphDomain.hasDerivAt_norm_sq_zero` | theorem | 205 |
| `KomorebiPhysics.GraphDomain.norm_sq_constant` | theorem | 211 |
| `KomorebiPhysics.GraphDomain.packet_energy_constant` | theorem | 220 |

## KomorebiPhysics.DiagonalDomain

| Name | Kind | Source line |
|---|---|---:|
| `KomorebiPhysics.DiagonalDomain.domain` | def | 23 |
| `KomorebiPhysics.DiagonalDomain.operator` | def | 38 |
| `KomorebiPhysics.DiagonalDomain.operator_apply` | theorem | 46 |
| `KomorebiPhysics.DiagonalDomain.weighted_single` | theorem | 50 |
| `KomorebiPhysics.DiagonalDomain.single_mem` | theorem | 58 |
| `KomorebiPhysics.DiagonalDomain.single` | def | 62 |
| `KomorebiPhysics.DiagonalDomain.single_coe` | theorem | 65 |
| `KomorebiPhysics.DiagonalDomain.operator_single` | theorem | 68 |
| `KomorebiPhysics.DiagonalDomain.coordinate` | def | 73 |
| `KomorebiPhysics.DiagonalDomain.coordinate_apply` | theorem | 77 |
| `KomorebiPhysics.DiagonalDomain.coordinateAtlas` | def | 80 |
| `KomorebiPhysics.DiagonalDomain.atlas` | def | 89 |
| `KomorebiPhysics.DiagonalDomain.action_project` | theorem | 93 |
| `KomorebiPhysics.DiagonalDomain.graph_compatible` | theorem | 99 |
| `KomorebiPhysics.DiagonalDomain.symmetric` | theorem | 106 |
| `KomorebiPhysics.DiagonalDomain.dense_domain` | theorem | 115 |
| `KomorebiPhysics.DiagonalDomain.adjoint_apply_coordinate` | theorem | 123 |
| `KomorebiPhysics.DiagonalDomain.adjoint_domain_le` | theorem | 131 |
| `KomorebiPhysics.DiagonalDomain.selfAdjoint` | theorem | 139 |
| `KomorebiPhysics.DiagonalDomain.closed` | theorem | 149 |

## KomorebiPhysics.SpectralGraph

| Name | Kind | Source line |
|---|---|---:|
| `KomorebiPhysics.SpectralGraph.norm_sq_tsum` | theorem | 18 |
| `KomorebiPhysics.SpectralGraph.norm_sq_summable` | theorem | 22 |
| `KomorebiPhysics.SpectralGraph.weighted_norm_sq` | theorem | 26 |
| `KomorebiPhysics.SpectralGraph.domain_iff` | theorem | 31 |
| `KomorebiPhysics.SpectralGraph.action_norm_sq` | theorem | 38 |
| `KomorebiPhysics.SpectralGraph.graph_weight_summable` | theorem | 44 |
| `KomorebiPhysics.SpectralGraph.graph_norm_sq` | theorem | 50 |
| `KomorebiPhysics.SpectralGraph.coordinate_tail_sq` | theorem | 57 |
| `KomorebiPhysics.SpectralGraph.graph_tail_sq` | theorem | 65 |
| `KomorebiPhysics.SpectralGraph.graph_tail_tendsto` | theorem | 82 |
| `KomorebiPhysics.SpectralGraph.graph_tail_series` | theorem | 96 |
| `KomorebiPhysics.SpectralGraph.graph_range_tail_tendsto` | theorem | 105 |
| `KomorebiPhysics.SpectralGraph.spectral_current_zero` | theorem | 113 |

## KomorebiPhysics.UnboundedExamples

| Name | Kind | Source line |
|---|---|---:|
| `KomorebiPhysics.UnboundedExamples.harmonicEigenvalue` | def | 16 |
| `KomorebiPhysics.UnboundedExamples.harmonic` | def | 18 |
| `KomorebiPhysics.UnboundedExamples.harmonicAtlas` | def | 21 |
| `KomorebiPhysics.UnboundedExamples.eigenvalue_pos` | theorem | 23 |
| `KomorebiPhysics.UnboundedExamples.harmonic_selfAdjoint` | theorem | 27 |
| `KomorebiPhysics.UnboundedExamples.harmonic_graph_compatible` | theorem | 30 |
| `KomorebiPhysics.UnboundedExamples.harmonic_domain` | theorem | 34 |
| `KomorebiPhysics.UnboundedExamples.basisState` | def | 38 |
| `KomorebiPhysics.UnboundedExamples.basis_norm` | theorem | 40 |
| `KomorebiPhysics.UnboundedExamples.basis_action` | theorem | 44 |
| `KomorebiPhysics.UnboundedExamples.basis_action_norm` | theorem | 49 |
| `KomorebiPhysics.UnboundedExamples.harmonic_unbounded` | theorem | 54 |
| `KomorebiPhysics.UnboundedExamples.no_bounded_extension` | theorem | 63 |
| `KomorebiPhysics.UnboundedExamples.shrinking` | def | 73 |
| `KomorebiPhysics.UnboundedExamples.shrinking_norm` | theorem | 76 |
| `KomorebiPhysics.UnboundedExamples.shrinking_action` | theorem | 82 |
| `KomorebiPhysics.UnboundedExamples.shrinking_action_norm` | theorem | 89 |
| `KomorebiPhysics.UnboundedExamples.eigenvalue_tendsto` | theorem | 92 |
| `KomorebiPhysics.UnboundedExamples.shrinking_strong` | theorem | 96 |
| `KomorebiPhysics.UnboundedExamples.shrinking_action_not_zero` | theorem | 102 |
| `KomorebiPhysics.UnboundedExamples.shrinking_not_graph` | theorem | 111 |
| `KomorebiPhysics.UnboundedExamples.shrinking_graph_sq` | theorem | 118 |
| `KomorebiPhysics.UnboundedExamples.graph_norm_not_ambient` | theorem | 122 |
| `KomorebiPhysics.UnboundedExamples.harmonic_current_zero` | theorem | 131 |

## KomorebiPhysics.DomainExamples

| Name | Kind | Source line |
|---|---|---:|
| `KomorebiPhysics.DomainExamples.hamiltonian` | def | 15 |
| `KomorebiPhysics.DomainExamples.op` | def | 18 |
| `KomorebiPhysics.DomainExamples.atlas` | def | 21 |
| `KomorebiPhysics.DomainExamples.symmetric` | theorem | 25 |
| `KomorebiPhysics.DomainExamples.graph_compatible` | theorem | 32 |
| `KomorebiPhysics.DomainExamples.state` | def | 35 |
| `KomorebiPhysics.DomainExamples.current_bridge` | theorem | 37 |
| `KomorebiPhysics.DomainExamples.exact_current` | theorem | 47 |
| `KomorebiPhysics.DomainExamples.exact_rate` | theorem | 51 |
| `KomorebiPhysics.DomainExamples.localCurve` | def | 58 |
| `KomorebiPhysics.DomainExamples.localCurve_zero` | theorem | 61 |
| `KomorebiPhysics.DomainExamples.generator_eq_rotation` | theorem | 65 |
| `KomorebiPhysics.DomainExamples.localCurve_hasDerivAt` | theorem | 71 |
| `KomorebiPhysics.DomainExamples.actual_packet_derivative` | theorem | 80 |
| `KomorebiPhysics.DomainExamples.current_hasSum_nonzero` | theorem | 86 |
| `KomorebiPhysics.DomainExamples.reverse_without_conjugation_false` | theorem | 89 |
