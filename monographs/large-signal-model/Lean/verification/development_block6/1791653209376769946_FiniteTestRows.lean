import KomorebiLSM.TestCones

/-! A finite explicit half-space representation of each finite test level.
The rows can grow with the horizon; finite stopping is not asserted without equality. -/
set_option autoImplicit false
namespace Komorebi.LSM.TestDomains
open scoped BigOperators
variable {E S : Type*} [AddCommGroup E] [Module ℝ E] [Fintype S]

noncomputable def testRows (B : S → E →ₗ[ℝ] E) (l : E →ₗ[ℝ] ℝ) :
    ℕ → Finset (E →ₗ[ℝ] ℝ) := by
  classical
  exact Nat.rec {l} (fun _ rows => rows ∪ Finset.univ.biUnion
    (fun s => rows.image (fun r => r.comp (B s))))

@[simp] theorem testRows_zero (B : S → E →ₗ[ℝ] E) (l : E →ₗ[ℝ] ℝ) :
    testRows B l 0 = {l} := rfl

/-- Recursive row generation is an exact finite half-space description. -/
theorem testLevel_eq_rows (B : S → E →ₗ[ℝ] E) (l : E →ₗ[ℝ] ℝ) (h : ℕ) :
    testLevel B l h = {x | ∀ r ∈ testRows B l h, 0 ≤ r x} := by
  classical
  induction h with
  | zero => simp [testLevel_zero]
  | succ h ih =>
    rw [testLevel_succ,ih]
    ext x
    simp only [Set.mem_inter_iff,Set.mem_ofPred_eq,Set.mem_iInter,Set.mem_preimage]
    constructor
    · rintro ⟨hx,hs⟩ r hr
      change r ∈ testRows B l h ∪ Finset.univ.biUnion
        (fun s => (testRows B l h).image (fun q => q.comp (B s))) at hr
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

/-- If two adjacent finite descriptions agree, these finite rows certify all tests. -/
theorem finite_stopping_certificate (B : S → E →ₗ[ℝ] E) (l : E →ₗ[ℝ] ℝ)
    (h : ℕ) (he : testLevel B l (h+1) = testLevel B l h) :
    allTests B l = {x | ∀ r ∈ testRows B l h, 0 ≤ r x} := by
  rw [← testLevel_stopping B l h he,testLevel_eq_rows]

end Komorebi.LSM.TestDomains
