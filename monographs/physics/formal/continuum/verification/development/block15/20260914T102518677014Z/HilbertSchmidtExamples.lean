module
public import KomorebiPhysics.HilbertSchmidtReconstruction
public import KomorebiPhysics.SpectralTruncation
public import KomorebiPhysics.SpectralErrorBounds
public import Mathlib.Analysis.SpecificLimits.Normed

/-! Exact infinite-tail tests for the actual HS norm and spectral sandwiches.
All displayed infinite sums have summability or HasSum proofs. -/
@[expose] public section
noncomputable section
set_option autoImplicit false
namespace KomorebiPhysics
namespace HilbertSchmidtExamples
open Filter BoundedSpectral SpectralTruncation
open scoped Topology BigOperators lp

/-- The actual coordinate Hilbert basis of infinite l2. -/
def basis : HilbertBasis ℕ ℂ Space := .ofRepr (LinearIsometryEquiv.refl ℂ Space)

theorem basis_apply (n : ℕ) : basis n = lp.single 2 n (1 : ℂ) := rfl

/-- A bounded multiplier with nonzero coefficients at every coordinate. -/
def geometric : Symbol := ofBound (fun n => (((1/2 : ℝ)^n : ℝ) : ℂ)) 1 (by
  intro n
  simpa only [Complex.norm_real, Real.norm_eq_abs, abs_of_nonneg (pow_nonneg (by norm_num) _)] using
    pow_le_one₀ (by norm_num : (0 : ℝ) ≤ 1/2) (by norm_num : (1/2 : ℝ) ≤ 1))

theorem geometric_apply (n : ℕ) : geometric n = (((1/2 : ℝ)^n : ℝ) : ℂ) := rfl

theorem geometric_norm (n : ℕ) : ‖geometric n‖ = (1/2 : ℝ)^n := by
  rw [geometric_apply, Complex.norm_real, Real.norm_eq_abs,
    abs_of_nonneg (pow_nonneg (by norm_num) _)]

theorem column_energy (n : ℕ) : ‖diagonal geometric (basis n)‖^2 = (1/4 : ℝ)^n := by
  rw [basis_apply, diagonal_single, mul_one, lp.norm_single (by norm_num), geometric_norm]
  rw [← pow_mul, Nat.mul_comm n 2, pow_mul]
  norm_num

theorem geometric_hasSum : HasSum (fun n => ‖diagonal geometric (basis n)‖^2) (4/3 : ℝ) := by
  simp_rw [column_energy]
  convert hasSum_geometric_of_norm_lt_one (by norm_num : ‖(1/4 : ℝ)‖ < 1) using 1 <;> norm_num

theorem geometric_isHS : HilbertSchmidtCore.IsHS basis (diagonal geometric) :=
  geometric_hasSum.summable

theorem geometric_hs_norm_sq : HilbertSchmidtCore.hsNorm basis (diagonal geometric)^2 = 4/3 := by
  rw [HilbertSchmidtCore.norm_sq]
  exact geometric_hasSum.tsum_eq

/-- The actual difference of the infinite operator and its finite sandwich. -/
def residual (M : ℕ) : Space →L[ℂ] Space :=
  diagonal geometric - diagonal (truncate geometric M)

theorem residual_sandwich (M : ℕ) : residual M = diagonal geometric -
    StrongReconstruction.compression (cutoff M) (diagonal geometric) := by
  rw [residual, truncate_sandwich]
  rfl

theorem residual_column_energy (M n : ℕ) :
    ‖residual M (basis n)‖^2 = if n < M then 0 else (1/4 : ℝ)^n := by
  rw [residual, ← diagonal_sub, basis_apply, diagonal_single, mul_one,
    lp.norm_single (by norm_num)]
  change ‖geometric n - truncate geometric M n‖^2 = _
  rw [truncate_apply]
  split_ifs with hn
  · simp
  · rw [sub_zero, geometric_norm]
    rw [← pow_mul, Nat.mul_comm n 2, pow_mul]
    norm_num

/-- Exact nonzero infinite tail; this is a HasSum, not a default value of tsum. -/
theorem residual_hasSum (M : ℕ) : HasSum (fun n => ‖residual M (basis n)‖^2)
    ((1/4 : ℝ)^M * (4/3)) := by
  have h : HasSum (fun n : ℕ => (1/4 : ℝ)^M * (1/4 : ℝ)^n)
      ((1/4 : ℝ)^M * (4/3)) := by
    convert (hasSum_geometric_of_norm_lt_one (by norm_num : ‖(1/4 : ℝ)‖ < 1)).mul_left
      ((1/4 : ℝ)^M) using 1 <;> norm_num
  have hs : HasSum (fun n => ‖residual M (basis (n+M))‖^2)
      ((1/4 : ℝ)^M * (4/3)) := by
    convert h using 1
    funext n
    rw [residual_column_energy, ite_eq_right (by omega), pow_add]
    ring
  have hfull := hs.sum_range_add
  have hz : (∑ n ∈ Finset.range M, ‖residual M (basis n)‖^2) = 0 := by
    apply Finset.sum_eq_zero
    intro n hn
    rw [residual_column_energy, ite_eq_left (Finset.mem_range.mp hn)]
  simpa only [hz, zero_add] using hfull

theorem residual_isHS (M : ℕ) : HilbertSchmidtCore.IsHS basis (residual M) :=
  (residual_hasSum M).summable

theorem residual_hs_norm_sq (M : ℕ) :
    HilbertSchmidtCore.hsNorm basis (residual M)^2 = (1/4 : ℝ)^M * (4/3) := by
  rw [HilbertSchmidtCore.norm_sq]
  exact (residual_hasSum M).tsum_eq

theorem residual_opNorm (M : ℕ) : ‖residual M‖ = (1/2 : ℝ)^M := by
  have hn : ∀ n, M ≤ n → ‖geometric n - (0 : ℂ)‖ ≤ (1/2 : ℝ)^M := by
    intro n hn
    rw [sub_zero, geometric_norm]
    exact pow_le_pow_of_le_one (by norm_num) (by norm_num) hn
  have hu := error_norm_le geometric 0 M (pow_nonneg (by norm_num) M) hn
  have hl := tail_le_error_norm geometric 0 M M le_rfl
  rw [sub_zero, geometric_norm] at hl
  simpa only [anchored_zero, residual] using le_antisymm hu hl

theorem residual_norm_converges : Tendsto (fun M => ‖residual M‖) atTop (𝓝 0) := by
  simp_rw [residual_opNorm]
  exact tendsto_pow_atTop_nhds_zero_of_lt_one (by norm_num) (by norm_num)

theorem residual_hs_converges :
    Tendsto (fun M => HilbertSchmidtCore.hsNorm basis (residual M)) atTop (𝓝 0) := by
  have h : Tendsto (fun M => HilbertSchmidtCore.hsNorm basis (residual M)^2) atTop (𝓝 0) := by
    simp_rw [residual_hs_norm_sq]
    simpa using (tendsto_pow_atTop_nhds_zero_of_lt_one
      (by norm_num : (0 : ℝ) ≤ 1/4) (by norm_num : (1/4 : ℝ) < 1)).mul_const (4/3 : ℝ)
  simpa only [Function.comp_def, Real.sqrt_sq (HilbertSchmidtCore.norm_nonneg _ _),
    Real.sqrt_zero] using Real.continuous_sqrt.continuousAt.tendsto.comp h

theorem residual_ne_zero (M : ℕ) : residual M ≠ 0 := by
  intro h
  have hn := residual_opNorm M
  rw [h, norm_zero] at hn
  exact (ne_of_gt (pow_pos (by norm_num : (0 : ℝ) < 1/2) M)) hn.symm

theorem cutoff_two_exact :
    ‖residual 2‖ = 1/4 ∧ HilbertSchmidtCore.hsNorm basis (residual 2)^2 = 1/12 := by
  constructor
  · norm_num [residual_opNorm]
  · norm_num [residual_hs_norm_sq]

end HilbertSchmidtExamples
end KomorebiPhysics
