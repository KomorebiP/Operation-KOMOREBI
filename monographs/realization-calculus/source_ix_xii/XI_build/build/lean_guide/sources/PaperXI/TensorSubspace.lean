import Mathlib.LinearAlgebra.Dimension.Constructions
import Mathlib.LinearAlgebra.FiniteDimensional.Basic
import Mathlib.RingTheory.Flat.Basic

/-! Tensoring a multiplicity subspace with a nonzero finite-dimensional
factor preserves whether it is zero or the whole space. The actual image
is transported through a specified, independently proved tensor equivalence. -/
set_option autoImplicit false
noncomputable section
namespace PaperXI.TensorSubspace
open scoped TensorProduct

variable {k W M X : Type*} [Field k]
variable [AddCommGroup W] [Module k W] [AddCommGroup M] [Module k M]
variable [AddCommGroup X] [Module k X]

/-- The actual tensor image of a subspace through the given equivalence. -/
def image (e : W ⊗[k] M ≃ₗ[k] X) (L : Submodule k M) : Submodule k X :=
  LinearMap.range (e.toLinearMap.comp (L.subtype.lTensor W))

theorem inclusion_injective (L : Submodule k M) :
    Function.Injective (L.subtype.lTensor W) :=
  Module.Flat.lTensor_preserves_injective_linearMap L.subtype L.subtype_injective

theorem map_injective (e : W ⊗[k] M ≃ₗ[k] X) (L : Submodule k M) :
    Function.Injective (e.toLinearMap.comp (L.subtype.lTensor W)) :=
  e.injective.comp (inclusion_injective L)

theorem tmul_mem (e : W ⊗[k] M ≃ₗ[k] X) (L : Submodule k M)
    (w : W) (m : M) (hm : m ∈ L) : e (w ⊗ₜ[k] m) ∈ image e L := by
  exact ⟨w ⊗ₜ[k] (⟨m, hm⟩ : L), by simp⟩

/-- Stability follows from the actual factorwise action on pure tensors. -/
theorem image_stable (e : W ⊗[k] M ≃ₗ[k] X) (L : Submodule k M)
    (P : Module.End k X) (A : Module.End k W) (B : Module.End k M)
    (hL : ∀ m, m ∈ L → B m ∈ L)
    (hP : ∀ w m, P (e (w ⊗ₜ[k] m)) = e (A w ⊗ₜ[k] B m)) :
    ∀ x, x ∈ image e L → P x ∈ image e L := by
  rintro x ⟨t, rfl⟩
  induction t using TensorProduct.induction_on with
  | zero => simp
  | add s t hs ht => simpa using (image e L).add_mem hs ht
  | tmul w m =>
    change P (e (w ⊗ₜ[k] (m : M))) ∈ image e L
    rw [hP]
    exact tmul_mem e L (A w) (B m) (hL m m.property)

theorem finrank_image (e : W ⊗[k] M ≃ₗ[k] X) (L : Submodule k M) :
    Module.finrank k (image e L) = Module.finrank k W * Module.finrank k L := by
  rw [image, LinearMap.finrank_range_of_inj (map_injective e L)]
  exact Module.finrank_tensorProduct

variable [FiniteDimensional k W] [FiniteDimensional k M] [Nontrivial W]

theorem image_eq_bot_iff (e : W ⊗[k] M ≃ₗ[k] X) (L : Submodule k M) :
    image e L = ⊥ ↔ L = ⊥ := by
  let : FiniteDimensional k X := Module.Finite.equiv e
  rw [← Submodule.finrank_eq_zero, finrank_image, ← Submodule.finrank_eq_zero]
  exact mul_eq_zero.trans (or_iff_right (ne_of_gt (Module.finrank_pos (R := k) (M := W))))

theorem image_eq_top_iff (e : W ⊗[k] M ≃ₗ[k] X) (L : Submodule k M) :
    image e L = ⊤ ↔ L = ⊤ := by
  let : FiniteDimensional k X := Module.Finite.equiv e
  have he : Module.finrank k X = Module.finrank k W * Module.finrank k M := by
    rw [← e.finrank_eq, Module.finrank_tensorProduct]
  constructor
  · intro h
    apply Submodule.eq_top_of_finrank_eq
    apply Nat.eq_of_mul_eq_mul_left (Module.finrank_pos (R := k) (M := W))
    have hr := congrArg (fun S : Submodule k X => Module.finrank k S) h
    simpa only [finrank_image, finrank_top, he] using hr
  · rintro rfl
    apply Submodule.eq_top_of_finrank_eq
    rw [finrank_image, finrank_top, he]

end PaperXI.TensorSubspace
