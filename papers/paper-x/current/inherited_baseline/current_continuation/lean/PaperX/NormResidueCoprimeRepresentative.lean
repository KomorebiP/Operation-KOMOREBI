import PaperX.CoprimeClassRepresentative
import PaperX.NormResidueRepresentative
import Mathlib.RingTheory.DedekindDomain.Factorization
import Mathlib.RingTheory.Ideal.Norm.AbsNorm

/-!
# Automatic coprime inverse-class representatives for number fields

For a nonzero integer modulus `m`, only finitely many prime ideals divide the
principal modulus ideal `(m)`.  Finite-prime avoidance supplies an inverse-class
representative avoiding all of them.  A rational prime dividing both its
absolute norm and `m` would produce a maximal ideal above that prime dividing
both ideals, contradicting the avoidance property.
-/

set_option autoImplicit false
noncomputable section

open Ideal NumberField
open scoped NumberField nonZeroDivisors

namespace PaperX.NormResidue

open PaperX.IdealPrimeAvoidance

variable (K : Type*) [Field K] [NumberField K]

/-- A nonzero integer modulus generates a nonzero ideal in the ring of integers. -/
theorem modulusIdeal_ne_bot (m : ℕ) (hm : m ≠ 0) :
    modulusIdeal (𝓞 K) m ≠ (⊥ : Ideal (𝓞 K)) := by
  rw [modulusIdeal, ne_eq, Ideal.span_singleton_eq_bot]
  exact Nat.cast_ne_zero.mpr hm

/-- Every ideal class has an inverse-class integral representative whose
absolute norm is coprime to any prescribed nonzero integer modulus. -/
theorem exists_coprime_inverse_class_representative
    (C : ClassGroup (𝓞 K)) (m : ℕ) (hm : m ≠ 0) :
    ∃ J : (Ideal (𝓞 K))⁰,
      ClassGroup.mk0 J = C⁻¹ ∧
      (absNorm (J : Ideal (𝓞 K))).Coprime m := by
  classical
  let M : Ideal (𝓞 K) := modulusIdeal (𝓞 K) m
  have hM : M ≠ ⊥ := by
    simpa [M] using modulusIdeal_ne_bot K m hm
  let s : Finset (IsDedekindDomain.HeightOneSpectrum (𝓞 K)) :=
    (Ideal.finite_factors hM).toFinset
  obtain ⟨I, hI⟩ := ClassGroup.mk0_surjective C
  let P : {v // v ∈ s} → Ideal (𝓞 K) := fun v => v.1.asIdeal
  have hP : ∀ v, Prime (P v) := fun v => v.1.prime
  have hpair : Pairwise fun i j : {v // v ∈ s} => P i ≠ P j := by
    intro i j hij hEq
    apply hij
    apply Subtype.ext
    exact IsDedekindDomain.HeightOneSpectrum.asIdeal_injective hEq
  obtain ⟨J, hJclass, havoid⟩ :=
    exists_inverse_class_representative_avoiding P hP hpair I
  refine ⟨J, by simpa [hI] using hJclass, ?_⟩
  by_contra hcop
  obtain ⟨p, hp, hpJ, hpm⟩ := Nat.Prime.not_coprime_iff_dvd.mp hcop
  obtain ⟨Q, hQmax, hQunder, hQJ⟩ :=
    Ideal.exists_isMaximal_dvd_of_dvd_absNorm' hp (J : Ideal (𝓞 K)) hpJ
  let v : IsDedekindDomain.HeightOneSpectrum (𝓞 K) :=
    ⟨Q, hQmax.isPrime, Ideal.IsMaximal.ne_bot_of_isIntegral_int Q⟩
  have hQm : Q ∣ M := by
    rw [Ideal.dvd_iff_le]
    change modulusIdeal (𝓞 K) m ≤ Q
    rw [modulusIdeal]
    apply Ideal.span_le.mpr
    intro x hx
    change x ∈ ({(m : 𝓞 K)} : Set (𝓞 K)) at hx
    simp only [Set.mem_singleton_iff] at hx
    subst x
    have hpUnder : (p : ℤ) ∈ Q.under ℤ := by
      rw [hQunder]
      exact Ideal.mem_span_singleton_self (p : ℤ)
    have hpQ : (p : 𝓞 K) ∈ Q := by
      simpa [Ideal.mem_under] using hpUnder
    have hpd : (p : 𝓞 K) ∣ (m : 𝓞 K) := by
      obtain ⟨k, rfl⟩ := hpm
      exact ⟨(k : 𝓞 K), by simp⟩
    exact Q.mem_of_dvd hpd hpQ
  have hvs : v ∈ s := by
    simpa [s, v] using hQm
  let q : {v // v ∈ s} := ⟨v, hvs⟩
  exact havoid q (by simpa [P, q, v] using hQJ)

end PaperX.NormResidue
