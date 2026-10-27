/-
Copyright (c) 2026 Komorebi P. All rights reserved.
Authors: Komorebi P.
-/
import KomorebiPaperIV.ZeroSequenceCounting

namespace Komorebi.PaperIV
noncomputable section
open Set Metric

/-- Sum of natural weights over a finite set. The infinite-set fallback is never
used for the zero disks considered below. -/
def finiteWeight {α : Type*} (w : α → ℕ) (s : Set α) : ℕ := by
  classical
  exact if hs : s.Finite then ∑ x ∈ hs.toFinset, w x else 0

theorem finiteWeight_of_finite {α : Type*} (w : α → ℕ) {s : Set α} (hs : s.Finite) :
    finiteWeight w s = ∑ x ∈ hs.toFinset, w x := by
  classical
  unfold finiteWeight
  rw [dite_eq_left hs]

theorem finiteWeight_mono {α : Type*} (w : α → ℕ) {s t : Set α}
    (hs : s.Finite) (ht : t.Finite) (hst : s ⊆ t) : finiteWeight w s ≤ finiteWeight w t := by
  classical
  rw [finiteWeight_of_finite w hs, finiteWeight_of_finite w ht]
  exact Finset.sum_le_sum_of_subset_of_nonneg (hs.toFinset_mono hst) (fun _ _ _ => Nat.zero_le _)

theorem finiteWeight_union_le {α : Type*} (w : α → ℕ) {s t : Set α}
    (hs : s.Finite) (ht : t.Finite) :
    finiteWeight w (s ∪ t) ≤ finiteWeight w s + finiteWeight w t := by
  classical
  rw [finiteWeight_of_finite w (hs.union ht), finiteWeight_of_finite w hs,
    finiteWeight_of_finite w ht, Set.Finite.toFinset_union hs ht (hs.union ht)]
  have h := Finset.sum_union_inter (s₁ := hs.toFinset) (s₂ := ht.toFinset) (f := w)
  omega

theorem finiteWeight_eq_ncard {α : Type*} {w : α → ℕ} {s : Set α}
    (hs : s.Finite) (hw : ∀ x ∈ s, w x = 1) : finiteWeight w s = s.ncard := by
  rw [finiteWeight_of_finite w hs, ncard_eq_toFinset_card s hs]
  calc
    _ = ∑ x ∈ hs.toFinset, (1 : ℕ) := Finset.sum_congr rfl (fun x hx => hw x (hs.mem_toFinset.mp hx))
    _ = _ := by simp


/-- A finite exceptional set contributes at most its total multiplicity. -/
theorem finiteWeight_between_tail_and_exceptions {α : Type*} (w : α → ℕ)
    {S T E : Set α} (hS : S.Finite) (hT : T.Finite) (hE : E.Finite)
    (hTS : T ⊆ S) (hSTE : S ⊆ T ∪ E) (hw : ∀ x ∈ T, w x = 1) :
    T.ncard ≤ finiteWeight w S ∧ finiteWeight w S ≤ T.ncard + finiteWeight w E := by
  have ht := finiteWeight_eq_ncard hT hw
  constructor
  · rw [← ht]; exact finiteWeight_mono w hT hS hTS
  · calc
      _ ≤ finiteWeight w (T ∪ E) := finiteWeight_mono w hS (hT.union hE) hSTE
      _ ≤ finiteWeight w T + finiteWeight w E := finiteWeight_union_le w hT hE
      _ = _ := by rw [ht]

/-- The actual zeros in a closed disk. -/
def zeroDisk (f : ℂ → ℂ) (R : ℝ) : Set ℂ := {z | ‖z‖ ≤ R ∧ f z = 0}

/-- The manuscript's disk count, including analytic multiplicity. -/
def analyticZeroCount (f : ℂ → ℂ) (R : ℝ) : ℕ :=
  finiteWeight (analyticOrderNatAt f) (zeroDisk f R)

/-- Nonzero entire functions have finite analytic order at every point. -/
theorem entire_analyticOrderAt_ne_top {f : ℂ → ℂ} (hf : ∀ z, AnalyticAt ℂ f z)
    {a : ℂ} (ha : f a ≠ 0) (z : ℂ) : analyticOrderAt f z ≠ ⊤ := by
  intro h
  have hall : AnalyticOnNhd ℂ f univ := fun w _ => hf w
  have he := hall.eq_of_eventuallyEq (show AnalyticOnNhd ℂ (0 : ℂ → ℂ) univ from
    fun _ _ => analyticAt_const) (analyticOrderAt_eq_top.mp h)
  exact ha (congrFun he a)

theorem canonicalSignedDenominator_order_ne_top {N : ℕ} (hN : 0 < N) (z : ℂ) :
    analyticOrderAt (canonicalSignedDenominator N) z ≠ ⊤ :=
  entire_analyticOrderAt_ne_top (f := canonicalSignedDenominator N) (a := 0) (fun w => analyticAt_entireSigned N 0 _ _ w)
    (by rw [canonicalSignedDenominator_zero hN]; exact one_ne_zero) z

theorem entireReducedDenominator_order_ne_top {N : ℕ} (hN : 0 < N) (z : ℂ) :
    analyticOrderAt (entireReducedDenominator N) z ≠ ⊤ :=
  entire_analyticOrderAt_ne_top (a := 0) (analyticAt_entireReducedDenominator hN)
    (by rw [entireReducedDenominator_zero]; exact one_ne_zero) z

theorem canonicalSignedDenominator_zeroDisk_finite {N : ℕ} (hN : 0 < N) (R : ℝ) :
    (zeroDisk (canonicalSignedDenominator N) R).Finite := by
  simpa only [zeroDisk, mem_closedBall, dist_zero_right] using
    canonicalSignedDenominator_finite_zeros_on_compact hN (isCompact_closedBall (0 : ℂ) R)

theorem entireReducedDenominator_zeroDisk_finite {N : ℕ} (hN : 0 < N) (R : ℝ) :
    (zeroDisk (entireReducedDenominator N) R).Finite := by
  simpa only [zeroDisk, mem_closedBall, dist_zero_right] using
    entireReducedDenominator_finite_zeros_on_compact hN (isCompact_closedBall (0 : ℂ) R)

end
end Komorebi.PaperIV
