import PaperXI.RepresentationStability
import Mathlib.LinearAlgebra.Dual.Lemmas
import Mathlib.RepresentationTheory.Invariants

/-! Actual dual representations, invariant spaces and tensor/Hom comparison.
No fixed-space dimension, invariant-space equivalence or dual irreducibility
is supplied as a hypothesis. -/
set_option autoImplicit false
noncomputable section
namespace PaperXI.DualityLinear
open scoped TensorProduct
open Representation
variable {k G V W : Type*} [Field k] [Group G]
variable [AddCommGroup V] [Module k V] [AddCommGroup W] [Module k W]

/-- Restrict an actual equivariant linear equivalence to fixed subspaces. -/
def invariantsEquiv (ρ : Representation k G V) (σ : Representation k G W)
    (e : Representation.Equiv ρ σ) : ρ.invariants ≃ₗ[k] σ.invariants where
  toFun x := ⟨e x, fun g => by
    have h := LinearMap.congr_fun (e.isIntertwining' g) (x : V)
    change e (ρ g x) = σ g (e x) at h
    rw [x.property g] at h
    exact h.symm⟩
  invFun x := ⟨e.symm x, fun g => by
    have h := LinearMap.congr_fun (e.symm.isIntertwining' g) (x : W)
    change e.symm (σ g x) = ρ g (e.symm x) at h
    rw [x.property g] at h
    exact h.symm⟩
  left_inv x := by apply Subtype.ext; exact e.toLinearEquiv.symm_apply_apply x
  right_inv x := by apply Subtype.ext; exact e.toLinearEquiv.apply_symm_apply x
  map_add' x y := by apply Subtype.ext; exact e.map_add x y
  map_smul' c x := by apply Subtype.ext; exact e.map_smul c x

/-- The canonical double-dual equivalence is equivariant. -/
def bidualEquiv [FiniteDimensional k V] (ρ : Representation k G V) :
    Representation.Equiv ρ ρ.dual.dual where
  toLinearEquiv := Module.evalEquiv k V
  isIntertwining' g := by
    ext v f
    simp [Representation.dual_apply, Module.Dual.transpose_apply]

/-- The annihilator in V of a stable dual subspace is stable in V. -/
theorem coannihilator_stable (ρ : Representation k G V)
    (S : Submodule k (Module.Dual k V))
    (hS : PaperXI.RepresentationStability.Stable ρ.dual S) :
    PaperXI.RepresentationStability.Stable ρ S.dualCoannihilator := by
  intro g v hv
  rw [Submodule.mem_dualCoannihilator] at hv ⊢
  intro f hf
  have hh := hv (ρ.dual g⁻¹ f) (hS g⁻¹ f hf)
  simpa [Representation.dual_apply, Module.Dual.transpose_apply] using hh

/-- Finite-dimensional duality preserves irreducibility; proved by annihilators. -/
theorem dual_irreducible [FiniteDimensional k V]
    (ρ : Representation k G V) [Representation.IsIrreducible ρ] :
    Representation.IsIrreducible ρ.dual := by
  let : Nontrivial V := PaperXI.GeneratedIrreducibility.nontrivial_space ρ
  let : Nontrivial (Module.Dual k V) := inferInstance
  apply PaperXI.RepresentationStability.irreducible_of_stable
  intro S hS
  have h := PaperXI.RepresentationStability.eq_bot_or_top ρ S.dualCoannihilator
    (coannihilator_stable ρ S hS)
  have he := Subspace.dualCoannihilator_dualAnnihilator_eq (W := S)
  rcases h with h | h
  · right
    simpa [h] using he.symm
  · left
    simpa [h] using he.symm

/-- Actual V tensor W is Hom(V*,W), with its natural group action. -/
def tensorHomEquiv [FiniteDimensional k V] [FiniteDimensional k W]
    (ρ : Representation k G V) (σ : Representation k G W) :
    Representation.Equiv (ρ.tprod σ) (Representation.linHom ρ.dual σ) where
  toLinearEquiv :=
    (TensorProduct.congr (Module.evalEquiv k V) (LinearEquiv.refl k W)).trans
      (dualTensorHomEquiv (R := k) (M := Module.Dual k V) (N := W))
  isIntertwining' g := by
    ext v w f
    simp [Representation.dual_apply, Module.Dual.transpose_apply]

/-- Fixed tensors correspond linearly to genuine intertwining maps. -/
def fixedTensorHomEquiv [FiniteDimensional k V] [FiniteDimensional k W]
    (ρ : Representation k G V) (σ : Representation k G W) :
    (ρ.tprod σ).invariants ≃ₗ[k] Representation.IntertwiningMap ρ.dual σ :=
  (invariantsEquiv _ _ (tensorHomEquiv ρ σ)).trans
    (Representation.invariantsEquivIntertwiningMap ρ.dual σ)

theorem hom_finrank_eq_tensor_invariants [FiniteDimensional k V] [FiniteDimensional k W]
    (ρ : Representation k G V) (σ : Representation k G W) :
    Module.finrank k (Representation.IntertwiningMap ρ.dual σ) =
      Module.finrank k (ρ.tprod σ).invariants :=
  (fixedTensorHomEquiv ρ σ).finrank_eq.symm

end PaperXI.DualityLinear
