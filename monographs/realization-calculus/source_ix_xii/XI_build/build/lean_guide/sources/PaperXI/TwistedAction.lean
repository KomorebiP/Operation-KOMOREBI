import PaperXI.TwistedAlgebra

/-! Universal extension of actual projective operators to an action of the
constructed twisted group algebra. -/
set_option autoImplicit false
noncomputable section
namespace PaperXI.TwistedAction

open CocycleCommutator Module
variable {A V : Type*} [CommGroup A] [Fintype A]
variable [AddCommGroup V] [Module ℂ V]

/-- The canonical linear extension of a family of operators along the actual
basis of the constructed twisted algebra. -/
def linearExtension (c : Cocycle A ℂˣ) (hc : Normalized c)
    (T : A → Module.End ℂ V) : TwistedAlgebra.Algebra c hc →ₗ[ℂ] Module.End ℂ V :=
  (TwistedAlgebra.basis c hc).constr ℂ T

@[simp] theorem linearExtension_basis (c : Cocycle A ℂˣ) (hc : Normalized c)
    (T : A → Module.End ℂ V) (a : A) :
    linearExtension c hc T (TwistedAlgebra.basis c hc a) = T a :=
  (TwistedAlgebra.basis c hc).constr_basis ℂ T a

theorem linearExtension_one (c : Cocycle A ℂˣ) (hc : Normalized c)
    (T : A → Module.End ℂ V) (hOne : T 1 = 1) :
    linearExtension c hc T 1 = 1 := by
  rw [← TwistedAlgebra.basis_one c hc, linearExtension_basis, hOne]

theorem linearExtension_mul (c : Cocycle A ℂˣ) (hc : Normalized c)
    (T : A → Module.End ℂ V)
    (hMul : ∀ a b, T a * T b = (c.coeff a b : ℂ) • T (a * b))
    (x y : TwistedAlgebra.Algebra c hc) :
    linearExtension c hc T (x * y) = linearExtension c hc T x * linearExtension c hc T y := by
  classical
  conv_lhs => rw [← (TwistedAlgebra.basis c hc).sum_repr x,
    ← (TwistedAlgebra.basis c hc).sum_repr y]
  conv_rhs => rw [← (TwistedAlgebra.basis c hc).sum_repr x,
    ← (TwistedAlgebra.basis c hc).sum_repr y]
  simp only [Finset.sum_mul, Finset.mul_sum, map_sum, map_smul, smul_mul_assoc,
    mul_smul_comm, TwistedAlgebra.basis_mul, linearExtension_basis, hMul]

/-- Actual algebra action extending projective operators with the prescribed
normalized cocycle. No action of the algebra is assumed in the inputs. -/
def action (c : Cocycle A ℂˣ) (hc : Normalized c)
    (T : A → Module.End ℂ V) (hOne : T 1 = 1)
    (hMul : ∀ a b, T a * T b = (c.coeff a b : ℂ) • T (a * b)) :
    TwistedAlgebra.Algebra c hc →ₐ[ℂ] Module.End ℂ V :=
  AlgHom.ofLinearMap (linearExtension c hc T)
    (linearExtension_one c hc T hOne) (linearExtension_mul c hc T hMul)

@[simp] theorem action_basis (c : Cocycle A ℂˣ) (hc : Normalized c)
    (T : A → Module.End ℂ V) (hOne : T 1 = 1)
    (hMul : ∀ a b, T a * T b = (c.coeff a b : ℂ) • T (a * b)) (a : A) :
    action c hc T hOne hMul (TwistedAlgebra.basis c hc a) = T a :=
  linearExtension_basis c hc T a

/-- An algebra action is uniquely determined by its prescribed basis operators. -/
theorem action_unique (c : Cocycle A ℂˣ) (hc : Normalized c)
    (T : A → Module.End ℂ V) (hOne : T 1 = 1)
    (hMul : ∀ a b, T a * T b = (c.coeff a b : ℂ) • T (a * b))
    (F : TwistedAlgebra.Algebra c hc →ₐ[ℂ] Module.End ℂ V)
    (hF : ∀ a, F (TwistedAlgebra.basis c hc a) = T a) :
    F = action c hc T hOne hMul := by
  apply AlgHom.toLinearMap_injective
  apply (TwistedAlgebra.basis c hc).ext
  intro a
  exact (hF a).trans (action_basis c hc T hOne hMul a).symm

/-- The complete universal action property of the constructed twisted algebra. -/
theorem existsUnique_action (c : Cocycle A ℂˣ) (hc : Normalized c)
    (T : A → Module.End ℂ V) (hOne : T 1 = 1)
    (hMul : ∀ a b, T a * T b = (c.coeff a b : ℂ) • T (a * b)) :
    ∃! F : TwistedAlgebra.Algebra c hc →ₐ[ℂ] Module.End ℂ V,
      ∀ a, F (TwistedAlgebra.basis c hc a) = T a := by
  refine ⟨action c hc T hOne hMul, action_basis c hc T hOne hMul, ?_⟩
  intro F hF
  exact action_unique c hc T hOne hMul F hF

end PaperXI.TwistedAction
