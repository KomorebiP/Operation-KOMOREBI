import KomorebiSpace.InfiniteDiagonalModel
import KomorebiSpace.HilbertKernelProjection

/-!
# The concrete infinite diagonal closed-range obstruction

The vectors here are actual unit coordinate vectors in `lp (fun _ : ℕ => ℝ) 2`.
The operator is the same `T` used by the diagonal regularization model.
-/

set_option autoImplicit false
noncomputable section
namespace KomorebiSpace.DiagonalRegularization
open Filter Topology
open scoped RealInnerProductSpace

/-- The unit vector in natural coordinate `j`, representing printed coordinate `j+1`. -/
def unitCoordinate (j : ℕ) : H := lp.single 2 j (1 : ℝ)

@[simp] theorem norm_unitCoordinate (j : ℕ) : ‖unitCoordinate j‖ = 1 := by
  simp [unitCoordinate, lp.norm_single (by norm_num : (0 : ENNReal) < 2)]

/-- The actual diagonal operator has eigenvalue `1/(j+1)` on each coordinate. -/
theorem T_unitCoordinate (j : ℕ) : T (unitCoordinate j) = wCoord j • unitCoordinate j := by
  apply lp.ext
  funext k
  by_cases hk : k = j
  · subst k
    simp [unitCoordinate]
  · simp [unitCoordinate, lp.single_apply, Pi.single_apply, hk]

/-- Unit witnesses have exactly the printed reciprocal residual norm. -/
theorem norm_T_unitCoordinate (j : ℕ) : ‖T (unitCoordinate j)‖ = 1 / ((j : ℝ) + 1) := by
  rw [T_unitCoordinate, norm_smul, norm_unitCoordinate, mul_one]
  simp [wCoord, index, Real.norm_eq_abs, abs_of_pos (by positivity : (0 : ℝ) < j + 1),
    one_div]

/-- The residuals of actual unit vectors tend to zero in the infinite Hilbert model. -/
theorem tendsto_norm_T_unitCoordinate :
    Tendsto (fun j : ℕ => ‖T (unitCoordinate j)‖) atTop (𝓝 0) := by
  simpa only [norm_T_unitCoordinate] using
    (tendsto_one_div_add_atTop_nhds_zero_nat (𝕜 := ℝ))

/-- Injectivity identifies the exact space of the actual diagonal operator with zero. -/
theorem T_ker_eq_bot : T.ker = ⊥ := by
  exact LinearMap.ker_eq_bot.mpr T_injective

/-- The coordinate witnesses lie in the orthogonal complement required by the abstract theorem. -/
theorem unitCoordinate_mem_ker_orthogonal (j : ℕ) : unitCoordinate j ∈ T.kerᗮ := by
  rw [T_ker_eq_bot, Submodule.bot_orthogonal_eq_top]
  trivial

/-- Every proposed finite inverse gain fails on a concrete unit coordinate vector. -/
theorem unitCoordinate_witness (C : ℝ) (_hC : 0 ≤ C) :
    ∃ j : ℕ, C * ‖T (unitCoordinate j)‖ < 1 := by
  obtain ⟨j, hj⟩ := exists_nat_gt C
  refine ⟨j, ?_⟩
  rw [norm_T_unitCoordinate, mul_one_div]
  exact (div_lt_one (by positivity : (0 : ℝ) < j + 1)).mpr (by linarith)

/-- The actual infinite diagonal operator has nonclosed range. -/
theorem T_not_closed_range : ¬ IsClosed (Set.range T) := by
  apply HilbertKernelProjection.not_closed_range_of_unit_witnesses T
  intro C hC
  obtain ⟨j, hj⟩ := unitCoordinate_witness C hC
  exact ⟨unitCoordinate j, unitCoordinate_mem_ker_orthogonal j, norm_unitCoordinate j, hj⟩

end KomorebiSpace.DiagonalRegularization
