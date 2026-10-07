/-
Copyright (c) 2026 Komorebi P. All rights reserved.
Authors: Komorebi P.
-/
import KomorebiPaperIV.JensenZeroGrowth

namespace Komorebi.PaperIV
noncomputable section
open Set Real
open scoped Classical
set_option maxHeartbeats 800000

/-- Weighted counting bounds imply convergence above the counting exponent. -/
theorem weighted_growth_summable_large {ι : Type*} {x w : ι → ℝ} {C p q : ℝ}
    (hx : ∀ i, 1 ≤ x i) (hw : ∀ i, 0 ≤ w i) (hC : 0 ≤ C)
    (hp : 0 ≤ p) (hpq : p < q)
    (hg : ∀ R : ℝ, 1 ≤ R → ∀ S : Finset ι, (∀ i ∈ S, x i ≤ R) →
      ∑ i ∈ S, w i ≤ C * R ^ p) : Summable (fun i => w i / (x i) ^ q) := by
  let shell : ι → ℕ := fun i => ⌊log (x i)⌋₊
  let g : ℕ → ℝ := fun n => (C * exp p) * exp (p - q) ^ n
  have hgs : Summable g := (summable_geometric_of_lt_one (exp_pos _).le
    (exp_lt_one_iff.mpr (sub_neg.mpr hpq))).mul_left (C * exp p)
  have hg0 : ∀ n, 0 ≤ g n := fun n => by dsimp [g]; positivity
  apply summable_of_sum_le (fun i => div_nonneg (hw i) (rpow_nonneg (by linarith [hx i]) _))
    (c := ∑' n, g n)
  intro S
  have hfiber (n : ℕ) : ∑ i ∈ S.filter (fun i => shell i = n), w i / (x i) ^ q ≤ g n := by
    let T := S.filter (fun i => shell i = n)
    have hlog (i : ι) (hi : i ∈ T) : (n : ℝ) ≤ log (x i) ∧ log (x i) < (n : ℝ) + 1 := by
      have he : shell i = n := (Finset.mem_filter.mp hi).2
      constructor
      · simpa only [shell, he] using Nat.floor_le (log_nonneg (hx i))
      · simpa only [shell, he] using Nat.lt_floor_add_one (log (x i))
    have hupper : ∀ i ∈ T, x i ≤ exp ((n : ℝ) + 1) := by
      intro i hi
      rw [← exp_log (by linarith [hx i] : 0 < x i)]
      exact (exp_lt_exp.mpr (hlog i hi).2).le
    have hsum := hg (exp ((n : ℝ) + 1)) (one_le_exp (by positivity)) T hupper
    calc
      _ ≤ ∑ i ∈ T, w i * exp (-(q * (n : ℝ))) := by
        apply Finset.sum_le_sum
        intro i hi
        rw [rpow_def_of_pos (by linarith [hx i] : 0 < x i), div_eq_mul_inv, ← exp_neg]
        apply mul_le_mul_of_nonneg_left _ (hw i)
        apply exp_le_exp.mpr
        nlinarith [(hlog i hi).1]
      _ = (∑ i ∈ T, w i) * exp (-(q * (n : ℝ))) := (Finset.sum_mul ..).symm
      _ ≤ (C * exp ((n : ℝ) + 1) ^ p) * exp (-(q * (n : ℝ))) :=
        mul_le_mul_of_nonneg_right hsum (exp_pos _).le
      _ = g n := by
        dsimp [g]
        rw [← exp_mul, mul_assoc, ← exp_add, ← exp_nat_mul, mul_assoc, ← exp_add]
        congr 2
        ring
  calc
    _ = ∑ n ∈ S.image shell, ∑ i ∈ S.filter (fun i => shell i = n), w i / (x i) ^ q :=
      (Finset.sum_fiberwise_of_maps_to (fun i hi => Finset.mem_image_of_mem shell hi) _).symm
    _ ≤ ∑ n ∈ S.image shell, g n := Finset.sum_le_sum (fun n _ => hfiber n)
    _ ≤ ∑' n, g n := hgs.sum_le_tsum _ (fun n _ => hg0 n)

theorem weighted_growth_summable {ι : Type*} {x w : ι → ℝ} {C p q : ℝ}
    (hw : ∀ i, 0 ≤ w i) (hC : 0 ≤ C) (hp : 0 ≤ p) (hpq : p < q)
    (hsmall : {i | x i < 1}.Finite)
    (hg : ∀ R : ℝ, 1 ≤ R → ∀ S : Finset ι, (∀ i ∈ S, x i ≤ R) →
      ∑ i ∈ S, w i ≤ C * R ^ p) : Summable (fun i => w i / (x i) ^ q) := by
  apply (summable_subtype_and_compl (s := {i | x i < 1})).mp
  refine ⟨hsmall.summable (fun i => w i / (x i) ^ q), ?_⟩
  apply weighted_growth_summable_large (ι := {i // ¬ x i < 1})
    (x := fun i => x i.val) (w := fun i => w i.val) (C := C) (p := p)
    (fun i => le_of_not_gt i.property) (fun i => hw i) hC hp hpq
  intro R hR S hS
  let e : {i // ¬ x i < 1} ↪ ι := ⟨Subtype.val, Subtype.val_injective⟩
  have h := hg R hR (S.map e) (by
    intro i hi
    obtain ⟨v, hv, rfl⟩ := Finset.mem_map.mp hi
    exact hS v hv)
  simpa only [Finset.sum_map, e, Function.Embedding.coeFn_mk] using h

theorem entire_growth_zeroPowerSummable {f : ℂ → ℂ} (hf : Differentiable ℂ f)
    (h0 : f 0 = 1) {C p q : ℝ} (hC : 0 ≤ C) (hp : 0 ≤ p) (hpq : p < q)
    (hg : ∀ R : ℝ, 1 ≤ R → ∀ z : ℂ, ‖z‖ ≤ R → ‖f z‖ ≤ exp (C * R ^ p)) :
    ZeroPowerSummable f q := by
  have hne : f 0 ≠ 0 := by simp [h0]
  apply weighted_growth_summable (C := C * 2 ^ p / log 2) (p := p)
  · intro z; positivity
  · exact div_nonneg (mul_nonneg hC (rpow_nonneg (by norm_num) _)) (log_pos (by norm_num)).le
  · exact hp
  · exact hpq
  · exact (entire_zero_bounded_finite hf hne 1).subset (fun z hz => show ‖(z : ℂ)‖ ≤ 1 from le_of_lt hz)
  · intro R hR S hS
    exact entire_zero_subtype_weight_growth hf h0 hC hg hR S hS

end
end Komorebi.PaperIV
