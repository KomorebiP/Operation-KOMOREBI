import PaperXI.ActualELatticeTypeGroup59

/-!
# Uniformizer freeness for the actual lattice-product group

Freeness is proved directly from the integral lattice and the strict valuation
of the actual extension-field uniformizer. It does not assume compactness of
the group or a matrix determinant identity.
-/
set_option autoImplicit false
noncomputable section
namespace PaperXI.ActualELatticeFreeness59
open Matrix ValuativeRel
open ActualELatticeNormalizer59 ActualELatticeResidue59 ActualELatticeTypeGroup59

variable (K E : Type*) [Field K] [Field E] [Algebra K E]
variable (n : Type*) [Fintype n] [DecidableEq n]
variable [ValuativeRel E] [TopologicalSpace E] [IsNonarchimedeanLocalField E]

/-- Literal extension-field scalar multiplication as a group homomorphism. -/
def scalarAction : Eˣ →* ((n → E) ≃ₗ[K] (n → E)) where
  toFun u := (LinearEquiv.smulOfUnit u : (n → E) ≃ₗ[E] (n → E)).restrictScalars K
  map_one' := by ext v i; simp [LinearEquiv.smulOfUnit]
  map_mul' u v := by ext w i; simp [LinearEquiv.smulOfUnit, mul_smul]

omit [Fintype n] [DecidableEq n] [ValuativeRel E]
  [TopologicalSpace E] [IsNonarchimedeanLocalField E] in
@[simp] theorem scalarAction_apply (u : Eˣ) (v : n → E) :
    scalarAction K E n u v = (u : E) • v := rfl

omit [Fintype n] [DecidableEq n] in
/-- Every integer power acts by the corresponding actual field scalar. -/
theorem uniformizerAction_zpow_apply (r : ℤ) (v : n → E) :
    (uniformizerAction K E n ^ r) v =
      (ActualLocalUnitDecomposition.uniformizer E : E) ^ r • v := by
  change ((scalarAction K E n (ActualLocalUnitDecomposition.uniformizerUnit E)) ^ r) v = _
  rw [← map_zpow, scalarAction_apply, Units.val_zpow_eq_zpow_val]
  rfl

/-- The entire actual product group preserves each lattice level. -/
theorem typeGroup_le_stabilizer :
    typeGroup K E n ≤ chainStabilizer (latticeChain K E n) := by
  apply sup_le
  · rintro g ⟨h, rfl⟩
    exact integralMatrix_mem_stabilizer K E n h
  · exact firstCongruence_le (latticeChain K E n)

/-- A uniformizer power preserving the integral lattice has nonnegative exponent. -/
theorem uniformizerAction_exponent_nonneg [Nonempty n] (r : ℤ)
    (hr : uniformizerAction K E n ^ r ∈ typeGroup K E n) : 0 ≤ r := by
  classical
  let i : n := Classical.choice inferInstance
  have hv : (fun _ : n => (1 : E)) ∈ integralLattice E n :=
    fun _ => (valuation E).integer.one_mem
  have hg := typeGroup_le_stabilizer K E n hr
  have h := (hg 0 (fun _ : n => (1 : E))).mpr (by rw [latticeChain_zero]; exact hv)
  rw [latticeChain_zero, uniformizerAction_zpow_apply] at h
  have hi := h i
  change valuation E ((ActualLocalUnitDecomposition.uniformizer E : E) ^ r * 1) ≤ 1 at hi
  simp only [mul_one, map_zpow₀] at hi
  exact (zpow_le_one_iff_right_of_lt_one₀
    (ActualLocalUnitDecomposition.uniformizer_value_pos E)
    (ActualLocalUnitDecomposition.uniformizer_value_lt_one E)).mp hi

/-- No nonzero uniformizer power belongs to the actual lattice-product group. -/
theorem uniformizerAction_free [Nonempty n] (r : ℤ)
    (hr : uniformizerAction K E n ^ r ∈ typeGroup K E n) : r = 0 := by
  have h₁ := uniformizerAction_exponent_nonneg K E n r hr
  have h₂ := uniformizerAction_exponent_nonneg K E n (-r)
    (by simpa using (typeGroup K E n).inv_mem hr)
  omega

end PaperXI.ActualELatticeFreeness59
