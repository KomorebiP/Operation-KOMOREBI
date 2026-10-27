import KomorebiSpace.CascadeLimits
import Mathlib.Tactic.NormNum

set_option autoImplicit false

/-!
# Coarse decay and detail summability do not remove the persistent term

A completely specified scalar cascade has down=1/2 and lift=2. Its coarse
coordinates tend to zero, but restoring them gives back the entire input.
-/
noncomputable section
namespace KomorebiSpace
namespace CascadeBoundaryExamples
open Filter
open scoped Topology

abbrev scalarDown : ℝ →L[ℝ] ℝ := (1/2 : ℝ) • ContinuousLinearMap.id ℝ ℝ
abbrev scalarUp : ℝ →L[ℝ] ℝ := (2 : ℝ) • ContinuousLinearMap.id ℝ ℝ

theorem scalar_right_inv (x : ℝ) : scalarDown (scalarUp x) = x := by
  change (1/2 : ℝ)*(2*x)=x
  ring

abbrev system : CoarseningCascade ℝ where
  Obj _ := ℝ
  down _ := scalarDown
  splitting _ := { lift := scalarUp, right_inv := scalar_right_inv }

@[simp] theorem level_formula (x : ℝ) (N : ℕ) :
    system.level x N = (1/2 : ℝ)^N*x := by
  induction N with
  | zero => simp
  | succ N ih =>
    change (1/2 : ℝ)*system.level x N = _
    rw [ih, pow_succ]
    ring

@[simp] theorem restore_formula (x : ℝ) (N : ℕ) :
    system.restore N x = (2 : ℝ)^N*x := by
  induction N generalizing x with
  | zero => change x = (2 : ℝ)^0*x; simp
  | succ N ih =>
    change system.restore N (2*x) = _
    rw [ih, pow_succ]
    ring

@[simp] theorem remainder_identity (x : ℝ) (N : ℕ) : system.remainder N x = x := by
  rw [CoarseningCascade.remainder_apply, level_formula, restore_formula]
  rw [← mul_assoc, ← mul_pow]
  norm_num

@[simp] theorem every_detail_zero (x : ℝ) (N : ℕ) : system.detail x N = 0 := by
  exact (system.persistent_iff_details_zero x).1 (fun n => remainder_identity x n) N

@[simp] theorem every_detailTerm_zero (x : ℝ) (N : ℕ) : system.detailTerm x N = 0 := by
  simp only [CoarseningCascade.detailTerm, every_detail_zero, map_zero]

/-- Every coarse coordinate tends to zero, including those of nonzero inputs. -/
theorem coarse_tends_zero (x : ℝ) :
    Tendsto (fun N => system.level x N) atTop (𝓝 0) := by
  have h := (tendsto_pow_atTop_nhds_zero_of_lt_one
    (show (0 : ℝ) ≤ 1/2 by norm_num) (show (1/2 : ℝ) < 1 by norm_num)).mul_const x
  simpa only [level_formula, zero_mul] using h

/-- Vanishing coarse coordinates plus summable details does not imply recovery. -/
theorem coarse_decay_and_summability_not_enough :
    Tendsto (fun N => system.level (1 : ℝ) N) atTop (𝓝 0) ∧
    Summable (fun N => ‖system.detailTerm (1 : ℝ) N‖) ∧
    (1 : ℝ) ∉ system.recoverable := by
  refine ⟨coarse_tends_zero 1, ?_, ?_⟩
  · simp only [every_detailTerm_zero, norm_zero]
    exact summable_zero
  · intro h
    change Tendsto (fun N => system.remainder N (1 : ℝ)) atTop (𝓝 0) at h
    have hh : Tendsto (fun _ : ℕ => (1 : ℝ)) atTop (𝓝 0) := by
      have heq : (fun N => system.remainder N (1 : ℝ)) = (fun _ : ℕ => (1 : ℝ)) :=
        funext (remainder_identity 1)
      rw [heq] at h
      exact h
    have he : (1 : ℝ) = 0 := tendsto_nhds_unique tendsto_const_nhds hh
    norm_num at he

end CascadeBoundaryExamples
end KomorebiSpace
end
