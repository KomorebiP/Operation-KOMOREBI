/-
Copyright (c) 2026 Komorebi P. All rights reserved.
Authors: Komorebi P.
-/

import KomorebiVerification.MathlibImports

/-!
# Finite packet maps over any normed field

The continuous coordinate identities do not require a nontrivial valuation.
The separate GeneralPacketBounds module uses actual projector norm bounds,
since continuity alone need not imply boundedness over a trivially valued field.
-/

set_option autoImplicit false
noncomputable section

open scoped BigOperators InnerProduct lp
open Set Function UniformSpace

namespace Komorebi.PaperIRelease.GeneralNormedPackets

/-! ## Finite bounded packet systems -/

/-- A finite family of continuous projectors which is pairwise annihilating and
sums pointwise to the identity. -/
structure ContinuousProjectorFamily
    (𝕜 : Type*) (X : Type*) (ι : Type*)
    [NormedField 𝕜] [NormedAddCommGroup X] [NormedSpace 𝕜 X]
    [Fintype ι] where
  proj : ι → X →L[𝕜] X
  idempotent : ∀ i x, proj i (proj i x) = proj i x
  annihilate : ∀ {i j}, i ≠ j → ∀ x, proj i (proj j x) = 0
  complete : ∀ x, (∑ i, proj i x) = x

namespace ContinuousProjectorFamily

variable {𝕜 X ι : Type*}
variable [NormedField 𝕜]
variable [NormedAddCommGroup X] [NormedSpace 𝕜 X]
variable [Fintype ι]

/-- The `i`th packet is the range of its continuous projector. -/
def packet (P : ContinuousProjectorFamily 𝕜 X ι) (i : ι) : Submodule 𝕜 X :=
  (P.proj i).range

/-- Every packet range is closed. -/
theorem isClosed_packet (P : ContinuousProjectorFamily 𝕜 X ι) (i : ι) :
    IsClosed (P.packet i : Set X) := by
  apply ContinuousLinearMap.IsIdempotentElem.isClosed_range
  apply ContinuousLinearMap.ext
  intro x
  exact P.idempotent i x

/-- Analysis into the finite product of packet ranges. -/
def analysis (P : ContinuousProjectorFamily 𝕜 X ι) :
    X →L[𝕜] ∀ i, P.packet i :=
  ContinuousLinearMap.pi fun i ↦
    (P.proj i).codRestrict (P.packet i) fun x ↦ by
      change P.proj i x ∈ (P.proj i).range
      exact ⟨x, rfl⟩

@[simp]
theorem analysis_apply_coe (P : ContinuousProjectorFamily 𝕜 X ι) (x : X) (i : ι) :
    ((P.analysis x i : P.packet i) : X) = P.proj i x :=
  by simp [analysis]

/-- Synthesis is the finite sum of the packet inclusions. -/
def synthesis (P : ContinuousProjectorFamily 𝕜 X ι) :
    (∀ i, P.packet i) →L[𝕜] X :=
  ∑ i, (P.packet i).subtypeL.comp (ContinuousLinearMap.proj i)

@[simp]
theorem synthesis_apply (P : ContinuousProjectorFamily 𝕜 X ι)
    (x : ∀ i, P.packet i) :
    P.synthesis x = ∑ i, (x i : X) := by
  simp [synthesis]

@[simp]
theorem synthesis_analysis (P : ContinuousProjectorFamily 𝕜 X ι) (x : X) :
    P.synthesis (P.analysis x) = x := by
  simpa [synthesis] using P.complete x

@[simp]
theorem analysis_synthesis (P : ContinuousProjectorFamily 𝕜 X ι)
    (x : ∀ i, P.packet i) :
    P.analysis (P.synthesis x) = x := by
  classical
  ext i
  rw [analysis_apply_coe, synthesis_apply]
  change P.proj i (∑ j, (x j : X)) = (x i : X)
  rw [map_sum, Finset.sum_eq_single i]
  · rcases (x i).property with ⟨y, hy⟩
    rw [← hy]
    exact P.idempotent i y
  · intro j _ hji
    rcases (x j).property with ⟨y, hy⟩
    rw [← hy]
    exact P.annihilate hji.symm y
  · simp

/-- The topological packet isomorphism: continuous analysis and synthesis are
mutually inverse.  A finite product is the finite direct sum as a vector
space, and carries one of its equivalent finite-product norms. -/
def packetEquiv (P : ContinuousProjectorFamily 𝕜 X ι) :
    X ≃L[𝕜] ∀ i, P.packet i :=
  ContinuousLinearEquiv.equivOfInverse P.analysis P.synthesis
    P.synthesis_analysis P.analysis_synthesis

@[simp]
theorem packetEquiv_apply (P : ContinuousProjectorFamily 𝕜 X ι) (x : X) :
    P.packetEquiv x = P.analysis x :=
  rfl

/-- Literal Banach-space wrapper for the topological packet theorem.  It
packages both manuscript conclusions: every packet is closed and analysis is
a continuous linear isomorphism whose forward and inverse maps are the declared
analysis and synthesis operators. -/
theorem topological_packet_isomorphism [CompleteSpace X]
    (P : ContinuousProjectorFamily 𝕜 X ι) :
    (∀ i, IsClosed (P.packet i : Set X)) ∧
      ∃ e : X ≃L[𝕜] ∀ i, P.packet i,
        e.toContinuousLinearMap = P.analysis ∧
          e.symm.toContinuousLinearMap = P.synthesis := by
  refine ⟨P.isClosed_packet, P.packetEquiv, rfl, ?_⟩
  rfl

/-! ## Completion preserves finite packet extraction -/

/-- The image of a dense submodule under an arbitrary bounded idempotent is
dense in the full range.  This is the literal manuscript completion lemma;
it does not require the projector to belong to a finite packet family. -/
theorem idempotentRange_eq_closure_map
    (Q : X →L[𝕜] X) (hQ : ∀ x, Q (Q x) = Q x)
    (M : Submodule 𝕜 X) (hM : M.topologicalClosure = ⊤) :
    (M.map Q.toLinearMap).topologicalClosure = Q.range := by
  have hclosed : IsClosed (Q.range : Set X) := by
    apply ContinuousLinearMap.IsIdempotentElem.isClosed_range
    apply ContinuousLinearMap.ext
    intro x
    exact hQ x
  apply le_antisymm
  · apply Submodule.topologicalClosure_minimal
    · exact LinearMap.map_le_range
    · exact hclosed
  · have h := Submodule.topologicalClosure_map Q M
    rw [hM] at h
    simpa using h

/-- For a dense submodule `M`, the image of `M` under any bounded idempotent
projector is dense in the full packet range.  This is the exact completion
claim `P_i X = closure (P_i M)`, stated as equality of submodules.  The result
is slightly stronger than the manuscript statement because invariance
`P_i M ⊆ M` is not needed for this equality. -/
theorem packetRange_eq_closure_map
    (P : ContinuousProjectorFamily 𝕜 X ι) (M : Submodule 𝕜 X)
    (hM : M.topologicalClosure = ⊤) (i : ι) :
    (M.map (P.proj i).toLinearMap).topologicalClosure = P.packet i := by
  simpa [packet] using
    idempotentRange_eq_closure_map (P.proj i) (P.idempotent i) M hM


end ContinuousProjectorFamily
end Komorebi.PaperIRelease.GeneralNormedPackets
