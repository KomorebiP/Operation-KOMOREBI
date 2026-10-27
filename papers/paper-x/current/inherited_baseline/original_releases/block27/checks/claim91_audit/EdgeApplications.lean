import PaperX.CyclotomicSystemSeparation
import PaperX.FiniteAvoidanceBoundary

set_option autoImplicit false
noncomputable section
open PaperX.CyclotomicPrimeCoverage PaperX.CofiniteConjugacyCoverage

-- Coverage on the original index set does not imply coverage after finite deletion.
example : ¬ CofiniteQuotientCoverage PaperX.FiniteAvoidanceBoundary.sample := by
  intro h
  exact PaperX.FiniteAvoidanceBoundary.remaining_quotient_coverage_fails (h {0})

-- Conductor one is included: nonzero conductor, not an unstated n > 1 hypothesis.
example (B : ℕ) : ∃ p : PermittedPrime 1 {2, 3, 5, 7}, B < p.val := by
  obtain ⟨p, hp, _⟩ := exists_prime_with_residue 1 {2, 3, 5, 7} 1 B
  exact ⟨p, hp⟩

-- The arithmetic action is exponent p; for conductor five p = 2 is not its inverse.
example (L : Type*) [Field L] [NumberField L]
    [IsCyclotomicExtension {5} ℚ L] (x : L) (hx : x ^ 5 = 1) :
    primePowerAutomorphism 5 L 2 (by decide) x = x ^ 2 := by
  exact primePowerAutomorphism_apply 5 L 2 (by decide) hx

local instance : IsCyclotomicExtension {4} ℚ (CyclotomicField 4 ℚ) :=
  CyclotomicField.isCyclotomicExtension 4 ℚ

-- Distinct natural primes, arbitrary finite deletion, and arbitrary strict lower bound.
example (σ : Gal(CyclotomicField 4 ℚ/ℚ)) (B : ℕ) :
    ∃ p : PermittedPrime 4 {2, 3, 5, 7, 11}, B < p.val ∧
      primeSample 4 (CyclotomicField 4 ℚ) {2, 3, 5, 7, 11} p = σ := by
  let : IsCyclotomicExtension {4} ℚ (CyclotomicField 4 ℚ) :=
    CyclotomicField.isCyclotomicExtension 4 ℚ
  exact exists_prime_with_automorphism 4 (CyclotomicField 4 ℚ) {2, 3, 5, 7, 11} σ B

-- Empty family: determinant one, including the case of an empty sample domain.
example : ∃ v : Fin 0 → Empty, Function.Injective v ∧
    (PaperX.FiniteSeparation.sampleMatrix (fun (i : Fin 0) => Fin.elim0 i) v :
      Matrix (Fin 0) (Fin 0) ℚ).det ≠ 0 := by
  exact PaperX.FiniteSeparation.exists_nonsingular_samples _
    (linearIndependent_empty_type : LinearIndependent ℚ _)
