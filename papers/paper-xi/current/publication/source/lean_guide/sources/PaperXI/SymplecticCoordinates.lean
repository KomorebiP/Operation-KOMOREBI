import PaperXI.SymplecticSplit
import PaperXI.SymplecticAssembly
import PaperXI.DyadicDimension

/-! Symplectic coordinates constructed from alternation and nondegeneracy,
by strong induction on the dimension. -/
set_option autoImplicit false
noncomputable section
namespace PaperXI.SymplecticCoordinates
open scoped BigOperators Classical
open PaperXI.Dyadic PaperXI.DyadicCoordinates

variable {V : Type*} [AddCommGroup V] [Module F2 V] [FiniteDimensional F2 V]

/-- Every finite-dimensional alternating left-nondegenerate F2-form admits
actual form-preserving coordinates in finitely many hyperbolic planes. -/
theorem exists_coordinates (b : V →ₗ[F2] V →ₗ[F2] F2)
    (ha : ∀ x, b x x = 0) (hn : ∀ x, (∀ y, b x y = 0) → x = 0) :
    ∃ r : ℕ, ∃ e : V ≃ₗ[F2] (Fin r → F2 × F2),
      ∀ x y, b x y = symplectic (e x) (e y) := by
  suffices ∀ n, Module.finrank F2 V = n →
      ∃ r : ℕ, ∃ e : V ≃ₗ[F2] (Fin r → F2 × F2),
        ∀ x y, b x y = symplectic (e x) (e y) by
    exact this _ rfl
  intro n hdim
  induction n using Nat.strong_induction_on generalizing V with
  | h n ih =>
    by_cases hz : n = 0
    · have hzero : Module.finrank F2 V = 0 := hdim.trans hz
      let : Subsingleton V := (Module.finrank_zero_iff (R := F2) (M := V)).mp hzero
      refine ⟨0, LinearEquiv.ofSubsingleton (R := F2) V (Fin 0 → F2 × F2), ?_⟩
      intro x y
      have hx : x = 0 := Subsingleton.elim _ _
      simp [hx, symplectic_apply]
    · let : Nontrivial V := (Module.finrank_pos_iff (R := F2) (M := V)).mp (by omega)
      obtain ⟨W, e, he, haW, hnW, hW⟩ :=
        PaperXI.SymplecticSplit.exists_split b ha hn
      obtain ⟨r, f, hf⟩ := ih (Module.finrank F2 W) (by omega)
        (b.compl₁₂ W.subtype W.subtype) haW hnW rfl
      refine ⟨r + 1, PaperXI.SymplecticAssembly.assemble r e f, ?_⟩
      exact PaperXI.SymplecticAssembly.assemble_form r b
        (b.compl₁₂ W.subtype W.subtype) e f he hf

/-- The chosen coordinate count is exactly half the dimension. -/
theorem exists_coordinates_dimension (b : V →ₗ[F2] V →ₗ[F2] F2)
    (ha : ∀ x, b x x = 0) (hn : ∀ x, (∀ y, b x y = 0) → x = 0) :
    ∃ r : ℕ, ∃ e : V ≃ₗ[F2] (Fin r → F2 × F2),
      (∀ x y, b x y = symplectic (e x) (e y)) ∧
      Module.finrank F2 V = 2 * r := by
  obtain ⟨r, e, he⟩ := exists_coordinates b ha hn
  refine ⟨r, e, he, ?_⟩
  simpa using PaperXI.DyadicDimension.finrank_eq_twice_card e

theorem even_finrank (b : V →ₗ[F2] V →ₗ[F2] F2)
    (ha : ∀ x, b x x = 0) (hn : ∀ x, (∀ y, b x y = 0) → x = 0) :
    Even (Module.finrank F2 V) := by
  obtain ⟨r, _, _, hr⟩ := exists_coordinates_dimension b ha hn
  exact ⟨r, by omega⟩

/-- Coordinates with the canonical half-dimension index. -/
theorem exists_half_coordinates (b : V →ₗ[F2] V →ₗ[F2] F2)
    (ha : ∀ x, b x x = 0) (hn : ∀ x, (∀ y, b x y = 0) → x = 0) :
    ∃ e : V ≃ₗ[F2] (Fin (Module.finrank F2 V / 2) → F2 × F2),
      ∀ x y, b x y = symplectic (e x) (e y) := by
  obtain ⟨r, e, he, hr⟩ := exists_coordinates_dimension b ha hn
  have h : r = Module.finrank F2 V / 2 := by omega
  subst r
  exact ⟨e, he⟩

end PaperXI.SymplecticCoordinates
