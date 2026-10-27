import PaperXII.DeterminantalBlockStabilization
import Mathlib.LinearAlgebra.Matrix.ToLin
import Mathlib.Algebra.Module.Projective

noncomputable section
namespace PaperXII.DeterminantalIdeals
open Matrix
variable {R : Type*} [CommRing R] {m n p q : Type*}

/-- A relation-submodule inclusion constructs a matrix factorization. -/
theorem exists_factor_of_range_le [Fintype n] [Fintype p]
    (U : Matrix m n R) (V : Matrix m p R)
    (hUV : U.mulVecLin.range ≤ V.mulVecLin.range) :
    ∃ C : Matrix p n R, V * C = U := by
  classical
  let f : (n → R) →ₗ[R] V.mulVecLin.range :=
    U.mulVecLin.codRestrict _ (fun x => hUV (LinearMap.mem_range_self _ x))
  have hs : Function.Surjective V.mulVecLin.rangeRestrict := by
    rintro ⟨v,x,hx⟩
    exact ⟨x, Subtype.ext hx⟩
  obtain ⟨g,hg⟩ := Module.projective_lifting_property V.mulVecLin.rangeRestrict f hs
  refine ⟨LinearMap.toMatrix' g, ?_⟩
  apply Matrix.toLin'.injective
  apply LinearMap.ext
  intro x
  ext i
  have hgi := congrArg (fun z : V.mulVecLin.range => z.val i) (LinearMap.congr_fun hg x)
  simpa [Matrix.toLin'_mul, f, Matrix.toLin'_apply'] using hgi

/-- Equality of generated relation submodules gives equality of all minor ideals. -/
theorem minorIdeal_eq_of_range_eq [Fintype n] [Fintype p]
    (A : Matrix m n R) (B : Matrix m p R)
    (h : A.mulVecLin.range = B.mulVecLin.range) (k : ℕ) :
    minorIdeal A k = minorIdeal B k := by
  obtain ⟨C,hC⟩ := exists_factor_of_range_le A B h.le
  obtain ⟨D,hD⟩ := exists_factor_of_range_le B A h.ge
  exact minorIdeal_eq_of_mutual_factorization A B C D hC hD k

/-- The relation matrix after adjoining generators lifted by C. -/
def augment [DecidableEq q] (A : Matrix m n R) (C : Matrix m q R) :
    Matrix (m ⊕ q) (n ⊕ q) R := Matrix.fromBlocks A (-C) 0 1

theorem presentationIdeal_augment [Fintype m] [Fintype q] [DecidableEq q]
    (A : Matrix m n R) (C : Matrix m q R) (j : ℕ) :
    presentationIdeal (augment A C) j = presentationIdeal A j := by
  classical
  let U : Matrix (m ⊕ q) (m ⊕ q) R := Matrix.fromBlocks 1 (-C) 0 1
  let V : Matrix (m ⊕ q) (m ⊕ q) R := Matrix.fromBlocks 1 C 0 1
  have hVU : V * U = 1 := by
    simp [V,U,Matrix.fromBlocks_multiply,← Matrix.fromBlocks_one]
  have hmul : U * stabilizeBlock A q = augment A C := by
    simp [U,stabilizeBlock,augment,Matrix.fromBlocks_multiply]
    ext a b
    simp [Matrix.one_apply]
  rw [← hmul]
  unfold presentationIdeal
  rw [minorIdeal_mul_left_eq U V hVU]
  exact presentationIdeal_stabilizeBlock A q j

variable {M : Type*} [AddCommGroup M] [Module R M]

/-- An exact finite relation matrix with its actual quotient map. -/
structure Presents [Fintype n] (A : Matrix m n R) (π : (m → R) →ₗ[R] M) : Prop where
  surjective : Function.Surjective π
  range_eq_ker : A.mulVecLin.range = π.ker

/-- Add two finite generating families into their common free carrier. -/
def commonMap (π : (m → R) →ₗ[R] M) (ρ : (q → R) →ₗ[R] M) :
    ((m ⊕ q) → R) →ₗ[R] M where
  toFun v := π (v ∘ Sum.inl) + ρ (v ∘ Sum.inr)
  map_add' := by
    intro x y
    change π ((x ∘ Sum.inl) + (y ∘ Sum.inl)) + ρ ((x ∘ Sum.inr) + (y ∘ Sum.inr)) = _
    rw [map_add,map_add]
    abel
  map_smul' := by
    intro a x
    change π (a • (x ∘ Sum.inl)) + ρ (a • (x ∘ Sum.inr)) = _
    rw [map_smul,map_smul,smul_add]
    rfl

theorem range_augment_eq_ker [Fintype n] [Fintype q] [DecidableEq q]
    (A : Matrix m n R) (π : (m → R) →ₗ[R] M) (ρ : (q → R) →ₗ[R] M)
    (C : Matrix m q R) (hA : A.mulVecLin.range = π.ker)
    (hC : π.comp C.mulVecLin = ρ) :
    (augment A C).mulVecLin.range = (commonMap π ρ).ker := by
  classical
  have hπA (x : n → R) : π (A *ᵥ x) = 0 := by
    have hx := LinearMap.mem_range_self A.mulVecLin x
    rw [hA] at hx
    exact hx
  have hπC (x : q → R) : π (C *ᵥ x) = ρ x := LinearMap.congr_fun hC x
  ext v
  constructor
  · rintro ⟨x,rfl⟩
    change (commonMap π ρ) ((augment A C) *ᵥ x) = 0
    rw [augment,Matrix.fromBlocks_mulVec]
    change π (A *ᵥ (x ∘ Sum.inl) + (-C) *ᵥ (x ∘ Sum.inr)) +
      ρ ((0 : Matrix q n R) *ᵥ (x ∘ Sum.inl) + (1 : Matrix q q R) *ᵥ (x ∘ Sum.inr)) = 0
    simp [Matrix.neg_mulVec,hπA,hπC]
  · intro hv
    have hv' : π (v ∘ Sum.inl) + ρ (v ∘ Sum.inr) = 0 := hv
    have hk : v ∘ Sum.inl + C *ᵥ (v ∘ Sum.inr) ∈ A.mulVecLin.range := by
      rw [hA]
      change π (v ∘ Sum.inl + C *ᵥ (v ∘ Sum.inr)) = 0
      simpa [map_add,hπC] using hv'
    obtain ⟨x,hx⟩ := hk
    refine ⟨Sum.elim x (v ∘ Sum.inr), ?_⟩
    change (augment A C) *ᵥ Sum.elim x (v ∘ Sum.inr) = v
    rw [augment,Matrix.fromBlocks_mulVec]
    ext i
    rcases i with i | i
    · have hxi := congrFun hx i
      simp only [Matrix.mulVecLin_apply,Pi.add_apply] at hxi
      simp only [Sum.elim_inl,Function.comp_def,Matrix.neg_mulVec,
        Pi.add_apply,Pi.neg_apply]
      change (A *ᵥ x) i + -(C *ᵥ (v ∘ Sum.inr)) i = v (.inl i)
      rw [hxi]
      abel
    · simp

end PaperXII.DeterminantalIdeals
