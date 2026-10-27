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
| (2.37)–(2.49), moving atlas | Preserved `MovingFrames` module | Finite-matrix moving-coordinate, connection and differentiated-unitarity results rechecked in equivalent Hamiltonian convention. General bounded-operator translation not yet added. |
| (2.50)–(2.57), whole-object deformation | No active module | Pending. Do not mark Chapter 2 wholly complete. |

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

## Limits of the counts

The 37 new declarations consist of 32 general mathematical/analytic lemmas and five exact realization or hypothesis-sensitivity theorems. There are also proof-bearing definitions, counted separately among the 96 audited declarations. The 39 preserved theorem declarations include supporting results outside the narrow Chapter 2 equation list. Their presence is not 39 additional independently novel physical conclusions.
