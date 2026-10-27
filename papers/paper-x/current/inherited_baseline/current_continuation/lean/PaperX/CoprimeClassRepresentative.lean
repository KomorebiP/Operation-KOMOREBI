import PaperX.FinitePrimeAvoidance
import Mathlib.RingTheory.ClassGroup.Basic

/-!
# Ideal-class representatives avoiding finitely many primes

This is the elementary class-group step needed by the norm-residue counting
lane.  Starting from a nonzero ideal `I`, finite-prime avoidance produces a
nonzero `a ∈ I` with `a ∉ P * I` for every selected prime.  Factoring the
principal ideal `(a)` as `I * J` then puts `J` in the inverse ideal class and
forces `J` to avoid every selected prime.
-/

set_option autoImplicit false
noncomputable section

open Ideal
open scoped nonZeroDivisors

namespace PaperX.IdealPrimeAvoidance

variable {R ι : Type*} [CommRing R] [IsDedekindDomain R]

/-- Every inverse ideal class has a nonzero integral representative avoiding a
prescribed finite pairwise-distinct family of prime ideals. -/
theorem exists_inverse_class_representative_avoiding [Fintype ι]
    (P : ι → Ideal R) (hP : ∀ i, Prime (P i))
    (hpair : Pairwise fun i j => P i ≠ P j)
    (I : (Ideal R)⁰) :
    ∃ J : (Ideal R)⁰,
      ClassGroup.mk0 J = (ClassGroup.mk0 I)⁻¹ ∧
      ∀ i, ¬ P i ∣ (J : Ideal R) := by
  classical
  obtain ⟨a, haI, ha0, haAvoid⟩ :=
    exists_ne_zero_mem_avoiding_prime_multiples P hP hpair (I : Ideal R)
      (mem_nonZeroDivisors_iff_ne_zero.mp I.2)
  have hdiv : (I : Ideal R) ∣ Ideal.span {a} :=
    Ideal.dvd_iff_le.mpr (Ideal.span_le.mpr (by
      intro x hx
      simp only [Set.mem_singleton_iff] at hx
      subst x
      exact haI))
  obtain ⟨J, hJ⟩ := hdiv
  have hJ0 : J ≠ (⊥ : Ideal R) := by
    intro h0
    subst J
    have : Ideal.span ({a} : Set R) = ⊥ := by simpa using hJ
    exact ha0 (Ideal.span_singleton_eq_bot.mp this)
  let J0 : (Ideal R)⁰ := ⟨J, mem_nonZeroDivisors_iff_ne_zero.mpr hJ0⟩
  refine ⟨J0, ?_, ?_⟩
  · have hclass : ClassGroup.mk0 I = (ClassGroup.mk0 J0)⁻¹ := by
      rw [ClassGroup.mk0_eq_mk0_inv_iff]
      exact ⟨a, ha0, by simpa [J0] using hJ.symm⟩
    have hinv := congrArg (fun z : ClassGroup R => z⁻¹) hclass
    simpa using hinv.symm
  · intro i hPiJ
    apply haAvoid i
    have hJP : J ≤ P i := Ideal.dvd_iff_le.mp hPiJ
    have hmul : (I : Ideal R) * J ≤ (I : Ideal R) * P i :=
      Ideal.mul_mono le_rfl hJP
    have haProd : a ∈ (I : Ideal R) * J := by
      rw [← hJ]
      exact Ideal.mem_span_singleton_self a
    have : a ∈ (I : Ideal R) * P i := hmul haProd
    simpa [mul_comm] using this

end PaperX.IdealPrimeAvoidance
