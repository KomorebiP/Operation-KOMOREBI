import PaperX.Singular
import Mathlib.Analysis.SpecialFunctions.Log.Basic
import Mathlib.Analysis.SpecificLimits.Basic

/-! The manuscript's branching dimension is a finite-level counting exponent.
It is not the cardinality or dimension of the set of infinite compatible roots. -/
set_option autoImplicit false
namespace PaperX.BranchingDimension
open Filter Topology

theorem ceil_ratio_bounds (m e : ℕ) (he : 0 < e) :
    (m : ℝ) / e ≤ (m ⌈/⌉ e : ℕ) ∧
    ((m ⌈/⌉ e : ℕ) : ℝ) ≤ (m : ℝ) / e + 1 := by
  have heR : 0 < (e : ℝ) := by exact_mod_cast he
  have hl : m ≤ e * (m ⌈/⌉ e) := le_smul_ceilDiv he
  have hu : e * (m ⌈/⌉ e) ≤ m+e := by
    have H := Nat.div_mul_le_self (m+e-1) e
    rw [Nat.ceilDiv_eq_add_pred_div]
    nlinarith [Nat.sub_le (m+e) 1]
  have hlR : (m : ℝ) ≤ (e : ℝ) * (m ⌈/⌉ e : ℕ) := by exact_mod_cast hl
  have huR : (e : ℝ) * (m ⌈/⌉ e : ℕ) ≤ (m : ℝ)+e := by exact_mod_cast hu
  constructor
  · exact (div_le_iff₀ heR).mpr (by nlinarith)
  · calc
      ((m ⌈/⌉ e : ℕ) : ℝ) ≤ ((m : ℝ)+e)/e :=
        (le_div_iff₀ heR).mpr (by nlinarith)
      _ = (m : ℝ)/e+1 := by rw [add_div, div_self (ne_of_gt heR)]

theorem ceil_ratio_limit (e : ℕ) (he : 0 < e) :
    Tendsto (fun m : ℕ => ((m ⌈/⌉ e : ℕ) : ℝ) / m) atTop (𝓝 (1/(e : ℝ))) := by
  have heR : (e : ℝ) ≠ 0 := by exact_mod_cast Nat.ne_of_gt he
  have hu : Tendsto (fun m : ℕ => 1/(e : ℝ)+1/(m : ℝ)) atTop (𝓝 (1/(e : ℝ))) := by
    simpa only [add_zero] using
      ((tendsto_const_nhds (x := 1/(e : ℝ))).add (tendsto_one_div_atTop_nhds_zero_nat (𝕜 := ℝ)))
  apply tendsto_of_tendsto_of_tendsto_of_le_of_le' tendsto_const_nhds hu
  · refine eventually_atTop.mpr ⟨1, fun m hm => ?_⟩
    have hmR : 0 < (m : ℝ) := by exact_mod_cast (by omega : 0 < m)
    calc
      1/(e : ℝ) = ((m : ℝ)/e)/m := by field_simp
      _ ≤ ((m ⌈/⌉ e : ℕ) : ℝ)/m :=
        div_le_div_of_nonneg_right (ceil_ratio_bounds m e he).1 (le_of_lt hmR)
  · refine eventually_atTop.mpr ⟨1, fun m hm => ?_⟩
    have hmR : 0 < (m : ℝ) := by exact_mod_cast (by omega : 0 < m)
    calc
      ((m ⌈/⌉ e : ℕ) : ℝ)/m ≤ ((m : ℝ)/e+1)/m :=
        div_le_div_of_nonneg_right (ceil_ratio_bounds m e he).2 (le_of_lt hmR)
      _ = 1/(e : ℝ)+1/m := by field_simp

/-- The actual logarithmic limit, not merely an estimate from fitted counts. -/
theorem power_count_dimension (q e : ℕ) (hq : 1 < q) (he : 0 < e) :
    Tendsto (fun m : ℕ => Real.log ((q : ℝ)^(m - (m ⌈/⌉ e))) /
      Real.log (q : ℝ) / m) atTop (𝓝 (1-1/(e : ℝ))) := by
  have hqR : Real.log (q : ℝ) ≠ 0 := (Real.log_pos (by exact_mod_cast hq)).ne'
  have h := (tendsto_const_nhds (x := (1 : ℝ))).sub (ceil_ratio_limit e he)
  apply h.congr'
  refine eventually_atTop.mpr ⟨1, fun m hm => ?_⟩
  have hmR : (m : ℝ) ≠ 0 := by exact_mod_cast (by omega : m ≠ 0)
  dsimp only
  rw [Real.log_pow, mul_div_cancel_right₀ _ hqR,
    Nat.cast_sub (PaperX.Singular.ceil_threshold_le m e he)]
  field_simp

variable {O : Type*} [CommRing O] [IsDomain O] [IsDiscreteValuationRing O]
variable [Finite (O ⧸ IsLocalRing.maximalIdeal O)]

/-- Paper X 6.6, using cardinalities of actual roots over a general finite-residue DVR. -/
theorem actual_singular_dimension (e : ℕ) (he : 0 < e) :
    Tendsto (fun m : ℕ => Real.log (Nat.card (PaperX.Singular.Roots (O := O) m e) : ℝ) /
      Real.log (Nat.card (O ⧸ IsLocalRing.maximalIdeal O) : ℝ) / m)
      atTop (𝓝 (1-1/(e : ℝ))) := by
  convert power_count_dimension (Nat.card (O ⧸ IsLocalRing.maximalIdeal O)) e
    Finite.one_lt_card he using 1
  ext m
  rw [PaperX.Singular.singular_root_count m e he, Nat.cast_pow]

end PaperX.BranchingDimension
