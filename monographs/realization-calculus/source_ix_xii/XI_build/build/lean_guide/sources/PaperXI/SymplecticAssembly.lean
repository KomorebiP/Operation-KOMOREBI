import PaperXI.DyadicCoordinates
import Mathlib.LinearAlgebra.Dimension.Finrank

/-! Adding one hyperbolic plane to an existing symplectic coordinate system. -/
set_option autoImplicit false
noncomputable section
namespace PaperXI.SymplecticAssembly
open scoped BigOperators Classical
open PaperXI.Dyadic PaperXI.DyadicCoordinates

def prepend (r : ℕ) : ((F2 × F2) × (Fin r → F2 × F2)) ≃ₗ[F2]
    (Fin (r + 1) → F2 × F2) where
  toFun x := Fin.cons x.1 x.2
  invFun x := (x 0, fun i => x i.succ)
  left_inv x := by rfl
  right_inv x := by
    funext i
    refine Fin.cases ?_ (fun j => ?_) i <;> simp
  map_add' x y := by
    funext i
    refine Fin.cases ?_ (fun j => ?_) i <;> simp
  map_smul' a x := by
    funext i
    refine Fin.cases ?_ (fun j => ?_) i <;> simp

theorem prepend_form (r : ℕ) (x y : (F2 × F2) × (Fin r → F2 × F2)) :
    symplectic (prepend r x) (prepend r y) =
      x.1.1 * y.1.2 + x.1.2 * y.1.1 + symplectic x.2 y.2 := by
  change symplectic (Fin.cons x.1 x.2) (Fin.cons y.1 y.2) = _
  simp [symplectic_apply, Fin.sum_univ_succ]

variable {V W : Type*} [AddCommGroup V] [Module F2 V]
  [AddCommGroup W] [Module F2 W]

def assemble (r : ℕ) (e : V ≃ₗ[F2] ((F2 × F2) × W))
    (f : W ≃ₗ[F2] (Fin r → F2 × F2)) :
    V ≃ₗ[F2] (Fin (r + 1) → F2 × F2) :=
  e.trans (((LinearEquiv.refl F2 (F2 × F2)).prodCongr f).trans (prepend r))

theorem assemble_form (r : ℕ) (b : V →ₗ[F2] V →ₗ[F2] F2)
    (c : W →ₗ[F2] W →ₗ[F2] F2)
    (e : V ≃ₗ[F2] ((F2 × F2) × W)) (f : W ≃ₗ[F2] (Fin r → F2 × F2))
    (he : ∀ x y, b x y = (e x).1.1 * (e y).1.2 +
      (e x).1.2 * (e y).1.1 + c (e x).2 (e y).2)
    (hf : ∀ x y, c x y = symplectic (f x) (f y)) (x y : V) :
    b x y = symplectic (assemble r e f x) (assemble r e f y) := by
  change b x y = symplectic (prepend r ((e x).1, f (e x).2))
    (prepend r ((e y).1, f (e y).2))
  rw [prepend_form, he, hf]

end PaperXI.SymplecticAssembly
