import CrossRadixMinimalAlgebraGenerators
import Mathlib.NumberTheory.ArithmeticFunction.Misc
import Mathlib.Data.Nat.Factorization.PrimePow
import Mathlib.Data.Nat.Prime.Int

open scoped ArithmeticFunction.Omega

namespace KomorebiCrossRadix

noncomputable section

/-- The powers of one prime that occur among the divisors of `T`. -/
def primePowerFiber (T p : ℕ) : Finset ℕ :=
  (Finset.Icc 1 (T.factorization p)).image (fun j => p ^ j)

/-- Union of the positive power fibers over the prime divisors of `T`. -/
def primePowerFiberUnion (T : ℕ) : Finset ℕ :=
  T.primeFactors.biUnion (primePowerFiber T)

lemma primePowerDivisors_eq_fiberUnion {T : ℕ} (hT : 0 < T) :
    primePowerDivisors T = primePowerFiberUnion T := by
  ext q
  simp only [primePowerDivisors, Finset.mem_filter, primePowerFiberUnion,
    Finset.mem_biUnion, primePowerFiber, Finset.mem_image, Finset.mem_Icc]
  constructor
  · rintro ⟨hqDiv, hqPP⟩
    obtain ⟨p, k, hp, hk, rfl⟩ := (isPrimePow_nat_iff q).mp hqPP
    have hT0 : T ≠ 0 := Nat.ne_of_gt hT
    have hpkT : p ^ k ∣ T := (Nat.mem_divisors.mp hqDiv).1
    have hle : k ≤ T.factorization p :=
      (hp.pow_dvd_iff_le_factorization hT0).mp hpkT
    have hpT : p ∣ T := dvd_trans (dvd_pow_self p hk.ne') hpkT
    have hpMem : p ∈ T.primeFactors := Nat.mem_primeFactors.mpr ⟨hp, hpT, hT0⟩
    exact ⟨p, hpMem, k, ⟨hk, hle⟩, rfl⟩
  · rintro ⟨p, hpMem, k, ⟨hk, hle⟩, rfl⟩
    have hT0 : T ≠ 0 := Nat.ne_of_gt hT
    have hp : p.Prime := (Nat.mem_primeFactors.mp hpMem).1
    have hpkT : p ^ k ∣ T :=
      (hp.pow_dvd_iff_le_factorization hT0).mpr hle
    exact ⟨Nat.mem_divisors.mpr ⟨hpkT, hT0⟩,
      (isPrimePow_nat_iff (p ^ k)).mpr ⟨p, k, hp, hk, rfl⟩⟩

lemma primePowerFiber_card {T p : ℕ} (hp : p.Prime) :
    (primePowerFiber T p).card = T.factorization p := by
  rw [primePowerFiber, Finset.card_image_of_injective _ (Nat.pow_right_injective hp.two_le),
    Nat.card_Icc]
  omega

lemma primePowerFibers_pairwiseDisjoint {T : ℕ} :
    ((T.primeFactors : Set ℕ).PairwiseDisjoint (primePowerFiber T)) := by
  intro p hpMem q hqMem hpq
  change Disjoint (primePowerFiber T p) (primePowerFiber T q)
  rw [Finset.disjoint_left]
  intro n hnp hnq
  simp only [primePowerFiber, Finset.mem_image, Finset.mem_Icc] at hnp hnq
  obtain ⟨j, ⟨hj, _⟩, rfl⟩ := hnp
  obtain ⟨k, ⟨hk, _⟩, hpow⟩ := hnq
  have hp : p.Prime := (Nat.mem_primeFactors.mp hpMem).1
  have hq : q.Prime := (Nat.mem_primeFactors.mp hqMem).1
  have hj0 : j ≠ 0 := by omega
  have hk0 : k ≠ 0 := by omega
  have hsame := hp.pow_inj' hq hj0 hk0 hpow.symm
  exact hpq hsame.1

/-- Number of prime-power divisor thresholds is exactly the total prime-factor multiplicity `Ω(T)`. -/
theorem primePowerDivisors_card_eq_Omega {T : ℕ} (hT : 0 < T) :
    (primePowerDivisors T).card = Ω T := by
  rw [primePowerDivisors_eq_fiberUnion hT, primePowerFiberUnion,
    Finset.card_biUnion primePowerFibers_pairwiseDisjoint]
  have hsum : (∑ p ∈ T.primeFactors, (primePowerFiber T p).card) =
      ∑ p ∈ T.primeFactors, T.factorization p := by
    apply Finset.sum_congr rfl
    intro p hpMem
    exact primePowerFiber_card (Nat.mem_primeFactors.mp hpMem).1
  rw [hsum, ArithmeticFunction.cardFactors_eq_sum_factorization]
  simp [Finsupp.sum, Nat.support_factorization]

end
end KomorebiCrossRadix
