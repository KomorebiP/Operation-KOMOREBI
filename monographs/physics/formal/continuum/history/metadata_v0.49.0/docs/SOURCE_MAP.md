# Source-to-Lean map

## Reference and conventions

Source: *Projector-Refinement Physics: Complete Unified Theory*, August 2026, 550 physical PDF pages. Chapter 2 occupies physical pages 17–19, printed pages 4–6. The master file and SHA-256 identity are recorded in `reference/source_manifest.json`.

The formal inner product is `inner ℂ`, conjugate-linear on the left and linear on the right. For Chapters 2–5 below, a finite index type represents the atlas. Block 09 has the separate infinite-index interface documented at the end. `H →L[ℂ] H` means a bounded, globally defined complex-linear operator. Composition is noncommutative multiplication. Skew-adjointness is supplied in the inner-product form

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
| (5.22)–(5.31) | Deferred in Block 07; checked in Block 08 | See constructed Parseval and universal square-root dilation below. |

Block 07 adds 89 theorem declarations, 19 definitions and one structure. The explicit general theory includes noncommuting effects because no commutation hypothesis is imposed; the supplied rational two-dimensional witness itself commutes. All derivative conclusions are conditional on stated actual trajectory/effect derivatives, not claims of dynamical existence or empirical adequacy.


## Block 08: Parseval reconstruction, universal finite dilation and cycles

Source: physical PDF pages 28–29, printed 15–16. Both page images inspected. All names below are relative to `KomorebiPhysics`. Finite outcomes and bounded operators on complete complex Hilbert spaces; no finite-dimensionality required.

| Source | Formal representatives | Exact scope |
|---|---|---|
| (5.22) | `ParsevalFamily`, `ParsevalFamily.effectAtlas` | Given actual heterogeneous bounded channels and their explicit Parseval-resolution assumption; effects constructed with laws proved. |
| (5.23) | `probability_eq_norm_sq` | Actual Born probability equals squared channel norm, not squared effected-vector norm. |
| (5.24) | `reconstruct_state`, `reconstruct_inner`, `norm_sq_sum` | Exact finite synthesis, inner product and norm reconstruction. |
| (5.25)–(5.27) | `channelBlock`, `reconstruct_operator` | Full double-sum formula for arbitrary bounded X, with the correct source adjoint. |
| (5.28)–(5.29) | `analysis`, `synthesis`, `synthesis_eq_adjoint`, `analysisIsometry` | Actual finite L2 Hilbert sum and separately constructed adjoint synthesis. |
| (5.30) | `ChannelDilation.inclusion`, `coordinate`, `coordinateAtlas` | Coordinate maps, idempotence, pairwise orthogonality, Hermiticity, identity sum all proved. |
| (5.31) | `adjoint_analysis_comp_analysis`, `effect_compression`, `compressed_probability` | Isometry and actual effect compression, not given as input fields. |
| Added universal construction | `EffectAtlas.sqrtChannel`, `sqrtChannel_factor`, `sqrtFamily`, `dilation_compression`, `exists_finite_dilation` | Actual positive square roots applied to arbitrary finite bounded effects. Complete Hilbert H, not finite-dimensional; Mathlib CFC reused. |
| Added range/projector boundary | `rangeProjection_idempotent`, `rangeProjection_adjoint`, `rangeProjection_fixed_iff`, `liftOperator_one` | Q=VV* projects onto the image; lift(I)=Q, not automatically ambient I. |
| Added operator reconstruction bridge | `liftOperator_recover`, `liftOperator_mul`, `liftOperator_adjoint`, `lifted_block` | Supported operator lift is injective, multiplicative and adjoint preserving. |
| Added compression defect | `compress_mul_defect`, `effect_square_defect`, `effect_defect_norm` | Arbitrary compression need not preserve multiplication. Exact positive defect equals squared escape from the analysis image. |
| Added actual dynamics | `liftOperator_skew`, `lifted_flow`, `dilated_current`, `hasDerivAt_dilated_probability` | Fixed analysis map, original vector derivative, actual enlarged evolution and same currents. No constructed ODE solution. |
| (5.33)–(5.34) | `CycleGauge.IsCycle`, `add_row_sum`, `hasDerivAt_gauged_probability` | Antisymmetric zero-row-sum ambiguity of continuity. |
| Added converse/coarse cycle | `difference_cycle_iff`, `boundary_zero`, `coarse_cycle` | Equal divergence iff difference is cycle for antisymmetric arrays; finite subsystem and coarse invariance. |
| Exact witnesses | `DilationExamples`, `CycleGauge.triangle_nonzero` | Proper scalar isometry; diagonal-only 337/625 vs full 1; defect 144/625; nonzero soft current/local derivative; nonzero zero-divergence cycle. |
| (5.35)–(5.43) | Historical numerical residuals, not rerun | Not converted into exact new proofs or empirical validation. |
| (6.1)–(6.9), (6.26)–(6.36) | Next target | Domain-preserving countable projectors, graph convergence and actual infinite-limit current formula require separate construction. |

Block 08 adds 98 theorem declarations, 21 definitions and one structure. The universal construction closes the finite bounded factorization/dilation gap left in Block 07, not the countable/unbounded gap. The historical guides remain dated records; this source map and the current claim ledger record the updated state.

## Block 09 — Explicit domains and countable continuity

Physical PDF pages 30–33 (printed 17–20) were read and the source images inspected. The master file hash is unchanged. Generic `LinearPMap` means a linear map on an explicit domain, not a bounded everywhere-defined map. `StrongAtlas` uses an unconditional finite-subset net. The old finite/bounded modules are unchanged.

| Source | Formal representatives | Scope |
|---|---|---|
| (6.1)–(6.2) | `DomainAtlas.partialSum`, `GraphDomain.graphMap`, `graphNorm_sq` | Actual domain sum and actual L2 graph norm. |
| (6.3)–(6.6) | `StrongAtlas`, `DomainAtlas`, `GraphCompatible` | Explicit independent assumptions for generic atlases. |
| (6.7)–(6.9) | `squared_graph_convergence_iff`, `graph_convergence_iff`, `graph_components` | Both state and generator-image convergence proved. |
| (6.10)–(6.11) | `DiagonalDomain.operator`, `SpectralGraph.domain_iff`, `UnboundedExamples.basis_action` | Constructed spectral multiplier, maximal weighted-l2 domain. Not differential-oscillator identification. |
| (6.12), hierarchy | Not covered | Form-domain and strict inclusions still separate. |
| (6.13)–(6.14) | `SpectralGraph.graph_tail_series`, `graph_range_tail_tendsto` | Exact infinite weighted tail and actual limit. |
| (6.15)–(6.25) | Not covered | Bounded surrogates and topology-specific operator norm estimates next. |
| (6.26) | Original ambient `HasDerivAt` assumption | No construction of the unitary group. |
| (6.27)–(6.33) | `DomainAtlas.hasDerivAt_energy`, `energy_derivative_graph_limit` | Actual energy derivative and literal graph-compatible current limit. |
| Added fixed-row strengthening | `current_hasSum`, `current_row_abs_summable`, `current_tail_strong_bound` | Symmetry/domain invariance give scalar row convergence from strong reconstruction; no full action limit or double summability. |
| (6.34)–(6.35) | `amplitude_reverse`, `current_antisymm` | Correct conjugation and sign; formal symmetry is sufficient. |
| (6.36)–(6.37) | `boundary_identity`, `region_derivative_boundary_limit` | Finite receiving region, eventual containing finite subset and actual derivative. |
| (6.38)–(6.40) | `StrongAtlas.partial_norm_sq`, `energy_hasSum`, `energy_tsum` | Finite Pythagoras and true infinite Parseval. |
| (6.41) | `GraphDomain.packet_energy_constant` | Conservation along supplied all-time solution, not proof of (6.26). |
| Added realization | `DiagonalDomain.selfAdjoint`, `closed`, `graph_compatible` | Actual adjoint equality and graph compatibility of maximal weighted multiplier. |
| Added tests | `UnboundedExamples`, `DomainExamples` | Genuine unbounded and topology-limit tests; separate finite nonzero derivative witness. |
| (6.42) onward | Not covered | Infinite coarse domains and rearrangement still need proofs. |

See `BLOCK_09_PROOF_GUIDE.md` and the complete declaration index. Block 09 does not supersede the remaining continuum, gravitational, cosmological or empirical boundaries.


## Block 10 — Bounded spectral surrogates and true truncation topologies

Physical PDF page 31 (printed 18), equations (6.15)–(6.25). The source image was inspected and the master hash is unchanged. The generic multiplier is an actual bounded operator on l2(N,C). Physical specializations use the already constructed maximal harmonic spectral operator. Historical “not covered” rows above describe their dated block; this section and the current claim ledger supersede the Block 09 surrogate gap within this stated spectral scope.

| Source or added target | Formal representatives | Exact scope |
|---|---|---|
| Bounded diagonal foundation | `BoundedSpectral.diagonal`, `norm_diagonal`, `diagonal_adjoint` | Square-summability and boundedness constructed; actual supremum norm and adjoint. |
| Actual S_M | `SpectralTruncation.cutoff`, `HarmonicSurrogates.cutoff_eq_old_partial` | Bounded coordinate cutoff identified with old finite projector sum. |
| (6.15), (6.18) | `resolvent_mem_domain`, `resolventDomain`, `resolvent_right_inverse`, `resolvent_left_inverse`, `resolvent_truncation_norm`, `resolvent_truncation_tendsto` | Harmonic spectral gap, all real eta including zero; genuine inverse with domain range. |
| Added sharp resolvent endpoint | `SpectralErrorBounds.resolvent_error_endpoint`, `resolvent_error_bound` | First omitted index realizes tail supremum; bound uniform in eta. |
| (6.19) | `heatSymbol`, `heat_truncation_exact`, `heat_truncation_tendsto` | Constructed for t>=0; convergence only for fixed t>0. |
| Added time-boundary tests | `heat_zero_error`, `heat_zero_not_norm`, `backward_heat_unbounded` | Exact error one at zero time and unbounded coefficient sequence at negative time. |
| (6.20)–(6.21) | `phaseSymbol`, `phase_tail_eigenvector`, `phase_truncation_exact`, `phase_truncation_strong`, `phase_truncation_not_norm` | Actual phase coefficients and every tail eigenvector; strong cutoff convergence but norm error exactly one. |
| Partial (6.26) construction support | `phase_zero`, `phase_add`, `phase_inverse`, `phase_preserves_norm` | Actual norm-preserving phase family with algebraic group law. Time continuity/domain invariance/derivative remain open. |
| (6.16) | `boundedSymbol`, `regularizer_mem_domain`, `regularizerDomain`, `bounded_transform_action` | Actual harmonic spectral regularizer and domain-correct H composition; not a general unbounded functional calculus. |
| (6.17) | `cayleySymbol`, `cayley_transform_action`, `cayley_preserves_norm` | Actual Cayley formula through the proved resolvent range. |
| (6.22)–(6.23) | `SpectralTruncation.anchored_sandwich` | Exact operator construction S_M D_a S_M + c(I-S_M), with c=1 for the source transforms. |
| (6.24) | `bounded_anchored_exact`, `bounded_anchored_tendsto`, `bounded_error_endpoint` | Literal supremum, actual limit and harmonic endpoint. |
| (6.25) | `cayley_anchored_exact`, `cayley_anchored_tendsto`, `cayley_error_endpoint` | Literal supremum, actual limit and harmonic endpoint; denominator/factor two retained. |
| Added generic sharp criterion | `SpectralTruncation.anchored_norm_iff`, `SpectralErrorBounds.wrong_anchor_not_norm` | Norm convergence iff the bounded scalar symbol tends to the specified anchor. |
| Added exact rate bounds | `bounded_error_rationalized`, `bounded_error_bound`, `cayley_error_bound` | Quantified real errors; no floating-point certification. |
| Added exact failure of zero padding | `bounded_zero_padded_exact`, `cayley_zero_padded_exact`, `identity_cutoff_norm_error` | Error one at every finite cutoff despite strong convergence on each fixed state. |

The source's general self-adjoint functional-calculus interpretation remains separate from this constructed harmonic diagonal realization. All 47 previous mathematical modules are preserved. Form domains, infinite coarse cells and the later physical continuum limits are not covered by this block.


## Block 11: constructed spectral evolution and sharp domain boundary

Source: physical PDF pages 31–33, printed 18–20. This section supersedes the Block 10 open statement about phase time continuity/domain derivatives, specifically for the real diagonal model. Prior general theorem hypotheses are preserved.

| Source or added result | Checked declarations | Scope |
|---|---|---|
| (6.26), constructed exponential evolution | `SpectralEvolution.continuous_orbit`, `domain_preserved`, `orbit_hasDerivAt` | Arbitrary real diagonal spectrum on l2. True strong continuity, maximal-domain preservation, actual ambient derivative. |
| Added existence and uniqueness | `SpectralEvolution.exists_unique_solution`, `solution_formula`, `GraphDomain.solution_unique` | Global domain solutions. Existence is diagonal-specific; uniqueness alone applies to supplied symmetric-operator solutions. |
| Added exact derivative-domain boundary | `SpectralEvolution.differentiableAt_iff_mem_domain` | At every real time, actual l2 derivative iff initial state belongs to D(H). |
| (6.27)–(6.35) | `SpectralEvolution.packet_hasDerivAt`, `packet_current_hasSum` | General compatible domain atlas, actual constructed flow and genuine summability. |
| (6.37) | `SpectralEvolution.region_boundary_limit` | Finite receiving region, finite-subset boundary-current limit. |
| (6.38)–(6.41) | `SpectralEvolution.total_packet_energy` | Every l2 initial state, Parseval and norm conservation without differentiating an infinite sum. |
| Added graph continuity | `SpectralEvolution.graph_continuity`, `graphNorm_preserved` | Actual graph norm, not a graph derivative. |
| Added uniform-in-time cutoff estimates | `SpectralEvolution.cutoff_uniform_in_time`, `cutoff_velocity_uniform` | One fixed state; velocity requires its generator-domain membership. |
| Added exact counterexamples | `SpectralEvolutionExamples` | Rough reciprocal state, cutoff velocity norm squared M, norm distance two at small times, coherent normalized observable rate 12/25. |

Section 6.5 infinite coarse cells remains the next obligation. No all-state differentiability, uniform unit-ball cutoff convergence, general Stone theorem, non-diagonal existence, form-domain hierarchy or empirical physics validation follows from this block.


## Block 12 — Section 6.5, infinite-cell refinement

Physical PDF page 33, printed page 20; image inspected. The unchanged source hash is recorded in the reference manifest. All labels below refer to actual source definitions and Lean proof terms, not an assumption that an infinite sum exists.

| Source obligation | Declarations (prefix KomorebiPhysics) | Exact scope |
|---|---|---|
| (6.42), strong coarse projector | `StrongAtlas.cell`, `cell_sum`, `coarsenInfinite` | Complete complex Hilbert space; unconditional strong orthogonal fine resolution; arbitrary infinite/empty fibers. Positivity/self-adjointness/idempotence/boundedness proved. |
| (6.43)–(6.44), energy | `cell_energy_hasSum`, `coarsenInfinite_energy` | Actual scalar HasSum and equality to actual coarse vector norm squared; no generator assumption. |
| Domain of (6.45) | `DomainAtlas.cell_pair_mem_graph`, `cell_mem_domain`, `coarsenClosed` | Closed T plus full finite-subset graph compatibility derives coarse domain preservation. `coarsenOfPreserves` accepts an independently proved alternative. |
| (6.46)–(6.47), iterated interpretation | `coarse_amplitude_iterated_hasSum`, `coarse_current_iterated_hasSum`, `coarse_current_reverse_hasSum` | Symmetry and coarse domain preservation; both inner and outer series certified. No independent graph hypothesis at this scalar layer. |
| (6.46)–(6.47), product-index interpretation | `coarse_amplitude_product`, `coarse_current_product` | Explicit joint summability required, separately for complex amplitudes and real currents. |
| Added composition | `StrongAtlas.coarsen_cell`, `coarsenInfinite_comp` | Actual operator equality for sequential infinite coarsening. |
| Added actual infinite-cell derivative | `DomainAtlas.infinite_cell_hasDerivAt` | Original ambient Schrödinger derivative supplied; coarse bounded projection differentiated, not an infinite termwise exchange. |
| Constructed-solution version | `SpectralCells.constructed_coarse_hasDerivAt` | Closed real diagonal model and graph-compatible fine atlas; original derivative supplied by the constructed spectral solution theorem. |
| Spectral masks | `SpectralCells.mask_apply`, `operator_mask`, `graph_mask_hasSum` | Actual arbitrary cell, maximal-domain invariance and weighted graph sum. Spectral currents zero. |
| Nonzero infinite-cell test | `InfiniteCoarseExamples.infinite_even_energy_hasDerivAt` | Infinite even/odd fibers in l2, non-spectral reflected atlas and unbounded harmonic H; global normalized two-mode solution, rate 288/625. |
| Summability warning | `CurrentSummationExamples.not_joint_summable` | Abstract row/column finite-support antisymmetric array with both iterated sums zero, but no joint summability. Not claimed to be a particular Hamiltonian realization. |

The display of a real or complex `tsum` alone is not treated as existence. The inner/outer `HasSum` proofs are separate from the joint-product hypothesis. Full-edition coverage beyond this scope is not inferred from the count of declarations. Section 6.6 residue/ladder targets remain next.


## Block 13 — Section 6.6 residue projectors and ladders

Physical PDF page 33, printed page 20. Positive modulus is an explicit `NeZero M` input. The full source page image was inspected. The completed current cumulative production report is PASS. Scope remains the explicit hypotheses below.

| Source | Actual declarations | Scope and interpretation |
|---|---|---|
| (6.48) finite character formula | `ResidueCharacters.exponential_selection`, `ResidueProjectors.projector_number_average` | Actual number-spectrum phases, literal exponential weights, canonical ZMod representatives. Negative receiving phase and normalization retained. |
| (6.49) infinite mask identity | `ResidueProjectors.projector_apply`, `projector_eq_mask`, `projector_hasSum` | Equality of bounded operators on every l2 vector. Infinite subseries has a proved HasSum. |
| (6.49) support/energy/domain consequences | `atlas`, `atlas_proj`, `projector_idempotent`, `projector_orthogonal`, `projector_complete`, `projector_energy`, `projector_mem_domain` | Proof-bearing atlas construction; bounded norm and maximal real-diagonal domain preservation. |
| (6.50) lowering/raising amplitudes | `LadderDomains.lower_single_zero`, `lower_single_succ`, `raise_single` | Actual partially defined operators. Vacuum has its own theorem. |
| (6.50) omitted domain obligations made explicit | `domain_iff`, `lower_mem_iff`, `raise_mem_iff`, `lower`, `raise` | Exact common maximal first-moment domain. Raw sequence maps become Hilbert outputs only after summability proofs. |
| (6.50) dagger interpretation strengthened | `lower_adjoint`, `raise_adjoint`, `lower_closed`, `raise_closed`, `ladder_norm_difference` | Genuine unbounded adjoint equalities and norm identities; no unproved product-domain commutator. |
| (6.51) lowering routing | `LadderRouting.packet_mem`, `packet`, `lower_packet`, `lower_routing` | Domain-valued input, all positive moduli and all domain states; labels computed in ZMod. |
| (6.52) raising routing | `raise_packet`, `raise_routing`, `raise_allowed_corner` | Correct plus-one receiving lane, actual sqrt amplitudes, no assumed second ladder application. |
| Exact tests / added consequences | `LadderExamples` and `ResidueCharacters.wrong_sign_three` | Wraparound, nonzero outputs, vacuum, wrong sign/normalization/amplitude and genuine unboundedness. |

Qualified names use the `KomorebiPhysics` prefix. The complete 101-name list is in `BLOCK_13_DECLARATION_INDEX.md`. This block does not prove coherent-state factorial-lane weights, differential-oscillator identification, harmonic half-power hierarchy, ladder product-domain identities or a canonical commutation theorem on an actual product domain. The next literal source is Section 6.7's domain-sensitive resolvent commutator.


## Block 14 — Domain-correct resolvent commutator certificates

Physical PDF page 34 (printed 21), Section 6.7. The source page image was inspected and the original PDF is unchanged. Historical pending Section 6.7 entries are superseded by this block only within its stated hypotheses and after the completed audit passes.

| Source or addition | Formal representatives | Scope |
|---|---|---|
| (6.53) | `ResolventDomain.shifted`, `BoundedCommutator.shifted_commutator`, `Certificate.packet_resolvent` | Actual domain restriction and both inverse identities; no off-domain application of T. |
| (6.54) | `Certificate.commutator_identity` | [R,P]=-RBR with a genuine bounded extension B of [T,P]. P need not be a projector or reduce T. |
| (6.55) | `Certificate.commutator_norm_bound`, `commutator_state_bound` | True operator norms and their statewise consequence. |
| (6.56) | `shifted_coercive`, `Certificate.nonreal_norm_bound`, `imaginary_axis_commutator_bound` | Derived from symmetry and actual inverse; eta!=0 explicit. |
| Added construction | `DiagonalResolvents.certificate`, `range_mem`, `right_inverse`, `left_inverse` | Arbitrary real diagonal sequences, all nonreal complex z, maximal l2 domain. |
| Added converse | `Certificate.commutator_zero_iff` | Zero resolvent commutator iff invariant domain and zero generator commutator on it. |
| Added parameter control | `Certificate.difference_identity`, `commute`, `difference_norm_nonreal` | Actual inverse comparisons, sign z-w. |
| Added exact tests | `NonreducingPacket`, `ResolventExamples` | Infinite harmonic model; actual nonreducing packet and B; norm B=12/25, leakage at eta=0 is 16/25 and squared leakage at eta=1 is 2304/40625. |

See `BLOCK_14_PROOF_GUIDE.md` and `BLOCK_14_DECLARATION_INDEX.md`. General inverse existence outside the diagonal realization and Section 6.8 reconstruction remain separate.


# Block 15 — Section 6.8 (physical page 34 / printed page 21)

The literal source page image was inspected. The status of the new mapping is subordinate to the completed Block 15 cumulative report.

## C6-RECONSTRUCTION-STRONG — 6.57, 6.60–6.62

Actual bounded sandwiches on complex normed spaces, explicit uniform contraction and strong convergence. No compactness or operator-norm convergence inferred.

- `KomorebiPhysics.StrongReconstruction.error_identity`
- `KomorebiPhysics.StrongReconstruction.state_error_bound`
- `KomorebiPhysics.StrongReconstruction.compression_strong`
- `KomorebiPhysics.StrongReconstruction.perturbed_compression_strong`

## C6-RECONSTRUCTION-COMPACT — 6.58, 6.63–6.64

Actual IsCompactOperator X, strongly convergent self-adjoint contractions on a complete complex Hilbert space. Finite-net left proof and compact Gram-operator right proof. Self-adjointness is sufficient, not claimed necessary. Strong convergence alone is not promoted to adjoint convergence.

- `KomorebiPhysics.StrongReconstruction.comparison_bound`
- `KomorebiPhysics.CompactReconstruction.uniform_compact`
- `KomorebiPhysics.CompactReconstruction.compact_left`
- `KomorebiPhysics.CompactReconstruction.right_error_sq_bound`
- `KomorebiPhysics.CompactReconstruction.compact_right`
- `KomorebiPhysics.CompactReconstruction.compact_compression`

## C6-HS-CLASS — Added foundation for 6.59, 6.65

Square-summable actual bounded-operator columns form an actual lp-2 vector. Basis independence, adjoint invariance, norm inequalities and ideal membership proved. The total scalar formula hsNorm is interpreted as a norm only under IsHS. Not a complete bundled Schatten theory.

- `KomorebiPhysics.HilbertSchmidtCore.IsHS`
- `KomorebiPhysics.HilbertSchmidtCore.columns`
- `KomorebiPhysics.HilbertSchmidtCore.columns_norm`
- `KomorebiPhysics.HilbertSchmidtCore.entries_summable`
- `KomorebiPhysics.HilbertSchmidtCore.basis_independent`
- `KomorebiPhysics.HilbertSchmidtCore.norm_basis_independent`
- `KomorebiPhysics.HilbertSchmidtCore.norm_adjoint`
- `KomorebiPhysics.HilbertSchmidtCore.left_norm_bound`
- `KomorebiPhysics.HilbertSchmidtCore.right_norm_bound`
- `KomorebiPhysics.HilbertSchmidtCore.opNorm_le`
- `KomorebiPhysics.HilbertSchmidtCore.norm_eq_zero_iff`

## C6-RECONSTRUCTION-HS — 6.59, 6.65

Actual dominated convergence of squared columns under a proved summable bound. Right convergence uses proved adjoint invariance and self-adjoint cutoffs; errors are proved HS. No unverified infinite double-sum interchange.

- `KomorebiPhysics.HilbertSchmidtReconstruction.left_energy_tendsto`
- `KomorebiPhysics.HilbertSchmidtReconstruction.left_norm_tendsto`
- `KomorebiPhysics.HilbertSchmidtReconstruction.right_norm_tendsto`
- `KomorebiPhysics.HilbertSchmidtReconstruction.compression_error_mem`
- `KomorebiPhysics.HilbertSchmidtReconstruction.compression_norm_tendsto`
- `KomorebiPhysics.HilbertSchmidtReconstruction.compression_opNorm_tendsto`

## C6-RECONSTRUCTION-ATLAS — Constructed cutoffs for 6.57–6.59

Actual finite-subset operator sum of a StrongAtlas. Orthogonality, contraction and strong convergence are proved. Finite numbers of sectors do not imply finite-dimensional ranges. Countable and arbitrary-label atlas nets supported.

- `KomorebiPhysics.AtlasReconstruction.cutoff`
- `KomorebiPhysics.AtlasReconstruction.cutoff_norm_le`
- `KomorebiPhysics.AtlasReconstruction.cutoff_idempotent`
- `KomorebiPhysics.AtlasReconstruction.cutoff_selfAdjoint`
- `KomorebiPhysics.AtlasReconstruction.cutoff_strong`
- `KomorebiPhysics.AtlasReconstruction.bounded_reconstruction`
- `KomorebiPhysics.AtlasReconstruction.compact_reconstruction`
- `KomorebiPhysics.AtlasReconstruction.hs_reconstruction`

## C6-RECONSTRUCTION-GRAPH — 6.66–6.67

Actual partially defined T and domain-valued cutoff input. GraphCompatible supplies action convergence. Ambient norm limit, not graph-norm convergence of generator images or automatic second-domain membership. Constructed maximal diagonal model instantiates the general theorem.

- `KomorebiPhysics.GraphReconstruction.reconstructed`
- `KomorebiPhysics.GraphReconstruction.error_identity`
- `KomorebiPhysics.GraphReconstruction.error_bound`
- `KomorebiPhysics.GraphReconstruction.graph_error_bound`
- `KomorebiPhysics.GraphReconstruction.tendsto`
- `KomorebiPhysics.GraphReconstruction.cofinal_reconstruction`
- `KomorebiPhysics.ReconstructionExamples.diagonal_graph_reconstruction`

## C6-HS-EXACT-TAIL — Added exact example

Actual multiplier 2^(-n) on infinite l2. HS squared norm 4/3; residual squared HS norm (4/3)4^(-M) and operator norm 2^(-M). Nonzero at every finite cutoff. Exact HasSum and operator norms, no numerical truncation.

- `KomorebiPhysics.HilbertSchmidtExamples.geometric`
- `KomorebiPhysics.HilbertSchmidtExamples.geometric_hasSum`
- `KomorebiPhysics.HilbertSchmidtExamples.geometric_isHS`
- `KomorebiPhysics.HilbertSchmidtExamples.residual_sandwich`
- `KomorebiPhysics.HilbertSchmidtExamples.residual_hasSum`
- `KomorebiPhysics.HilbertSchmidtExamples.residual_hs_norm_sq`
- `KomorebiPhysics.HilbertSchmidtExamples.residual_opNorm`
- `KomorebiPhysics.HilbertSchmidtExamples.residual_ne_zero`
- `KomorebiPhysics.HilbertSchmidtExamples.cutoff_two_exact`

## C6-CUTOFF-HYPOTHESIS-COUNTEREXAMPLE — Added boundary test for 6.58

Uniformly bounded S_n=I+|e0><e_(n+1)| converges strongly while compact rank-one sandwich error is exactly one. Adjoints fail strong convergence. These S_n are not asserted contractive or orthogonal. Separate orthogonal-cutoff identity error is one. Infinite identity is not HS.

- `KomorebiPhysics.ReconstructionExamples.packet_compact`
- `KomorebiPhysics.ReconstructionExamples.packet_idempotent`
- `KomorebiPhysics.ReconstructionExamples.sheared_norm_le`
- `KomorebiPhysics.ReconstructionExamples.sheared_strong`
- `KomorebiPhysics.ReconstructionExamples.sheared_packet_error`
- `KomorebiPhysics.ReconstructionExamples.sheared_compact_not_norm`
- `KomorebiPhysics.ReconstructionExamples.adjoint_not_strong`
- `KomorebiPhysics.ReconstructionExamples.sheared_not_selfAdjoint`
- `KomorebiPhysics.ReconstructionExamples.identity_not_hs`
- `KomorebiPhysics.ReconstructionExamples.identity_norm_error`

The isolated phrase “S_N approaches I strongly” is not sufficient for arbitrary compact right sandwiches. The checked statements use self-adjoint contractive cutoffs constructed from the atlas, and a genuine compact counterexample disproves the overly broad reading. The historical (6.68)–(6.69) numerical residuals were not rerun. Earlier pending 6.8 notes in this map are historical and superseded only within this stated scope.
\n\n## Block 16: finite differential no-go and corner-algebra resolution\n\nSource: physical PDF pages 36–38, printed 23–25, Chapter 7. Namespace prefixes are relative to `KomorebiPhysics`.\n\n| Source | Formal representatives | Exact scope |\n|---|---|---|\n| (7.1)–(7.8) | `PointwiseNoGo.atom_mul_self`, `atom_derivative_coordinate`, `map_atom_eq_zero`, `derivation_eq_zero`, `finite_source_no_go` | Finite product `ι → ℂ`, ordinary pointwise product, complex-linear derivation. Not every finite-dimensional commutative algebra. |\n| (7.9) | Stronger structural theorem above | Historical rank checks for N=2..8 not rerun; the exact general finite-label no-go is proved instead. |\n| (7.10)–(7.11) | `finite_source_no_go`; `CornerExamples.nonzero_finite_matrix_derivation` | Exact contrast: pointwise conjunction cannot support a nonzero derivation, while the noncommutative matrix algebra does. |\n| (7.12)–(7.14) | `CornerDerivation.delta`, `delta_mul` | Actual finite matrix expression and exact Leibniz. |\n| (7.15) | `delta_conjTranspose`, `delta_preserves_hermitian` | Hermitian generator hypothesis explicit. |\n| (7.16)–(7.23) | `trace_delta`, `trace_integration_by_parts`, `trace_delta_mul_add` | Exact trace cyclicity/integration by parts; no numerical residual. |\n| (7.24)–(7.30) | `CornerCurvature.curvature`, `commutator_jacobi`, `derivation_commutator`, `derivations_commute_of_generators_commute` | Exact inner-derivation curvature/Jacobi identity. Added central-curvature theorem separates matrix value from induced action. |\n| (7.31)–(7.32) | `CornerReconstruction.reconstruct`, `reconstruct_delta` | Actual complete orthogonal packet family. |\n| (7.33)–(7.35) | `insert_resolution_left/right`, `corner_delta_path`, `corner_delta_path_products` | Intermediate packet inserted explicitly in both commutator terms. |\n| (7.36)–(7.37) | `coarseProjector`, `coarse_corner`, `coarse_delta_corner` | Actual coarse finite sums and exact fine-corner regrouping. |\n| Added exact witnesses | `CornerExamples.delta_K_L_exact`, `curvature_action_on_Z_exact`, `offdiag_corner_exact`, `exact_trace_ibp_nonzero_left/right` | Nonzero 2x2 derivation, curvature action, corner phase and trace-sign checks. |\n\nBlock 16 adds 90 theorem declarations and reaches 1,461 cumulative theorems / 1,731 audited names. Equations (7.38)–(7.44) are historical floating residuals and were not rerun; their algebraic target identities above are checked exactly.\n
## Block 19 — Exact 1D continuum frequency and velocity

Source: physical PDF pages 40–41, printed pages 27–28, Chapter 8.1. All leading-positive-energy asymptotics are stated on the positive-spacing filter `𝓝[>] 0`; the exact signed principal frequency is odd in spacing.

| Source | Formal representatives | Exact scope |
|---|---|---|
| (8.11) exact-frequency asymptotic | `Relativistic1DContinuumLimit.principalPhase_expansion_isBigO`, `positiveFrequency_expansion_isBigO`, `tendsto_positiveFrequency` | Actual principal branch for sufficiently small positive spacing; `E ≠ 0`. Derived through normalized sine-square, a proved square-root expansion, and an actual arcsine remainder. |
| (8.12) mass-shell defect | `positiveFrequency_sq_sub_poly_sq_isBigO`, `positiveFrequency_mass_shell_isBigO` | Exact-frequency square, not only the Block 18 polynomial candidate. Remainder `O(ε⁴)` and coefficient `-m²k²/3`. |
| (8.14) continuum group velocity | `normalizedVelocityNumerator_expansion_isBigO`, `eventually_positiveGroupVelocity_eq_normalized_div`, `positiveGroupVelocity_expansion_isBigO` | Exact formula from (8.13), normalized by positive spacing; denominator lower bound derived from `radial → E`. |
| Actual derivative bridge | `eventually_abs_shell_lt_one`, `eventually_hasDerivAt_positiveGroupVelocity` | Proves the asymptotic velocity expression is the actual momentum derivative of `positiveFrequency` eventually. |
| Support for inverse step | `sinQ_expansion_isBigO`, `radial_expansion_isBigO`, `arcsin_cubic_expansion_isBigO`, `phaseInput_expansion_isBigO` | Explicit analytic chain; no assumed inverse-cosine series or division by zero. |
| Exact witnesses | `Relativistic1DContinuumExamples` | `m=k=1`: frequency coefficient `-1/(6√2)`, shell defect `-1/3`, velocity limit `1/√2`, and actual derivative specialization. |

This closes the nondegenerate one-dimensional continuum bridge. It does not assert a two-sided `+E` expansion, handle `E=0` by totalized division, or establish finite-spacing Lorentz invariance. Chapter 8.2's exact `4×4` Clifford walk remains next.


# Block 20 — Chapter 8.2 exact three-dimensional sector

Physical PDF page 41, printed page 28. The literal source targets are equations (8.18)–(8.30). All qualifications below remain subordinate to the completed cumulative verifier.

| Source | Formal representatives | Scope and interpretation |
|---|---|---|
| (8.18)–(8.20) Clifford algebra | `RelativisticClifford3D.alpha_clifford`, `alpha_beta_anticommute`, `beta_sq`, `alpha_sq` | Explicit complex `4×4` matrices; no abstract Clifford structure assumed. Hermiticity and traces are additional checked facts. |
| (8.21)–(8.25) palindromic update | `DiracWalk3D.massHalf`, `xHalf`, `yHalf`, `zFull`, `walk` | Literal matrix exponentials and explicit parenthesized seven-factor product. |
| Exact factor calculus | `InvolutionExponential4.exp_beta_closed`, `exp_alphaX_closed`, `exp_alphaY_closed`, `exp_alphaZ_closed`, `closedFactor_sandwich_closedFactor` | Spatial exponential identities transported through a proved invertible Clifford bridge; exact unitarity and determinant-one factors. |
| Exact update reduction | `DiracWalk3D.walk_eq_closedWalk`, `walk_unitary`, `det_walk`, `trace_walk` | The closed Clifford form is derived from the literal product, not used as its definition. |
| (8.26) microcell convention | `Relativistic3DExamples.microcell`, `two_mul_microcell` | Algebraic spacing identity only; no separate position-space locality implementation. |
| (8.27), (8.30) shell | `DiracWalk3D.shell`, `Dispersion3D.phase`, `cos_phase`, `frequency`, `cos_frequency_spacing` | Principal arccos branch; frequency shell requires nonzero spacing. |
| Quadratic walk identity | `Dispersion3D.coefficient_norm_real`, `vectorPart_sq`, `walk_quadratic` | Added exact support connecting Clifford coefficient norm to the characteristic polynomial. |
| (8.28) characteristic polynomial | `Spectrum3D.det_cliffordPencil`, `characteristic_polynomial` | Exact determinant `(z²-2Cz+1)²` for the actual walk. |
| (8.29) doubled phase branches | `rootMinus`, `rootPlus`, `quadratic_factorization`, `characteristic_double_factorization`, `det_at_rootMinus`, `det_at_rootPlus` | Each branch has algebraic multiplicity two. Distinctness is not global; phases zero or pi give coincident branches. |
| Exact tests | `Relativistic3DExamples` | Nonidentity axis walk, determinant one, `(z²+1)²`, roots `±i`, zero-parameter quadruple root, order sensitivity, and momentum sign sensitivity. |

Equations (8.31)–(8.48) remain outside Block 20. In particular, no `O(Δ²)` anisotropy, continuum velocity, or observer-shell defect is claimed here.

# Block 21 — Chapter 8.2 three-dimensional continuum sector

Physical PDF pages 41–42, printed pages 28–29. The literal source targets are equations (8.31)–(8.41). All leading-positive-energy asymptotics are on the positive-spacing filter `𝓝[>] 0`, under the stated nonzero-energy hypotheses.

| Source | Formal representatives | Scope and interpretation |
|---|---|---|
| (8.31)–(8.32) energy and anisotropy polynomial | `Relativistic3DShellAsymptotics.energy3`, `anisotropyQ`, `shellQuarticCoeff3_eq_source` | Exact real algebra. `Q` is the displayed quartic anisotropy polynomial. |
| (8.36) four-cosine shell expansion | `shell3_deriv2_zero`, `shell3_deriv4_zero`, `shell3_deriv6_zero`, `taylor6_shell3_closed`, `shell3_expansion_isBigO` | Actual shell, derivatives through order six, genuine `O(Δ⁶)` remainder. |
| (8.33) frequency correction | `Relativistic3DContinuumLimit.phase3_expansion_isBigO`, `positiveFrequency3_expansion_isBigO`, `tendsto_positiveFrequency3` | Principal positive-spacing branch, `E ≠ 0`; branch inversion proceeds through normalized sine square, positive square root, and arcsine. |
| (8.34) exact component derivatives | `Relativistic3DGroupVelocity.hasDerivAt_frequency_kx`, `hasDerivAt_frequency_ky`, `hasDerivAt_frequency_kz` | Exact shell derivatives on the nonsingular principal branch. |
| (8.35) continuum velocity | `positiveGroupVelocityX3_expansion_isBigO`, `positiveGroupVelocityY3_expansion_isBigO`, `positiveGroupVelocityZ3_expansion_isBigO`, `tendsto_positiveGroupVelocityVector3` | Each component has `O(Δ²)` error; vector converges to `k/E`. Eventual derivative theorems connect formulas to the original frequency. |
| (8.37)–(8.38) fixed-radius momenta | `Relativistic3DAnisotropy.axis_radius_sq`, `diagonal_radius_sq`, `energy3_axis_eq_diagonal` | Axis and body diagonal have exactly equal continuum energy. |
| (8.40)–(8.41) anisotropy values | `anisotropyQ_axis`, `anisotropyQ_diagonal`, `anisotropyQ_diagonal_sub_axis` | Exact difference `κ⁴/3`. |
| (8.39) frequency anisotropy | `axis_sub_diagonal_frequency_expansion_isBigO`, `axis_sub_diagonal_coefficient_pos` | Exact-frequency difference `κ⁴ Δ²/(18E)+O(Δ⁴)`; coefficient positive for `κ ≠ 0`, `E ≠ 0`. |
| Exact witnesses | `Relativistic3DContinuumExamples` | `m=1, k=(1,0,0)` and massless unit-radius axis/diagonal specializations. Symbolic witnesses, not empirical validation. |

Equations (8.42)–(8.48) remain outside Block 21. In particular, the moving-momentum transfer required by the observer-shell defect has not been replaced by a fixed-momentum asymptotic.


## Block 22 source map — equations (8.42)–(8.48)

| Source target | Checked declaration layer | Boundary |
|---|---|---|
| Subluminal three-vector Lorentz boost | `Relativistic3DLorentzKinematics` | Regularized at zero velocity; source quotient form proved only away from zero speed. |
| Boosted discrete four-momentum | `Relativistic3DDiscreteBoost` | Exact transformed momentum moves by the source frequency error. |
| Moving shell and branch inversion | `Relativistic3DPathInversion`, `Relativistic3DMovingShell`, `Relativistic3DMovingFrequency` | Positive-spacing, nonzero-energy asymptotics with explicit `O(Δ⁴)`/`O(Δ⁶)` remainders. |
| Observer-shell defect | `Relativistic3DObserverDefect.observerDefect_expansion_isBigO` | Leading defect only; no exact finite-spacing Lorentz invariance. |
| Exact witnesses | `Relativistic3DObserverExamples` | Zero-velocity identity and rational nonzero coefficient `-693/104`; not empirical validation. |


## Block 26: geometric edge refinement

Block 26 is a derived refinement layer rather than a claim that a specific manuscript equation has already supplied the continuum construction.  It replaces the Block 25 spectator cylinder by a genuine oriented edge subdivision.

| Physical role | Formal representative | Checked scope |
|---|---|---|
| Half-spacing edge geometry | `HalfSite`, `halfShift`, `MeshScale.half` | Two fine translations equal one lifted coarse translation; scale metadata halves. |
| Ordered link subdivision | `EdgeSubdivision` | `second * first = coarse link`; order is explicit. |
| Covariant interpolation | `EdgeSubdivision.embed`, `embed_gauge_covariant` | Midpoint value is first-sublink parallel transport. |
| Adjacent-scale directional dynamics | `two_halfSteps_embed`, `intertwiningDefect_eq_zero` | Exact for one Clifford direction on the interpolated subspace. |
| Hilbert refinement | `halfCellIP`, `embed_halfCellIP_isometry`, `embed_restrict_adjoint` | Half-cell measure gives an isometry and adjoint restriction. |
| Factorwise one-axis walk | `refinedOneAxisWalk_embed`, `refinedOneAxisWalk_halfCellIP` | Exact `M-S-M` refinement and weighted unitarity. |
| Curvature obstruction | `plaquette_eq_one_iff_path_independent`, `corner_transport_eq_iff_flat` | Flatness iff corner-path transport agrees. |
| Nonflat witness | `bool_plaquette_witness`, `bool_plaquette_nonflat` | Exact plaquette value `-1`. |

The block does not map a complete three-dimensional fine walk to the full continuum theory.  It isolates the theorem and obstruction needed for that later construction.


## Block 27 cubical refinement advance and boundary

Block 27 formalizes the local three-dimensional cell obligation following Block 26.  It constructs eight child vertices, twelve `U(1)` edges, six gauge-invariant face plaquettes, all six origin-to-opposite-corner paths, an abelian cube Bianchi identity, flat-sector path independence, exact nonflat `(Ω-1)` spinor defects, and one-eighth Hilbert-normalized interpolation.

This closes local cubical path consistency only.  The complete fine/coarse seven-factor Clifford walk, shared-cell gluing, scale-dependent curvature bounds, continuum reconstruction, and gauge dynamics remain outside the checked scope.

## Block 30 — Continuous operator two-budget refinement

This block is formal support for the local-discrete/global-continuous program.
It is not assigned to a new manuscript equation number beyond the checked
Chapter 8 refinement development.

| Formal representatives | Exact scope |
|---|---|
| `Relativistic3DCombinedDefect.directionalShiftCLM`, `frameEmbedCLM`, `straightDefectOpX/Y/Z` | Actual continuous-linear packaging on finite site types; continuity follows from finite dimensionality. |
| `fineEdgeDefectCLM_halfCellIP`, `fineEdgeDefectCLM_energy` | Exact preservation of the Block 29 half-cell Hilbert mismatch formula after operator packaging. |
| `norm_straightSevenFactorDefect_le` | Complete `M-X-Y-Z-Y-X-M` straight-stage defect bounded by five actual spatial operator norms under contraction and exact mass-step hypotheses. |
| `straightSevenFactorDefect_eq_zero` | Exact full-walk intertwining from straight reconstruction, independently of plaquette flatness. |
| `edgeRatioX/Y/Z`, `straightCompatible*_iff_ratios_one` | Multiplicative edge ratios equal one exactly when the framed ordered half-link product reconstructs the coarse link. |
| `curvatureBudget`, `norm_straightSeven_then_gluing_le`, `norm_combinedFiberDefect_le` | Edge and path-curvature budgets enter additively and remain logically independent. |
| `summable_combinedScaleBudget`, `tendsto_twoBudgetLimit`, `dist_twoBudgetLimit_le_tail` | Conditional global convergence and tail estimate from separately summable edge and curvature budgets. |

Boundary: the current straight budget is expressed in actual operator norms.
No sharp scalar reduction to `sup |E_i-1|`, concrete mesh-decay law, continuum
Dirac convergence, dynamical gauge equation, gravity, cosmology, or empirical
claim is included.


## Block 34: coordinate-regular connection refinement

This block extends the model-specific refinement analysis beyond affine backgrounds.

| Formal representative | Exact scope |
|---|---|
| `RegularConnection3`, `CrossDerivativeBounds` | Explicit coordinate-line continuity/differentiability and six global cross-derivative bounds; not an implicit generic smoothness assumption. |
| `edgeAngle*`, `link*`, `link*_half_product` | Exact coordinate interval integrals and exact ordered half-edge reconstruction. |
| `abs_*_shift*_sub_le`, `abs_edgeAngle*_shift*_sub_le` | One-dimensional fundamental-theorem and integrated transverse-variation bounds. |
| `norm_plaquette*_sub_one_le` | Quadratic plaquette control from the six cross-derivative envelopes. |
| `curvatureBudget_regularCubeLinks_le` | Five-face cubical gluing budget bounded by `h²` times an explicit derivative amplitude. |
| `norm_regularGeneratedCombinedHilbertDefect_le` | Complete finite-Hilbert edge-plus-gluing defect bound; straight-edge budget vanishes for exact line-integral links. |
| `summable_norm_regularGeneratedCombinedHilbertDefect_dyadic` | Summability of actual generated operator defects on the dyadic mesh. |
| `sinusoidalYConnection` and witness theorems | Non-affine background `A_y=sin x`, varying curvature `F_xy=cos x`, certified total defect at most `h²`. |

The block does not yet identify the abstract completed limit with an `L²` continuum spinor or the continuum Dirac propagator.


## Block 35: finite-cell L² reconstruction

This block supplies the first explicit continuum Hilbert reconstruction in the
local-discrete/global-continuous program.

| Formal representative | Exact scope |
|---|---|
| `UnitVolumePartition` | Finite measurable, pairwise-disjoint, unit-volume cells covering the measure space. |
| `stepLinear`, `stepIsometry`, `step_inner` | Exact step-function interpolation `ℓ²(I;E) → L²(Ω;E)` and inner-product preservation. |
| `averagingCLM`, `averaging_step`, `averaging_apply` | Hilbert adjoint, left inverse, and explicit Bochner cell-integral formula. |
| `stepProjection`, `stepProjection_idem`, `adjoint_stepProjection` | Self-adjoint idempotent orthogonal projection onto the finite step subspace. |
| `norm_sq_stepProjection_add_residual`, `norm_residual_le_norm_sub_step` | Pythagorean decomposition and best `L²` approximation. |
| `stepProjection_tendsto_of_step_approximation` | Conditional strong convergence of cell-average projections whenever step approximants are dense along the chosen family. |

Boundary: unit-volume normalization is explicit. No particular 3D dyadic
partition, weighted `a_n^3` normalization, density theorem, lattice-to-`L²`
identification, Dirac-generator consistency, or propagator convergence is
claimed.

## Block 39: Euclidean transported finite-resolution projections

| Formal object | Role | Exact boundary |
|---|---|---|
| `Relativistic3DEuclideanDyadicProjection.cubePullback` | Block 38 measure-preserving `L²` pullback from cube fields to octree fields | Isometric embedding, not yet asserted surjective |
| `cubeAdjoint`, `cubeAdjoint_pullback` | Hilbert adjoint and left-inverse identity `U†U=I` | Does not construct a pointwise inverse to binary decoding |
| `euclideanLevelRaw`, `euclideanLevel` | Adjoint transport and closure of octree finite-prefix levels | Not yet identified with ordinary half-open dyadic-box steps |
| `exists_euclideanLevel_approx`, `euclideanFiniteSubmodule_dense` | Density in Euclidean cube `L²` | Uses octree density plus adjoint contractivity |
| `euclideanProjection` and projection lemmas | Orthogonal best approximation at each transported level | Closed-subspace Hilbert projection |
| `euclideanProjection_tendsto` | Strong convergence `P_n f → f` for every cube `L²` field | State-space theorem only; no generator or propagator limit |


## Block 40: concrete Euclidean dyadic boxes

Source: formal support for the local-discrete/global-continuous reconstruction program. This block does not map a new numbered manuscript equation. It closes the explicit boundary recorded after Block 39.

- `dyadicBox`, `cubeVolume_dyadicBox`: ordinary Cartesian boxes with exact `8⁻ⁿ` volume.
- `prefixCell_ae_eq_preimage_dyadicBox`: octree cylinders equal box preimages almost everywhere.
- `cubePullback_euclideanBoxIndicator`, `cubeAdjoint_octreePrefixIndicator`: exact `L²` transport.
- `euclideanLevel_eq_euclideanDyadicLevel`: transported and concrete finite-resolution levels coincide.
- `euclideanDyadicFiniteSubmodule_dense`, `euclideanDyadicProjection_tendsto`: concrete density and strong convergence.

The equality is modulo null dyadic boundaries. Generator and propagator convergence remain open.

## Block 41 — Fourier-mode generator consistency

- Source: `KomorebiPhysics/Relativistic3DFourierGenerator.lean`
- Central finite difference: exact multiplier `i sin(kh)/h`.
- Free Dirac kinetic multiplier: exact `sin(kh)/h` after the `-i` prefactor.
- Continuum and lattice Clifford symbols: exact mass-shell squares.
- Continuum consistency: `O(h²)` on fixed modes and fixed finite Fourier packets.
- Boundary: no full `L²` generator or propagator theorem.

## Block 43 — Fixed-cutoff Fourier exponential evolution

Formal support for the dynamical continuum bridge.

| Formal representative | Exact scope |
|---|---|
| `Relativistic3DFourierPropagator.continuumModeOperator`, `centralModeOperator` | Finite-dimensional bounded Dirac mode generators as continuous linear endomorphisms. |
| `centralModeOperator_sub_continuum_isBigO` | Operator-norm generator residual is `O(h²)` for each fixed Fourier mode. |
| `continuumModePropagator`, `centralModePropagator` | Banach-algebra exponentials `exp(-itH)` at fixed mode and mesh. |
| `continuumModePropagator_add_time`, `centralModePropagator_add_time`, `*_neg_mul` | Exact zero-time, additive-time, and inverse-time exponential group identities. |
| `centralModePropagator_sub_isBigO` | Fixed-time propagator residual is `O(h²)` in mode-operator norm. |
| `packetPropagatorResidualL2_norm_sq` | Exact Parseval decomposition of finite-cutoff propagator error. |
| `packetPropagatorResidualL2_isBigO`, `tendsto_centralPropagatedPacketL2` | `O(h²)` and strong torus-`L²` convergence for fixed finite support and fixed time. |

Boundary: no Hilbert-unitarity theorem, no compact-time uniform estimate, no growing or infinite cutoff, and no unbounded self-adjoint Dirac operator is included.

## Block 46 — Full Fourier coefficient evolution

| Formal representative | Exact scope |
|---|---|
| `CoeffL2`, `modewiseIsometry` | Complete square-summable Fourier coefficient Hilbert space and exact coordinatewise isometries. |
| `continuumCoeffPropagator`, `centralCoeffPropagator` | Full continuum and central-difference coefficient evolutions, not finite cutoffs. |
| `continuumCoeffUnitary`, `centralCoeffUnitary` | Surjective linear isometric equivalences and full time-group laws. |
| `coeffTruncation`, `exists_coeffTruncation_approx` | Canonical finite Fourier truncations approximate every coefficient field. |
| `coeffPacketResidual_norm_sq`, `norm_coeffPacketResidual_eq_torus` | Exact Parseval residual and identification with the checked finite torus packet residual. |
| `eventually_fullCoeffResidual_lt`, `fullCoeffPropagator_compactTime_converges` | Cutoff removal and compact-time strong convergence for every coefficient field. |

Boundary: this block works on canonical Fourier coefficient `ℓ²`. The unitary Fourier transform to physical torus `L²`, the unbounded Dirac operator/domain, strong-resolvent convergence, and interacting gauge dynamics remain open.


## Block 49 — weighted domain and physical torus Hamiltonian

| Formal representative | Exact scope |
|---|---|
| `modeEnergySq`, `norm_continuumHilbertModeOperator_sq` | Exact mode identity `‖H_m(n)ψ‖² = (m² + |k_n|²)‖ψ‖²`. |
| `mem_continuumDiracDomain_iff_summable_weighted` | Maximal domain equals summability of exact modal Dirac energies. |
| `mem_continuumDiracDomain_iff_summable_h1` | Equivalent inhomogeneous first-order Fourier condition. |
| `mem_continuumDiracDomain_iff_mass` | The maximal free domain is independent of mass. |
| `physicalDiracPMap` | Fourier-conjugated unbounded Hamiltonian on physical torus `L²`. |
| `physicalDiracPMap_selfAdjoint`, `physicalDiracPMap_isClosed` | Dense, self-adjoint, closed physical realization. |
| `norm_*_sq_eq_tsum_weighted` | Exact global energy sums in coefficient and physical spaces. |

Boundary: no spectral-exponential identification and no graph/strong-resolvent lattice convergence are claimed.
