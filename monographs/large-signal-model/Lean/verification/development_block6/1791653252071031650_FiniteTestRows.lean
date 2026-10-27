import KomorebiLSM.TestCones

/-! Finite half-space representations of test levels. The construction proceeds
by adjoining the pullbacks of the current rows under every symbol. -/
set_option autoImplicit false
namespace Komorebi.LSM.TestDomains
open scoped BigOperators
variable {E S : Type*} [AddCommGroup E] [Module ℝ E] [Fintype S]

/-- Every finite test level is cut out by a finite set of linear half-spaces. -/
theorem finite_test_halfspaces (B : S → E →ₗ[ℝ] E) (l : E →ₗ[ℝ] ℝ) (h : ℕ) :
    ∃ rows : Finset (E →ₗ[ℝ] ℝ), testLevel B l h = {x | ∀ r ∈ rows, 0 ≤ r x} := by
  classical
  induction h with
  | zero => exact ⟨{l},by simp [testLevel_zero]⟩
  | succ h ih =>
    obtain ⟨rows,he⟩ := ih
    let next : Finset (E →ₗ[ℝ] ℝ) := rows ∪ Finset.univ.biUnion
      (fun s => rows.image (fun r => r.comp (B s)))
    refine ⟨next, ?_⟩
    rw [testLevel_succ,he]
    ext x
    simp only [Set.mem_inter_iff,Set.mem_ofPred_eq,Set.mem_iInter,Set.mem_preimage]
    constructor
    · rintro ⟨hx,hs⟩ r hr
      rcases Finset.mem_union.mp hr with hr|hr
      · exact hx r hr
      · obtain ⟨s,_,hr⟩ := Finset.mem_biUnion.mp hr
        obtain ⟨q,hq,rfl⟩ := Finset.mem_image.mp hr
        exact hs s q hq
    · intro hx
      constructor
      · intro r hr
        exact hx r (Finset.mem_union.mpr (Or.inl hr))
      · intro s r hr
        exact hx (r.comp (B s)) (Finset.mem_union.mpr (Or.inr
          (Finset.mem_biUnion.mpr ⟨s,Finset.mem_univ s,
            Finset.mem_image.mpr ⟨r,hr,rfl⟩⟩)))

/-- Equality of adjacent test levels yields finite constraints for every future. -/
theorem finite_stopping_certificate (B : S → E →ₗ[ℝ] E) (l : E →ₗ[ℝ] ℝ)
    (h : ℕ) (he : testLevel B l (h+1) = testLevel B l h) :
    ∃ rows : Finset (E →ₗ[ℝ] ℝ), allTests B l = {x | ∀ r ∈ rows, 0 ≤ r x} := by
  rw [← testLevel_stopping B l h he]
  exact finite_test_halfspaces B l h

end Komorebi.LSM.TestDomains
