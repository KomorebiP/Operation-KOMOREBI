import KomorebiSpace.DiagonalDefinitions
import KomorebiSpace.RegularizedHilbertRepair
import KomorebiSpace.BudgetProfile
import Mathlib.Analysis.InnerProductSpace.l2Space
import Mathlib.Tactic

/-!
# The actual infinite Hilbert diagonal model

Natural coordinate `j` denotes the printed positive integer `j + 1`.
All vectors below belong to mathlib's real `lp` space at exponent two.
-/

set_option autoImplicit false
noncomputable section
namespace KomorebiSpace.DiagonalRegularization
open scoped RealInnerProductSpace

/-- The real Hilbert space on the printed positive integer coordinates. -/
abbrev H : Type := lp (fun _ : ℕ => ℝ) 2

private theorem hilbert_index_pos (j : ℕ) : 0 < index j := by
  unfold index
  positivity

private theorem hilbert_index_ge_one (j : ℕ) : 1 ≤ index j := by
  unfold index
  have hj : (0 : ℝ) ≤ j := Nat.cast_nonneg j
  linarith

private theorem hilbert_denominator_pos (m j : ℕ) :
    0 < (m : ℝ)^2 + (index j)^2 := by
  have hj := hilbert_index_pos j
  positivity

private theorem hilbert_weight_norm_le (j : ℕ) : ‖wCoord j‖ ≤ 1 := by
  rw [wCoord, norm_inv, Real.norm_eq_abs, abs_of_pos (hilbert_index_pos j)]
  exact inv_le_one_of_one_le₀ (hilbert_index_ge_one j)

private theorem hilbert_mem_of_sq_summable (f : ℕ → ℝ)
    (hf : Summable (fun j => f j ^ 2)) : Memℓp f 2 := by
  apply memℓp_gen
  simpa only [ENNReal.toReal_ofNat, Real.rpow_two, Real.norm_eq_abs, sq_abs] using hf

/-- Coordinate multiplication by the real weights `1/(j+1)`. -/
def Tlinear : H →ₗ[ℝ] H where
  toFun u := ⟨fun j => wCoord j * u j,
    (lp.memℓp u).mono' (fun j => by
      rw [norm_mul]
      exact mul_le_of_le_one_left (norm_nonneg _) (hilbert_weight_norm_le j))⟩
  map_add' u v := by
    apply lp.ext
    funext j
    change wCoord j * (u j + v j) = wCoord j * u j + wCoord j * v j
    ring
  map_smul' r u := by
    apply lp.ext
    funext j
    change wCoord j * (r * u j) = r * (wCoord j * u j)
    ring

/-- The diagonal operator is bounded, with operator norm at most one. -/
def T : H →L[ℝ] H :=
  Tlinear.mkContinuous 1 (by
    intro u
    rw [one_mul]
    apply lp.norm_mono (by norm_num)
    intro j
    change ‖wCoord j * u j‖ ≤ ‖u j‖
    rw [norm_mul]
    exact mul_le_of_le_one_left (norm_nonneg _) (hilbert_weight_norm_le j))

@[simp] theorem T_apply (u : H) (j : ℕ) : T u j = wCoord j * u j := rfl

theorem T_norm_le (u : H) : ‖T u‖ ≤ ‖u‖ := by
  apply lp.norm_mono (by norm_num)
  intro j
  rw [T_apply, norm_mul]
  exact mul_le_of_le_one_left (norm_nonneg _) (hilbert_weight_norm_le j)

theorem T_opNorm_le_one : ‖T‖ ≤ 1 := by
  apply T.opNorm_le_bound (by norm_num)
  intro u
  simpa only [one_mul] using T_norm_le u

/-- Self-adjointness is proved from the infinite Hilbert inner product. -/
theorem T_adjoint : T.adjoint = T := by
  apply ContinuousLinearMap.ext
  intro x
  apply ext_inner_right ℝ
  intro y
  rw [ContinuousLinearMap.adjoint_inner_left, lp.inner_eq_tsum, lp.inner_eq_tsum]
  apply tsum_congr
  intro j
  simp only [T_apply, Real.inner_apply]
  ring

theorem T_isSelfAdjoint : IsSelfAdjoint T :=
  ContinuousLinearMap.isSelfAdjoint_iff'.mpr T_adjoint

/-- No nonzero coordinate is killed by `T`. -/
theorem T_injective : Function.Injective T := by
  intro x y h
  apply lp.ext
  funext j
  have hj := congrArg (fun u : H => u j) h
  simp only [T_apply] at hj
  exact mul_left_cancel₀ (inv_ne_zero (ne_of_gt (hilbert_index_pos j))) hj


end KomorebiSpace.DiagonalRegularization
