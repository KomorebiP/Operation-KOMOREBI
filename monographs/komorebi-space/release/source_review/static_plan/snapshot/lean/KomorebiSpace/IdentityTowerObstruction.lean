import KomorebiSpace.ConstantTower
import KomorebiSpace.SplitTowerCoordinates

set_option autoImplicit false

/-!
# A boundary counterexample

For identity bonding maps on the reals, the bounded constant residual 1 has
no bounded primitive. Thus the tower differential has no right inverse on all
bounded residuals. This does not deny the already proved exact repair of
bounded candidates preserving their initial value.
-/
noncomputable section
open scoped NNReal ENNReal
namespace KomorebiSpace
namespace IdentityTowerObstruction
open BanachTower

abbrev realTower : BanachTower ℝ where
  Obj _ := ℝ
  down _ := ContinuousLinearMap.id ℝ ℝ
  bound := 1
  down_bound _ := ContinuousLinearMap.norm_id_le

def splitting : Splitting realTower where
  up _ := ContinuousLinearMap.id ℝ ℝ
  down_up _ := rfl
  bound := 1
  up_bound _ := ContinuousLinearMap.norm_id_le

theorem propagation_product_one : (splitting.bound : ℝ) * realTower.bound = 1 := by
  norm_num [splitting, realTower]

def unitResidual : Residuals realTower realTower :=
  ⟨fun _ => ContinuousLinearMap.id ℝ ℝ, memℓp_infty ⟨1, by
    rintro _ ⟨n, rfl⟩
    exact ContinuousLinearMap.norm_id_le⟩⟩

@[simp] theorem unitResidual_apply (n : ℕ) (x : ℝ) : unitResidual n x = x := rfl

/-- A primitive of the unit residual would grow by one at every resolution. -/
theorem primitive_growth (f : Candidates realTower realTower)
    (hf : differential realTower realTower f = unitResidual) (n : ℕ) :
    f n 1 = f 0 1 + (n : ℝ) := by
  induction n with
  | zero => simp
  | succ n ih =>
    have h := congrArg (fun r : Residuals realTower realTower => r n 1) hf
    change f (n+1) 1 - f n 1 = 1 at h
    rw [Nat.cast_add, Nat.cast_one]
    linarith

/-- This is an infinite mathematical obstruction, not a finite search result. -/
theorem no_bounded_primitive :
    ¬ ∃ f : Candidates realTower realTower, differential realTower realTower f = unitResidual := by
  rintro ⟨f, hf⟩
  obtain ⟨n, hn⟩ := exists_nat_gt (‖f‖ - f 0 1)
  have hb : f n 1 ≤ ‖f‖ := by
    calc
      f n 1 ≤ ‖f n 1‖ := le_abs_self _
      _ ≤ ‖f n‖ * ‖(1 : ℝ)‖ := (f n).le_opNorm 1
      _ = ‖f n‖ := by simp
      _ ≤ ‖f‖ := lp.norm_apply_le_norm ENNReal.top_ne_zero f n
  rw [primitive_growth f hf n] at hb
  linarith

/-- Even an arbitrary function-valued right inverse is impossible in this bounded space. -/
theorem no_right_inverse :
    ¬ ∃ A : Residuals realTower realTower → Candidates realTower realTower,
      ∀ r, differential realTower realTower (A r) = r := by
  rintro ⟨A, hA⟩
  exact no_bounded_primitive ⟨A unitResidual, hA unitResidual⟩

/-- Exact repair of candidates and surjectivity onto all residuals are different assertions. -/
theorem repair_exists_but_right_inverse_does_not :
    (∀ f : Candidates realTower realTower, ∃! g : Candidates realTower realTower,
      Exact realTower realTower g ∧ g 0 = f 0) ∧
    (¬ ∃ A : Residuals realTower realTower → Candidates realTower realTower,
      ∀ r, differential realTower realTower (A r) = r) := by
  exact ⟨fun f => constant_unique_repair f, no_right_inverse⟩

end IdentityTowerObstruction
end KomorebiSpace
end
