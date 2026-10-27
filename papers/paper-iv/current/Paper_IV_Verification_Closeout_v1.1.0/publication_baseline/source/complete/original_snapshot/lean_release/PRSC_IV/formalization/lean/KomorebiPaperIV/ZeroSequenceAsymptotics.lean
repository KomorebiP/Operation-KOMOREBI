/-
Copyright (c) 2026 Komorebi P. All rights reserved.
Authors: Komorebi P.
-/
import KomorebiPaperIV.SignedZeroSequence
import Mathlib.Analysis.PSeries
import Mathlib.Analysis.Asymptotics.SpecificAsymptotics
import Mathlib.Analysis.Normed.Module.FiniteDimension

namespace Komorebi.PaperIV
noncomputable section
open Filter Asymptotics Metric

theorem signedZeroCenter_tendsto_atTop {N : ℕ} (hN : 2 ≤ N) :
    Tendsto (signedZeroCenter N) atTop atTop := by
  exact (tendsto_atTop_add_const_right atTop (1 / 2 : ℝ) tendsto_natCast_atTop_atTop).const_mul_atTop
    (div_pos Real.pi_pos (signed_sine_pos hN))

theorem signedPositiveZero_sub_center_isBigO_one {N : ℕ} (hN : 3 ≤ N) :
    (fun m => signedPositiveZero N m - signedZeroCenter N m) =O[atTop] (fun _ => (1 : ℝ)) := by
  obtain ⟨C, _, m0, hm0⟩ := signedPositiveZero_local_strings hN
  apply isBigO_iff.mpr
  refine ⟨1 / ‖signedZeroFrequency N‖, ?_⟩
  filter_upwards [eventually_ge_atTop m0] with m hm
  have hb := (hm0 m hm).1.2.2
  simpa only [mem_closedBall, dist_eq_norm, ← Complex.ofReal_sub, Complex.norm_real,
    Real.norm_eq_abs, norm_one, mul_one] using hb

theorem signedPositiveZero_equivalent_center {N : ℕ} (hN : 3 ≤ N) :
    signedPositiveZero N ~[atTop] signedZeroCenter N := by
  have ht : Tendsto (fun m => ‖signedZeroCenter N m‖) atTop atTop := by
    apply (signedZeroCenter_tendsto_atTop (by omega : 2 ≤ N)).congr'
    filter_upwards [] with m
    rw [Real.norm_eq_abs, abs_of_nonneg]
    exact (le_of_lt (one_div_pos.mpr (norm_pos_iff.mpr (signedZeroFrequency_ne_zero (by omega))))).trans
      (signedZeroCenter_ge_radius (by omega) m)
  exact (signedPositiveZero_sub_center_isBigO_one hN).trans_isLittleO
    (isLittleO_const_left.mpr (Or.inr ht))

theorem signedPositiveZero_tendsto_atTop {N : ℕ} (hN : 3 ≤ N) :
    Tendsto (signedPositiveZero N) atTop atTop := by
  have he := signedPositiveZero_equivalent_center hN
  exact he.symm.tendsto_atTop (signedZeroCenter_tendsto_atTop (by omega))

theorem reducedPositiveZero_equivalent_center_power {N : ℕ} (hN : 3 ≤ N) :
    reducedPositiveZero N ~[atTop] (fun m => signedZeroCenter N m ^ N) :=
  (signedPositiveZero_equivalent_center hN).pow N

/-- The reciprocal powers of the actual positive zero sequence have the sharp threshold `s > 1`. -/
theorem signedPositiveZero_reciprocal_rpow_summable_iff {N : ℕ} (hN : 3 ≤ N) (s : ℝ) :
    Summable (fun m => 1 / signedPositiveZero N m ^ s) ↔ 1 < s := by
  have hA : 0 < Real.pi / Real.sin (Real.pi / N) := div_pos Real.pi_pos (signed_sine_pos (by omega))
  have ht : 0 ≤ signedZeroCenter N := fun m => by unfold signedZeroCenter; positivity
  have he := (IsEquivalent.rpow ht (signedPositiveZero_equivalent_center hN) (r := s)).inv
  have heq : (fun m => 1 / signedPositiveZero N m ^ s) ~[atTop]
      (fun m => 1 / signedZeroCenter N m ^ s) := by simpa only [one_div] using! he
  rw [heq.summable_iff_nat]
  have hf : (fun m => 1 / signedZeroCenter N m ^ s) =
      (fun m : ℕ => (1 / (Real.pi / Real.sin (Real.pi / N)) ^ s) * (1 / |(m : ℝ) + 1 / 2| ^ s)) := by
    funext m
    rw [signedZeroCenter, Real.mul_rpow hA.le (by positivity), abs_of_pos (by positivity : 0 < (m : ℝ) + 1 / 2)]
    ring
  rw [hf, summable_mul_left_iff (one_div_ne_zero (ne_of_gt (Real.rpow_pos_of_pos hA s)))]
  exact Real.summable_one_div_nat_add_rpow (1 / 2) s

/-- The reduced positive zeros have reciprocal-power threshold `N s > 1`. -/
theorem reducedPositiveZero_reciprocal_rpow_summable_iff {N : ℕ} (hN : 3 ≤ N) (s : ℝ) :
    Summable (fun m => 1 / reducedPositiveZero N m ^ s) ↔ 1 < (N : ℝ) * s := by
  have he : (fun m => 1 / reducedPositiveZero N m ^ s) =
      (fun m => 1 / signedPositiveZero N m ^ ((N : ℝ) * s)) := by
    funext m
    rw [reducedPositiveZero, ← Real.rpow_natCast, ← Real.rpow_mul (le_of_lt (signedPositiveZero_pos (by omega) m))]
  rw [he]
  exact signedPositiveZero_reciprocal_rpow_summable_iff hN _

theorem reducedPositiveZero_reciprocal_summable {N : ℕ} (hN : 3 ≤ N) :
    Summable (fun m => 1 / reducedPositiveZero N m) := by
  simpa using (reducedPositiveZero_reciprocal_rpow_summable_iff hN 1).mpr (by exact_mod_cast (show 1 < N * 1 by omega))

end
end Komorebi.PaperIV
