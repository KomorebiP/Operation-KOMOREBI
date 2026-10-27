/-
Copyright (c) 2026 Komorebi P. All rights reserved.
Authors: Komorebi P.
-/
import KomorebiPaperIV.EntireQuotientGrowth

namespace Komorebi.PaperIV
noncomputable section
open Set Filter Metric Real MeromorphicOn
open scoped Topology Classical

theorem finite_sum_le_finsum_nonneg {α : Type*} {g : α → ℤ}
    (hg : (Function.support g).Finite) (h0 : ∀ x, 0 ≤ g x) (S : Finset α) :
    ∑ x ∈ S, g x ≤ ∑ᶠ x, g x := by
  have he : (∑ᶠ x, g x) = ∑ x ∈ S ∪ hg.toFinset, g x := by
    apply finsum_eq_sum_of_support_subset
    intro x hx
    exact Finset.mem_union_right S (hg.mem_toFinset.mpr hx)
  rw [he]
  exact Finset.sum_le_sum_of_subset_of_nonneg Finset.subset_union_left (fun x _ _ => h0 x)

theorem entire_divisor_eq_orderNat {f : ℂ → ℂ} (hf : Differentiable ℂ f)
    (h0 : f 0 ≠ 0) {R : ℝ} {z : ℂ} (hz : ‖z‖ ≤ R) :
    divisor f (closedBall 0 R) z = (analyticOrderNatAt f z : ℤ) := by
  have ha : AnalyticOnNhd ℂ f (closedBall 0 R) := fun w _ => hf.analyticAt w
  rw [ha.divisor_apply (by simpa using hz),
    ← Nat.cast_analyticOrderNatAt (entire_analyticOrderAt_ne_top (fun w => hf.analyticAt w) h0 z),
    ENat.map_natCast]
  rfl

theorem entire_zero_finite_weight_growth {f : ℂ → ℂ} (hf : Differentiable ℂ f)
    (h0 : f 0 = 1) {C p : ℝ} (hC : 0 ≤ C)
    (hgrowth : ∀ R : ℝ, 1 ≤ R → ∀ z : ℂ, ‖z‖ ≤ R → ‖f z‖ ≤ exp (C * R ^ p))
    {R : ℝ} (hR : 1 ≤ R) (S : Finset ℂ) (hS : ∀ z ∈ S, ‖z‖ ≤ R) :
    (∑ z ∈ S, (analyticOrderNatAt f z : ℝ)) ≤ (C * (2 : ℝ) ^ p / log 2) * R ^ p := by
  have hr : 0 < R := by linarith
  have ha : AnalyticOnNhd ℂ f (closedBall 0 |2 * R|) := fun z _ => hf.analyticAt z
  have hne : f 0 ≠ 0 := by rw [h0]; exact one_ne_zero
  have hj := ha.sum_divisor_le (r := R) (M := exp (C * (2 * R) ^ p))
    (by simpa only [abs_of_pos hr] using hr)
    (by rw [abs_of_pos hr, abs_of_pos (by positivity : 0 < 2 * R)]; linarith)
    (Real.one_le_exp_iff.mpr (by positivity)) hne (fun z hz => ?_)
  · have haR : AnalyticOnNhd ℂ f (closedBall 0 R) := fun z _ => hf.analyticAt z
    have hs : (∑ z ∈ S, (analyticOrderNatAt f z : ℤ)) ≤ ∑ᶠ z, divisor f (closedBall 0 R) z := by
      calc
        _ = ∑ z ∈ S, divisor f (closedBall 0 R) z :=
          Finset.sum_congr rfl (fun z hz => (entire_divisor_eq_orderNat hf hne (hS z hz)).symm)
        _ ≤ _ := finite_sum_le_finsum_nonneg
          ((divisor f (closedBall 0 R)).finiteSupport (isCompact_closedBall ..))
          (fun z => haR.divisor_nonneg z) S
    have hsR : (Int.cast (∑ z ∈ S, (analyticOrderNatAt f z : ℤ)) : ℝ) ≤
        Int.cast (∑ᶠ z, divisor f (closedBall 0 R) z) := Int.cast_le.mpr hs
    simp only [Int.cast_sum, Int.cast_natCast] at hsR
    rw [abs_of_pos hr, h0, norm_one, div_one, log_exp,
      mul_div_cancel_right₀ (2 : ℝ) hr.ne', Real.mul_rpow (by norm_num) hr.le] at hj
    calc
      _ ≤ C * ((2 : ℝ) ^ p * R ^ p) / log 2 := hsR.trans hj
      _ = _ := by ring
  · rw [abs_of_pos (by positivity : 0 < 2 * R), mem_sphere_zero_iff_norm] at hz
    exact hgrowth (2 * R) (by linarith) z hz.le

theorem entire_zero_subtype_weight_growth {f : ℂ → ℂ} (hf : Differentiable ℂ f)
    (h0 : f 0 = 1) {C p : ℝ} (hC : 0 ≤ C)
    (hgrowth : ∀ R : ℝ, 1 ≤ R → ∀ z : ℂ, ‖z‖ ≤ R → ‖f z‖ ≤ exp (C * R ^ p))
    {R : ℝ} (hR : 1 ≤ R) (S : Finset {z : ℂ // f z = 0}) (hS : ∀ z ∈ S, ‖(z : ℂ)‖ ≤ R) :
    (∑ z ∈ S, (analyticOrderNatAt f z : ℝ)) ≤ (C * (2 : ℝ) ^ p / log 2) * R ^ p := by
  let e : {z : ℂ // f z = 0} ↪ ℂ := ⟨Subtype.val, Subtype.val_injective⟩
  have h := entire_zero_finite_weight_growth hf h0 hC hgrowth hR (S.map e) (by
    intro z hz
    obtain ⟨u, hu, rfl⟩ := Finset.mem_map.mp hz
    exact hS u hu)
  simpa only [Finset.sum_map, e, Function.Embedding.coeFn_mk] using h

theorem entire_zero_bounded_finite {f : ℂ → ℂ} (hf : Differentiable ℂ f)
    (h0 : f 0 ≠ 0) (R : ℝ) :
    {z : {z : ℂ // f z = 0} | ‖(z : ℂ)‖ ≤ R}.Finite := by
  have ha : AnalyticOnNhd ℂ f univ := fun z _ => hf.analyticAt z
  have hn : ¬ EqOn f 0 univ := fun h => h0 (h (mem_univ (0 : ℂ)))
  have he := (ha.eqOn_zero_or_eventually_ne_zero_of_preconnected isPreconnected_univ).resolve_left hn
  have hk := (codiscreteWithin_mono (subset_univ (closedBall (0 : ℂ) R))) he
  have hc := (isCompact_closedBall (0 : ℂ) R).finite_sdiff_of_mem_codiscreteWithin hk
  apply Set.Finite.of_finite_image (f := fun z : {z : ℂ // f z = 0} => (z : ℂ)) _ Subtype.val_injective.injOn
  exact hc.subset (by rintro z ⟨u, hu, rfl⟩; exact ⟨by simpa using hu, fun hn => hn u.property⟩)

end
end Komorebi.PaperIV
