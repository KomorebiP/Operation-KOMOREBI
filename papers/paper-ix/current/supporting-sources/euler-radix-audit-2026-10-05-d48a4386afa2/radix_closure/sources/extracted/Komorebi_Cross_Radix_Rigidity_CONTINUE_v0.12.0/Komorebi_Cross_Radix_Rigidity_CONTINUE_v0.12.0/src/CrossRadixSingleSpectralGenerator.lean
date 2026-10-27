import CrossRadixComplexityProfile

open scoped BigOperators

namespace KomorebiCrossRadix

noncomputable section
variable {T : ℕ}

/-- A single global spectral label: distinct divisor coordinates receive distinct complex scalars. -/
def spectralLabelVec : DivCoord T := fun c => (c.1 : ℂ)

/-- Lagrange factor that vanishes at `d` and equals one at the target coordinate `c`. -/
def lagrangeFactor (c d : DivIdx T) : DivCoord T :=
  ((c.1 : ℂ) - (d.1 : ℂ))⁻¹ •
    (spectralLabelVec - (d.1 : ℂ) • (1 : DivCoord T))

lemma divisor_cast_ne {c d : DivIdx T} (hcd : c ≠ d) : (c.1 : ℂ) ≠ (d.1 : ℂ) := by
  intro h
  have hnat : c.1 = d.1 := by exact_mod_cast h
  exact hcd (Subtype.ext hnat)

lemma lagrangeFactor_target (c d : DivIdx T) (hcd : c ≠ d) :
    lagrangeFactor c d c = 1 := by
  have hcast := divisor_cast_ne hcd
  have hden : (c.1 : ℂ) - (d.1 : ℂ) ≠ 0 := sub_ne_zero.mpr hcast
  simp [lagrangeFactor, spectralLabelVec, hden]

@[simp] lemma lagrangeFactor_zero (c d : DivIdx T) :
    lagrangeFactor c d d = 0 := by
  simp [lagrangeFactor, spectralLabelVec]

/-- Primitive shell reconstructed as a polynomial/Lagrange expression in one label observable. -/
def lagrangeShellFormula (c : DivIdx T) : DivCoord T :=
  fun x => ∏ d ∈ (Finset.univ.erase c), lagrangeFactor c d x

lemma lagrangeShellFormula_eq_shell (c : DivIdx T) :
    lagrangeShellFormula c = shellVec c := by
  funext x
  by_cases hxc : x = c
  · subst x
    rw [shellVec, ite_eq_left rfl]
    simp only [lagrangeShellFormula]
    apply Finset.prod_eq_one
    intro d hd
    have hdc : d ≠ c := by
      exact Finset.ne_of_mem_erase hd
    exact lagrangeFactor_target c d hdc.symm
  · rw [shellVec, ite_eq_right hxc]
    simp only [lagrangeShellFormula]
    have hxmem : x ∈ Finset.univ.erase c := by
      simp [hxc]
    exact Finset.prod_eq_zero hxmem (lagrangeFactor_zero c x)

/-- The singleton set containing the global spectral label. -/
def spectralLabelGeneratorSet (T : ℕ) : Set (DivCoord T) := {spectralLabelVec (T := T)}

lemma spectralLabelVec_mem_adjoin :
    spectralLabelVec (T := T) ∈ Algebra.adjoin ℂ (spectralLabelGeneratorSet T) := by
  apply Algebra.subset_adjoin
  simp [spectralLabelGeneratorSet]

lemma lagrangeFactor_mem_spectralLabel_adjoin (c d : DivIdx T) :
    lagrangeFactor c d ∈ Algebra.adjoin ℂ (spectralLabelGeneratorSet T) := by
  let S := Algebra.adjoin ℂ (spectralLabelGeneratorSet T)
  have hlabel : spectralLabelVec (T := T) ∈ S := spectralLabelVec_mem_adjoin
  have hconst : (d.1 : ℂ) • (1 : DivCoord T) ∈ S := S.smul_mem S.one_mem (d.1 : ℂ)
  have hdiff : spectralLabelVec - (d.1 : ℂ) • (1 : DivCoord T) ∈ S := S.sub_mem hlabel hconst
  exact S.smul_mem hdiff (((c.1 : ℂ) - (d.1 : ℂ))⁻¹)

lemma lagrangeShellFormula_eq_algebra_prod (c : DivIdx T) :
    lagrangeShellFormula c =
      ∏ d ∈ (Finset.univ.erase c), lagrangeFactor c d := by
  funext x
  simp [lagrangeShellFormula]

lemma shellVec_mem_spectralLabel_adjoin (c : DivIdx T) :
    shellVec c ∈ Algebra.adjoin ℂ (spectralLabelGeneratorSet T) := by
  rw [← lagrangeShellFormula_eq_shell c, lagrangeShellFormula_eq_algebra_prod]
  exact (Algebra.adjoin ℂ (spectralLabelGeneratorSet T)).prod_mem
    (fun d _ => lagrangeFactor_mem_spectralLabel_adjoin c d)

/-- One unrestricted global spectral observable generates the full diagonal coordinate algebra. -/
theorem spectralLabel_adjoin_eq_top :
    Algebra.adjoin ℂ (spectralLabelGeneratorSet T) = ⊤ := by
  rw [eq_top_iff]
  intro a ha
  rw [← sum_smul_shellVec a]
  exact (Algebra.adjoin ℂ (spectralLabelGeneratorSet T)).sum_mem
    (fun c _ => (Algebra.adjoin ℂ (spectralLabelGeneratorSet T)).smul_mem
      (shellVec_mem_spectralLabel_adjoin c) (a c))

end
end KomorebiCrossRadix

namespace KomorebiCrossRadix

noncomputable section
variable {T : ℕ}

/-- For a nontrivial divisor spectrum, the empty generator set cannot generate the full algebra. -/
theorem emptyGenerator_adjoin_ne_top (hT : 1 < T) :
    Algebra.adjoin ℂ (∅ : Set (DivCoord T)) ≠ ⊤ := by
  let oneIdx : DivIdx T := ⟨1, Nat.one_mem_divisors.mpr (by omega)⟩
  let topIdx : DivIdx T := ⟨T, Nat.mem_divisors_self T (by omega)⟩
  have hne : oneIdx ≠ topIdx := by
    intro h
    have hv := congrArg Subtype.val h
    change 1 = T at hv
    omega
  intro htop
  have hsubset : (∅ : Set (DivCoord T)) ⊆ coordinateEqualizer oneIdx topIdx := by
    intro a ha
    simp at ha
  have hadj : Algebra.adjoin ℂ (∅ : Set (DivCoord T)) ≤ coordinateEqualizer oneIdx topIdx :=
    Algebra.adjoin_le hsubset
  rw [htop] at hadj
  have hshell : shellVec oneIdx ∈ coordinateEqualizer oneIdx topIdx := hadj (by simp)
  change shellVec oneIdx oneIdx = shellVec oneIdx topIdx at hshell
  have heq : topIdx = oneIdx := by simpa [shellVec] using hshell
  exact hne heq.symm

/-- For `T>1`, the unrestricted diagonal coordinate algebra has exact generator number one. -/
theorem unrestricted_generator_number_one (hT : 1 < T) :
    Algebra.adjoin ℂ (spectralLabelGeneratorSet T) = ⊤ ∧
      Algebra.adjoin ℂ (∅ : Set (DivCoord T)) ≠ ⊤ := by
  exact ⟨spectralLabel_adjoin_eq_top, emptyGenerator_adjoin_ne_top hT⟩

end
end KomorebiCrossRadix
