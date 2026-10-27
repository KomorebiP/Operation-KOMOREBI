import CrossRadixValuationCoordinates

open scoped ArithmeticFunction.Omega

namespace KomorebiCrossRadix

noncomputable section
variable {T : ℕ}

/-- Exact number of primitive spectral atoms / algebra dimension. -/
theorem spectralAtomCount_prime_product (hT : 0 < T) :
    Fintype.card (DivIdx T) =
      T.primeFactors.prod (fun p => T.factorization p + 1) :=
  card_DivIdx_prime_product hT

/-- Exact size of the unique least canonical-width generator family. -/
theorem minimalWidthGeneratorCount_eq_Omega (hT : 0 < T) :
    (primePowerDivisors T).card = Ω T :=
  primePowerDivisors_card_eq_Omega hT

/-- Exact number of idempotents in the complete diagonal projector algebra. -/
theorem idempotentOperatorCount_prime_product (hT : 0 < T) :
    Fintype.card (IdemAlg T) =
      2 ^ (T.primeFactors.prod (fun p => T.factorization p + 1)) := by
  rw [idemAlg_card, card_DivIdx_prime_product hT]

/-- Finite complexity ledger: generators, primitive atoms, and idempotents. -/
theorem crossRadix_complexity_ledger (hT : 0 < T) :
    (primePowerDivisors T).card = Ω T ∧
    Module.finrank ℂ (ProjectorAlg T) =
      T.primeFactors.prod (fun p => T.factorization p + 1) ∧
    Fintype.card (IdemAlg T) =
      2 ^ (T.primeFactors.prod (fun p => T.factorization p + 1)) := by
  exact ⟨minimalWidthGeneratorCount_eq_Omega hT,
    projectorAlg_finrank_prime_product hT,
    idempotentOperatorCount_prime_product hT⟩

end
end KomorebiCrossRadix
