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
