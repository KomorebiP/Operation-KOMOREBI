import Mathlib.Analysis.PSeries
import Mathlib.Analysis.Asymptotics.SpecificAsymptotics
import Mathlib.Analysis.SpecialFunctions.Log.Basic
import Mathlib.Tactic

/-! A qualitative zero-mean counting error does not imply convergence of
its Dirichlet series at one. This is a counterexample to that analytic
inference, not a statement about the actual arithmetic ray-class errors. -/
set_option autoImplicit false
noncomputable section
namespace PaperX.CountErrorBoundary
open Filter Finset
open scoped Topology

def coefficient (n : ℕ) : ℝ := (Real.log (n : ℝ))⁻¹
def weighted (n : ℕ) : ℝ := coefficient n / n

theorem coefficient_tendsto_zero : Tendsto coefficient atTop (𝓝 0) := by
  exact tendsto_inv_atTop_zero.comp
    (Real.tendsto_log_atTop.comp tendsto_natCast_atTop_atTop)

/-- The summatory coefficients have size o(N), expressed as a normalized limit. -/
theorem summatory_div_tendsto_zero :
    Tendsto (fun N : ℕ => (∑ n ∈ range N, coefficient n) / N) atTop (𝓝 0) := by
  simpa only [div_eq_mul_inv, mul_comm] using coefficient_tendsto_zero.cesaro

theorem weighted_eventually_nonneg : 0 ≤ᶠ[atTop] weighted := by
  filter_upwards [eventually_ge_atTop 2] with n hn
  have hnr : (1 : ℝ) ≤ n := by exact_mod_cast (show 1 ≤ n by omega)
  exact div_nonneg (inv_nonneg.mpr (Real.log_nonneg hnr)) (Nat.cast_nonneg n)

theorem weighted_eventually_antitone :
    ∀ᶠ n in atTop, weighted (n + 1) ≤ weighted n := by
  filter_upwards [eventually_ge_atTop 2] with n hn
  have hn0 : (0 : ℝ) < n := by exact_mod_cast (show 0 < n by omega)
  have hn1 : (1 : ℝ) < n := by exact_mod_cast (show 1 < n by omega)
  have hlog := Real.log_pos hn1
  have hle : (n : ℝ) ≤ n + 1 := by linarith
  have hlogle := Real.log_le_log hn0 hle
  simp only [weighted, coefficient, Nat.cast_add, Nat.cast_one,
    div_eq_mul_inv, ← mul_inv_rev]
  apply inv_anti₀
  · exact mul_pos hn0 hlog
  · exact mul_le_mul hle hlogle hlog.le (by positivity)

theorem condensed_identity (k : ℕ) :
    Real.log 2 * ((2 : ℝ) ^ k * weighted (2 ^ k)) = (k : ℝ)⁻¹ := by
  have hlog : Real.log 2 ≠ 0 := ne_of_gt (Real.log_pos (by norm_num))
  have hpow : (2 : ℝ) ^ k ≠ 0 := pow_ne_zero k (by norm_num)
  by_cases hk : k = 0
  · simp [hk, weighted, coefficient]
  have hkR : (k : ℝ) ≠ 0 := Nat.cast_ne_zero.mpr hk
  simp only [weighted, coefficient, Nat.cast_pow, Nat.cast_ofNat, Real.log_pow]
  field_simp

/-- Nevertheless the positive Dirichlet series at s=1 is nonsummable. -/
theorem weighted_not_summable : ¬ Summable weighted := by
  intro h
  have hc := (summable_condensed_iff_of_eventually_nonneg
    weighted_eventually_nonneg weighted_eventually_antitone).mpr h
  have hs := hc.mul_left (Real.log 2)
  exact Real.not_summable_natCast_inv (hs.congr condensed_identity)

/-- Therefore normalized summatory convergence alone cannot justify the
claimed s=1 convergence for all real coefficient sequences. -/
theorem qualitative_counting_does_not_imply_convergence :
    ¬ (∀ a : ℕ → ℝ,
      Tendsto (fun N : ℕ => (∑ n ∈ range N, a n) / N) atTop (𝓝 0) →
      Summable (fun n => a n / n)) := by
  intro h
  exact weighted_not_summable (h coefficient summatory_div_tendsto_zero)

end PaperX.CountErrorBoundary
