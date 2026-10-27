import CrossRadixPrimePowerAlgebraGeneration

namespace KomorebiCrossRadix

noncomputable section
variable {T : ℕ}

/-- Width vectors coming from a chosen family of canonical divisor widths. -/
def canonicalWidthGeneratorSet (S : Set (DivIdx T)) : Set (DivCoord T) :=
  {a | ∃ g, g ∈ S ∧ a = widthVec g}

/-- Canonical width family generates the full divisor-coordinate algebra. -/
def AlgebraGeneratesWidths (S : Set (DivIdx T)) : Prop :=
  Algebra.adjoin ℂ (canonicalWidthGeneratorSet S) = ⊤

/-- Functions agreeing on two divisor coordinates form a subalgebra. -/
def coordinateEqualizer (x y : DivIdx T) : Subalgebra ℂ (DivCoord T) where
  carrier := {a | a x = a y}
  mul_mem' := by
    intro a b ha hb
    change a x = a y at ha
    change b x = b y at hb
    change (a * b) x = (a * b) y
    rw [Pi.mul_apply, Pi.mul_apply, ha, hb]
  one_mem' := by simp
  add_mem' := by
    intro a b ha hb
    change a x = a y at ha
    change b x = b y at hb
    change (a + b) x = (a + b) y
    rw [Pi.add_apply, Pi.add_apply, ha, hb]
  zero_mem' := by simp
  algebraMap_mem' := by intro r; rfl

/-- Full algebra generation forces the selected widths to separate divisor coordinates. -/
lemma algebraGeneratesWidths_implies_separates {S : Set (DivIdx T)}
    (hgen : AlgebraGeneratesWidths S) : SeparatesWidths S := by
  intro x y hxy
  by_contra hnone
  push Not at hnone
  have hsubset : canonicalWidthGeneratorSet S ⊆ coordinateEqualizer x y := by
    intro a ha
    rcases ha with ⟨g, hgS, rfl⟩
    exact hnone g hgS
  have hadj : Algebra.adjoin ℂ (canonicalWidthGeneratorSet S) ≤ coordinateEqualizer x y :=
    Algebra.adjoin_le hsubset
  rw [hgen] at hadj
  have hshell : shellVec x ∈ coordinateEqualizer x y := by
    exact hadj (by simp)
  change shellVec x x = shellVec x y at hshell
  have hyx : y = x := by simpa [shellVec] using hshell
  exact hxy hyx.symm

lemma canonical_primePower_generators_eq_raw :
    canonicalWidthGeneratorSet (primePowerWidthSet (T := T)) =
      primePowerWidthGeneratorSet T := by
  ext a
  constructor
  · rintro ⟨g, hgpp, rfl⟩
    have hgmem : g.1 ∈ primePowerDivisors T := by
      rw [primePowerDivisors, Finset.mem_filter]
      exact ⟨g.2, hgpp⟩
    refine ⟨g.1, hgmem, ?_⟩
    exact (rawWidthVec_dividx g).symm
  · rintro ⟨q, hq, rfl⟩
    have hqd : q ∈ T.divisors := (Finset.mem_filter.mp hq).1
    have hqpp : IsPrimePow q := (Finset.mem_filter.mp hq).2
    let g : DivIdx T := ⟨q, hqd⟩
    refine ⟨g, ?_, ?_⟩
    · exact hqpp
    · exact rawWidthVec_dividx g

/-- Prime-power canonical widths generate the complete algebra. -/
theorem primePowerWidthSet_algebra_generates (hT : 0 < T) :
    AlgebraGeneratesWidths (primePowerWidthSet (T := T)) := by
  unfold AlgebraGeneratesWidths
  rw [canonical_primePower_generators_eq_raw]
  exact primePowerWidths_adjoin_eq_top hT

/-- Every algebra-generating family of canonical widths contains all prime-power widths. -/
theorem primePowerWidthSet_minimal_algebra_generators (hT : 0 < T)
    {S : Set (DivIdx T)} (hgen : AlgebraGeneratesWidths S) :
    primePowerWidthSet (T := T) ⊆ S := by
  exact primePowerWidthSet_minimal hT (algebraGeneratesWidths_implies_separates hgen)

/-- Prime-power widths are the unique least algebra-generating canonical-width family. -/
theorem primePowerWidthSet_least_algebra_generating (hT : 0 < T) :
    AlgebraGeneratesWidths (primePowerWidthSet (T := T)) ∧
      ∀ S : Set (DivIdx T), AlgebraGeneratesWidths S →
        primePowerWidthSet (T := T) ⊆ S := by
  exact ⟨primePowerWidthSet_algebra_generates hT,
    fun S hS => primePowerWidthSet_minimal_algebra_generators hT hS⟩

end
end KomorebiCrossRadix
