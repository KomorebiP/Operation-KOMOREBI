# Block 11 — Declaration index

All names below are included in the cumulative axiom audit. Source lines refer to the active release files. Counts include supporting lemmas and exact examples.

## KomorebiPhysics.L2DominatedLimits

| Kind | Declaration | Source line |
|---|---|---:|
| theorem | `KomorebiPhysics.L2DominatedLimits.tendsto_zero` | 20 |
| theorem | `KomorebiPhysics.L2DominatedLimits.tendsto` | 42 |
| theorem | `KomorebiPhysics.L2DominatedLimits.tendsto_of_vector_bound` | 55 |
| theorem | `KomorebiPhysics.L2DominatedLimits.hasDerivAt_of_dominated_slope` | 64 |

## KomorebiPhysics.SpectralTimeContinuity

| Kind | Declaration | Source line |
|---|---|---:|
| def | `KomorebiPhysics.SpectralEvolution.evolution` | 20 |
| theorem | `KomorebiPhysics.SpectralEvolution.evolution_apply` | 22 |
| theorem | `KomorebiPhysics.SpectralEvolution.phase_hasDerivAt` | 27 |
| theorem | `KomorebiPhysics.SpectralEvolution.coordinate_hasDerivAt` | 33 |
| theorem | `KomorebiPhysics.SpectralEvolution.coordinate_norm` | 38 |
| theorem | `KomorebiPhysics.SpectralEvolution.continuous_orbit` | 43 |
| theorem | `KomorebiPhysics.SpectralEvolution.norm_preserved` | 59 |
| theorem | `KomorebiPhysics.SpectralEvolution.norm_difference` | 62 |
| theorem | `KomorebiPhysics.SpectralEvolution.domain_preserved` | 67 |
| def | `KomorebiPhysics.SpectralEvolution.domainEvolution` | 76 |
| theorem | `KomorebiPhysics.SpectralEvolution.domainEvolution_coe` | 79 |
| theorem | `KomorebiPhysics.SpectralEvolution.operator_commutes` | 83 |
| theorem | `KomorebiPhysics.SpectralEvolution.evolution_zero` | 91 |
| theorem | `KomorebiPhysics.SpectralEvolution.evolution_add` | 94 |
| theorem | `KomorebiPhysics.SpectralEvolution.evolution_inverse` | 98 |
| theorem | `KomorebiPhysics.SpectralEvolution.domain_iff` | 102 |
| theorem | `KomorebiPhysics.SpectralEvolution.domainEvolution_zero` | 110 |
| theorem | `KomorebiPhysics.SpectralEvolution.domainEvolution_add` | 115 |
| theorem | `KomorebiPhysics.SpectralEvolution.graphNorm_preserved` | 120 |
| theorem | `KomorebiPhysics.SpectralEvolution.graph_continuity` | 129 |
| theorem | `KomorebiPhysics.SpectralEvolution.phase_increment_bound` | 139 |
| theorem | `KomorebiPhysics.SpectralEvolution.coordinate_increment_bound` | 151 |

## KomorebiPhysics.SpectralSchrodinger

| Kind | Declaration | Source line |
|---|---|---:|
| theorem | `KomorebiPhysics.SpectralEvolution.slope_coordinate_bound` | 17 |
| theorem | `KomorebiPhysics.SpectralEvolution.velocity_coordinate_norm` | 37 |
| theorem | `KomorebiPhysics.SpectralEvolution.orbit_hasDerivAt` | 46 |
| theorem | `KomorebiPhysics.SpectralEvolution.orbit_hasDerivAt_zero` | 67 |
| theorem | `KomorebiPhysics.SpectralEvolution.differentiable_orbit` | 71 |
| theorem | `KomorebiPhysics.SpectralEvolution.deriv_orbit` | 75 |
| theorem | `KomorebiPhysics.SpectralEvolution.norm_deriv` | 80 |
| theorem | `KomorebiPhysics.SpectralEvolution.continuous_velocity` | 86 |
| theorem | `KomorebiPhysics.SpectralEvolution.domain_increment_bound` | 93 |
| theorem | `KomorebiPhysics.SpectralEvolution.derivative_coordinates` | 106 |
| theorem | `KomorebiPhysics.SpectralEvolution.mem_domain_of_hasDerivAt` | 113 |
| theorem | `KomorebiPhysics.SpectralEvolution.differentiableAt_iff_mem_domain` | 123 |
| theorem | `KomorebiPhysics.SpectralEvolution.not_differentiable_outside` | 131 |

## KomorebiPhysics.SpectralSolutions

| Kind | Declaration | Source line |
|---|---|---:|
| theorem | `KomorebiPhysics.GraphDomain.solution_unique` | 19 |
| theorem | `KomorebiPhysics.SpectralEvolution.exists_unique_solution` | 42 |
| theorem | `KomorebiPhysics.SpectralEvolution.solution_formula` | 54 |
| theorem | `KomorebiPhysics.SpectralEvolution.packet_hasDerivAt` | 68 |
| theorem | `KomorebiPhysics.SpectralEvolution.packet_current_hasSum` | 76 |
| theorem | `KomorebiPhysics.SpectralEvolution.region_boundary_limit` | 84 |
| theorem | `KomorebiPhysics.SpectralEvolution.total_packet_energy` | 94 |
| theorem | `KomorebiPhysics.SpectralEvolution.coordinate_energy_constant` | 98 |
| theorem | `KomorebiPhysics.SpectralEvolution.coordinate_current_zero` | 106 |
| theorem | `KomorebiPhysics.SpectralEvolution.action_norm_preserved` | 112 |

## KomorebiPhysics.SpectralTimeApproximation

| Kind | Declaration | Source line |
|---|---|---:|
| theorem | `KomorebiPhysics.SpectralEvolution.cutoff_commutes` | 15 |
| theorem | `KomorebiPhysics.SpectralEvolution.cutoff_error_time` | 23 |
| theorem | `KomorebiPhysics.SpectralEvolution.cutoff_uniform_in_time` | 28 |
| def | `KomorebiPhysics.SpectralEvolution.cutoffDomain` | 38 |
| theorem | `KomorebiPhysics.SpectralEvolution.cutoffDomain_coe` | 41 |
| theorem | `KomorebiPhysics.SpectralEvolution.cutoffDomain_action` | 47 |
| theorem | `KomorebiPhysics.SpectralEvolution.cutoff_hasDerivAt` | 55 |
| theorem | `KomorebiPhysics.SpectralEvolution.cutoff_velocity_error` | 63 |
| theorem | `KomorebiPhysics.SpectralEvolution.cutoff_velocity_uniform` | 71 |

## KomorebiPhysics.SpectralEvolutionExamples

| Kind | Declaration | Source line |
|---|---|---:|
| def | `KomorebiPhysics.SpectralEvolutionExamples.roughState` | 17 |
| theorem | `KomorebiPhysics.SpectralEvolutionExamples.roughState_apply` | 25 |
| theorem | `KomorebiPhysics.SpectralEvolutionExamples.roughState_weighted` | 27 |
| theorem | `KomorebiPhysics.SpectralEvolutionExamples.roughState_not_domain` | 30 |
| theorem | `KomorebiPhysics.SpectralEvolutionExamples.roughState_nonzero` | 37 |
| theorem | `KomorebiPhysics.SpectralEvolutionExamples.rough_orbit_continuous` | 42 |
| theorem | `KomorebiPhysics.SpectralEvolutionExamples.rough_orbit_not_differentiable` | 45 |
| theorem | `KomorebiPhysics.SpectralEvolutionExamples.rough_coordinates_differentiable` | 50 |
| theorem | `KomorebiPhysics.SpectralEvolutionExamples.rough_cutoffs_differentiable` | 55 |
| theorem | `KomorebiPhysics.SpectralEvolutionExamples.rough_cutoff_action_apply` | 60 |
| theorem | `KomorebiPhysics.SpectralEvolutionExamples.rough_cutoff_action_norm_sq` | 68 |
| theorem | `KomorebiPhysics.SpectralEvolutionExamples.rough_cutoff_velocity_norm_sq` | 83 |
| def | `KomorebiPhysics.SpectralEvolutionExamples.halfTurnTime` | 91 |
| theorem | `KomorebiPhysics.SpectralEvolutionExamples.halfTurnTime_tendsto` | 93 |
| theorem | `KomorebiPhysics.SpectralEvolutionExamples.phase_halfTurn` | 98 |
| theorem | `KomorebiPhysics.SpectralEvolutionExamples.operator_distance_le_two` | 105 |
| theorem | `KomorebiPhysics.SpectralEvolutionExamples.halfTurn_operator_distance` | 116 |
| theorem | `KomorebiPhysics.SpectralEvolutionExamples.not_operator_norm_continuous` | 127 |
| def | `KomorebiPhysics.SpectralEvolutionExamples.coherentState` | 138 |
| theorem | `KomorebiPhysics.SpectralEvolutionExamples.coherentState_coe` | 142 |
| theorem | `KomorebiPhysics.SpectralEvolutionExamples.coherentState_norm` | 145 |
| theorem | `KomorebiPhysics.SpectralEvolutionExamples.coherentState_zero` | 155 |
| theorem | `KomorebiPhysics.SpectralEvolutionExamples.coherentState_one` | 158 |
| theorem | `KomorebiPhysics.SpectralEvolutionExamples.coherent_orbit_normalized` | 161 |
| theorem | `KomorebiPhysics.SpectralEvolutionExamples.coherent_orbit_hasDerivAt` | 165 |
| def | `KomorebiPhysics.SpectralEvolutionExamples.coherentAmplitude` | 172 |
| theorem | `KomorebiPhysics.SpectralEvolutionExamples.coherentAmplitude_zero` | 176 |
| theorem | `KomorebiPhysics.SpectralEvolutionExamples.coherentAmplitude_hasDerivAt` | 179 |
| theorem | `KomorebiPhysics.SpectralEvolutionExamples.coherent_observable_hasDerivAt` | 198 |
| theorem | `KomorebiPhysics.SpectralEvolutionExamples.coherent_observable_rate_nonzero` | 208 |

