import CrossRadixSingleSpectralGenerator

open scoped ArithmeticFunction.Omega

namespace KomorebiCrossRadix

noncomputable section
variable {T : ℕ}

/-- Exact separation between unrestricted and width-compatible algebra generation. -/
theorem generatorComplexitySeparation (hT : 1 < T) :
    Algebra.adjoin ℂ (spectralLabelGeneratorSet T) = ⊤ ∧
    Algebra.adjoin ℂ (∅ : Set (DivCoord T)) ≠ ⊤ ∧
    AlgebraGeneratesWidths (primePowerWidthSet (T := T)) ∧
    (∀ S : Set (DivIdx T), AlgebraGeneratesWidths S →
      primePowerWidthSet (T := T) ⊆ S) ∧
    (primePowerDivisors T).card = Ω T := by
  have hT0 : 0 < T := by omega
  exact ⟨spectralLabel_adjoin_eq_top,
    emptyGenerator_adjoin_ne_top hT,
    primePowerWidthSet_algebra_generates hT0,
    fun S hS => primePowerWidthSet_minimal_algebra_generators hT0 hS,
    primePowerDivisors_card_eq_Omega hT0⟩

end
end KomorebiCrossRadix
