import PaperX.CarrierSummands
import Mathlib.LinearAlgebra.TensorProduct.Pi

/-! Scalar extension with the diagonal semilinear action.
The action is linear over the fixed coefficient field R and sigma-semilinear
 over B. The finite-copy equivalence is constructed from tensor products. -/
set_option autoImplicit false
noncomputable section
namespace PaperX.SemilinearScalarExtension
open TensorProduct
open PaperX.CarrierSummands
variable {R B G : Type*} [Field R] [Field B] [Algebra R B] [Group G]
variable (σ : G →* (B ≃ₐ[R] B))
variable {V : Type*} [AddCommGroup V] [Module R V]

/-- The diagonal action on the actual scalar extension B tensor_R V. -/
def tensorRep (ρ : Representation R G V) : Representation R G (B ⊗[R] V) where
  toFun g := TensorProduct.map (σ g).toLinearMap (ρ g)
  map_one' := by
    ext b v
    simp
  map_mul' g h := by
    ext b v
    simp

@[simp] theorem tensorRep_tmul (ρ : Representation R G V) (g : G) (b : B) (v : V) :
    tensorRep σ ρ g (b ⊗ₜ[R] v) = σ g b ⊗ₜ[R] ρ g v := rfl

/-- This is semilinearity over B, not B-linearity. -/
theorem tensorRep_semilinear (ρ : Representation R G V) (g : G) (b : B)
    (x : B ⊗[R] V) : tensorRep σ ρ g (b • x) = σ g b • tensorRep σ ρ g x := by
  induction x using TensorProduct.induction_on with
  | zero => simp
  | tmul a v => simp [TensorProduct.smul_tmul', smul_eq_mul, map_mul]
  | add x y hx hy => simp [smul_add, hx, hy]

variable {U : Type*} [AddCommGroup U] [Module R U]

/-- Scalar extension of an actual linear map, linear over B. -/
def extendMap (f : V →ₗ[R] U) : B ⊗[R] V →ₗ[B] B ⊗[R] U :=
  TensorProduct.AlgebraTensorModule.map (LinearMap.id : B →ₗ[B] B) f

@[simp] theorem extendMap_tmul (f : V →ₗ[R] U) (b : B) (v : V) :
    extendMap (B := B) f (b ⊗ₜ[R] v) = b ⊗ₜ[R] f v := rfl

/-- Intertwiners stay intertwiners for the diagonal semilinear action. -/
theorem extendMap_equivariant (ρ : Representation R G V) (ρ' : Representation R G U)
    (f : V →ₗ[R] U) (hf : ∀ g v, f (ρ g v) = ρ' g (f v))
    (g : G) (x : B ⊗[R] V) :
    extendMap (B := B) f (tensorRep σ ρ g x) =
      tensorRep σ ρ' g (extendMap (B := B) f x) := by
  induction x using TensorProduct.induction_on with
  | zero => simp
  | tmul b v => simp [hf]
  | add x y hx hy => simp [hx, hy]

/-- Scalar extension of a comparison isomorphism. -/
def extendEquiv (e : V ≃ₗ[R] U) : B ⊗[R] V ≃ₗ[B] B ⊗[R] U :=
  TensorProduct.AlgebraTensorModule.congr (LinearEquiv.refl B B) e

@[simp] theorem extendEquiv_tmul (e : V ≃ₗ[R] U) (b : B) (v : V) :
    extendEquiv (B := B) e (b ⊗ₜ[R] v) = b ⊗ₜ[R] e v := rfl

theorem extendEquiv_equivariant (ρ : Representation R G V) (ρ' : Representation R G U)
    (e : V ≃ₗ[R] U) (he : ∀ g v, e (ρ g v) = ρ' g (e v))
    (g : G) (x : B ⊗[R] V) :
    extendEquiv (B := B) e (tensorRep σ ρ g x) =
      tensorRep σ ρ' g (extendEquiv (B := B) e x) :=
  extendMap_equivariant σ ρ ρ' e.toLinearMap he g x

variable {I : Type*} [Fintype I]
variable {W : I → Type*} [∀ i, AddCommGroup (W i)] [∀ i, Module R (W i)]

/-- The literal tensor-product finite-copy comparison. No comparison map is supplied. -/
def copiesEquiv (m : I → ℕ) :
    B ⊗[R] Copies W m ≃ₗ[B] Copies (fun i => B ⊗[R] W i) m := by
  classical
  exact (TensorProduct.piRight R B B (fun i => Fin (m i) → W i)).trans
    (LinearEquiv.piCongrRight fun i => TensorProduct.piRight R B B (fun _ : Fin (m i) => W i))

@[simp] theorem copiesEquiv_tmul (m : I → ℕ) (b : B) (x : Copies W m) (i : I)
    (k : Fin (m i)) : copiesEquiv (R := R) (B := B) m (b ⊗ₜ[R] x) i k = b ⊗ₜ[R] x i k := rfl

/-- The constructed tensor/direct-sum equivalence intertwines the actual diagonal action. -/
theorem copiesEquiv_equivariant (ρ : ∀ i, Representation R G (W i)) (m : I → ℕ)
    (g : G) (x : B ⊗[R] Copies W m) :
    copiesEquiv (R := R) (B := B) m (tensorRep σ (copiesRep ρ m) g x) =
      copiesRep (fun i => tensorRep σ (ρ i)) m g (copiesEquiv (R := R) (B := B) m x) := by
  induction x using TensorProduct.induction_on with
  | zero => simp
  | tmul b x => rfl
  | add x y hx hy => simp [hx, hy]

/-- Projection to any selected copy agrees with tensoring the original projection. -/
theorem copiesEquiv_component (m : I → ℕ) (i : I) (k : Fin (m i))
    (x : B ⊗[R] Copies W m) :
    copiesEquiv (R := R) (B := B) m x i k =
      extendMap (B := B) ((LinearMap.proj k : (Fin (m i) → W i) →ₗ[R] W i).comp
        (LinearMap.proj i : Copies W m →ₗ[R] (Fin (m i) → W i))) x := by
  induction x using TensorProduct.induction_on with
  | zero => simp
  | tmul b x => rfl
  | add x y hx hy => simp [hx, hy]

omit [Fintype I] in
/-- Actual selected-copy inclusion remains equivariant after scalar extension. -/
theorem scalar_inclusion_equivariant (ρ : ∀ i, Representation R G (W i))
    {m c : I → ℕ} (h : ∀ i, m i ≤ c i) (g : G) (x : B ⊗[R] Copies W m) :
    extendMap (B := B) (inclusion (R := R) h)
        (tensorRep σ (copiesRep ρ m) g x) =
      tensorRep σ (copiesRep ρ c) g
        (extendMap (B := B) (inclusion (R := R) h) x) :=
  extendMap_equivariant σ (copiesRep ρ m) (copiesRep ρ c) _
    (inclusion_equivariant ρ h) g x

omit [Fintype I] in
/-- The split summand is preserved on the actual tensor product. -/
theorem scalar_selected_split {m c : I → ℕ} (h : ∀ i, m i ≤ c i)
    (x : B ⊗[R] Copies W m) :
    extendMap (B := B) (retraction (R := R) h)
      (extendMap (B := B) (inclusion (R := R) h) x) = x := by
  induction x using TensorProduct.induction_on with
  | zero => simp
  | tmul b x => simp
  | add x y hx hy => simp [hx, hy]

end PaperX.SemilinearScalarExtension
