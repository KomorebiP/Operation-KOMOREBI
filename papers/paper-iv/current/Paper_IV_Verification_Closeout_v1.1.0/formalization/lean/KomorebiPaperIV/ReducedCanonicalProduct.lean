/-
Copyright (c) 2026 Komorebi P. All rights reserved.
Authors: Komorebi P.
-/
import KomorebiPaperIV.ZeroSequenceAsymptotics
import Mathlib.Analysis.Normed.Module.MultipliableUniformlyOn
import Mathlib.Analysis.Complex.LocallyUniformLimit

/-! The genus-zero product over the constructed positive tail is entire.
This file does not assert its equality with the reduced denominator: the finite
exceptional factor and the zero-free quotient still need to be identified. -/
namespace Komorebi.PaperIV
noncomputable section
open Filter Set

def reducedTailProduct (N M : ℕ) (w : ℂ) : ℂ :=
  ∏' m : ℕ, (1 - w / (reducedPositiveZero N (m + M) : ℂ))

theorem reducedPositiveZero_pos {N : ℕ} (hN : 2 ≤ N) (m : ℕ) :
    0 < reducedPositiveZero N m := pow_pos (signedPositiveZero_pos hN m) N

theorem reducedTail_reciprocal_summable {N : ℕ} (hN : 3 ≤ N) (M : ℕ) :
    Summable (fun m => 1 / reducedPositiveZero N (m + M)) :=
  (summable_nat_add_iff M).mpr (reducedPositiveZero_reciprocal_summable hN)

theorem reducedTail_factors_norm_summable {N : ℕ} (hN : 3 ≤ N) (M : ℕ) (w : ℂ) :
    Summable (fun m => ‖w / (reducedPositiveZero N (m + M) : ℂ)‖) := by
  simpa only [norm_div, Complex.norm_real, Real.norm_eq_abs,
    abs_of_pos (reducedPositiveZero_pos (by omega : 2 ≤ N) _), mul_one_div] using
    (reducedTail_reciprocal_summable hN M).mul_left ‖w‖

theorem reducedTailProduct_multipliable {N : ℕ} (hN : 3 ≤ N) (M : ℕ) (w : ℂ) :
    Multipliable (fun m => 1 - w / (reducedPositiveZero N (m + M) : ℂ)) :=
  multipliable_one_sub_of_summable (reducedTail_factors_norm_summable hN M w)

theorem reducedTailProduct_uniform_on_compact {N : ℕ} (hN : 3 ≤ N) (M : ℕ)
    {K : Set ℂ} (hK : IsCompact K) :
    HasProdUniformlyOn (fun m w => 1 - w / (reducedPositiveZero N (m + M) : ℂ))
      (reducedTailProduct N M) K := by
  obtain ⟨B, hB⟩ := hK.isBounded.exists_norm_le
  have hs := (reducedTail_reciprocal_summable hN M).mul_left B
  have hh := hs.hasProdUniformlyOn_nat_one_add hK
    (f := fun (m : ℕ) (w : ℂ) => -w / (reducedPositiveZero N (m + M) : ℂ))
    (Filter.Eventually.of_forall (fun m w hw => ?_)) (fun _ => by fun_prop)
  · simpa only [reducedTailProduct, neg_div, ← sub_eq_add_neg] using! hh
  · rw [norm_div, norm_neg, Complex.norm_real, Real.norm_eq_abs,
      abs_of_pos (reducedPositiveZero_pos (by omega : 2 ≤ N) _), mul_one_div]
    exact div_le_div_of_nonneg_right (hB w hw) (le_of_lt (reducedPositiveZero_pos (by omega) _))

theorem reducedTailProduct_locally_uniform {N : ℕ} (hN : 3 ≤ N) (M : ℕ) :
    HasProdLocallyUniformlyOn (fun m w => 1 - w / (reducedPositiveZero N (m + M) : ℂ))
      (reducedTailProduct N M) univ := by
  apply hasProdLocallyUniformlyOn_of_forall_compact isOpen_univ
  intro K _ hK
  exact reducedTailProduct_uniform_on_compact hN M hK

theorem analyticAt_reducedTailProduct {N : ℕ} (hN : 3 ≤ N) (M : ℕ) (w : ℂ) :
    AnalyticAt ℂ (reducedTailProduct N M) w := by
  have he : ∀ s : Finset ℕ, DifferentiableOn ℂ
      (fun w : ℂ => ∏ m ∈ s, (1 - w / (reducedPositiveZero N (m + M) : ℂ))) univ := by
    intro s
    exact DifferentiableOn.fun_finsetProd (fun _ _ => by fun_prop)
  have hd := (reducedTailProduct_locally_uniform hN M).differentiableOn
    (Filter.Eventually.of_forall (fun s => by simpa only [Finset.prod_fn] using he s)) isOpen_univ
  exact (differentiableOn_univ.mp hd).analyticAt w

@[simp] theorem reducedTailProduct_zero (N M : ℕ) : reducedTailProduct N M 0 = 1 := by
  simp [reducedTailProduct]

theorem reducedTailProduct_ne_zero {N : ℕ} (hN : 3 ≤ N) (M : ℕ) {w : ℂ}
    (hw : ∀ m : ℕ, w ≠ (reducedPositiveZero N (m + M) : ℂ)) :
    reducedTailProduct N M w ≠ 0 := by
  have hs : Summable (fun m => ‖-w / (reducedPositiveZero N (m + M) : ℂ)‖) := by
    simpa only [neg_div, norm_neg] using reducedTail_factors_norm_summable hN M w
  have hh := tprod_one_add_ne_zero_of_summable (f := fun m => -w / (reducedPositiveZero N (m + M) : ℂ))
    (fun m => ?_) hs
  · simpa only [reducedTailProduct, neg_div, ← sub_eq_add_neg] using! hh
  · rw [neg_div, ← sub_eq_add_neg, sub_ne_zero]
    intro h
    apply hw m
    exact (div_eq_one_iff_eq (Complex.ofReal_ne_zero.mpr (ne_of_gt (reducedPositiveZero_pos (by omega) _)))).mp h.symm

/-- The convergent product has exactly the chosen sequence entries as zeros. -/
theorem reducedTailProduct_zero_iff {N : ℕ} (hN : 3 ≤ N) (M : ℕ) (w : ℂ) :
    reducedTailProduct N M w = 0 ↔ ∃ m : ℕ, w = (reducedPositiveZero N (m + M) : ℂ) := by
  constructor
  · intro hz
    by_contra h
    push Not at h
    exact reducedTailProduct_ne_zero hN M h hz
  · rintro ⟨m, rfl⟩
    apply tprod_of_exists_eq_zero
    refine ⟨m, ?_⟩
    rw [div_self (Complex.ofReal_ne_zero.mpr (ne_of_gt (reducedPositiveZero_pos (by omega) _))), sub_self]

end
end Komorebi.PaperIV
