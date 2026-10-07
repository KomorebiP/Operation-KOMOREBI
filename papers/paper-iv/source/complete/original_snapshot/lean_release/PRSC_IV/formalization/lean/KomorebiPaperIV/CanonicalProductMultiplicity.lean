/-
Copyright (c) 2026 Komorebi P. All rights reserved.
Authors: Komorebi P.
-/
import KomorebiPaperIV.FullCanonicalProduct

namespace Komorebi.PaperIV
noncomputable section
open Set Filter

/-- A general normally convergent reciprocal product, also used after deleting
all copies of a single zero. -/
def reciprocalProduct {ι : Type*} (a : ι → ℂ) (w : ℂ) : ℂ := ∏' i, (1 - w / a i)

theorem reciprocalProduct_locally_uniform {ι : Type*} (a : ι → ℂ)
    (hs : Summable (fun i => 1 / ‖a i‖)) :
    HasProdLocallyUniformlyOn (fun i w => 1 - w / a i) (reciprocalProduct a) univ := by
  apply hasProdLocallyUniformlyOn_of_forall_compact isOpen_univ
  intro K _ hK
  obtain ⟨B, hB⟩ := hK.isBounded.exists_norm_le
  have h := (hs.mul_left B).hasProdUniformlyOn_one_add hK
    (f := fun i w => -w / a i) (Eventually.of_forall (fun i w hw => ?_)) (fun _ => by fun_prop)
  · simpa only [reciprocalProduct, neg_div, ← sub_eq_add_neg] using! h
  · rw [norm_div, norm_neg, mul_one_div]
    exact div_le_div_of_nonneg_right (hB w hw) (norm_nonneg _)

theorem reciprocalProduct_entire {ι : Type*} (a : ι → ℂ)
    (hs : Summable (fun i => 1 / ‖a i‖)) : Differentiable ℂ (reciprocalProduct a) := by
  apply differentiableOn_univ.mp
  apply (reciprocalProduct_locally_uniform a hs).differentiableOn _ isOpen_univ
  apply Eventually.of_forall
  intro S
  have h : DifferentiableOn ℂ (fun w : ℂ => ∏ i ∈ S, (1 - w / a i)) univ :=
    DifferentiableOn.fun_finsetProd (fun _ _ => by fun_prop)
  simpa only [Finset.prod_fn] using h

theorem reciprocalProduct_ne_zero {ι : Type*} (a : ι → ℂ)
    (hs : Summable (fun i => 1 / ‖a i‖)) (ha : ∀ i, a i ≠ 0)
    {w : ℂ} (hw : ∀ i, w ≠ a i) : reciprocalProduct a w ≠ 0 := by
  have h := tprod_one_add_ne_zero_of_summable (f := fun i => -w / a i) (fun i => ?_)
    (by simpa only [norm_div, norm_neg, mul_one_div] using hs.mul_left ‖w‖)
  · simpa only [reciprocalProduct, neg_div, ← sub_eq_add_neg] using! h
  · rw [neg_div, ← sub_eq_add_neg, sub_ne_zero]
    intro he
    exact hw i ((div_eq_one_iff_eq (ha i)).mp he.symm)

def zeroIndexFiberEquiv (f : ℂ → ℂ) (z : {z : ℂ // f z = 0}) :
    Fin (analyticOrderNatAt f z) ≃ {i : ZeroMultiplicityIndex f // i.1 = z} where
  toFun k := ⟨⟨z, k⟩, rfl⟩
  invFun i := by
    rcases i with ⟨⟨w, k⟩, h⟩
    cases h
    exact k
  left_inv _ := rfl
  right_inv i := by
    rcases i with ⟨⟨w, k⟩, h⟩
    cases h
    rfl

def otherZeroProduct (f : ℂ → ℂ) (z : {z : ℂ // f z = 0}) (w : ℂ) : ℂ :=
  reciprocalProduct (fun i : {i : ZeroMultiplicityIndex f // i.1 ≠ z} => indexedZero i.val) w

theorem otherZeroProduct_entire {f : ℂ → ℂ} (hs : ZeroPowerSummable f 1)
    (z : {z : ℂ // f z = 0}) : Differentiable ℂ (otherZeroProduct f z) :=
  reciprocalProduct_entire _ ((zeroMultiplicity_reciprocal_summable hs).subtype _)

theorem otherZeroProduct_ne_zero_at_zero {f : ℂ → ℂ} (hs : ZeroPowerSummable f 1)
    (hf0 : f 0 ≠ 0) (z : {z : ℂ // f z = 0}) : otherZeroProduct f z z ≠ 0 := by
  apply reciprocalProduct_ne_zero _ ((zeroMultiplicity_reciprocal_summable hs).subtype _)
    (fun i => indexedZero_ne_zero hf0 i.val)
  intro i he
  apply i.property
  exact Subtype.ext he.symm

/-- The factor at one distinct zero has exactly the prescribed multiplicity. -/
theorem fullCanonicalProduct_factor_at_zero {f : ℂ → ℂ} (hs : ZeroPowerSummable f 1)
    (z : {z : ℂ // f z = 0}) (w : ℂ) :
    fullCanonicalProduct f w = (1 - w / (z : ℂ)) ^ analyticOrderNatAt f z * otherZeroProduct f z w := by
  have hm := fullCanonicalProduct_factors_summable hs w
  let S : Set (ZeroMultiplicityIndex f) := {i | i.1 = z}
  have he := Multipliable.tprod_mul_tprod_compl
    (f := fun i : ZeroMultiplicityIndex f => 1 - w / indexedZero i) (s := S)
    (multipliable_one_sub_of_summable (hm.subtype S))
    (multipliable_one_sub_of_summable (hm.subtype (Sᶜ)))
  have hfiber : (∏' _k : Fin (analyticOrderNatAt f z), (1 - w / (z : ℂ))) =
      ∏' i : S, (1 - w / indexedZero i.val) :=
    (zeroIndexFiberEquiv f z).tprod_eq (fun i => 1 - w / indexedZero i.val)
  have hf : (∏' i : S, (1 - w / indexedZero i.val)) =
      (1 - w / (z : ℂ)) ^ analyticOrderNatAt f z := by
    simpa only [tprod_fintype, Finset.prod_const,
      Finset.card_univ, Fintype.card_fin] using hfiber.symm
  rw [hf] at he
  exact he.symm

theorem linear_zero_factor_order {z : ℂ} (hz : z ≠ 0) :
    analyticOrderAt (fun w : ℂ => 1 - w / z) z = 1 := by
  apply (show AnalyticAt ℂ (fun w : ℂ => 1 - w / z) z by fun_prop).analyticOrderAt_eq_one_of_zero_deriv_ne_zero
  · rw [div_self hz, sub_self]
  · have hd := ((hasDerivAt_id z).div_const z).const_sub 1
    erw [hd.deriv]
    exact neg_ne_zero.mpr (one_div_ne_zero hz)

theorem fullCanonicalProduct_order_at_zero {f : ℂ → ℂ} (hs : ZeroPowerSummable f 1)
    (hf0 : f 0 ≠ 0) (z : {z : ℂ // f z = 0}) :
    analyticOrderAt (fullCanonicalProduct f) z = (analyticOrderNatAt f z : ℕ∞) := by
  have hz : (z : ℂ) ≠ 0 := by intro h; apply hf0; simpa only [h] using z.property
  have he : fullCanonicalProduct f =
      (fun w : ℂ => (1 - w / (z : ℂ)) ^ analyticOrderNatAt f z) * otherZeroProduct f z :=
    funext (fullCanonicalProduct_factor_at_zero hs z)
  rw [he, analyticOrderAt_mul (by fun_prop) ((otherZeroProduct_entire hs z).analyticAt z)]
  have ho := ((otherZeroProduct_entire hs z).analyticAt z).analyticOrderAt_eq_zero.mpr
    (otherZeroProduct_ne_zero_at_zero hs hf0 z)
  rw [ho, add_zero]
  erw [analyticOrderAt_pow (f := fun w : ℂ => 1 - w / (z : ℂ)) (by fun_prop)]
  rw [linear_zero_factor_order hz]
  simp only [nsmul_one]

theorem fullCanonicalProduct_same_orders {f : ℂ → ℂ} (hf : Differentiable ℂ f)
    (hs : ZeroPowerSummable f 1) (hf0 : f 0 ≠ 0) (z : ℂ) :
    analyticOrderAt (fullCanonicalProduct f) z = analyticOrderAt f z := by
  by_cases hz : f z = 0
  · have h := fullCanonicalProduct_order_at_zero hs hf0 ⟨z, hz⟩
    simpa only [Nat.cast_analyticOrderNatAt (entire_analyticOrderAt_ne_top (fun w => hf.analyticAt w) hf0 z)] using h
  · rw [((fullCanonicalProduct_entire hs).analyticAt z).analyticOrderAt_eq_zero.mpr
      (fun h => hz ((fullCanonicalProduct_zero_iff hf hs hf0 z).mp h)),
      (hf.analyticAt z).analyticOrderAt_eq_zero.mpr hz]

theorem entireReducedDenominator_full_product_same_orders {N : ℕ} (hN : 2 ≤ N) (z : ℂ) :
    analyticOrderAt (fullCanonicalProduct (entireReducedDenominator N)) z =
      analyticOrderAt (entireReducedDenominator N) z :=
  fullCanonicalProduct_same_orders
    (fun z => (analyticAt_entireReducedDenominator (by omega) z).differentiableAt)
    (entireReducedDenominator_reciprocal_zeros_summable hN)
    (by rw [entireReducedDenominator_zero]; exact one_ne_zero) z

end
end Komorebi.PaperIV
