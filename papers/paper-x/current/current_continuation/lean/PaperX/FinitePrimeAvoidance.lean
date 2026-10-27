import PaperX.NormResidueRepresentative
import Mathlib.RingTheory.DedekindDomain.Ideal.Lemmas

/-!
# Simultaneous finite-prime avoidance inside a nonzero Dedekind ideal

For a finite family of distinct nonzero prime ideals and a nonzero integral
ideal `I`, construct an element of `I` whose valuation at every selected prime
is exactly the valuation already forced by `I`.  Equivalently, the element is
not in `P * I` for any selected prime `P`.

This is the algebraic CRT mechanism needed to replace a prescribed ideal-class
representative by one avoiding all primes above a fixed modulus.
-/

set_option autoImplicit false
noncomputable section

open Ideal
open scoped BigOperators

namespace PaperX.IdealPrimeAvoidance

variable {R ι : Type*} [CommRing R] [IsDedekindDomain R]

private theorem exists_mem_not_mem_prime_mul
    (P I : Ideal R) (hP : Prime P) (hI : I ≠ ⊥) :
    ∃ a : R, a ∈ I ∧ a ∉ P * I := by
  have hPt : P < (⊤ : Ideal R) :=
    lt_top_iff_ne_top.mpr (isPrime_of_prime hP).ne_top
  have hpos : (⊥ : Ideal R) < I := bot_lt_iff_ne_bot.mpr hI
  have hmul : P * I < (⊤ : Ideal R) * I :=
    mul_lt_mul_of_pos_right hPt hpos
  have hstrict : P * I < I := by simpa using hmul
  obtain ⟨a, haI, haPI⟩ := SetLike.exists_of_lt hstrict
  exact ⟨a, haI, haPI⟩

/-- A nonzero ideal contains an element which simultaneously avoids `P * I`
for every ideal in a finite pairwise-distinct prime family. -/
theorem exists_mem_avoiding_prime_multiples [Fintype ι]
    (P : ι → Ideal R) (hP : ∀ i, Prime (P i))
    (hpair : Pairwise fun i j => P i ≠ P j)
    (I : Ideal R) (hI : I ≠ ⊥) :
    ∃ a : R, a ∈ I ∧ ∀ i, a ∉ P i * I := by
  classical
  have ha_exists : ∀ i : ι, ∃ a : R, a ∈ I ∧ a ∉ P i * I :=
    fun i => exists_mem_not_mem_prime_mul (P i) I (hP i) hI
  choose a0 ha0I ha0not using ha_exists

  let target : ι → (↥(Finset.univ : Finset ι) → R) := fun i j =>
    if (j : ι) = i then 1 else 0

  have he_exists : ∀ i : ι, ∃ e : R, ∀ j : ι,
      e - (if j = i then 1 else 0) ∈ P j := by
    intro i
    obtain ⟨e, he⟩ := IsDedekindDomain.exists_forall_sub_mem_ideal
      (s := (Finset.univ : Finset ι)) P (fun _ => 1)
      (fun j _ => hP j)
      (fun j _ k _ hjk => hpair hjk)
      (target i)
    refine ⟨e, ?_⟩
    intro j
    simpa [target] using he j (Finset.mem_univ j)
  choose e he using he_exists

  let a : R := ∑ i : ι, e i * a0 i
  refine ⟨a, ?_, ?_⟩
  · dsimp [a]
    exact Ideal.sum_mem _ fun i _ => I.mul_mem_left (e i) (ha0I i)
  · intro k hak
    have hdiff : a - a0 k ∈ P k * I := by
      have hsum :
          ∑ i : ι, (e i - (if i = k then 1 else 0)) * a0 i ∈ P k * I := by
        exact Ideal.sum_mem _ fun i _ =>
          Ideal.mul_mem_mul (by simpa [eq_comm] using he i k) (ha0I i)
      have hid :
          (∑ i : ι, (e i - (if i = k then 1 else 0)) * a0 i) = a - a0 k := by
        simp [a, sub_mul]
      rw [hid] at hsum
      exact hsum
    have ha0bad : a0 k ∈ P k * I := by
      have : a0 k = a - (a - a0 k) := by ring
      rw [this]
      exact (P k * I).sub_mem hak hdiff
    exact (ha0not k) ha0bad


/-- The simultaneous avoiding element can be chosen nonzero, including when the
finite prime family is empty. -/
theorem exists_ne_zero_mem_avoiding_prime_multiples [Fintype ι]
    (P : ι → Ideal R) (hP : ∀ i, Prime (P i))
    (hpair : Pairwise fun i j => P i ≠ P j)
    (I : Ideal R) (hI : I ≠ ⊥) :
    ∃ a : R, a ∈ I ∧ a ≠ 0 ∧ ∀ i, a ∉ P i * I := by
  classical
  cases isEmpty_or_nonempty ι with
  | inl hEmpty =>
      obtain ⟨a, haI, ha0⟩ := (Submodule.ne_bot_iff I).mp hI
      exact ⟨a, haI, ha0, fun i => (hEmpty.false i).elim⟩
  | inr hNonempty =>
      obtain ⟨a, haI, ha⟩ :=
        exists_mem_avoiding_prime_multiples P hP hpair I hI
      refine ⟨a, haI, ?_, ha⟩
      intro ha0
      subst a
      let i : ι := Classical.choice hNonempty
      exact ha i (P i * I).zero_mem

end PaperX.IdealPrimeAvoidance
