import PaperXI.DyadicBasis
import PaperXI.DyadicTranslation
import Mathlib.LinearAlgebra.BilinearMap

noncomputable section
set_option autoImplicit false
namespace PaperXI.DyadicOrthogonal
open scoped BigOperators Classical
open PaperXI.Dyadic PaperXI.DyadicAffine PaperXI.DyadicCoordinates
variable {V W ι κ : Type*} [AddCommGroup V] [Module F2 V]
  [AddCommGroup W] [Module F2 W] [Fintype ι] [Fintype κ]
variable (b : V →ₗ[F2] V →ₗ[F2] F2) (c : W →ₗ[F2] W →ₗ[F2] F2)

def form : (V × W) →ₗ[F2] (V × W) →ₗ[F2] F2 :=
  b.compl₁₂ (LinearMap.fst F2 V W) (LinearMap.fst F2 V W) +
  c.compl₁₂ (LinearMap.snd F2 V W) (LinearMap.snd F2 V W)

@[simp] theorem form_apply (x y : V × W) : form b c x y = b x.1 y.1 + c x.2 y.2 := rfl

def refinement (q : Refinement b) (r : Refinement c) : Refinement (form b c) where
  value x := q.value x.1 + r.value x.2
  polar x y := by
    simp only [Prod.fst_add, Prod.snd_add, q.polar, r.polar, form_apply]
    ring

variable {b c}

theorem gauss_product [Fintype V] [Fintype W] (q : Refinement b) (r : Refinement c) :
    (∑ x, sign ((refinement b c q r).value x)) =
      (∑ x, sign (q.value x)) * ∑ y, sign (r.value y) := by
  simp only [refinement, sign_add, Fintype.sum_prod_type, Finset.mul_sum,
    Finset.sum_mul]
  exact Finset.sum_comm

def coordinates (e : V ≃ₗ[F2] (ι → F2 × F2))
    (f : W ≃ₗ[F2] (κ → F2 × F2)) :
    (V × W) ≃ₗ[F2] ((ι ⊕ κ) → F2 × F2) :=
  (e.prodCongr f).trans (LinearEquiv.sumArrowLequivProdArrow ι κ F2 (F2 × F2)).symm

theorem coordinates_form (e : V ≃ₗ[F2] (ι → F2 × F2))
    (f : W ≃ₗ[F2] (κ → F2 × F2))
    (he : ∀ x y, b x y = symplectic (e x) (e y))
    (hf : ∀ x y, c x y = symplectic (f x) (f y)) (x y : V × W) :
    form b c x y = symplectic (coordinates e f x) (coordinates e f y) := by
  rw [form_apply, he, hf]
  simp [symplectic_apply, coordinates, Fintype.sum_sum_type]

theorem arf_add [Fintype V] [Fintype W]
    (e : V ≃ₗ[F2] (ι → F2 × F2)) (f : W ≃ₗ[F2] (κ → F2 × F2))
    (he : ∀ x y, b x y = symplectic (e x) (e y))
    (hf : ∀ x y, c x y = symplectic (f x) (f y))
    (q : Refinement b) (r : Refinement c) :
    PaperXI.DyadicBasis.basisArf (coordinates e f) (refinement b c q r) =
      PaperXI.DyadicBasis.basisArf e q + PaperXI.DyadicBasis.basisArf f r := by
  apply sign_injective
  apply mul_right_cancel₀ (pow_ne_zero (Fintype.card ι + Fintype.card κ)
    (by norm_num : (2 : ℤ) ≠ 0))
  have h := PaperXI.DyadicBasis.gauss_sum (coordinates e f) (coordinates_form e f he hf)
    (refinement b c q r)
  rw [gauss_product, PaperXI.DyadicBasis.gauss_sum e he,
    PaperXI.DyadicBasis.gauss_sum f hf] at h
  rw [Fintype.card_sum] at h
  rw [sign_add, pow_add]
  rw [pow_add] at h
  linear_combination -h

theorem normalized_sign_product [Fintype V] [Fintype W]
    (e : V ≃ₗ[F2] (ι → F2 × F2)) (f : W ≃ₗ[F2] (κ → F2 × F2))
    (he : ∀ x y, b x y = symplectic (e x) (e y))
    (hf : ∀ x y, c x y = symplectic (f x) (f y))
    (q : Refinement b) (r : Refinement c) :
    sign (PaperXI.DyadicBasis.basisArf (coordinates e f) (refinement b c q r)) =
      sign (PaperXI.DyadicBasis.basisArf e q) * sign (PaperXI.DyadicBasis.basisArf f r) := by
  rw [arf_add e f he hf, sign_add]

end PaperXI.DyadicOrthogonal
