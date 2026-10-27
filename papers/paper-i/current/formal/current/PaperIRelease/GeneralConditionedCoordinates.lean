import PaperIRelease.GeneralPacketBounds

set_option autoImplicit false
noncomputable section

namespace Komorebi.PaperIRelease.GeneralConditionedCoordinates

variable {X Y : Type*} [NormedAddCommGroup X] [NormedAddCommGroup Y]

/-- The usual infimum-of-bounds operator norm is available for bounded
additive maps without a nontriviality assumption on a scalar valuation. -/
def ofBoundedLinear {𝕜 : Type*} [Semiring 𝕜] [Module 𝕜 X] [Module 𝕜 Y]
    (f : X →ₗ[𝕜] Y) (h : IsBoundedLinearMap 𝕜 f) : NormedAddGroupHom X Y where
  toFun := f
  map_add' := f.map_add
  bound' := by obtain ⟨C, _, hC⟩ := h.bound; exact ⟨C, hC⟩

def conditionNumber (A : NormedAddGroupHom X Y) (S : NormedAddGroupHom Y X) : ℝ :=
  ‖A‖ * ‖S‖

def coordinateOperator (A : NormedAddGroupHom X Y) (S : NormedAddGroupHom Y X)
    (T : NormedAddGroupHom X X) : NormedAddGroupHom Y Y := A.comp (T.comp S)

theorem one_le_conditionNumber [Nontrivial X]
    (A : NormedAddGroupHom X Y) (S : NormedAddGroupHom Y X)
    (hSA : ∀ x, S (A x) = x) : 1 ≤ conditionNumber A S := by
  have h : S.comp A = NormedAddGroupHom.id X := by ext x; exact hSA x
  calc
    1 = ‖NormedAddGroupHom.id X‖ := (NormedAddGroupHom.norm_id X).symm
    _ = ‖S.comp A‖ := congrArg norm h.symm
    _ ≤ ‖S‖ * ‖A‖ := NormedAddGroupHom.norm_comp_le S A
    _ = conditionNumber A S := by unfold conditionNumber; ring

theorem norm_coordinateOperator_le (A : NormedAddGroupHom X Y)
    (S : NormedAddGroupHom Y X) (T : NormedAddGroupHom X X) :
    ‖coordinateOperator A S T‖ ≤ conditionNumber A S * ‖T‖ := by
  calc
    ‖coordinateOperator A S T‖ ≤ ‖A‖ * ‖T.comp S‖ := NormedAddGroupHom.norm_comp_le _ _
    _ ≤ ‖A‖ * (‖T‖ * ‖S‖) :=
      mul_le_mul_of_nonneg_left (NormedAddGroupHom.norm_comp_le _ _) (norm_nonneg _)
    _ = conditionNumber A S * ‖T‖ := by unfold conditionNumber; ring

theorem coordinateOperator_inverse (A : NormedAddGroupHom X Y)
    (S : NormedAddGroupHom Y X) (hSA : ∀ x, S (A x) = x)
    (T : NormedAddGroupHom X X) : coordinateOperator S A (coordinateOperator A S T) = T := by
  ext x
  change S (A (T (S (A x)))) = T x
  rw [hSA, hSA]

theorem conditioned_coordinate_bounds (A : NormedAddGroupHom X Y)
    (S : NormedAddGroupHom Y X) (hSA : ∀ x, S (A x) = x)
    (T : NormedAddGroupHom X X) :
    ‖coordinateOperator A S T‖ ≤ conditionNumber A S * ‖T‖ ∧
      ‖T‖ ≤ conditionNumber A S * ‖coordinateOperator A S T‖ := by
  refine ⟨norm_coordinateOperator_le A S T, ?_⟩
  have h := norm_coordinateOperator_le S A (coordinateOperator A S T)
  rw [coordinateOperator_inverse A S hSA T] at h
  simpa only [conditionNumber, mul_comm ‖S‖ ‖A‖] using h

open GeneralNormedPackets

variable {𝕜 I : Type*} [NormedField 𝕜] [NormedSpace 𝕜 X] [Fintype I]

def packetAnalysis (P : ContinuousProjectorFamily 𝕜 X I)
    (hb : ∀ i, IsBoundedLinearMap 𝕜 (P.proj i)) :
    NormedAddGroupHom X (∀ i, P.packet i) :=
  ofBoundedLinear P.analysis.toLinearMap (P.analysis_isBounded hb)

def packetSynthesis (P : ContinuousProjectorFamily 𝕜 X I) :
    NormedAddGroupHom (∀ i, P.packet i) X :=
  ofBoundedLinear P.synthesis.toLinearMap P.synthesis_isBounded

/-- The abstract norm argument applies to the actual finite-packet maps
over every normed field, including a trivially valued one. -/
theorem packet_conditioned_coordinate_bounds (P : ContinuousProjectorFamily 𝕜 X I)
    (hb : ∀ i, IsBoundedLinearMap 𝕜 (P.proj i)) (T : X →ₗ[𝕜] X)
    (hT : IsBoundedLinearMap 𝕜 T) :
    ‖coordinateOperator (packetAnalysis P hb) (packetSynthesis P) (ofBoundedLinear T hT)‖ ≤
        conditionNumber (packetAnalysis P hb) (packetSynthesis P) * ‖ofBoundedLinear T hT‖ ∧
      ‖ofBoundedLinear T hT‖ ≤ conditionNumber (packetAnalysis P hb) (packetSynthesis P) *
        ‖coordinateOperator (packetAnalysis P hb) (packetSynthesis P) (ofBoundedLinear T hT)‖ :=
  conditioned_coordinate_bounds _ _ P.synthesis_analysis _

theorem one_le_packet_conditionNumber [Nontrivial X]
    (P : ContinuousProjectorFamily 𝕜 X I)
    (hb : ∀ i, IsBoundedLinearMap 𝕜 (P.proj i)) :
    1 ≤ conditionNumber (packetAnalysis P hb) (packetSynthesis P) :=
  one_le_conditionNumber _ _ P.synthesis_analysis

/-- The same condition number estimates hold in each equivalent finite
product norm, with the actual coordinate maps and their usual operator norms. -/
theorem equivalent_norm_conditioned_coordinates [NormedSpace 𝕜 Y] [Nontrivial X]
    (P : ContinuousProjectorFamily 𝕜 X I)
    (hb : ∀ i, IsBoundedLinearMap 𝕜 (P.proj i))
    (e : (∀ i, P.packet i) ≃ₗ[𝕜] Y)
    (C D : ℝ) (hC : ∀ z, ‖e z‖ ≤ C * ‖z‖)
    (hD : ∀ y, ‖e.symm y‖ ≤ D * ‖y‖) :
    ∃ (A : NormedAddGroupHom X Y) (S : NormedAddGroupHom Y X),
      (∀ x, A x = e (P.analysis x)) ∧
      (∀ y, S y = P.synthesis (e.symm y)) ∧
      1 ≤ conditionNumber A S ∧
      ∀ (T : X →ₗ[𝕜] X) (hT : IsBoundedLinearMap 𝕜 T),
        ‖coordinateOperator A S (ofBoundedLinear T hT)‖ ≤
          conditionNumber A S * ‖ofBoundedLinear T hT‖ ∧
        ‖ofBoundedLinear T hT‖ ≤ conditionNumber A S *
          ‖coordinateOperator A S (ofBoundedLinear T hT)‖ := by
  obtain ⟨_, hA, hS, hSA, _⟩ := P.equivalent_norm_packet_bounds hb e C D hC hD
  let A := ofBoundedLinear (e.toLinearMap.comp P.analysis.toLinearMap) hA
  let S := ofBoundedLinear (P.synthesis.toLinearMap.comp e.symm.toLinearMap) hS
  exact ⟨A, S, fun _ => rfl, fun _ => rfl, one_le_conditionNumber A S hSA,
    fun T hT => conditioned_coordinate_bounds A S hSA (ofBoundedLinear T hT)⟩

end Komorebi.PaperIRelease.GeneralConditionedCoordinates
