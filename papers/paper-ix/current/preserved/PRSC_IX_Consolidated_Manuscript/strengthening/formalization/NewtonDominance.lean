module

public import GlobalEulerBoundary
public import Mathlib.NumberTheory.Padics.PadicVal.Basic

@[expose] public section
noncomputable section
set_option autoImplicit false

namespace KomorebiPaperIX.NewtonDominance

open Mahler GlobalEulerBoundary

lemma precision_mono {L M : ℤ} {x : ℚ} (h : L ≤ M)
    (hx : precision 2 M x) : precision 2 L x := by
  rcases hx with hx | hx
  · exact Or.inl hx
  · exact Or.inr (h.trans hx)

lemma precision_add {L : ℤ} {x y : ℚ}
    (hx : precision 2 L x) (hy : precision 2 L y) : precision 2 L (x + y) := by
  rcases hx with rfl | hx
  · simpa using hy
  rcases hy with rfl | hy
  · rw [add_zero]
    exact Or.inr hx
  by_cases h : x + y = 0
  · exact Or.inl h
  · exact Or.inr ((le_min hx hy).trans (padicValRat.min_le_padicValRat_add h))

lemma precision_sum {ι : Type*} (S : Finset ι) (g : ι → ℚ) (L : ℤ)
    (H : ∀ i ∈ S, precision 2 L (g i)) : precision 2 L (∑ i ∈ S, g i) := by
  classical
  induction S using Finset.induction_on with
  | empty => simp
  | @insert i S hi ih =>
    rw [Finset.sum_insert hi]
    exact precision_add (H i (Finset.mem_insert_self _ _))
      (ih (by intro j hj; exact H j (Finset.mem_insert_of_mem hj)))

lemma precision_mul {L M : ℤ} {x y : ℚ}
    (hx : precision 2 L x) (hy : precision 2 M y) : precision 2 (L + M) (x * y) := by
  by_cases hxn : x = 0
  · simp [hxn]
  by_cases hyn : y = 0
  · simp [hyn]
  have hxv := hx.resolve_left hxn
  have hyv := hy.resolve_left hyn
  exact Or.inr (by rw [padicValRat.mul hxn hyn]; omega)

lemma precision_mul_nat {L : ℤ} {x : ℚ} (hx : precision 2 L x) (b : ℕ) :
    precision 2 L (x * (b : ℚ)) := by
  simpa using precision_mul hx (Or.inr (zero_le_padicValRat_of_nat b) : precision 2 0 (b : ℚ))

/-- A strictly higher precision perturbation cannot cancel the leading term. -/
lemma strict_dominance (x y : ℚ) (c : ℤ) (hx : x ≠ 0)
    (hv : padicValRat 2 x = c) (hy : precision 2 (c + 1) y) :
    x + y ≠ 0 ∧ padicValRat 2 (x + y) = c := by
  rcases hy with rfl | hy
  · simpa using And.intro hx hv
  have hsum : x + y ≠ 0 := by
    intro h
    have heq : y = -x := by linarith
    rw [heq, padicValRat.neg, hv] at hy
    omega
  by_cases hyn : y = 0
  · simp [hyn, hx, hv]
  exact ⟨hsum, (padicValRat.add_eq_of_lt hsum hx hyn (by omega)).trans hv⟩

/-- Translation preserves a monotone lower envelope on the Newton coefficients. -/
lemma translated_tail (f : ℕ → ℚ) (c k n : ℕ) (hk : 2 ≤ k)
    (H : ∀ i, 2 ≤ i → precision 2 ((c + 1 + Nat.log 2 i : ℕ) : ℤ) (coefficient f i)) :
    precision 2 ((c + 1 + Nat.log 2 k : ℕ) : ℤ) (difference 1 k f n) := by
  rw [difference_from_coefficients]
  apply precision_sum
  intro j _
  apply precision_mul_nat
  apply precision_mono _ (H (k + j) (by omega))
  exact_mod_cast Nat.add_le_add_left (Nat.log_monotone (show k ≤ k + j by omega)) (c + 1)

lemma first_difference_tail (f : ℕ → ℚ) (c n : ℕ)
    (H : ∀ i, 2 ≤ i → precision 2 ((c + 1 + Nat.log 2 i : ℕ) : ℤ) (coefficient f i)) :
    precision 2 ((c : ℤ) + 1) (difference 1 1 f n - coefficient f 1) := by
  rw [difference_from_coefficients, Finset.sum_range_succ']
  simp only [Nat.add_zero, Nat.choose_zero_right, Nat.cast_one, mul_one]
  rw [add_sub_cancel_right]
  apply precision_sum
  intro j _
  apply precision_mul_nat
  exact precision_mono (by norm_num) (H (1 + (j + 1)) (by omega))

/-- The standard binomial denominator identity retains the valuation of the displacement. -/
lemma choose_precision (T k : ℕ) (hT : 0 < T) (hk : 0 < k) :
    precision 2 ((padicValNat 2 T : ℤ) - Nat.log 2 k) (T.choose k : ℚ) := by
  by_cases hzero : T.choose k = 0
  · simp [hzero]
  have hkT : k ≤ T := Nat.le_of_not_gt (by intro h; exact hzero (Nat.choose_eq_zero_of_lt h))
  have hprev : (T - 1).choose (k - 1) ≠ 0 := Nat.ne_of_gt (Nat.choose_pos (by omega))
  have hid : T * ((T - 1).choose (k - 1)) = T.choose k * k := by
    simpa only [Nat.sub_add_cancel hT, Nat.sub_add_cancel hk] using
      Nat.add_one_mul_choose_eq (T - 1) (k - 1)
  have hv := congrArg (padicValNat 2) hid
  rw [padicValNat.mul (by omega) hprev, padicValNat.mul hzero (by omega)] at hv
  have hlog := padicValNat_le_nat_log (p := 2) k
  apply Or.inr
  rw [padicValRat.of_nat]
  omega

/-- Finite Gregory–Newton expansion, with its first two terms separated. -/
lemma displacement_expansion (f : ℕ → ℚ) (n T : ℕ) (hT : 0 < T) :
    f (n + T) - f n = difference 1 1 f n * (T : ℚ) +
      ∑ k ∈ Finset.range (T - 1), difference 1 (k + 2) f n * (T.choose (k + 2) : ℚ) := by
  have hn := shift_eq_sum_fwdDiff_iter 1 f T n
  simp only [nsmul_eq_mul, Nat.mul_one] at hn
  change f (n + T) = ∑ k ∈ Finset.range (T + 1), (T.choose k : ℚ) * difference 1 k f n at hn
  have ht : T + 1 = (T - 1) + 1 + 1 := by omega
  rw [ht, Finset.sum_range_succ', Finset.sum_range_succ'] at hn
  simp only [Nat.choose_zero_right, Nat.cast_one, difference_zero, one_mul,
    Nat.zero_add, Nat.choose_one_right] at hn
  rw [hn]
  simp only [Nat.add_assoc, show 1 + 1 = 2 by rfl]
  rw [show (∑ k ∈ Finset.range (T - 1), (T.choose (k + 2) : ℚ) * difference 1 (k + 2) f n) =
      ∑ k ∈ Finset.range (T - 1), difference 1 (k + 2) f n * (T.choose (k + 2) : ℚ) by
      apply Finset.sum_congr rfl; intro k _; ring]
  ring

/-- A strict Newton coefficient envelope gives the exact valuation of every displacement. -/
theorem exact_displacement (f : ℕ → ℚ) (c : ℕ)
    (h1 : coefficient f 1 ≠ 0) (hv1 : padicValRat 2 (coefficient f 1) = (c : ℤ))
    (H : ∀ k, 2 ≤ k → precision 2 ((c + 1 + Nat.log 2 k : ℕ) : ℤ) (coefficient f k))
    (n T : ℕ) (hT : 0 < T) :
    f (n + T) - f n ≠ 0 ∧
      padicValRat 2 (f (n + T) - f n) = (padicValNat 2 T : ℤ) + (c : ℤ) := by
  have hd := strict_dominance (coefficient f 1)
    (difference 1 1 f n - coefficient f 1) (c : ℤ) h1 hv1 (first_difference_tail f c n H)
  rw [add_sub_cancel] at hd
  have hTq : (T : ℚ) ≠ 0 := by exact_mod_cast (Nat.ne_of_gt hT)
  have hvlead : padicValRat 2 (difference 1 1 f n * (T : ℚ)) =
      (padicValNat 2 T : ℤ) + (c : ℤ) := by
    rw [padicValRat.mul hd.1 hTq, hd.2, padicValRat.of_nat]
    omega
  rw [displacement_expansion f n T hT]
  apply strict_dominance _ _ _ (mul_ne_zero hd.1 hTq) hvlead
  apply precision_sum
  intro k _
  have hmul := precision_mul (translated_tail f c (k + 2) n (by omega) H)
    (choose_precision T (k + 2) hT (by omega))
  convert hmul using 1
  push_cast
  ring

end KomorebiPaperIX.NewtonDominance
