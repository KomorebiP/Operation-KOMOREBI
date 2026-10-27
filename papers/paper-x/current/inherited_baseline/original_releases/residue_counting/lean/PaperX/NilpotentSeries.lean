import Mathlib.RingTheory.PowerSeries.Log
import Mathlib.RingTheory.Nilpotent.Exp

set_option autoImplicit false

namespace PaperX.NilpotentSeries

open scoped BigOperators

variable {A : Type*} [CommRing A]

theorem hasSubst_C {a : A} (ha : IsNilpotent a) :
    PowerSeries.HasSubst (PowerSeries.C a) := by
  change IsNilpotent (PowerSeries.constantCoeff (PowerSeries.C a))
  simpa using ha

/-- Evaluation of a formal series at a nilpotent element, using algebraic substitution. -/
noncomputable def eval (a : A) (f : PowerSeries A) : A :=
  PowerSeries.constantCoeff (f.subst (PowerSeries.C a))

theorem eval_eq_finsum {a : A} (ha : IsNilpotent a) (f : PowerSeries A) :
    eval a f = ∑ᶠ n, PowerSeries.coeff n f * a ^ n := by
  unfold eval
  rw [PowerSeries.constantCoeff_eq, PowerSeries.constantCoeff_subst (hasSubst_C ha)]
  simp only [map_pow, ← PowerSeries.constantCoeff_eq, PowerSeries.constantCoeff_C, smul_eq_mul]

theorem eval_eq_sum {a : A} {k : ℕ} (hk : a ^ k = 0) (f : PowerSeries A) :
    eval a f = ∑ n ∈ Finset.range k, PowerSeries.coeff n f * a ^ n := by
  rw [eval_eq_finsum ⟨k, hk⟩]
  apply finsum_eq_sum_of_support_subset
  intro n hn
  by_contra hnk
  have hkn : k ≤ n := Nat.le_of_not_gt (by simpa using hnk)
  exact hn (by simp [pow_eq_zero_of_le hkn hk])

theorem subst_C_eq_C_eval {a : A} (ha : IsNilpotent a) (f : PowerSeries A) :
    f.subst (PowerSeries.C a) = PowerSeries.C (eval a f) := by
  apply PowerSeries.ext
  intro n
  by_cases hn : n = 0
  · subst n
    simp [eval]
  · rw [PowerSeries.coeff_subst' (hasSubst_C ha)]
    simp [← map_pow, PowerSeries.coeff_C, hn]

variable [Algebra ℚ A]

theorem eval_exp {a : A} (ha : IsNilpotent a) :
    eval a (PowerSeries.exp A) = IsNilpotent.exp a := by
  obtain ⟨k, hk⟩ := ha
  rw [eval_eq_sum hk, IsNilpotent.exp_eq_sum hk]
  apply Finset.sum_congr rfl
  intro n _
  simp [PowerSeries.coeff_exp, Algebra.smul_def]

end PaperX.NilpotentSeries
