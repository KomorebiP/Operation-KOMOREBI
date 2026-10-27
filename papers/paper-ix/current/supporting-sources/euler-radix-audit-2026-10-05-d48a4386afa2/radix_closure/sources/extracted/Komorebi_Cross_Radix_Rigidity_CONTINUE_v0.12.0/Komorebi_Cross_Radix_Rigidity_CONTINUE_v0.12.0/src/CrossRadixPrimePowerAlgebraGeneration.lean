import CrossRadixPrimePowerGenerators

open scoped BigOperators

namespace KomorebiCrossRadix

noncomputable section
variable {T : ℕ}

/-- The canonical prime-power width vectors, viewed as algebra generators. -/
def primePowerWidthGeneratorSet (T : ℕ) : Set (DivCoord T) :=
  {a | ∃ q, q ∈ primePowerDivisors T ∧ a = rawWidthVec (T := T) q}

lemma rawWidthVec_mem_primePower_adjoin {q : ℕ} (hq : q ∈ primePowerDivisors T) :
    rawWidthVec (T := T) q ∈ Algebra.adjoin ℂ (primePowerWidthGeneratorSet T) := by
  apply Algebra.subset_adjoin
  exact ⟨q, hq, rfl⟩

lemma thresholdLiteral_mem_primePower_adjoin (c : DivIdx T) {q : ℕ}
    (hq : q ∈ primePowerDivisors T) :
    thresholdLiteral c q ∈ Algebra.adjoin ℂ (primePowerWidthGeneratorSet T) := by
  by_cases hqc : q ∣ c.1
  · simpa [thresholdLiteral, hqc] using rawWidthVec_mem_primePower_adjoin (T := T) hq
  · simp only [thresholdLiteral, hqc, ↓reduceIte]
    exact (Algebra.adjoin ℂ (primePowerWidthGeneratorSet T)).sub_mem
      (Algebra.adjoin ℂ (primePowerWidthGeneratorSet T)).one_mem
      (rawWidthVec_mem_primePower_adjoin (T := T) hq)

lemma primePowerShellFormula_eq_algebra_prod (c : DivIdx T) :
    primePowerShellFormula c =
      ∏ q ∈ primePowerDivisors T, thresholdLiteral c q := by
  funext x
  simp [primePowerShellFormula]

lemma shellVec_mem_primePower_adjoin (hT : 0 < T) (c : DivIdx T) :
    shellVec c ∈ Algebra.adjoin ℂ (primePowerWidthGeneratorSet T) := by
  rw [← primePowerShellFormula_eq_shell hT c,
      primePowerShellFormula_eq_algebra_prod]
  exact (Algebra.adjoin ℂ (primePowerWidthGeneratorSet T)).prod_mem
    (fun q hq => thresholdLiteral_mem_primePower_adjoin (T := T) c hq)

lemma sum_smul_shellVec (a : DivCoord T) :
    (∑ c : DivIdx T, (a c) • shellVec c) = a := by
  funext x
  simp [shellVec]

/-- The canonical prime-power widths generate the entire divisor-coordinate algebra. -/
theorem primePowerWidths_adjoin_eq_top (hT : 0 < T) :
    Algebra.adjoin ℂ (primePowerWidthGeneratorSet T) = ⊤ := by
  rw [eq_top_iff]
  intro a ha
  rw [← sum_smul_shellVec a]
  exact (Algebra.adjoin ℂ (primePowerWidthGeneratorSet T)).sum_mem
    (fun c _ => (Algebra.adjoin ℂ (primePowerWidthGeneratorSet T)).smul_mem
      (shellVec_mem_primePower_adjoin hT c) (a c))

end
end KomorebiCrossRadix
