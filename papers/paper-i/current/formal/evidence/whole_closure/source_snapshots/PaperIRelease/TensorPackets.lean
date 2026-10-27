import KomorebiVerification.PacketNaturalityCompletion
import Mathlib.LinearAlgebra.TensorProduct.Map
import Mathlib.LinearAlgebra.Dual.Defs

set_option autoImplicit false
set_option maxHeartbeats 2000000

namespace Komorebi.PaperIRelease
open Komorebi.Foundation
open TensorProduct

universe u v w v' w'
variable {K : Type u} [Field K]
variable {X : Type v} [AddCommGroup X] [Module K X]
variable {Y : Type w} [AddCommGroup Y] [Module K Y]
variable {I : Type v'} [Fintype I] {J : Type w'} [Fintype J]

/-- The actual tensor maps of the two given families, with all packet laws proved. -/
noncomputable def tensorPackets
    (P : LinearProjectorFamily K X I) (Q : LinearProjectorFamily K Y J) :
    LinearProjectorFamily K (X ⊗[K] Y) (I × J) where
  proj ij := TensorProduct.map (P.proj ij.1) (Q.proj ij.2)
  idempotent ij z := by
    induction z using TensorProduct.induction_on with
    | zero => simp
    | tmul x y => simp only [TensorProduct.map_tmul, P.idempotent, Q.idempotent]
    | add a b ha hb => simp only [map_add, ha, hb]
  orthogonal := by
    intro ij kl h z
    induction z using TensorProduct.induction_on with
    | zero => simp
    | tmul x y =>
      by_cases h1 : ij.1 = kl.1
      · have h2 : ij.2 ≠ kl.2 := fun h2 => h (Prod.ext h1 h2)
        simp only [TensorProduct.map_tmul, Q.orthogonal h2, tmul_zero]
      · simp only [TensorProduct.map_tmul, P.orthogonal h1, zero_tmul]
    | add a b ha hb => simp only [map_add, ha, hb, add_zero]
  complete z := by
    induction z using TensorProduct.induction_on with
    | zero => simp
    | tmul x y =>
      simp only [TensorProduct.map_tmul, Fintype.sum_prod_type]
      simp only [← TensorProduct.tmul_sum, Q.complete]
      rw [← TensorProduct.sum_tmul, P.complete]
    | add a b ha hb => simp only [map_add, Finset.sum_add_distrib, ha, hb]

/-- Tensor packet range equals the span of tensors of the original packet ranges. -/
theorem tensor_packet_range
    (P : LinearProjectorFamily K X I) (Q : LinearProjectorFamily K Y J)
    (i : I) (j : J) :
    LinearMap.range ((tensorPackets P Q).proj (i,j)) =
      Submodule.map₂ (TensorProduct.mk K X Y)
        (LinearMap.range (P.proj i)) (LinearMap.range (Q.proj j)) := by
  exact TensorProduct.range_map _ _

/-- The resulting finite direct-product coordinates use the actual tensor-projector ranges. -/
noncomputable def tensorPacketCoordinates
    (P : LinearProjectorFamily K X I) (Q : LinearProjectorFamily K Y J) :=
  (tensorPackets P Q).exactPacketCoordinates

/-- Transfer blocks of a tensor map factor in the same source/target order. -/
theorem tensor_transfer_blocks
    (P : LinearProjectorFamily K X I) (Q : LinearProjectorFamily K Y J)
    (S : Module.End K X) (T : Module.End K Y) (b a : I) (d c : J) :
    transferBlock (tensorPackets P Q) (tensorPackets P Q)
      (TensorProduct.map S T) (b,d) (a,c) =
    TensorProduct.map (transferBlock P P S b a) (transferBlock Q Q T d c) := by
  simp only [transferBlock, tensorPackets, ← TensorProduct.map_comp]

/-- Algebraic dual projectors; finite dimensionality is not needed for this construction. -/
def dualPackets (P : LinearProjectorFamily K X I) :
    LinearProjectorFamily K (Module.Dual K X) I where
  proj i := (P.proj i).dualMap
  idempotent i φ := by
    ext x
    exact congrArg φ (P.idempotent i x)
  orthogonal := by
    intro i j hij φ
    ext x
    change φ (P.proj j (P.proj i x)) = 0
    rw [P.orthogonal hij.symm, map_zero]
  complete φ := by
    ext x
    simp only [LinearMap.sum_apply, LinearMap.dualMap_apply]
    change (∑ i, φ (P.proj i x)) = φ x
    rw [← map_sum, P.complete]

open Komorebi.PacketNaturalityCompletion.FullBlocks

/-- Inclusion of tensor factors identifies their tensor product with the actual tensor packet. -/
noncomputable def tensorPacketRangeEquiv
    (P : LinearProjectorFamily K X I) (Q : LinearProjectorFamily K Y J) (i : I) (j : J) :
    (LinearMap.range (P.proj i) ⊗[K] LinearMap.range (Q.proj j)) ≃ₗ[K]
      LinearMap.range ((tensorPackets P Q).proj (i,j)) := by
  classical
  let inc := TensorProduct.map (packetInclusion P i) (packetInclusion Q j)
  let pr := TensorProduct.map (packetProjection P i) (packetProjection Q j)
  have hleft : Function.LeftInverse pr inc := by
    intro z
    induction z using TensorProduct.induction_on with
    | zero => simp [inc, pr]
    | tmul x y =>
      simp only [inc, pr, TensorProduct.map_tmul, packetInclusion,
        Submodule.subtype_apply, packetProjection_apply_coe]
    | add a b ha hb => simp only [map_add, ha, hb]
  have hrange : LinearMap.range inc = LinearMap.range ((tensorPackets P Q).proj (i,j)) := by
    simp only [inc, packetInclusion, tensorPackets, TensorProduct.range_map,
      Submodule.range_subtype]
  exact (LinearEquiv.ofInjective inc hleft.injective).trans (LinearEquiv.ofEq _ _ hrange)

/-- Tensor coordinates with the tensor products of original packet spaces as factors. -/
noncomputable def tensorFactorCoordinates
    (P : LinearProjectorFamily K X I) (Q : LinearProjectorFamily K Y J) :
    (X ⊗[K] Y) ≃ₗ[K] ((ij : I × J) →
      LinearMap.range (P.proj ij.1) ⊗[K] LinearMap.range (Q.proj ij.2)) :=
  (tensorPackets P Q).exactPacketCoordinates.trans
    (LinearEquiv.piCongrRight fun ij => (tensorPacketRangeEquiv P Q ij.1 ij.2).symm)

/-- Restriction identifies the range of the dual projector with the dual of its range. -/
noncomputable def dualPacketRangeEquiv (P : LinearProjectorFamily K X I) (i : I) :
    LinearMap.range ((dualPackets P).proj i) ≃ₗ[K]
      Module.Dual K (LinearMap.range (P.proj i)) where
  toFun φ := (φ : Module.Dual K X).comp (packetInclusion P i)
  invFun ψ := ⟨ψ.comp (packetProjection P i), by
    refine ⟨ψ.comp (packetProjection P i), ?_⟩
    ext x
    change ψ ⟨P.proj i (P.proj i x), _⟩ = ψ ⟨P.proj i x, _⟩
    congr 1
    exact Subtype.ext (P.idempotent i x)⟩
  left_inv φ := by
    apply Subtype.ext
    ext x
    rcases φ.property with ⟨ψ, hψ⟩
    have hfix : (dualPackets P).proj i (φ : Module.Dual K X) = φ := by
      rw [← hψ]
      exact (dualPackets P).idempotent i ψ
    exact congrArg (fun f : Module.Dual K X => f x) hfix
  right_inv ψ := by
    classical
    ext x
    change ψ (packetProjection P i (x : X)) = ψ x
    rw [packetProjection_apply_coe]
  map_add' φ ψ := by ext x; rfl
  map_smul' c φ := by ext x; rfl

/-- Dual coordinates are the product of the duals of the original packet ranges. -/
noncomputable def dualPacketCoordinates (P : LinearProjectorFamily K X I) :
    Module.Dual K X ≃ₗ[K] ((i : I) → Module.Dual K (LinearMap.range (P.proj i))) :=
  (dualPackets P).exactPacketCoordinates.trans
    (LinearEquiv.piCongrRight fun i => dualPacketRangeEquiv P i)

/-- Literal finite-direct-sum form of the tensor packet theorem. -/
noncomputable def tensorPacketDirectSumCoordinates
    (P : LinearProjectorFamily K X I) (Q : LinearProjectorFamily K Y J) :
    (X ⊗[K] Y) ≃ₗ[K] DirectSum (I × J) (fun ij =>
      LinearMap.range (P.proj ij.1) ⊗[K] LinearMap.range (Q.proj ij.2)) := by
  classical
  exact (tensorFactorCoordinates P Q).trans (DirectSum.linearEquivFunOnFintype K _ _).symm

/-- Literal finite-direct-sum form of algebraic dual packet coordinates. -/
noncomputable def dualPacketDirectSumCoordinates (P : LinearProjectorFamily K X I) :
    Module.Dual K X ≃ₗ[K] DirectSum I (fun i => Module.Dual K (LinearMap.range (P.proj i))) := by
  classical
  exact (dualPacketCoordinates P).trans (DirectSum.linearEquivFunOnFintype K _ _).symm

end Komorebi.PaperIRelease
