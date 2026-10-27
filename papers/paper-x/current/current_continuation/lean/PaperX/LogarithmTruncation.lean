import PaperX.LogarithmicRecovery

set_option autoImplicit false

/-!
# Exponential and logarithm retain a supplied nilpotency bound

The same annihilating exponent works before and after the finite exponential
or logarithm. In particular, logarithmic recovery can use the supplied bound
without calculating a new nilpotency class.
-/

namespace PaperX.LogarithmTruncation

open Finset PaperX.FiniteLogarithm

variable {A : Type*} [Ring A] [Algebra ℚ A]

/-- A polynomial without a constant term retains an annihilating exponent. -/
theorem sum_smul_pow_succ_pow_eq_zero {a : A} {d : ℕ} (ha : a ^ d = 0)
    (s : Finset ℕ) (c : ℕ → ℚ) :
    (∑ j ∈ s, c j • a ^ (j + 1)) ^ d = 0 := by
  let b := ∑ j ∈ s, c j • a ^ j
  have hab : Commute a b := by
    exact Commute.sum_right _ _ _ fun j _ => ((Commute.refl a).pow_right j).smul_right _
  have hfactor : (∑ j ∈ s, c j • a ^ (j + 1)) = a * b := by
    simp only [b, mul_sum, mul_smul_comm, ← pow_succ']
  rw [hfactor, hab.mul_pow, ha, zero_mul]

/-- Passing from a nilpotent element to its unipotent exponential preserves
every supplied annihilating exponent. -/
theorem exp_sub_one_pow_eq_zero {a : A} {d : ℕ} (ha : a ^ d = 0) :
    (IsNilpotent.exp a - 1) ^ d = 0 := by
  nontriviality A
  have hd : 0 < d := by
    by_contra h
    have hz : d = 0 := Nat.eq_zero_of_not_pos h
    simp [hz] at ha
  rw [IsNilpotent.exp_eq_sum ha, ← Nat.sub_add_cancel hd, Finset.sum_range_succ']
  simp only [Nat.succ_eq_add_one, zero_add, Nat.factorial_zero, Nat.cast_one, inv_one,
    pow_zero, one_smul, add_sub_cancel_right]
  rw [Nat.sub_add_cancel hd]
  exact sum_smul_pow_succ_pow_eq_zero ha _ _

/-- Passing from a unipotent element to its logarithm preserves every supplied
annihilating exponent. -/
theorem log_pow_eq_zero {u : A} {d : ℕ} (hu : (u - 1) ^ d = 0) :
    (log u) ^ d = 0 := by
  nontriviality A
  have hd : 0 < d := by
    by_contra h
    have hz : d = 0 := Nat.eq_zero_of_not_pos h
    simp [hz] at hu
  rw [log_eq_sum hu, ← Nat.sub_add_cancel hd, Finset.sum_range_succ']
  simp only [Nat.succ_eq_add_one, Nat.cast_zero, div_zero, zero_smul, add_zero, zero_add]
  rw [Nat.sub_add_cancel hd]
  exact sum_smul_pow_succ_pow_eq_zero hu _ _

/-- The inverse logarithm may be truncated at the original nilpotency bound. -/
theorem log_exp_eq_sum {a : A} {d : ℕ} (ha : a ^ d = 0) :
    (∑ j ∈ range d, ((-1 : ℚ) ^ (j + 1) / (j : ℚ)) •
      (IsNilpotent.exp a - 1) ^ j) = a := by
  rw [← log_eq_sum (exp_sub_one_pow_eq_zero ha)]
  exact PaperX.NilpotentLogarithm.log_exp ⟨d, ha⟩

/-- The exponential preserves the complete collection of annihilating exponents. -/
theorem exp_sub_one_pow_eq_zero_iff {a : A} (ha : IsNilpotent a) (d : ℕ) :
    (IsNilpotent.exp a - 1) ^ d = 0 ↔ a ^ d = 0 := by
  constructor
  · intro h
    simpa only [PaperX.NilpotentLogarithm.log_exp ha] using log_pow_eq_zero h
  · exact exp_sub_one_pow_eq_zero

/-- The logarithm preserves the complete collection of annihilating exponents. -/
theorem log_pow_eq_zero_iff {u : A} (hu : IsNilpotent (u - 1)) (d : ℕ) :
    (log u) ^ d = 0 ↔ (u - 1) ^ d = 0 := by
  constructor
  · intro h
    simpa only [PaperX.NilpotentLogarithm.exp_log hu] using exp_sub_one_pow_eq_zero h
  · exact log_pow_eq_zero

/-- The nilpotency class is unchanged by the exponential minus the identity. -/
theorem nilpotencyClass_exp_sub_one {a : A} (ha : IsNilpotent a) :
    nilpotencyClass (IsNilpotent.exp a - 1) = nilpotencyClass a := by
  apply congrArg sInf
  ext d
  exact exp_sub_one_pow_eq_zero_iff ha d

/-- The nilpotency class is unchanged by the finite logarithm. -/
theorem nilpotencyClass_log {u : A} (hu : IsNilpotent (u - 1)) :
    nilpotencyClass (log u) = nilpotencyClass (u - 1) := by
  apply congrArg sInf
  ext d
  exact log_pow_eq_zero_iff hu d

section CoefficientField

variable {K V : Type*} [Field K] [CharZero K] [AddCommGroup V] [Module K V]

local instance : Algebra ℚ (Module.End K V) :=
  Algebra.compHom (Module.End K V) (algebraMap ℚ K)

/-- A supplied monodromy bound gives an explicit recovery polynomial over
the original coefficient field, with precisely that cutoff. -/
theorem monodromy_eq_log_sum {N : Module.End K V} {d : ℕ} (hN : N ^ d = 0)
    {t : K} (ht : t ≠ 0) :
    N = t⁻¹ • ∑ j ∈ range d, ((-1 : K) ^ (j + 1) / (j : K)) •
      (PaperX.NilpotentExponential.expN N t - 1) ^ j := by
  have htN : (t • N) ^ d = 0 := by rw [smul_pow, hN, smul_zero]
  have hU : (PaperX.NilpotentExponential.expN N t - 1) ^ d = 0 :=
    exp_sub_one_pow_eq_zero htN
  calc
    N = PaperX.LogarithmicRecovery.recoverN t (PaperX.NilpotentExponential.expN N t) :=
      (PaperX.LogarithmicRecovery.recoverN_expN ⟨d, hN⟩ ht).symm
    _ = _ := by
      rw [PaperX.LogarithmicRecovery.recoverN, PaperX.LogarithmicRecovery.log_polynomial hU]

end CoefficientField

end PaperX.LogarithmTruncation
