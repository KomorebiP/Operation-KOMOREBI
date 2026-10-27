import PaperXI.TwistedAction
import PaperXI.TwistedModules
import PaperXI.AlgebraActionModule
import Mathlib.LinearAlgebra.FiniteDimensional.Lemmas

/-! The actual algebra action of an irreducible projective operator family is
an isomorphism when its scalar commutator is nondegenerate. -/
set_option autoImplicit false
set_option backward.isDefEq.respectTransparency false
noncomputable section
namespace PaperXI.TwistedActionEquivalence
open CocycleCommutator AlgebraActionModule

variable {A V : Type*} [CommGroup A] [Fintype A]
variable [AddCommGroup V] [Module ℂ V]
variable (c : Cocycle A ℂˣ) (hc : Normalized c)
variable (T : A → Module.End ℂ V) (hOne : T 1 = 1)
variable (hMul : ∀ a b, T a * T b = (c.coeff a b : ℂ) • T (a * b))

/-- Stability for the actual extended action is equivalent to generator stability. -/
theorem stable_iff (S : Submodule ℂ V) :
    Stable (B := ↥(TwistedAlgebra.Algebra c hc)) (TwistedAction.action c hc T hOne hMul) S ↔
      ∀ a v, v ∈ S → T a v ∈ S := by
  constructor
  · intro h a v hv
    simpa only [TwistedAction.action_basis] using h (TwistedAlgebra.basis c hc a) v hv
  · intro h x v hv
    rw [← (TwistedAlgebra.basis c hc).sum_repr x]
    simp only [map_sum, map_smul, TwistedAction.action_basis,
      LinearMap.sum_apply, LinearMap.smul_apply]
    exact S.sum_mem fun a _ => S.smul_mem _ (h a v hv)

/-- The actual operator irreducibility criterion gives a simple algebra module. -/
theorem simpleModule [Nontrivial V]
    (hIrr : ∀ S : Submodule ℂ V, (∀ a v, v ∈ S → T a v ∈ S) → S = ⊥ ∨ S = ⊤) :
    IsSimpleModule (TwistedAlgebra.Algebra c hc)
      (Space (B := ↥(TwistedAlgebra.Algebra c hc)) (TwistedAction.action c hc T hOne hMul)) := by
  apply (simple_iff (B := ↥(TwistedAlgebra.Algebra c hc)) _).2
  exact ⟨inferInstance, fun S hS => hIrr S ((stable_iff c hc T hOne hMul S).1 hS)⟩

variable (hnd : radical c = ⊥) [Nontrivial V]
variable (hIrr : ∀ S : Submodule ℂ V, (∀ a v, v ∈ S → T a v ∈ S) → S = ⊥ ∨ S = ⊤)

include c hc T hOne hMul hnd hIrr

/-- Finite dimensionality of the actual operator space follows from irreducibility. -/
theorem finiteDimensional : FiniteDimensional ℂ V := by
  let φ := TwistedAction.action c hc T hOne hMul
  let : IsSimpleModule (TwistedAlgebra.Algebra c hc)
      (Space (B := ↥(TwistedAlgebra.Algebra c hc)) φ) := simpleModule c hc T hOne hMul hIrr
  let : FiniteDimensional ℂ (Space (B := ↥(TwistedAlgebra.Algebra c hc)) φ) :=
    TwistedModules.finiteDimensional c hc hnd _
  exact FiniteDimensional.of_injective
    (AlgebraActionModule.equiv (B := ↥(TwistedAlgebra.Algebra c hc)) φ).symm.toLinearMap
    (AlgebraActionModule.equiv (B := ↥(TwistedAlgebra.Algebra c hc)) φ).symm.injective

/-- The square of the actual operator-space dimension equals the group order. -/
theorem finrank_sq : Module.finrank ℂ V ^ 2 = Fintype.card A := by
  let φ := TwistedAction.action c hc T hOne hMul
  let : IsSimpleModule (TwistedAlgebra.Algebra c hc)
      (Space (B := ↥(TwistedAlgebra.Algebra c hc)) φ) := simpleModule c hc T hOne hMul hIrr
  rw [← (AlgebraActionModule.equiv (B := ↥(TwistedAlgebra.Algebra c hc)) φ).finrank_eq]
  exact TwistedModules.finrank_sq c hc hnd _

/-- The source packet dimension, derived for the actual operator space. -/
theorem finrank_sqrt : Module.finrank ℂ V = Nat.sqrt (Fintype.card A) := by
  rw [← finrank_sq c hc T hOne hMul hnd hIrr, Nat.sqrt_eq']

omit hIrr in
/-- Simplicity forces injectivity of this action map. -/
theorem action_injective : Function.Injective (TwistedAction.action c hc T hOne hMul) := by
  let : IsSimpleRing (TwistedAlgebra.Algebra c hc) := TwistedSimple.isSimpleRing c hc hnd
  exact RingHom.injective (R := ↥(TwistedAlgebra.Algebra c hc))
    (TwistedAction.action c hc T hOne hMul).toRingHom

/-- Equal dimensions and injectivity prove surjectivity of this action map. -/
theorem action_surjective : Function.Surjective (TwistedAction.action c hc T hOne hMul) := by
  let : FiniteDimensional ℂ V := finiteDimensional c hc T hOne hMul hnd hIrr
  have hd : Module.finrank ℂ (TwistedAlgebra.Algebra c hc) =
      Module.finrank ℂ (Module.End ℂ V) := by
    rw [TwistedAlgebra.finrank_eq_card, Module.finrank_linearMap, ← pow_two,
      finrank_sq c hc T hOne hMul hnd hIrr]
  let F : (TwistedAlgebra.Algebra c hc) →ₗ[ℂ] Module.End ℂ V :=
    (TwistedAction.action c hc T hOne hMul).toLinearMap
  have hf : Function.Injective F := action_injective c hc T hOne hMul hnd
  change Function.Surjective F
  exact (LinearMap.injective_iff_surjective_of_finrank_eq_finrank
    (K := ℂ) (V := ↥(TwistedAlgebra.Algebra c hc)) (V₂ := Module.End ℂ V)
    hd (f := F)).1 hf

/-- Bijectivity belongs to the literal action homomorphism. -/
theorem action_bijective : Function.Bijective (TwistedAction.action c hc T hOne hMul) :=
  ⟨action_injective c hc T hOne hMul hnd, action_surjective c hc T hOne hMul hnd hIrr⟩

/-- The actual action, bundled as an algebra equivalence. -/
def actionEquiv : TwistedAlgebra.Algebra c hc ≃ₐ[ℂ] Module.End ℂ V :=
  AlgEquiv.ofBijective (TwistedAction.action c hc T hOne hMul)
    (action_bijective c hc T hOne hMul hnd hIrr)

@[simp] theorem actionEquiv_apply (x : TwistedAlgebra.Algebra c hc) :
    actionEquiv c hc T hOne hMul hnd hIrr x = TwistedAction.action c hc T hOne hMul x := rfl

@[simp] theorem actionEquiv_basis (a : A) :
    actionEquiv c hc T hOne hMul hnd hIrr (TwistedAlgebra.basis c hc a) = T a :=
  TwistedAction.action_basis c hc T hOne hMul a

end PaperXI.TwistedActionEquivalence
