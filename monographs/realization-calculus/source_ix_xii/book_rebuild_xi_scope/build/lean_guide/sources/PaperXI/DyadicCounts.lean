import PaperXI.DyadicGauss
import Mathlib.Algebra.BigOperators.Group.Finset.Piecewise
import Mathlib.Tactic

/-! Exact counts for binary quadratic coefficient spaces. -/
set_option autoImplicit false
noncomputable section
open scoped BigOperators Classical
namespace PaperXI.DyadicCounts

variable {α : Type*} [Fintype α]

theorem signed_sum_eq_card_difference (p : α → Prop) [DecidablePred p] :
    (∑ x, if p x then (1 : ℤ) else -1) =
      ((Finset.univ.filter p).card : ℤ) - (Finset.univ.filter fun x => ¬ p x).card := by
  rw [Finset.sum_ite]
  simp [sub_eq_add_neg]

theorem card_partition (p : α → Prop) [DecidablePred p] :
    (Finset.univ.filter p).card + (Finset.univ.filter fun x => ¬ p x).card =
      Fintype.card α := by
  simpa using (Finset.card_filter_add_card_filter_not (s := Finset.univ) p)

open PaperXI.Dyadic
variable {ι : Type*} [Fintype ι]

def evenCount (ι : Type*) [Fintype ι] : ℕ :=
  (Finset.univ.filter fun a : ι → F2 × F2 => arf a = 0).card

def oddCount (ι : Type*) [Fintype ι] : ℕ :=
  (Finset.univ.filter fun a : ι → F2 × F2 => arf a = 1).card

theorem f2_ne_zero_iff_eq_one (t : F2) : t ≠ 0 ↔ t = 1 := by
  constructor
  · intro h
    apply Fin.ext
    change Fin.val t = 1
    have hn : Fin.val t ≠ 0 := by
      intro hz
      apply h
      apply Fin.ext
      exact hz
    exact Nat.le_antisymm (Nat.le_of_lt_succ (Fin.isLt t)) (Nat.pos_of_ne_zero hn)
  · intro h hz
    exact zero_ne_one (hz.symm.trans h)

theorem parameter_card : Fintype.card (ι → F2 × F2) = 2 ^ (2 * Fintype.card ι) := by
  simp [Fintype.card_prod, F2, ZMod.card, pow_mul]

theorem even_add_odd : evenCount ι + oddCount ι = 2 ^ (2 * Fintype.card ι) := by
  have h := card_partition (fun a : ι → F2 × F2 => arf a = 0)
  simpa [evenCount, oddCount, f2_ne_zero_iff_eq_one, F2, pow_mul] using h

theorem even_sub_odd : (evenCount ι : ℤ) - oddCount ι = 2 ^ Fintype.card ι := by
  have h := gauss_sum (fun _ : ι => (0, 0))
  have he : (∑ x : ι → F2 × F2, sign (arf x)) = (2 : ℤ) ^ Fintype.card ι := by
    simpa [quadratic, plane, arf] using h
  simp only [sign] at he
  rw [signed_sum_eq_card_difference] at he
  simpa [f2_ne_zero_iff_eq_one, evenCount, oddCount] using he

/-- Unlike the factored formula, this also applies in dimension zero. -/
theorem twice_even : 2 * (evenCount ι : ℤ) =
    2 ^ (2 * Fintype.card ι) + 2 ^ Fintype.card ι := by
  have htot : (evenCount ι : ℤ) + oddCount ι = 2 ^ (2 * Fintype.card ι) := by
    exact_mod_cast (even_add_odd (ι := ι))
  have hdiff := even_sub_odd (ι := ι)
  omega

/-- Unlike the factored formula, this also applies in dimension zero. -/
theorem twice_odd : 2 * (oddCount ι : ℤ) =
    2 ^ (2 * Fintype.card ι) - 2 ^ Fintype.card ι := by
  have htot : (evenCount ι : ℤ) + oddCount ι = 2 ^ (2 * Fintype.card ι) := by
    exact_mod_cast (even_add_odd (ι := ι))
  have hdiff := even_sub_odd (ι := ι)
  omega

theorem even_factored (hr : 0 < Fintype.card ι) :
    (evenCount ι : ℤ) = 2 ^ (Fintype.card ι - 1) * (2 ^ Fintype.card ι + 1) := by
  have h := twice_even (ι := ι)
  have hsq : (2 : ℤ) ^ (2 * Fintype.card ι) = ((2 : ℤ) ^ Fintype.card ι) ^ 2 := by
    rw [Nat.mul_comm 2, pow_mul]
  have hp : (2 : ℤ) ^ Fintype.card ι = 2 * 2 ^ (Fintype.card ι - 1) := by
    conv_lhs => rw [show Fintype.card ι = (Fintype.card ι - 1) + 1 by omega]
    rw [pow_succ]
    ring
  rw [hsq] at h
  nlinarith

theorem odd_factored (hr : 0 < Fintype.card ι) :
    (oddCount ι : ℤ) = 2 ^ (Fintype.card ι - 1) * (2 ^ Fintype.card ι - 1) := by
  have h := twice_odd (ι := ι)
  have hsq : (2 : ℤ) ^ (2 * Fintype.card ι) = ((2 : ℤ) ^ Fintype.card ι) ^ 2 := by
    rw [Nat.mul_comm 2, pow_mul]
  have hp : (2 : ℤ) ^ Fintype.card ι = 2 * 2 ^ (Fintype.card ι - 1) := by
    conv_lhs => rw [show Fintype.card ι = (Fintype.card ι - 1) + 1 by omega]
    rw [pow_succ]
    ring
  rw [hsq] at h
  nlinarith

theorem counts_rank_zero (hr : Fintype.card ι = 0) :
    evenCount ι = 1 ∧ oddCount ι = 0 := by
  have he := twice_even (ι := ι)
  have ho := twice_odd (ι := ι)
  simp only [hr, mul_zero, pow_zero] at he ho
  omega

/-- The manuscript's factored formula at every rank, with an integer exponent. -/
theorem even_factored_rational :
    (evenCount ι : ℚ) = (2 : ℚ) ^ ((Fintype.card ι : ℤ) - 1) *
      ((2 : ℚ) ^ Fintype.card ι + 1) := by
  by_cases hr : Fintype.card ι = 0
  · rw [(counts_rank_zero hr).1, hr]
    norm_num
  · have he := even_factored (Nat.pos_of_ne_zero hr)
    have hcast : (Fintype.card ι : ℤ) - 1 = ((Fintype.card ι - 1 : ℕ) : ℤ) := by
      omega
    rw [hcast, zpow_natCast]
    exact_mod_cast he

/-- The manuscript's factored formula at every rank, with an integer exponent. -/
theorem odd_factored_rational :
    (oddCount ι : ℚ) = (2 : ℚ) ^ ((Fintype.card ι : ℤ) - 1) *
      ((2 : ℚ) ^ Fintype.card ι - 1) := by
  by_cases hr : Fintype.card ι = 0
  · rw [(counts_rank_zero hr).2, hr]
    norm_num
  · have he := odd_factored (Nat.pos_of_ne_zero hr)
    have hcast : (Fintype.card ι : ℤ) - 1 = ((Fintype.card ι - 1 : ℕ) : ℤ) := by
      omega
    rw [hcast, zpow_natCast]
    exact_mod_cast he

end PaperXI.DyadicCounts
