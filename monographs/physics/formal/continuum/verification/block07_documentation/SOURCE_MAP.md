# Source-to-Lean map

## Reference and conventions

Source: *Projector-Refinement Physics: Complete Unified Theory*, August 2026, 550 physical PDF pages. Chapter 2 occupies physical pages 17–19, printed pages 4–6. The master file and SHA-256 identity are recorded in `reference/source_manifest.json`.

The formal inner product is `inner ℂ`, conjugate-linear on the left and linear on the right. A finite index type represents the atlas. `H →L[ℂ] H` means a bounded, globally defined complex-linear operator. Composition is noncommutative multiplication. Skew-adjointness is supplied in the inner-product form

`∀ x y, inner ℂ (A x) y = -inner ℂ x (A y)`.

No unbounded adjoint domain, countable sum or continuum limit is hidden in this interface. The fine projector laws are assumptions defining an atlas; coarse projector laws are derived.

| Manuscript | Formal representative | Status and scope |
|---|---|---|
| (2.1)–(2.3), fine atlas laws | `Atlas` and preserved `PacketFamily` fields | Explicit hypotheses. Coordinate atlases furnish actual finite-dimensional realizations. |
| (2.4), packet vector | `Atlas.packet` | Definition `Pᵢ ψ`. |
| (2.5), operator corner | Preserved `PacketFamily.block` | Definition with receiving index first. |
| (2.6), (2.8), vector reconstruction | `Atlas.reconstruct_state` | Checked from the operator resolution. |
| (2.7), (2.9)–(2.10), operator reconstruction | Preserved `PacketFamily.reconstruct` | Freshly rechecked, arbitrary ring of operators. |
| (2.11), squared-norm decomposition | `Atlas.norm_sq_reconstruct` | Checked from self-adjointness and reconstruction, not assumed. |
| (2.12), coarse projectors | `Atlas.coarsen`, `Atlas.coarsen_proj` | Constructed from arbitrary finite address map, including empty fibers. |
| (2.13)–(2.14), coarse atlas laws | `Atlas.coarsen` uses preserved `coarse_mul` and `coarse_complete` | Proof-bearing definition included in axiom audit. |
| (2.15), coarse corners | `Atlas.coarsen_corner` | Checked double sum with original operator order preserved. |
| (2.16), flow and skew condition | `HasDerivAt ψ (A (ψ t)) t`, `IsSkew A` | Hypotheses. Not claims of flow existence. |
| (2.17)–(2.18), energies and currents | `Atlas.energy`, `Atlas.current`, `pairCurrent` | Actual norms and inner products. |
| (2.19)–(2.20), local balance | `Atlas.hasDerivAt_packet_energy` | Actual real-time derivative proved by the chain rule. |
| (2.21), antisymmetry | `pairCurrent_antisymm`, `Atlas.current_antisymm` | Requires skew-adjointness. |
| (2.22), diagonal zero | `pairCurrent_self`, `Atlas.current_diagonal` | Derived, not an input field. |
| (2.23), (2.29), total cancellation | `Atlas.total_current_zero`, `Atlas.hasDerivAt_sum_packet_energy`, `hasDerivAt_total_energy` | Finite antisymmetric cancellation and actual norm derivative. |
| Global conservation consequence | `total_energy_constant` | Requires flow equation at every real time; uses the real mean value theorem. |
| (2.24)–(2.28), supporting derivative identities | `hasDerivAt_norm_sq`, `Atlas.inner_packet_project` and current lemmas | Direct analytic proof terms; not every intermediate printed line is a separate theorem. |
| (2.30), Hamiltonian current sign | `hamiltonian_current` | Exactly `A = -i B` gives `+2 Im ⟪x, B y⟫`. Hermiticity is unnecessary for this formula alone. |
| (2.31), coarse energy | `Atlas.coarsen_energy` | Derived using `norm_sq_packet_sum`. |
| (2.32)–(2.33), coarse current | `Atlas.coarsen_current` | Coarse inner-product expression equals sum of fine currents. |
| (2.34), coarse continuity | `Atlas.hasDerivAt_coarse_energy` | Actual derivative expanded into fine currents. |
| (2.35)–(2.36), internal cancellation | `Atlas.coarse_internal_cancel`, `Atlas.current_boundary_balance`, `Atlas.hasDerivAt_subset_energy` | Exact energy derivative equals only incoming boundary flux for every finite subset. |
| (2.37)–(2.49), moving atlas | New `MovingAtlas` module; preserved finite-matrix `MovingFrames` retained | Actual bounded-operator and state derivatives on arbitrary-dimensional complex Hilbert spaces. Two-sided unitarity is explicit. Detailed map below. |
| (2.50)–(2.57), whole-object deformation | New `Deformation` module | Actual normed-algebra derivatives. Main inverse specialization assumes completeness and invertibility at the base point; inverse differentiability is proved. Detailed map below. |

## The principal checked balance theorem

Let `P` be the atlas, `A` a bounded skew operator, and assume the actual trajectory obeys `HasDerivAt ψ (A (ψ t)) t`. For every finite subset `s` of sectors,

```lean
HasDerivAt (fun u => ∑ i ∈ s, P.energy (ψ u) i)
  (∑ i ∈ s, ∑ j ∈ sᶜ, P.current A (ψ t) i j) t
```

This is `Atlas.hasDerivAt_subset_energy`. Its derivative is not supplied as an assumption. The input derivative is the original vector equation, and the conclusion is obtained by differentiating projected vector norms and cancelling internal currents.

## Nonvacuity and hypothesis sensitivity

`Examples.coordinateAtlas` constructs a valid atlas for every finite coordinate space. `Examples.rotation2` is the skew matrix `[[0,-1],[1,0]]`. At `Examples.state2 = (1,1)`, the receiving-first currents are exactly `J₀←₁ = -2`, `J₁←₀ = 2`. The state is intentionally unnormalized; its total squared norm is 2.

For comparison, the identity generator on ℂ has `pairCurrent 1 1 1 = 2`, and `Examples.identity_not_skew` proves it is not skew. Dropping the skew condition is therefore not a harmless simplification.

These examples prove exact statements. They are not numerical observations and are not an empirical model of a particular physical system.

## Block 01 count boundaries

The 37 new declarations consist of 32 general mathematical/analytic lemmas and five exact realization or hypothesis-sensitivity theorems. There are also proof-bearing definitions, counted separately among the 96 audited declarations. The 39 preserved theorem declarations include supporting results outside the narrow Chapter 2 equation list. Their presence is not 39 additional independently novel physical conclusions.


## Block 02: literal moving-frame and deformation map

Source: physical PDF page 19, printed page 6. The page was inspected as a rendered image because the parsed text misplaces derivative dots. In particular, (2.54) has **P_alpha dot(X) P_beta**, not a derivative of the right projector in the first term.

Let `C(U,V,X) = U X V` and `comm(K,X) = K X - X K`. Matrix multiplication and bounded-operator multiplication retain this order throughout.

| Source | New formal representatives | Hypotheses and conclusion |
|---|---|---|
| (2.37) | `MovingAtlas.unitaryAtlas` | Constructs the transported complete orthogonal atlas from a fine `Atlas` and both unitary identities; self-adjointness is proved, not inserted as a new input. |
| (2.38), (2.41) | `MovingAtlas.effectiveGenerator`, `hasDerivAt_moving_coordinates` | Defines the correct skew-generator convention and the actual transformed state `star(U) psi`. |
| (2.39), (2.40), (2.44), (2.49) | `differentiated_unitarity`, `left_connection_skew` | Differentiates `U* U = 1`; derives `Gamma* = -Gamma`. Real-time operator-norm derivative required. |
| (2.42) | `effective_generator_skew`, `isSkew_of_star` | Skewness of A is an explicit input; skewness of the effective generator and compatibility with Block 01's inner-product interface are conclusions. |
| (2.43), (2.46)–(2.48) | `hasDerivAt_operator_apply`, `coordinate_rate_identity`, `hasDerivAt_moving_coordinates` | Actual state derivative from the original flow. No derivative of the transformed state is assumed. |
| (2.45) | `hasDerivAt_adjoint_inverse` | Derives the adjoint/inverse rate from differentiated two-sided unitarity. |
| (2.50), (2.53) | `Deformation.transport`, `transportedFamily`, `transport_corner` | Definitions and algebraic preservation of exact idempotent resolutions. Generic similarity is not claimed to preserve self-adjointness. |
| (2.51), (2.52), (2.56), (2.57) | `transport_rate_identity`, `hasDerivAt_transport_pair`, `hasDerivAt_moving_projector` | Derives the rate `[dot(U) U^{-1}, P(t)]`. The main theorem obtains the inverse derivative automatically. |
| (2.54) | `hasDerivAt_triple`, `hasDerivAt_corner`, `hasDerivAt_whole_object` | Genuine derivative with intrinsic, left-frame, and right-frame terms; all terms derived by the product rule. |
| (2.55) | `inverse_pair_rate`, `hasDerivAt_inverse_pair`, `hasDerivAt_ring_inverse` | Three interfaces: arbitrary differentiable inverse pair; inverse curve with differentiability but no assumed rate; complete normed algebra with only derivative of U and invertibility at t. The final interface discharges inverse regularity. |

### Additional checked consequences, not separate claims copied from the master

`corner_rate_split` and `hasDerivAt_corner_covariant` derive

    d(P X Q)/dt = [K, P X Q] + P (dot(X) - [K,X]) Q.

`hasDerivAt_comoving_corner` handles an actual co-moving object, with `dot(X) = [K,X]`. Its laboratory derivative remains `[K,P X Q]`; it is not generally zero.

`sum_comm_of_resolution`, `sum_corner_rates`, and `hasDerivAt_reconstructed_corners` prove that reconstruction cancels all frame terms and recovers the actual derivative of X. The last theorem requires the resolution at the base point and actual derivatives of every projector there; it does not assume the conclusion's derivative.

`transport_coarse` and `hasDerivAt_coarse_projector` prove compatibility with finite regrouping. This is a moving-frame/coarsening compatibility result, not a claim that arbitrary refinement towers or continuum limits are finished.

`right_velocity_skew` proves the laboratory frame velocity is skew for a unitary curve. `inner_unitary`, `norm_sq_unitary`, and `unitary_atlas_energy` identify the actual laboratory packet norm with the co-moving energy. `hasDerivAt_moving_norm_sq`, `hasDerivAt_moving_packet_energy`, and `hasDerivAt_lab_packet_energy` connect the new moving atlas to the actual energy derivative results from Block 01.

### Exact witnesses

`DeformationExamples` uses the real two-by-two shear `U(t)=I+tN`, with `N=[[0,1],[0,0]]` and exact inverse `I-tN`. It proves `P(t)=P-tN`, its idempotence, and its actual entrywise derivative `-N`. These componentwise examples are separate finite-dimensional witnesses; the general theorems have normed-algebra derivative statements.

For `P=diag(1,0)`, `Q=diag(0,1)`, `X=diag(2,3)`, and `dot(X)=4N`, the three corner contributions are `4N`, `-3N`, and `2N`. The full rate is `3N`. Deleting any one term changes the result. Reversing the commutator sign also fails. At t=1, the transported idempotent is not symmetric, so a nonunitary frame cannot silently be treated as orthogonal.

### Block 02 counting

Three new modules contain **51** theorem declarations: Deformation **24**, MovingAtlas **16**, DeformationExamples **11**. There are **13** new definitions, including two proof-bearing atlas constructions. Together with the unchanged Block 01 library, the inventory contains **127 theorems** and **160 audited named declarations** in **10 mathematical modules**. These are declaration counts, not a count of independent physical laws or a full-edition completion percentage.


## Block 03: Chapter 4 extensions

Source: physical PDF pages 23–24, printed pages 10–11. The page image confirms the conjugation bar in (4.14). Prefixes below are relative to `KomorebiPhysics`.

| Source equations | Formal representatives | Status, assumptions and scope |
|---|---|---|
| (4.1) | `NonlinearFlow.field` and actual `HasDerivAt` hypotheses | State/time dependence is allowed; flow existence is not asserted. Skewness is needed at the trajectory point, not everywhere in the ambient state space. |
| (4.2)–(4.3) | Existing `Atlas.energy` / `Atlas.current` evaluated at `A (ψ t) t` | Definitions of actual projected norms and pair currents. |
| (4.4) | `NonlinearFlow.hasDerivAt_packet` | Actual derivative derived from the original vector flow. |
| (4.5) | `NonlinearFlow.current_antisymm`, `current_total_zero`, `hasDerivAt_total`, `hasDerivAt_sum_packets` | Skew-dependent cancellation; arbitrary-dimensional inner-product space, bounded operators, finite atlas. |
| Added nonlinear consequences | `NonlinearFlow.total_constant`, `sum_packets_constant`, `hasDerivAt_subset`, `hasDerivAt_coarse` | All-time conservation along a supplied trajectory, actual subsystem/coarse derivatives. |
| (4.6) | `MixedTransfer.generator`, `generator_hermitian`, derivative hypotheses | Hermiticity, positivity, trace one and the evolution equation have separate roles. No ODE or positivity-preservation theorem is assumed proved. |
| (4.7) | `MixedTransfer.MatrixAtlas.probability`, `trace_probability_real`, `probability_cast` | Real-valued definition is proved equal to the literal complex trace under Hermiticity. |
| (4.8) | `MixedTransfer.MatrixAtlas.current` | Receiving index first; exact +2 Im convention. |
| (4.9) | `MixedTransfer.hasDerivAt_entry`, `hasDerivAt_trace_mul`, `MatrixAtlas.hasDerivAt_probability` | Actual finite matrix derivative implies actual trace/probability derivative; desired balance is not assumed. |
| (4.10)–(4.11) | `MixedTransfer.MatrixAtlas.current_antisymm`, `current_diagonal`, `hasDerivAt_total_probability` | Uses Hermiticity and the proved conjugation identity. |
| (4.12)–(4.14) | `MixedTransfer.MatrixAtlas.trace_generator_resolved`, `amplitude_reverse`, `probability_rate` | Exact noncommutative trace order, cyclicity, and conjugation retained. |
| (4.15) | `MixedTransfer.pureState`, `trace_mul_pureState`, `MatrixAtlas.pureState_current` | Actual rank-one operator and Hermitian finite-vector pairing. |
| Added probability consequences | `MixedTransfer.MatrixAtlas.probability_nonneg`, `probability_normalized` | PSD and trace-one hypotheses imply actual finite probability bounds and normalization. |
| Added mixed trace/boundary results | `MixedTransfer.trace_constant`, `MatrixAtlas.hasDerivAt_subset_probability` | Given all-time flow implies trace constancy; actual subsystem derivative equals boundary flux. |
| (4.16)–(4.19) | `RefinementTower.push_comp`, `incidence_comp`, `Atlas.coarsen_coarsen_proj` | Genuine address maps; partition condition explicit. All entries being binary alone is insufficient. |
| (4.20) | `RefinementTower.push_eq_mulVec`, `Atlas.coarsen_coarsen_energy`, `coarsen_energy_incidence` | Actual coarse energies match matrix aggregation. |
| (4.21) | `RefinementTower.aggregateCurrent_comp`, `aggregateCurrent_incidence_comp`, `Atlas.coarsen_current_incidence`, `coarsen_coarsen_current` | Algebraic matrix theorem also holds for arbitrary real weights; atlas interpretation only for genuine partitions. |
| (4.22) | `RefinementTower.push_comp`, `pushList_eq`, `Atlas.coarsen_coarsen_packet`, `coarsen_coarsen_corner` | Two-stage maps may have different label spaces; arbitrary-depth list theorem uses one fixed label type. |
| Added mixed refinement | `MixedTransfer.MatrixAtlas.coarsen`, `coarsen_probability`, `coarsen_current`, `coarsen_coarsen_proj`, `hasDerivAt_coarse_probability` | Genuine coarse matrix atlas; probability/current are actual expressions, not new assumed fields. |
| (4.23)–(4.28) | Tensor-product mixed-state atlas/marginals | Deferred in Block 03; now checked in Block 04, with detailed map below. |
| (4.29)–(4.31) | `UniversalBalance.source_boundary_sum`, `hasDerivAt_subset`, `hasDerivAt_total` | Scalar balance is an explicit input at this abstract layer. Sources remain in the derivative. |
| (4.32)–(4.34) | `UniversalBalance.coarse_antisymm`, `coarse_row_sum`, `hasDerivAt_coarse` | Exact finite coarsening of source-driven balance. |
| (4.35)–(4.52) | Entropy, moments, Rényi and Lindblad targets | Deferred in Block 03. Information transport was checked in Block 04; Lindblad was subsequently checked in Block 05. |

Sixteen exact example theorems and six new isolated invalid controls are detailed in `BLOCK_03_PROOF_GUIDE.md`. There are 83 new theorem declarations, 210 cumulative theorems and 263 audited named declarations. Counts include support lemmas, not only primary source equations.


## Block 04: tensor marginals and information transport

Source: physical PDF pages 24–25, printed pages 11–12, including rendered source images. All tensor/partial-trace statements here use finite complex matrices. Generic information transport uses finite real packet families. The prefixes below are relative to `KomorebiPhysics`.

| Source | Formal representatives | Status and scope |
|---|---|---|
| (4.23) | `MixedTransfer.MatrixAtlas.tensor`, `tensor_proj` | Actual Kronecker atlas constructed, not postulated; proof-bearing definition audited. |
| (4.24)–(4.25) | `tensor_mul_proj`, `tensor_sum_proj` and tensor constructor | Joint orthogonality, Hermiticity and completeness proved from local atlas laws. |
| (4.26) | Tensor atlas's existing `probability`; `tensor_probability_normalized` | Real probability equals complex trace under Hermiticity; PSD and trace one imply bounds and normalization. |
| (4.27) | `tensor_sum_right_proj`, `tensor_marginal_left_trace`, `tensor_marginal_left` | Actual left marginal for every joint matrix; product-state assumption absent. |
| (4.28) | `tensor_sum_left_proj`, `tensor_marginal_right_trace`, `tensor_marginal_right` | Actual right marginal for every joint matrix. |
| Additional coarsening bridge | `tensor_coarsen_fst_proj`, `tensor_coarsen_snd_proj` | Forgetting a subsystem address equals the actual coarse atlas construction. |
| Additional product specialization | `tensor_product_trace`, `tensor_product_probability` | Probability factorization requires actual product input and Hermiticity; not asserted for general joint states. |
| Additional joint dynamics | `tensor_hasDerivAt_probability` | Actual joint-state probability derivative from original matrix flow, allowing general joint Hamiltonian. |
| Added reduced matrices | `PartialTrace.left/right`, `left/right_posSemidef`, `trace_left/right`, `left/right_density` | Entrywise constructions, PSD and trace conservation; not ODE positivity preservation. |
| Added reduction bridge | `PartialTrace.trace_local_left/right`, `probability_left/right` | Actual partial-trace marginal identification. |
| Added derivative bridge | `PartialTrace.hasDerivAt_left/right` | Actual reduced derivative obtained from actual joint matrix derivative. |
| (4.35) | Explicit scalar derivative/antisymmetry hypotheses; matrix-flow specializations | Balance is an input only in the abstract scalar interface; matrix interfaces derive it. Positivity is strict at the base time. |
| (4.36) | `InformationTransport.entropy` | Packet Shannon functional with natural logarithm; not von Neumann entropy. |
| (4.37) | `hasDerivAt_xlogx`, `hasDerivAt_entropy_raw` | Actual chain rule on the strictly positive domain. |
| (4.38)–(4.40) | `weighted_current_symmetry`, `hasDerivAt_entropy_current` | Finite antisymmetric symmetrization; no automatic monotonicity. |
| (4.41)–(4.42) | `powerSum`, `hasDerivAt_powerSum_raw`, `hasDerivAt_powerSum_current` | Actual fixed real exponent, not restricted to integer orders; positive bases. |
| (4.43)–(4.44) | `renyi`, `powerSum_pos`, `hasDerivAt_renyi_current` | Nonempty index type, positive moment proved, q≠1 explicit. No Shannon-limit assertion at q=1. |
| Added functional generality | `InformationTransport.hasDerivAt_functional` | Actual differentiable scalar functional chain rule under component current balance. |
| Added quantum bridge | `MixedTransfer.MatrixAtlas.hasDerivAt_packet_entropy`, `hasDerivAt_packet_powerSum`, `hasDerivAt_packet_renyi` | Start from original matrix HasDerivAt and Hermiticity; derive the scalar entropy/moment laws. |
| Added finite entanglement witness | `EntanglementWitness.partialTranspose_posSemidef_of_decomposition`, `QuantumInformationExamples.bell_not_finite_product_mixture` | Every explicit finite nonnegative pure-product mixture has PSD partial transpose; exact Bell pairing -1 excludes all such mixtures. Not claimed as a new physical law. |
| (4.45)–(4.52) | Lindblad jump matrix and diagonal population reduction | Deferred in Block 04; **now checked in Block 05**, with the map below. |

The complete declaration inventory contains all supporting algebraic and example lemmas. Block 04 adds 94 theorems and 15 definitions, yielding 304 cumulative theorems and 372 audited names. Its 28 exact-example theorems and eight new rejection controls are described in `BLOCK_04_PROOF_GUIDE.md`. The source's entropy formulas are not evaluated without their strict-domain hypotheses, and the packet-order q=1 singularity is not silently totalized into a claimed Shannon limit.


## Block 05: Lindblad jumps and detailed balance

Physical PDF pages 25–26, printed 12–13. The formulas and summation conditions were read from the page images. All formal representatives below are in `KomorebiPhysics`.

| Source | Formal representatives | Exact scope |
|---|---|---|
| (4.45) | `LindbladJumps.jump`, `jump_eq_smul`, `sqrt_rate_product` | Actual finite matrix unit with real square-root amplitude; nonnegative rate is explicit. |
| (4.46) | `LindbladJumps.dissipator`, `generator` | Full gain-minus-half-anticommutator sum over distinct ordered labels. |
| (4.47) | `population`, `population_cast`; `LindbladDynamics.population_normalized` | Real diagonal agrees with literal complex diagonal under Hermiticity; PSD and trace one imply normalized nonnegative populations. |
| (4.48) | `generator_diagonal`, `population_rate`, `hasDerivAt_population` | Matrix entry calculation then actual derivative from the original matrix HasDerivAt, not assumed scalar balance. |
| (4.49)–(4.50) | `current`, `current_antisymm`, `current_diagonal`, `total_current_zero` | Receiving-first gain minus loss with proved antisymmetry and cancellation. |
| (4.51)–(4.52) | `jump_gain`, `jump_adjoint_mul` | Full matrix identities for arbitrary coherent input, with source support and square-root normalization proved. |
| Added conservation | `trace_dissipator`, `trace_generator`, `hasDerivAt_trace`, `trace_constant`, `hasDerivAt_subset_population` | Actual finite trace and subsystem laws. An actual trajectory is supplied; not an existence theorem. |
| Added coherences | `LindbladCoherence.escapeRate`, `generator_offdiag`, `hasDerivAt_coherence` | Half-sum of escape rates; self-jumps excluded as in source. Not an integrated solution. |
| Added full quantum dynamics | `LindbladDynamics.quantumGenerator`, `quantumCurrent`, `hasDerivAt_quantum_population`, `hasDerivAt_quantum_subset` | Coherent Hamiltonian current retained alongside dissipative current; Hermiticity hypotheses explicit. |
| Added coarse/information bridges | `hasDerivAt_coarse_population`, `hasDerivAt_entropy`, `hasDerivAt_powerSum`, `hasDerivAt_renyi`, `hasDerivAt_quantum_entropy` | Actual matrix input. Strict-positive information domain; fixed q, q!=1/nonempty for Renyi. No automatic coarse-rate closure. |
| (4.53) | `DetailedBalance.Balanced`, `conductance_symm`, `equilibrium_current` | Positive fixed reference and detailed balance explicit; positivity/normalization separate as needed. |
| (4.54) | `relativeEntropy`, `hasDerivAt_relative_term`, `hasDerivAt_relativeEntropy_raw` | Actual derivative of sum p log(p/pi), with positive p and pi. |
| (4.55)–(4.57) | `hasDerivAt_relativeEntropy`, `dissipation`, `current_factor`, `activeFluxCost`, `dissipation_eq_activeFlux`, `hasDerivAt_relativeEntropy_flux` | Conductance form includes zero-rate edges; explicit inactive-edge zero, active log arguments proved positive. |
| (4.56), (4.58) | `log_difference_product_nonneg`, `log_ratio_product_nonneg`, `dissipation_nonneg`, `relativeEntropy_deriv_nonpos`, `relativeEntropy_antitoneOn` | Derived sign and nonincrease on supplied positive trajectories on convex time sets. |
| Added matrix-to-dissipation bridge | `hasDerivAt_matrix_relativeEntropy`, `matrix_relativeEntropy_deriv_nonpos` | Original Lindblad matrix derivative discharges scalar population equation. |
| Added normalized/equality claims | `relativeEntropy_nonneg`, `dissipation_zero_iff`, `zero_dissipation_eq_reference` | Gibbs inequality; ratios equal on active edges; equilibrium equality additionally assumes every distinct rate positive and normalized p,pi. |
| Added exact witnesses | `LindbladExamples.generator_value`, `local_population_derivatives`, `local_coherence_derivative`, `local_relativeEntropy_derivative`, `wrong_reference_derivative` | Actual local matrix derivatives; exact rational rates and logarithms. Not global positive solutions. |
| (4.59)–(4.67) | Deferred in Block 05; now covered in Block 06 | Actual tower and finite-expansion analytic result; detailed map below. |

**Domain correction:** source (4.55) has a flux ratio that is undefined on two zero fluxes in ordinary real analysis. The formal statement uses an explicit inactive-edge convention and proves equivalence on active edges, rather than depending on Lean's totalized log/division. The source's positive-population hypothesis is retained. The packet relative entropy is not quantum density-operator relative entropy.


## Block 06: refinement-cancellation tower

Source: physical PDF page 26, printed 13, Chapter 4.9, equations (4.59)–(4.67). The actual page image was inspected. Namespace prefixes below are relative to `KomorebiPhysics`.

| Source | Formal representatives | Exact scope |
|---|---|---|
| (4.59) | `RefinementCancellation.expansion`; finite input `hexp` in the analytic theorems | Finite truncation with c(k) at degree k+1. Infinite formal-series convergence is **not proved** or assumed from notation. |
| (4.60) | `RefinementCancellation.table`, `table_zero`, `table_base_column` | Actual sampled function, arbitrary finite row/column indices. |
| (4.61) | `tower`, `table_succ`, `denominator_pos`, `denominator_ne_zero` | Literal dyadic recurrence, generalized to fixed real b>1; all denominators valid. |
| Exact cancellation behind (4.62) | `coefficient_product`, `tower_monomial`, `coefficient_cancel`, `tower_expansion_exact`, `tower_error_identity` | Algebraic proof on any real vector space, independent of analytic remainder hypotheses. |
| (4.62) | `RefinementAsymptotics.dyadic_order_improvement`, `cancellation_isBigO` | Actual original finite expansion with O(h^(m+1)) implies actual transformed bound on the punctured neighborhood filter. |
| Added one-sided/fixed-column versions | `positive_step_order_improvement`, `table_order_improvement` | Positive-step-only input need not extend to negative h. Fixed finite m,j and fixed b. |
| Added limit and little-o | `cancellation_isLittleO`, `tower_tendsto` | Genuine asymptotic/limit conclusions; convergence requires positive error order. |
| (4.63)–(4.64) | `RefinementExamples.quadratic_response`, `first_level_second_order` | Exact polynomial identity and separate original cubic-order remainder theorem. |
| (4.65)–(4.67) | `RefinementExamples.dyadic_first`, `dyadic_second`, `dyadic_third` | Actual formulas for arbitrary real vector-valued f. |
| Added fourth level | `RefinementExamples.dyadic_fourth` | Exact coefficient formula with denominator 315. |
| Added sharpness | `RefinementCancellation.coefficient_ne_zero_above`; `RefinementAsymptotics.power_not_isBigO_higher`, `tower_not_extra_order` | Degree m+1 survives and is not automatically O(h^(m+2)). Genuine asymptotic failure, not only sampled mismatch. |
| Added explicit error constants | `RefinementBounds.amplification_product`, `cancellation_bound` | Finite-radius remainder bound with proved scale-domain closure. |
| Added sample-error propagation | `perturbation_bound`, `noisy_cancellation_bound`; `RefinementExamples.sampleNoise_amplified` | Truncation plus sample perturbation, with exact failure of universal contraction. |
| Added nonzero analytic witness | `RefinementExamples.cubicFamily_input_asymptotic`, `cubicFamily_output_asymptotic`, `cubicFamily_actual_error` | Original cubic residual is proved, general theorem applied, actual output h^3/8. |
| Added zero-value independence | `RefinementCancellation.tower_congr_nonzero` | Values assigned at h=0 do not affect nonzero sampled towers. |
| (5.1)–(5.21) | Deferred in Block 06; now checked in Block 07 | Actual positive/overlapping effects, moving-source and coarse balance laws; map below. |

The full inventory records every support declaration. Block 06 adds 81 theorems and eight definitions. Its analytic assumptions do not certify a later physical discretization or prove continuum/empirical adequacy. Source (4.59)'s infinite-series interpretation remains a separate question; the finite-order version sufficient for (4.62) is proved.


## Block 07: positive effects, moving sources and exact postprocessing

Source: physical PDF pages 27–28, printed 14–15. Page 28 was inspected through Files. Files did not return page 27's image, so the already mounted master was rendered locally and its image inspected. The dot in (5.15) is on U before multiplication by U*: K=dot(U)U*. The master bytes and page identities are unchanged.

The names below are relative to `KomorebiPhysics`. A finite effect atlas has only positivity, the Hermitian pairing identity and the operator sum as fields. No probability derivative, source cancellation, current balance, idempotence or orthogonality is an assumed field. Completeness of H is needed by the unitary-adjoint section, not by the basic inner-product/derivative or coarsening results.

| Source | Formal representatives | Exact scope |
|---|---|---|
| (5.1) | `EffectAtlas` | Finite positive Hermitian bounded effects summing to I, no sharpness or pairwise commutation. |
| (5.2) | `effectExpectation`, `EffectAtlas.probability`, `probability_real`, `probability_cast` | Actual Born expectation, proved real; not squared effected norm. |
| Positive probability interpretation | `probability_nonneg`, `probability_sum`, `probability_le_norm_sq`, `normalized` | Nonnegative probabilities sum to norm squared; normalized state gives [0,1] probabilities. |
| (5.3)–(5.4) | `effectExchange`, `EffectAtlas.current`, `current_antisymm` | Literal antisymmetrized exchange; antisymmetry holds by construction even without skewness. |
| (5.5) | `hasDerivAt_effectExpectation`, `EffectAtlas.hasDerivAt_probability` | Derivative genuinely derived from original vector trajectory and fixed effect. |
| (5.6)–(5.10) | `current_row_sum`, `current_row_sum_skew`, `reconstruct`, `total_current_zero`, `hasDerivAt_total` | Both partition sums evaluated; skewness identifies current row with actual derivative. |
| (5.11)–(5.12) | `EffectAtlas.derivative_sum`, `source`, `source_sum`, `source_real`, `source_cast`; `differentiated_selfAdjoint` | Actual operator derivatives give zero total velocity and Hermitian velocities, hence actual real sources with zero sum. |
| (5.13) | `EffectAtlas.hasDerivAt_moving_probability`, `hasDerivAt_moving_total`, `hasDerivAt_moving_subset` | Actual derivatives of original state/effects; source retained, subsystem keeps only boundary exchange. |
| (5.14) | `EffectAtlas.conjugate`, `conjugate_probability` | Constructed positive Hermitian transported resolution. Algebraic constructor requires UU*=I; derivative theorem records stronger local identities. |
| (5.15)–(5.16) | `hasDerivAt_conjugate_effect`, `conjugate_velocity_skew`, `hasDerivAt_conjugate_probability`, `conjugate_source_sum` | Actual operator-norm derivative, K=dot(U)U*, correct commutator sign. |
| (5.17) | `EffectAtlas.coarsen`, `coarsen_effect` | Actual address-map fibers, hence genuine binary column-normalized incidence; no arbitrary overlapping binary duplication. |
| (5.18)–(5.20) | `coarsen_probability_incidence`, `coarsen_source_incidence`, `coarsen_current_incidence` | Actual p^c=Rp, s^c=Rs and J^c=RJR^T, not abstract symbols with equalities assumed. |
| (5.21) | `hasDerivAt_moving_coarse_probability`, `hasDerivAt_coarsen_effect` | Actual coarse derivative with derived coarse velocity. |
| Added composition | `coarsen_comp_effect`, `coarsen_comp_probability`, `coarsen_comp_current`, `coarsen_conjugate_effect` | Sequential address coarsening and transported/coarsened effects agree. |
| Added nonbinary extension | `EffectAtlas.postprocess`, `postprocess_probability`, `postprocess_current_matrix`, `postprocess_source`, `hasDerivAt_postprocess_probability`, `postprocess_comp_effect` | Fixed nonnegative real column-normalized weights; actual constructed effects and weighted derivatives. |
| (5.32) | `EffectAtlas.ofAtlas`, `ofAtlas_probability`, `ofAtlas_current` | Actual inclusion of sharp atlases and recovery of old energy/current. |
| Added nonzero witnesses | `EffectExamples.soft_probabilities`, `soft_probability_not_squared_norm`, `soft_overlap`, `soft_current_nonzero`, `soft_probability_hasDerivAt` | Exact normalized two-dimensional state, positive nonprojector overlapping effects, local flow witness. |
| Added moving-source witness | `EffectExamples.oscillatingAtlas_derivative`, `oscillating_sources`, `oscillating_probability_hasDerivAt` | Globally positive sine weights, constant state/zero generator, actual derivative 1/2 at t=0. Not a claimed unitary orbit. |
| (5.22)–(5.31) | Not formalized in Block 07 | Next: actual Parseval-channel realization, analysis/synthesis, direct sum and dilation. |

Block 07 adds 89 theorem declarations, 19 definitions and one structure. The explicit general theory includes noncommuting effects because no commutation hypothesis is imposed; the supplied rational two-dimensional witness itself commutes. All derivative conclusions are conditional on stated actual trajectory/effect derivatives, not claims of dynamical existence or empirical adequacy.
