import PaperXII.PresentationComparison

noncomputable section
namespace PaperXII.DeterminantalIdeals
open Matrix
variable {R : Type*} [CommRing R] {m n p q m' : Type*}

/-- Row-coordinate transport of the actual relation submodule. -/
theorem mem_range_submatrix_rows [Fintype n] (A : Matrix m n R) (e : m' ≃ m)
    (v : m' → R) :
    v ∈ (A.submatrix e id).mulVecLin.range ↔ v ∘ e.symm ∈ A.mulVecLin.range := by
  have heq (x : n → R) : (A.submatrix e id) *ᵥ x = (A *ᵥ x) ∘ e := rfl
  constructor
  · rintro ⟨x,hx⟩
    refine ⟨x, ?_⟩
    ext i
    have hi := congrFun hx (e.symm i)
    simpa [Matrix.mulVecLin_apply,heq,Function.comp_def] using hi
  · rintro ⟨x,hx⟩
    refine ⟨x, ?_⟩
    ext i
    have hi := congrFun hx (e i)
    simpa [Matrix.mulVecLin_apply,heq,Function.comp_def] using hi

variable {M : Type*} [AddCommGroup M] [Module R M]

/-- Independence from both the generators and the relations of a finite presentation. -/
theorem presentationIdeal_independent [Fintype m] [Fintype n] [Fintype p] [Fintype q]
    (A : Matrix m n R) (B : Matrix q p R)
    (π : (m → R) →ₗ[R] M) (ρ : (q → R) →ₗ[R] M)
    (hA : Presents A π) (hB : Presents B ρ) (j : ℕ) :
    presentationIdeal A j = presentationIdeal B j := by
  classical
  obtain ⟨c,hc⟩ := Module.projective_lifting_property π ρ hA.surjective
  obtain ⟨d,hd⟩ := Module.projective_lifting_property ρ π hB.surjective
  let C : Matrix m q R := LinearMap.toMatrix' c
  let D : Matrix q m R := LinearMap.toMatrix' d
  have hC : π.comp C.mulVecLin = ρ := by
    simpa only [C, ← Matrix.toLin'_apply', Matrix.toLin'_toMatrix'] using hc
  have hD : ρ.comp D.mulVecLin = π := by
    simpa only [D, ← Matrix.toLin'_apply', Matrix.toLin'_toMatrix'] using hd
  let B' := (augment B D).submatrix (Equiv.sumComm m q) id
  have hkerA := range_augment_eq_ker A π ρ C hA.range_eq_ker hC
  have hkerB := range_augment_eq_ker B ρ π D hB.range_eq_ker hD
  have hrange : (augment A C).mulVecLin.range = B'.mulVecLin.range := by
    ext v
    rw [hkerA]
    change v ∈ (commonMap π ρ).ker ↔
      v ∈ ((augment B D).submatrix (Equiv.sumComm m q) id).mulVecLin.range
    rw [mem_range_submatrix_rows, hkerB]
    change π (v ∘ Sum.inl) + ρ (v ∘ Sum.inr) = 0 ↔
      ρ ((v ∘ (Equiv.sumComm m q).symm) ∘ Sum.inl) +
      π ((v ∘ (Equiv.sumComm m q).symm) ∘ Sum.inr) = 0
    simp [Function.comp_def,add_comm]
  calc
    presentationIdeal A j = presentationIdeal (augment A C) j :=
      (presentationIdeal_augment A C j).symm
    _ = presentationIdeal B' j := minorIdeal_eq_of_range_eq _ _ hrange _
    _ = presentationIdeal (augment B D) j :=
      presentationIdeal_submatrix_equiv _ (Equiv.sumComm m q) (Equiv.refl (p ⊕ m)) j
    _ = presentationIdeal B j := presentationIdeal_augment B D j

end PaperXII.DeterminantalIdeals
