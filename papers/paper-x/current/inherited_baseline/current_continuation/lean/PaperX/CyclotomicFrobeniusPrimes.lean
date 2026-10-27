import PaperX.CyclotomicPrimeCoverage

/-! Existence of actual primes above the rational prime samples. Lying-over
supplies maximal ideals of the ring of integers; the preceding module then
proves unramifiedness and the arithmetic Frobenius residue action there. -/
set_option autoImplicit false
noncomputable section
namespace PaperX.CyclotomicFrobeniusPrimes
open NumberField PaperX.CyclotomicPrimeCoverage
open scoped Pointwise

variable (n : ℕ) [NeZero n] (K : Type*) [Field K] [NumberField K]
  [IsCyclotomicExtension {n} ℚ K]

/-- Every rational prime coprime to the conductor has an actual maximal ideal
above it witnessing the unramified arithmetic Frobenius property. -/
theorem exists_prime_above_with_frobenius (p : ℕ) [Fact (Nat.Prime p)]
    (hp : p.Coprime n) :
    ∃ P : Ideal (𝓞 K), P.IsMaximal ∧ P.LiesOver (Ideal.span {(p : ℤ)}) ∧
      Ideal.ramificationIdx P ℤ = 1 ∧
      primePowerAutomorphism n K p hp ∈ MulAction.stabilizer Gal(K/ℚ) P ∧
      ∀ x : 𝓞 K, Ideal.Quotient.mk P (primePowerAutomorphism n K p hp • x) =
        (Ideal.Quotient.mk P x) ^ p := by
  let : (Ideal.span {(p : ℤ)}).IsMaximal := Int.ideal_span_isMaximal_of_prime p
  obtain ⟨P, hP, hPlies⟩ :=
    Ideal.exists_maximal_ideal_liesOver_of_isIntegral (S := 𝓞 K) (Ideal.span {(p : ℤ)})
  let : P.IsMaximal := hP
  let : P.LiesOver (Ideal.span {(p : ℤ)}) := hPlies
  exact ⟨P, hP, hPlies, primePowerAutomorphism_unramified_arithmeticFrobenius n K p P hp⟩

/-- Each permitted prime comes with an actual prime ideal and the proved
unramified Frobenius action, rather than only a conditional statement about
all prime ideals that might lie above it. -/
theorem permitted_prime_has_frobenius_witness (forbidden : Finset ℕ)
    (p : PermittedPrime n forbidden) :
    ∃ P : Ideal (𝓞 K), P.IsMaximal ∧ P.LiesOver (Ideal.span {(p.val : ℤ)}) ∧
      Ideal.ramificationIdx P ℤ = 1 ∧
      primeSample n K forbidden p ∈ MulAction.stabilizer Gal(K/ℚ) P ∧
      ∀ x : 𝓞 K, Ideal.Quotient.mk P (primeSample n K forbidden p • x) =
        (Ideal.Quotient.mk P x) ^ p.val := by
  let : Fact (Nat.Prime p.val) := ⟨p.property.1⟩
  exact exists_prime_above_with_frobenius n K p.val p.property.2.1

/-- Every automorphism is arithmetic Frobenius at an actual unramified prime
ideal above a rational prime outside the chosen finite set and above the bound. -/
theorem exists_arithmetic_frobenius_prime (forbidden : Finset ℕ) (σ : Gal(K/ℚ)) (B : ℕ) :
    ∃ (p : PermittedPrime n forbidden) (P : Ideal (𝓞 K)),
      B < p.val ∧ primeSample n K forbidden p = σ ∧
      P.IsMaximal ∧ P.LiesOver (Ideal.span {(p.val : ℤ)}) ∧
      Ideal.ramificationIdx P ℤ = 1 ∧
      σ ∈ MulAction.stabilizer Gal(K/ℚ) P ∧
      ∀ x : 𝓞 K, Ideal.Quotient.mk P (σ • x) = (Ideal.Quotient.mk P x) ^ p.val := by
  obtain ⟨p, hB, hσ⟩ := exists_prime_with_automorphism n K forbidden σ B
  obtain ⟨P, hP, hPlies, he, hstab, hres⟩ :=
    permitted_prime_has_frobenius_witness n K forbidden p
  refine ⟨p, P, hB, hσ, hP, hPlies, he, ?_, ?_⟩
  · rwa [hσ] at hstab
  · rwa [hσ] at hres

end PaperX.CyclotomicFrobeniusPrimes
