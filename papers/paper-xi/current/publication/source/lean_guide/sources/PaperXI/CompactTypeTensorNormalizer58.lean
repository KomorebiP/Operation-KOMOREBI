import PaperXI.CompactTypeTensor58

/-!
# Lifting a prescribed normalizer intertwiner through the quotient tensor factor

When an actual normalizer automorphism acts trivially on the quotient, its
invertible intertwiner on the prescribed first factor supplies an invertible
intertwiner on the literal compact tensor action. The latter covariance is a
conclusion, not a hypothesis.
-/
set_option autoImplicit false
noncomputable section
namespace PaperXI.CompactTypeTensorNormalizer58

open Representation
open scoped TensorProduct

variable {J Q W U : Type*} [Group J] [Group Q]
variable [AddCommGroup W] [Module ℂ W] [AddCommGroup U] [Module ℂ U]
variable (q : J →* Q) (κ : Representation ℂ J W) (σ : Representation ℂ Q U)
variable (a : J ≃* J) (hq : ∀ j, q (a j) = q j)
variable (A : W ≃ₗ[ℂ] W)
variable (hA : ∀ j w, A (κ j w) = κ (a j) (A w))

/-- The invertible operator on the exact tensor space is constructed from A. -/
def tensorOperator : W ⊗[ℂ] U ≃ₗ[ℂ] W ⊗[ℂ] U :=
  TensorProduct.congr A (LinearEquiv.refl ℂ U)

@[simp] theorem tensorOperator_tmul (w : W) (u : U) :
    tensorOperator (U := U) A (w ⊗ₜ[ℂ] u) = A w ⊗ₜ[ℂ] u := rfl

include hq hA in
/-- Quotient-triviality and first-factor covariance imply whole-type covariance. -/
theorem tensorOperator_covariance (j : J) (x : W ⊗[ℂ] U) :
    tensorOperator A (CompactTypeTensor58.action q κ σ j x) =
      CompactTypeTensor58.action q κ σ (a j) (tensorOperator A x) := by
  induction x using TensorProduct.induction_on with
  | zero => simp
  | add x y hx hy => simp only [map_add, hx, hy]
  | tmul w u => simp [CompactTypeTensor58.action, hA, hq]

/-- The actual equivalent actions, with the specified tensor normalizer operator. -/
def normalizerEquiv : Representation.Equiv (CompactTypeTensor58.action q κ σ)
    ((CompactTypeTensor58.action q κ σ).comp a.toMonoidHom) :=
  Representation.Equiv.mk (tensorOperator A) (by
    intro j
    apply LinearMap.ext
    intro x
    exact tensorOperator_covariance q κ σ a hq A hA j x)

@[simp] theorem normalizerEquiv_linear :
    (normalizerEquiv q κ σ a hq A hA).toLinearEquiv = tensorOperator A := rfl

end PaperXI.CompactTypeTensorNormalizer58
