import PaperXII.DeterminantalIdeals

/-! Exact preservation under elementary stabilization of a presentation matrix. -/
noncomputable section
namespace PaperXII.DeterminantalIdeals
open Matrix
variable {R : Type*} [CommRing R] {m n m' n' : Type*}

/-- Reindexing rows or columns does not change the determinantal ideal. -/
theorem minorIdeal_submatrix_equiv (A : Matrix m n R) (e : m' ≃ m) (f : n' ≃ n)
    (k : ℕ) : minorIdeal (A.submatrix e f) k = minorIdeal A k := by
  apply le_antisymm
  · apply (minorIdeal_le_iff _ _ _).2
    intro r c
    exact minor_mem A k (e ∘ r) (f ∘ c)
  · apply (minorIdeal_le_iff _ _ _).2
    intro r c
    simpa only [Matrix.submatrix_submatrix, Function.comp_def, Equiv.apply_symm_apply]
      using minor_mem (A.submatrix e f) k (e.symm ∘ r) (f.symm ∘ c)

theorem det_submatrix_zero_of_not_injective_rows (A : Matrix m n R) {k : ℕ}
    (r : Fin k → m) (c : Fin k → n) (h : ¬ Function.Injective r) :
    (A.submatrix r c).det = 0 := by
  obtain ⟨i,j,hij,hne⟩ := Function.not_injective_iff.mp h
  exact Matrix.det_zero_of_row_eq hne (by ext t; simp [Matrix.submatrix_apply, hij])

theorem det_submatrix_zero_of_not_injective_cols (A : Matrix m n R) {k : ℕ}
    (r : Fin k → m) (c : Fin k → n) (h : ¬ Function.Injective c) :
    (A.submatrix r c).det = 0 := by
  obtain ⟨i,j,hij,hne⟩ := Function.not_injective_iff.mp h
  exact Matrix.det_zero_of_column_eq hne (by intro t; simp [Matrix.submatrix_apply, hij])

/-- Adding one generator together with its defining relation. -/
def stabilize (A : Matrix m n R) : Matrix (Option m) (Option n) R
  | none, none => 1
  | some i, some j => A i j
  | _, _ => 0

@[simp] theorem stabilize_none_none (A : Matrix m n R) : stabilize A none none = 1 := rfl
@[simp] theorem stabilize_none_some (A : Matrix m n R) (j : n) : stabilize A none (some j) = 0 := rfl
@[simp] theorem stabilize_some_none (A : Matrix m n R) (i : m) : stabilize A (some i) none = 0 := rfl
@[simp] theorem stabilize_some_some (A : Matrix m n R) (i : m) (j : n) :
    stabilize A (some i) (some j) = A i j := rfl

private theorem option_factor {α β : Type*} (r : α → Option β) (h : ∀ i, r i ≠ none) :
    ∃ s : α → β, ∀ i, r i = some (s i) := by
  choose s hs using fun i => Option.ne_none_iff_exists'.mp (h i)
  exact ⟨s,hs⟩

/-- Appending an identity corner shifts minor order by exactly one. -/
theorem minorIdeal_stabilize (A : Matrix m n R) (k : ℕ) :
    minorIdeal (stabilize A) (k+1) = minorIdeal A k := by
  classical
  apply le_antisymm
  · apply (minorIdeal_le_iff _ _ _).2
    intro r c
    by_cases hr : Function.Injective r
    · by_cases hc : Function.Injective c
      · by_cases hnone : ∃ i, r i = none
        · obtain ⟨i,hi⟩ := hnone
          rw [Matrix.det_succ_row _ i]
          apply Ideal.sum_mem
          intro j _
          cases hj : c j with
          | some t => simp [Matrix.submatrix_apply, hi, hj]
          | none =>
            obtain ⟨r',hr'⟩ := option_factor (r ∘ i.succAbove) (by
              intro a h
              exact Fin.succAbove_ne i a (hr (h.trans hi.symm)))
            obtain ⟨c',hc'⟩ := option_factor (c ∘ j.succAbove) (by
              intro b h
              exact Fin.succAbove_ne j b (hc (h.trans hj.symm)))
            have hsub : ((stabilize A).submatrix r c).submatrix i.succAbove j.succAbove =
                A.submatrix r' c' := by
              ext a b
              simp only [Matrix.submatrix_apply]
              change stabilize A ((r ∘ i.succAbove) a) ((c ∘ j.succAbove) b) = _
              rw [hr' a, hc' b]
              rfl
            rw [hsub]
            exact Ideal.mul_mem_left _ _ (minor_mem A k r' c')
        · have hrnone : ∀ i, r i ≠ none := by simpa using hnone
          obtain ⟨r',hr'⟩ := option_factor r hrnone
          by_cases hcnone : ∃ j, c j = none
          · obtain ⟨j,hj⟩ := hcnone
            have hz : ((stabilize A).submatrix r c).det = 0 :=
              Matrix.det_eq_zero_of_column_eq_zero j (by intro i; simp [Matrix.submatrix_apply,hr' i,hj])
            rw [hz]
            exact Ideal.zero_mem _
          · obtain ⟨c',hc'⟩ := option_factor c (by simpa using hcnone)
            have hsub : (stabilize A).submatrix r c = A.submatrix r' c' := by
              ext i j
              simp [Matrix.submatrix_apply,hr' i,hc' j]
            rw [hsub]
            exact minorIdeal_succ_le A k (minor_mem A (k+1) r' c')
      · rw [det_submatrix_zero_of_not_injective_cols _ r c hc]
        exact Ideal.zero_mem _
    · rw [det_submatrix_zero_of_not_injective_rows _ r c hr]
      exact Ideal.zero_mem _
  · apply (minorIdeal_le_iff _ _ _).2
    intro r c
    let r' : Fin (k+1) → Option m := Fin.cons none (fun i => some (r i))
    let c' : Fin (k+1) → Option n := Fin.cons none (fun i => some (c i))
    have heq : ((stabilize A).submatrix r' c').det = (A.submatrix r c).det := by
      rw [Matrix.det_succ_row_zero, Fin.sum_univ_succ]
      simp [r',c',Matrix.submatrix_apply,Matrix.submatrix_submatrix,
        Function.comp_def,Fin.succAbove_zero]; rfl
    rw [← heq]
    exact minor_mem (stabilize A) (k+1) r' c'

/-- The usual reversed-index Fitting ideal of a specified presentation matrix. -/
def presentationIdeal [Fintype m] (A : Matrix m n R) (j : ℕ) : Ideal R :=
  minorIdeal A (Fintype.card m - j)

/-- The natural-number boundary is handled explicitly: indices above generator rank give top. -/
theorem presentationIdeal_eq_top [Fintype m] (A : Matrix m n R) {j : ℕ}
    (h : Fintype.card m ≤ j) : presentationIdeal A j = ⊤ := by
  simp [presentationIdeal, Nat.sub_eq_zero_of_le h]

theorem presentationIdeal_stabilize [Fintype m] (A : Matrix m n R) (j : ℕ) :
    presentationIdeal (stabilize A) j = presentationIdeal A j := by
  by_cases h : j ≤ Fintype.card m
  · simp only [presentationIdeal, Fintype.card_option]
    have hn : Fintype.card m + 1 - j = (Fintype.card m - j) + 1 := by omega
    rw [hn, minorIdeal_stabilize]
  · have h₁ : Fintype.card m ≤ j := by omega
    have h₂ : Fintype.card (Option m) ≤ j := by simp only [Fintype.card_option]; omega
    rw [presentationIdeal_eq_top _ h₁, presentationIdeal_eq_top _ h₂]

end PaperXII.DeterminantalIdeals
