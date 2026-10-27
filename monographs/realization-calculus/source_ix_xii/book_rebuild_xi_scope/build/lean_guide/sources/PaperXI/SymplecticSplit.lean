import PaperXI.DyadicGauss
import Mathlib.LinearAlgebra.FiniteDimensional.Lemmas
import Mathlib.LinearAlgebra.Dimension.Constructions
import Mathlib.Algebra.CharP.Two

/-! A constructive hyperbolic-plane splitting of a nondegenerate alternating
form over F₂. The complement and both directions of the coordinate map are
built explicitly from one hyperbolic pair. -/
set_option autoImplicit false
noncomputable section
namespace PaperXI.SymplecticSplit
open PaperXI.Dyadic

variable {V : Type*} [AddCommGroup V] [Module F2 V]

/-- In characteristic two, an alternating bilinear form is symmetric. -/
theorem alternating_symmetric (b : V →ₗ[F2] V →ₗ[F2] F2)
    (ha : ∀ x, b x x = 0) (x y : V) : b x y = b y x := by
  have h := ha (x + y)
  simp only [map_add, LinearMap.add_apply, ha, zero_add, add_zero] at h
  exact ((eq_neg_of_add_eq_zero_left h).trans (CharTwo.neg_eq _)).symm

/-- Every nonzero nondegenerate alternating space contains a hyperbolic pair. -/
theorem exists_pair [Nontrivial V] (b : V →ₗ[F2] V →ₗ[F2] F2)
    (hn : ∀ x, (∀ y, b x y = 0) → x = 0) : ∃ u v, b u v = 1 := by
  obtain ⟨u, hu⟩ := exists_ne (0 : V)
  have h : ∃ v, b u v ≠ 0 := by
    by_contra! h
    exact hu (hn u h)
  obtain ⟨v, hv⟩ := h
  refine ⟨u, (b u v)⁻¹ • v, ?_⟩
  simp [hv]

/-- A hyperbolic pair supplies an actual product decomposition. -/
theorem split_of_pair [FiniteDimensional F2 V]
    (b : V →ₗ[F2] V →ₗ[F2] F2) (ha : ∀ x, b x x = 0)
    (hn : ∀ x, (∀ y, b x y = 0) → x = 0)
    (u v : V) (huv : b u v = 1) :
    ∃ W : Submodule F2 V, ∃ e : V ≃ₗ[F2] ((F2 × F2) × W),
      (∀ x y, b x y = (e x).1.1 * (e y).1.2 +
        (e x).1.2 * (e y).1.1 +
        (b.compl₁₂ W.subtype W.subtype) (e x).2 (e y).2) ∧
      (∀ w, (b.compl₁₂ W.subtype W.subtype) w w = 0) ∧
      (∀ w, (∀ z, (b.compl₁₂ W.subtype W.subtype) w z = 0) → w = 0) ∧
      Module.finrank F2 W < Module.finrank F2 V := by
  have hvu : b v u = 1 := (alternating_symmetric b ha v u).trans huv
  let W : Submodule F2 V := (b u).ker ⊓ (b v).ker
  let r : V →ₗ[F2] V := LinearMap.id - (b v).smulRight u - (b u).smulRight v
  have hr (x : V) : r x = x - (b v x) • u - (b u x) • v := rfl
  have hr_mem (x : V) : r x ∈ W := by
    change b u (r x) = 0 ∧ b v (r x) = 0
    simp [hr, huv, hvu, ha]
  have huW (w : W) : b u w = 0 := w.property.1
  have hvW (w : W) : b v w = 0 := w.property.2
  have hWu (w : W) : b w u = 0 := (alternating_symmetric b ha w u).trans (huW w)
  have hWv (w : W) : b w v = 0 := (alternating_symmetric b ha w v).trans (hvW w)
  let e : V ≃ₗ[F2] ((F2 × F2) × W) :=
    { toFun := fun x => ((b v x, b u x), ⟨r x, hr_mem x⟩)
      invFun := fun z => z.1.1 • u + z.1.2 • v + z.2
      left_inv := by
        intro x
        dsimp
        rw [hr]
        abel
      right_inv := by
        rintro ⟨⟨a, d⟩, w⟩
        apply Prod.ext
        · apply Prod.ext <;> simp [ha, huv, hvu, huW, hvW]
        · apply Subtype.ext
          dsimp
          rw [hr]
          simp [ha, huv, hvu, huW, hvW]
          abel
      map_add' := by
        intro x y
        apply Prod.ext
        · simp
        · apply Subtype.ext
          exact r.map_add x y
      map_smul' := by
        intro a x
        apply Prod.ext
        · simp
        · apply Subtype.ext
          exact r.map_smul a x }
  have hinv (z : (F2 × F2) × W) : e.symm z = z.1.1 • u + z.1.2 • v + z.2 := rfl
  have hform (x y : V) : b x y = (e x).1.1 * (e y).1.2 +
        (e x).1.2 * (e y).1.1 +
        (b.compl₁₂ W.subtype W.subtype) (e x).2 (e y).2 := by
    obtain ⟨s, rfl⟩ := e.symm.surjective x
    obtain ⟨t, rfl⟩ := e.symm.surjective y
    simp only [LinearEquiv.apply_symm_apply]
    rw [hinv, hinv]
    simp [map_add, map_smul, ha, huv, hvu, huW, hvW, hWu, hWv,
      LinearMap.compl₁₂_apply]
    ring
  refine ⟨W, e, hform, ?_, ?_, ?_⟩
  · intro w
    exact ha w
  · intro w hw
    apply Subtype.ext
    apply hn w
    intro y
    obtain ⟨z, rfl⟩ := e.symm.surjective y
    rw [hinv]
    simpa [hWu, hWv] using hw z.2
  · have hd := e.finrank_eq
    rw [Module.finrank_prod, Module.finrank_prod, Module.finrank_self] at hd
    omega

/-- A nontrivial nondegenerate alternating F₂-space splits as one hyperbolic
plane and a strictly smaller nondegenerate alternating space. -/
theorem exists_split [FiniteDimensional F2 V] [Nontrivial V]
    (b : V →ₗ[F2] V →ₗ[F2] F2) (ha : ∀ x, b x x = 0)
    (hn : ∀ x, (∀ y, b x y = 0) → x = 0) :
    ∃ W : Submodule F2 V, ∃ e : V ≃ₗ[F2] ((F2 × F2) × W),
      (∀ x y, b x y = (e x).1.1 * (e y).1.2 +
        (e x).1.2 * (e y).1.1 +
        (b.compl₁₂ W.subtype W.subtype) (e x).2 (e y).2) ∧
      (∀ w, (b.compl₁₂ W.subtype W.subtype) w w = 0) ∧
      (∀ w, (∀ z, (b.compl₁₂ W.subtype W.subtype) w z = 0) → w = 0) ∧
      Module.finrank F2 W < Module.finrank F2 V := by
  obtain ⟨u, v, huv⟩ := exists_pair b hn
  exact split_of_pair b ha hn u v huv

end PaperXI.SymplecticSplit
