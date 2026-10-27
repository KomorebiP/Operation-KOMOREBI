import KomorebiSpace.CompositionStack
import Mathlib.Tactic.FinCases

set_option autoImplicit false

/-!
# The composition topology is not merely object or arrow coverage

Proper patches of a four-view chain can cover all compositions. In a
three-view chain, proper patches cover all individual arrows but can omit
one composition. These examples test the specified covering doctrine.
-/
namespace KomorebiSpace
open CategoryTheory
namespace CompositionSiteExamples

/-- Delete one of the views, retaining the induced full patch. -/
def omitOne (n : ℕ) (i : Fin n) : Set (Fin n) := {x | x ≠ i}

/-- Four proper patches cover every composable pair in the four-view chain. -/
theorem four_proper_cover : CompositionSite.FamilyCovers
    (Set.univ : Set (Fin 4)) (omitOne 4) := by
  intro q _
  have he : ∀ a b c : Fin 4, ∃ i : Fin 4, a ≠ i ∧ b ≠ i ∧ c ≠ i := by decide
  obtain ⟨i, ha, hb, hc⟩ := he q.a q.b q.c
  exact ⟨i, (q.support_le_iff _).mpr ⟨ha, hb, hc⟩⟩

/-- None of the four patches is the global patch. -/
theorem four_patches_proper (i : Fin 4) : omitOne 4 i ≠ Set.univ := by
  intro h
  have hi : i ∈ omitOne 4 i := by rw [h]; trivial
  exact hi rfl

/-- Their generated sieve really belongs to the constructed Grothendieck topology. -/
theorem four_sieve_covering :
    Sieve.ofArrows (omitOne 4) (fun i => homOfLE (Set.subset_univ (omitOne 4 i))) ∈
      CompositionSite.topology (Fin 4) Set.univ := by
  rw [CompositionSite.ofArrows_covering_iff]
  exact four_proper_cover

/-- In three views, every individual arrow is still contained in a proper patch. -/
theorem three_cover_arrows : ViewSystem.TransitionCover (omitOne 3) := by
  intro a b _
  have he : ∃ i : Fin 3, a ≠ i ∧ b ≠ i := by
    fin_cases a <;> fin_cases b <;> decide
  exact he

/-- But the composition 0 to 1 to 2 is absent from every such patch. -/
theorem three_not_composition_cover : ¬ CompositionSite.FamilyCovers
    (Set.univ : Set (Fin 3)) (omitOne 3) := by
  intro h
  let q : CompositionSite.Triangle (Fin 3) :=
    ⟨0, 1, 2, homOfLE (by decide), homOfLE (by decide)⟩
  obtain ⟨i, hi⟩ := h q (Set.subset_univ _)
  have ha := hi q.a_mem
  have hb := hi q.b_mem
  have hc := hi q.c_mem
  fin_cases i
  · exact ha rfl
  · exact hb rfl
  · exact hc rfl

/-- Object and arrow coverage cannot replace composition coverage in this site. -/
theorem three_sieve_not_covering :
    Sieve.ofArrows (omitOne 3) (fun i => homOfLE (Set.subset_univ (omitOne 3 i))) ∉
      CompositionSite.topology (Fin 3) Set.univ := by
  rw [CompositionSite.ofArrows_covering_iff]
  exact three_not_composition_cover

end CompositionSiteExamples
end KomorebiSpace
