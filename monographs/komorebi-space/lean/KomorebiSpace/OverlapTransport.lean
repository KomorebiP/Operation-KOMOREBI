import Mathlib.Analysis.Normed.Operator.LinearIsometry
import Mathlib.Analysis.Normed.Group.Constructions
import Mathlib.Analysis.Normed.Operator.NormedSpace
import Mathlib.Tactic.Abel

set_option autoImplicit false

/-!
# Flat isometric overlap data and anchored repair

The supplied frames define actual overlap maps. Their existence is an explicit
model hypothesis, not asserted for arbitrary local systems. The repair below
is constructed, not assumed as a right inverse or a spectral estimate.
-/
universe u v
noncomputable section
namespace KomorebiSpace
namespace OverlapTransport
variable {V : Type u} {H : Type v}
variable [NormedAddCommGroup H] [NormedSpace ℝ H]
abbrev Frames := V → H ≃ₗᵢ[ℝ] H
variable (e : Frames (V := V) (H := H))
def normalized (x : V → H) (i : V) : H := (e i).symm (x i)
def transport (i j : V) : H ≃ₗᵢ[ℝ] H := (e j).symm.trans (e i)
@[simp] theorem transport_apply (i j : V) (z : H) :
    transport e i j z = e i ((e j).symm z) := rfl
@[simp] theorem transport_self (i : V) (z : H) : transport e i i z = z := by
  simp [transport_apply]
theorem transport_comp (i j k : V) (z : H) :
    transport e i j (transport e j k z) = transport e i k z := by
  simp [transport_apply]
/-- The residual has the same orientation as the existing view differential. -/
def defect (x : V → H) (i j : V) : H := transport e i j (x j) - x i
@[simp] theorem normalized_defect (x : V → H) (i j : V) :
    (e i).symm (defect e x i j) = normalized e x j - normalized e x i := by
  simp [defect, transport_apply, normalized, map_sub]
theorem norm_defect (x : V → H) (i j : V) :
    ‖defect e x i j‖ = ‖normalized e x j - normalized e x i‖ := by
  rw [← normalized_defect e x i j]
  exact ((e i).symm.norm_map _).symm
theorem defect_comp (x : V → H) (i j k : V) :
    defect e x i k = defect e x i j + transport e i j (defect e x j k) := by
  simp [defect, transport_apply, map_sub]
/-- The whole vector at the anchor is protected. -/
def repair (o : V) (x : V → H) (i : V) : H := transport e i o (x o)
@[simp] theorem repair_anchor (o : V) (x : V → H) : repair e o x o = x o := by
  simp [repair]
@[simp] theorem repair_defect (o : V) (x : V → H) (i j : V) :
    defect e (repair e o x) i j = 0 := by
  simp [defect, repair]
@[simp] theorem repair_idempotent (o : V) (x : V → H) :
    repair e o (repair e o x) = repair e o x := by
  funext i
  simp [repair]
theorem normalized_repair (o : V) (x : V → H) (i : V) :
    normalized e (repair e o x) i = normalized e x o := by
  simp [normalized, repair, transport_apply]
theorem repair_error_coordinate (o : V) (x : V → H) (i : V) :
    ‖x i - repair e o x i‖ = ‖normalized e x i - normalized e x o‖ := by
  rw [← (e i).symm.norm_map (x i - repair e o x i), map_sub]
  rw [show (e i).symm (repair e o x i) = normalized e x o from
    normalized_repair e o x i]
  rfl
theorem repair_fixes (o : V) (x : V → H)
    (hx : ∀ i j, defect e x i j = 0) : repair e o x = x := by
  funext i
  exact sub_eq_zero.mp (hx i o)
theorem unique_repair (o : V) (x : V → H) :
    ∃! y : V → H, (∀ i j, defect e y i j = 0) ∧ y o = x o := by
  refine ⟨repair e o x, ⟨repair_defect e o x, repair_anchor e o x⟩, ?_⟩
  intro y hy
  funext i
  have he := sub_eq_zero.mp (hy.1 i o)
  rw [hy.2] at he
  exact he.symm
section Finite
variable [Fintype V]
def repairLinear (o : V) : (V → H) →ₗ[ℝ] (V → H) where
  toFun := repair e o
  map_add' := by intro x y; funext i; simp [repair, map_add]
  map_smul' := by intro c x; funext i; simp [repair, map_smul]
theorem repair_bound (o : V) (x : V → H) : ‖repair e o x‖ ≤ ‖x‖ := by
  apply (pi_norm_le_iff_of_nonneg (norm_nonneg x)).mpr
  intro i
  simpa [repair] using norm_le_pi_norm x o
def repairCLM (o : V) : (V → H) →L[ℝ] (V → H) :=
  (repairLinear e o).mkContinuous 1 (by
    intro x
    change ‖repair e o x‖ ≤ 1 * ‖x‖
    simpa using repair_bound e o x)
@[simp] theorem repairCLM_apply (o : V) (x : V → H) :
    repairCLM e o x = repair e o x := rfl
theorem repair_opNorm (o : V) : ‖repairCLM e o‖ ≤ 1 := by
  apply (repairCLM e o).opNorm_le_bound zero_le_one
  intro x
  simpa using repair_bound e o x
theorem repair_stability (o : V) (x y : V → H) :
    ‖repair e o x - repair e o y‖ ≤ ‖x-y‖ := by
  change ‖repairCLM e o x - repairCLM e o y‖ ≤ _
  rw [← map_sub]
  exact repair_bound e o (x-y)
end Finite

def reframe (a : Frames (V := V) (H := H)) : Frames (V := V) (H := H) :=
  fun i => (e i).trans (a i)
def changeValues (a : Frames (V := V) (H := H)) (x : V → H) : V → H :=
  fun i => a i (x i)
theorem reframe_normalized (a : Frames (V := V) (H := H)) (x : V → H) (i : V) :
    normalized (reframe e a) (changeValues a x) i = normalized e x i := by
  simp [normalized, reframe, changeValues]
theorem reframe_defect (a : Frames (V := V) (H := H)) (x : V → H) (i j : V) :
    defect (reframe e a) (changeValues a x) i j = a i (defect e x i j) := by
  simp [defect, transport_apply, reframe, changeValues, map_sub]
theorem reframe_defect_norm (a : Frames (V := V) (H := H)) (x : V → H) (i j : V) :
    ‖defect (reframe e a) (changeValues a x) i j‖ = ‖defect e x i j‖ := by
  rw [reframe_defect]
  exact (a i).norm_map _
theorem reframe_repair (a : Frames (V := V) (H := H)) (o : V) (x : V → H) :
    repair (reframe e a) o (changeValues a x) = changeValues a (repair e o x) := by
  funext i
  simp [repair, transport_apply, reframe, changeValues]
end OverlapTransport
end KomorebiSpace
end
