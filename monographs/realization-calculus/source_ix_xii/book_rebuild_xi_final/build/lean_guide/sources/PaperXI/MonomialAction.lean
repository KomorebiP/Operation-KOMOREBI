import Mathlib.RepresentationTheory.Basic
import Mathlib.LinearAlgebra.Basis.Defs
import Mathlib.LinearAlgebra.TensorProduct.Basis
import Mathlib.Analysis.Complex.Basic

/-! Actual monomial actions on a supplied basis. The scalar cocycle laws are
proved from an honest representation, then reused to construct orbit actions. -/
set_option autoImplicit false
noncomputable section
namespace PaperXI.MonomialAction

variable {G X V : Type*} [Group G] [AddCommGroup V] [Module ℂ V]
variable (b : Module.Basis X ℂ V) (p : G →* Equiv.Perm X) (c : G → X → ℂˣ)

/-- The actual operator specified on the basis, extended linearly. -/
def operator (g : G) : Module.End ℂ V := b.constr ℂ (fun x => (c g x : ℂ) • b (p g x))

@[simp] theorem operator_basis (g : G) (x : X) :
    operator b p c g (b x) = (c g x : ℂ) • b (p g x) := b.constr_basis ℂ _ x

/-- Honest multiplication on the basis gives an honest representation. -/
def representation (h1 : ∀ x, c 1 x = 1)
    (hm : ∀ g h x, c (g*h) x = c g (p h x) * c h x) : Representation ℂ G V where
  toFun := operator b p c
  map_one' := by
    apply b.ext
    intro x
    simp [h1]
  map_mul' g h := by
    apply b.ext
    intro x
    simp only [operator_basis, Module.End.mul_apply, map_smul, hm, Units.val_mul,
      smul_smul, map_mul, Equiv.Perm.coe_mul]
    rw [mul_comm (c g (p h x) : ℂ) (c h x : ℂ)]
    rfl

@[simp] theorem representation_basis (h1 : ∀ x, c 1 x = 1)
    (hm : ∀ g h x, c (g*h) x = c g (p h x) * c h x) (g : G) (x : X) :
    representation b p c h1 hm g (b x) = (c g x : ℂ) • b (p g x) := operator_basis b p c g x

/-- Scalar cancellation on an actual nonzero basis vector. -/
theorem scalar_injective (x : X) {a d : ℂ} (h : a • b x = d • b x) : a = d := by
  have hv := congrArg (fun v => b.repr v x) h
  simpa using hv

/-- The one law is derived from the supplied honest action. -/
theorem weight_one (ρ : Representation ℂ G V)
    (hρ : ∀ g x, ρ g (b x) = (c g x : ℂ) • b (p g x)) (x : X) : c 1 x = 1 := by
  apply Units.ext
  apply scalar_injective b x
  simpa using (hρ 1 x).symm

/-- The cocycle law is derived from multiplication in the supplied action. -/
theorem weight_mul (ρ : Representation ℂ G V)
    (hρ : ∀ g x, ρ g (b x) = (c g x : ℂ) • b (p g x)) (g h : G) (x : X) :
    c (g*h) x = c g (p h x) * c h x := by
  apply Units.ext
  apply scalar_injective b (p (g*h) x)
  rw [← hρ, map_mul, Module.End.mul_apply, hρ, map_smul, hρ]
  simp [smul_smul, mul_comm]

/-- The reconstructed action is the original action on every vector. -/
theorem representation_eq (ρ : Representation ℂ G V)
    (hρ : ∀ g x, ρ g (b x) = (c g x : ℂ) • b (p g x)) :
    representation b p c (weight_one b p c ρ hρ) (weight_mul b p c ρ hρ) = ρ := by
  apply MonoidHom.ext
  intro g
  apply b.ext
  intro x
  rw [representation_basis]
  exact (hρ g x).symm

variable {Y W : Type*} [AddCommGroup W] [Module ℂ W]

/-- The actual tensor basis carries the product permutation. -/
def tensorPermutation (q : G →* Equiv.Perm Y) : G →* Equiv.Perm (X × Y) where
  toFun g := (p g).prodCongr (q g)
  map_one' := by ext x <;> simp
  map_mul' g h := by ext x <;> simp

/-- The tensor coefficient is a product of the actual factor coefficients. -/
theorem tensor_basis (ρ : Representation ℂ G V) (σ : Representation ℂ G W)
    (d : Module.Basis Y ℂ W) (q : G →* Equiv.Perm Y) (w : G → Y → ℂˣ)
    (hρ : ∀ g x, ρ g (b x) = (c g x : ℂ) • b (p g x))
    (hσ : ∀ g y, σ g (d y) = (w g y : ℂ) • d (q g y)) (g : G) (x : X × Y) :
    (ρ.tprod σ) g ((b.tensorProduct d) x) =
      ((c g x.1 * w g x.2 : ℂˣ) : ℂ) •
        (b.tensorProduct d) (tensorPermutation p q g x) := by
  simp [Representation.tprod, Module.Basis.tensorProduct_apply', hρ, hσ,
    tensorPermutation, TensorProduct.smul_tmul', TensorProduct.tmul_smul, smul_smul, mul_comm]

end PaperXI.MonomialAction
