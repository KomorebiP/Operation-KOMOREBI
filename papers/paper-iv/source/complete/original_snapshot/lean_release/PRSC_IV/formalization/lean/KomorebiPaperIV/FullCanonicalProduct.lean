/-
Copyright (c) 2026 Komorebi P. All rights reserved.
Authors: Komorebi P.
-/
import KomorebiPaperIV.FullZeroSummability
import Mathlib.Analysis.Normed.Module.MultipliableUniformlyOn
import Mathlib.Analysis.Complex.LocallyUniformLimit

namespace Komorebi.PaperIV
noncomputable section
open Set Filter

/-- Every distinct zero occurs exactly its analytic multiplicity many times. -/
def ZeroMultiplicityIndex (f : ℂ → ℂ) :=
  Σ z : {z : ℂ // f z = 0}, Fin (analyticOrderNatAt f z)

def indexedZero {f : ℂ → ℂ} (i : ZeroMultiplicityIndex f) : ℂ := i.1.val

def fullCanonicalProduct (f : ℂ → ℂ) (w : ℂ) : ℂ :=
  ∏' i : ZeroMultiplicityIndex f, (1 - w / indexedZero i)

theorem zeroMultiplicity_reciprocal_summable {f : ℂ → ℂ} (hf : ZeroPowerSummable f 1) :
    Summable (fun i : ZeroMultiplicityIndex f => 1 / ‖indexedZero i‖) := by
  apply (summable_sigma_of_nonneg (fun i : ZeroMultiplicityIndex f => by positivity)).mpr
  constructor
  · intro z
    exact (hasSum_fintype _).summable
  · simpa only [indexedZero, tsum_fintype, Finset.sum_const, Finset.card_univ,
      Fintype.card_fin, nsmul_eq_mul, mul_one_div, ZeroPowerSummable, Real.rpow_one] using hf

theorem fullCanonicalProduct_factors_summable {f : ℂ → ℂ} (hf : ZeroPowerSummable f 1) (w : ℂ) :
    Summable (fun i : ZeroMultiplicityIndex f => ‖w / indexedZero i‖) := by
  simpa only [norm_div, mul_one_div] using (zeroMultiplicity_reciprocal_summable hf).mul_left ‖w‖

theorem fullCanonicalProduct_multipliable {f : ℂ → ℂ} (hf : ZeroPowerSummable f 1) (w : ℂ) :
    Multipliable (fun i : ZeroMultiplicityIndex f => 1 - w / indexedZero i) :=
  multipliable_one_sub_of_summable (fullCanonicalProduct_factors_summable hf w)

theorem fullCanonicalProduct_uniform_on_compact {f : ℂ → ℂ} (hf : ZeroPowerSummable f 1)
    {K : Set ℂ} (hK : IsCompact K) :
    HasProdUniformlyOn (fun (i : ZeroMultiplicityIndex f) w => 1 - w / indexedZero i)
      (fullCanonicalProduct f) K := by
  obtain ⟨B, hB⟩ := hK.isBounded.exists_norm_le
  have h := ((zeroMultiplicity_reciprocal_summable hf).mul_left B).hasProdUniformlyOn_one_add hK
    (f := fun (i : ZeroMultiplicityIndex f) w => -w / indexedZero i)
    (Eventually.of_forall (fun i w hw => ?_)) (fun _ => by fun_prop)
  · simpa only [fullCanonicalProduct, neg_div, ← sub_eq_add_neg] using! h
  · rw [norm_div, norm_neg, mul_one_div]
    exact div_le_div_of_nonneg_right (hB w hw) (norm_nonneg _)

theorem fullCanonicalProduct_locally_uniform {f : ℂ → ℂ} (hf : ZeroPowerSummable f 1) :
    HasProdLocallyUniformlyOn (fun (i : ZeroMultiplicityIndex f) w => 1 - w / indexedZero i)
      (fullCanonicalProduct f) univ := by
  apply hasProdLocallyUniformlyOn_of_forall_compact isOpen_univ
  intro K _ hK
  exact fullCanonicalProduct_uniform_on_compact hf hK

theorem fullCanonicalProduct_entire {f : ℂ → ℂ} (hf : ZeroPowerSummable f 1) :
    Differentiable ℂ (fullCanonicalProduct f) := by
  apply differentiableOn_univ.mp
  apply (fullCanonicalProduct_locally_uniform hf).differentiableOn _ isOpen_univ
  apply Eventually.of_forall
  intro S
  have h : DifferentiableOn ℂ (fun w : ℂ => ∏ i ∈ S, (1 - w / indexedZero i)) univ :=
    DifferentiableOn.fun_finsetProd (fun _ _ => by fun_prop)
  simpa only [Finset.prod_fn] using h

theorem fullCanonicalProduct_zero (f : ℂ → ℂ) : fullCanonicalProduct f 0 = 1 := by
  simp [fullCanonicalProduct]

theorem fullCanonicalProduct_ne_zero {f : ℂ → ℂ} (hf : ZeroPowerSummable f 1)
    (hf0 : f 0 ≠ 0) {w : ℂ} (hw : ∀ i : ZeroMultiplicityIndex f, w ≠ indexedZero i) :
    fullCanonicalProduct f w ≠ 0 := by
  have h := tprod_one_add_ne_zero_of_summable
    (f := fun i : ZeroMultiplicityIndex f => -w / indexedZero i) (fun i => ?_)
    (by simpa only [neg_div, norm_neg] using fullCanonicalProduct_factors_summable hf w)
  · simpa only [fullCanonicalProduct, neg_div, ← sub_eq_add_neg] using! h
  · rw [neg_div, ← sub_eq_add_neg, sub_ne_zero]
    intro he
    apply hw i
    apply (div_eq_one_iff_eq ?_).mp he.symm
    intro hz
    apply hf0
    have he := i.1.property
    change f (indexedZero i) = 0 at he
    rw [hz] at he
    exact he

theorem fullCanonicalProduct_zero_iff_index {f : ℂ → ℂ} (hf : ZeroPowerSummable f 1)
    (hf0 : f 0 ≠ 0) (w : ℂ) :
    fullCanonicalProduct f w = 0 ↔ ∃ i : ZeroMultiplicityIndex f, w = indexedZero i := by
  constructor
  · intro hz
    by_contra h
    push Not at h
    exact fullCanonicalProduct_ne_zero hf hf0 h hz
  · rintro ⟨i, rfl⟩
    apply tprod_of_exists_eq_zero
    refine ⟨i, ?_⟩
    rw [div_self, sub_self]
    intro hz
    apply hf0
    have he := i.1.property
    change f (indexedZero i) = 0 at he
    rw [hz] at he
    exact he

theorem indexedZero_ne_zero {f : ℂ → ℂ} (hf0 : f 0 ≠ 0) (i : ZeroMultiplicityIndex f) :
    indexedZero i ≠ 0 := by
  intro h
  apply hf0
  have he := i.1.property
  change f (indexedZero i) = 0 at he
  rwa [h] at he

theorem entire_zero_multiplicity_pos {f : ℂ → ℂ} (hf : Differentiable ℂ f)
    (hf0 : f 0 ≠ 0) {w : ℂ} (hw : f w = 0) : 0 < analyticOrderNatAt f w := by
  apply ENat.toNat_pos
  · exact (hf.analyticAt w).analyticOrderAt_ne_zero.mpr hw
  · exact entire_analyticOrderAt_ne_top (fun z => hf.analyticAt z) hf0 w

theorem fullCanonicalProduct_zero_iff {f : ℂ → ℂ} (hf : Differentiable ℂ f)
    (hs : ZeroPowerSummable f 1) (hf0 : f 0 ≠ 0) (w : ℂ) :
    fullCanonicalProduct f w = 0 ↔ f w = 0 := by
  rw [fullCanonicalProduct_zero_iff_index hs hf0]
  constructor
  · rintro ⟨i, rfl⟩
    exact i.1.property
  · intro hw
    exact ⟨⟨⟨w, hw⟩, ⟨0, entire_zero_multiplicity_pos hf hf0 hw⟩⟩, rfl⟩

theorem zeroMultiplicityIndex_countable {f : ℂ → ℂ} (hs : ZeroPowerSummable f 1)
    (hf0 : f 0 ≠ 0) : Countable (ZeroMultiplicityIndex f) := by
  have hc := (zeroMultiplicity_reciprocal_summable hs).countable_support
  have he : Function.support (fun i : ZeroMultiplicityIndex f => 1 / ‖indexedZero i‖) = univ := by
    ext i
    simp only [Function.mem_support, mem_univ, iff_true]
    exact one_div_ne_zero (norm_ne_zero_iff.mpr (indexedZero_ne_zero hf0 i))
  rw [he] at hc
  exact countable_univ_iff.mp hc

/-- The complete product includes every exceptional zero with its actual multiplicity. -/
theorem entireReducedDenominator_full_product_properties {N : ℕ} (hN : 2 ≤ N) :
    Differentiable ℂ (fullCanonicalProduct (entireReducedDenominator N)) ∧
    fullCanonicalProduct (entireReducedDenominator N) 0 = 1 ∧
    (∀ w, fullCanonicalProduct (entireReducedDenominator N) w = 0 ↔ entireReducedDenominator N w = 0) ∧
    Countable (ZeroMultiplicityIndex (entireReducedDenominator N)) := by
  have hs := entireReducedDenominator_reciprocal_zeros_summable hN
  have h0 : entireReducedDenominator N 0 ≠ 0 := by rw [entireReducedDenominator_zero]; exact one_ne_zero
  refine ⟨fullCanonicalProduct_entire hs, fullCanonicalProduct_zero _, ?_, zeroMultiplicityIndex_countable hs h0⟩
  exact fullCanonicalProduct_zero_iff (fun z => (analyticAt_entireReducedDenominator (by omega) z).differentiableAt) hs h0

end
end Komorebi.PaperIV
