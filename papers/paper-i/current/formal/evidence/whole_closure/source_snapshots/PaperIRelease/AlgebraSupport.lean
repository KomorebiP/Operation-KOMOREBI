import KomorebiVerification.PacketNaturalityCompletion

set_option autoImplicit false
set_option maxHeartbeats 2000000

namespace Komorebi.PaperIRelease
open Komorebi.Foundation
open Komorebi.PacketNaturalityCompletion.FullBlocks

universe u v w
variable {K : Type u} [Field K]
variable {X : Type v} [AddCommGroup X] [Module K X]
variable {I : Type w} [Fintype I]

/-- Relation arguments are source first and target second. -/
def OperatorSupported (P : LinearProjectorFamily K X I)
    (rel : I → I → Prop) (T : Module.End K X) : Prop :=
  BlocksSupported P rel (restrictBlocks P T)

/-- The range-restricted and ambient formulations of zero transfer agree. -/
theorem restricted_block_zero_iff
    (P : LinearProjectorFamily K X I) (T : Module.End K X) (b a : I) :
    restrictBlocks P T b a = 0 ↔ transferBlock P P T b a = 0 := by
  constructor
  · intro h
    ext x
    have hh := LinearMap.congr_fun h (packetProjection P a x)
    exact congrArg Subtype.val hh
  · intro h
    ext x
    have hh := LinearMap.congr_fun h (x : X)
    change P.proj b (T (x : X)) = 0
    have hx : P.proj a (x : X) = x := by
      rcases x.property with ⟨y, hy⟩
      rw [← hy]
      exact P.idempotent a y
    simpa only [transferBlock, LinearMap.comp_apply, LinearMap.zero_apply, hx] using hh

/-- Exact correspondence with the support space printed in Paper I. -/
theorem operatorSupported_iff_ambient
    (P : LinearProjectorFamily K X I) (rel : I → I → Prop) (T : Module.End K X) :
    OperatorSupported P rel T ↔ ∀ b a, ¬ rel a b → transferBlock P P T b a = 0 := by
  constructor
  · intro h b a hab
    exact (restricted_block_zero_iff P T b a).mp (h b a hab)
  · intro h b a hab
    exact (restricted_block_zero_iff P T b a).mpr (h b a hab)

variable [DecidableEq I]

/-- Ambient operators with a prescribed zero pattern form a linear subspace. -/
def supportSubmodule (P : LinearProjectorFamily K X I) (rel : I → I → Prop) :
    Submodule K (Module.End K X) where
  carrier := {T | OperatorSupported P rel T}
  zero_mem' := by intro b a hab; ext x; simp [restrictBlocks, packetProjection, packetInclusion]
  add_mem' := by
    intro S T hS hT b a hab
    have h := (restrictBlocksLinear P).map_add S T
    have hh := congrFun (congrFun h b) a
    change restrictBlocks P (S + T) b a = restrictBlocks P S b a + restrictBlocks P T b a at hh
    change restrictBlocks P (S + T) b a = 0
    rw [hh, hS b a hab, hT b a hab]
    exact add_zero _
  smul_mem' := by
    intro c T hT b a hab
    have h := (restrictBlocksLinear P).map_smul c T
    have hh := congrFun (congrFun h b) a
    change restrictBlocks P (c • T) b a = c • restrictBlocks P T b a at hh
    change restrictBlocks P (c • T) b a = 0
    rw [hh, hT b a hab]
    exact smul_zero _

/-- Ambient multiplication closure is exactly block multiplication closure. -/
theorem support_mul_closed_iff
    (P : LinearProjectorFamily K X I) (rel : I → I → Prop) :
    (∀ S T : Module.End K X, OperatorSupported P rel S → OperatorSupported P rel T →
      OperatorSupported P rel (S * T)) ↔ BlockMulClosed P rel := by
  constructor
  · intro h B C hB hC
    obtain ⟨S, rfl⟩ := restrictBlocks_surjective P B
    obtain ⟨T, rfl⟩ := restrictBlocks_surjective P C
    have hh := h S T hB hC
    change BlocksSupported P rel (restrictBlocks P (S.comp T)) at hh
    rw [restrictBlocks_comp] at hh
    exact hh
  · intro h S T hS hT
    change BlocksSupported P rel (restrictBlocks P (S.comp T))
    rw [restrictBlocks_comp]
    exact h _ _ hS hT

/-- The support space is a unital subalgebra for every reflexive transitive pattern. -/
def supportSubalgebra (P : LinearProjectorFamily K X I) (rel : I → I → Prop)
    (hrefl : ∀ a, rel a a) (htrans : ∀ a c b, rel a c → rel c b → rel a b) :
    Subalgebra K (Module.End K X) where
  carrier := {T | OperatorSupported P rel T}
  zero_mem' := (supportSubmodule P rel).zero_mem
  add_mem' := fun hS hT => (supportSubmodule P rel).add_mem hS hT
  mul_mem' := fun hS hT =>
    (support_mul_closed_iff P rel).mpr (blockMulClosed_of_transitive P rel htrans) _ _ hS hT
  algebraMap_mem' c := by
    intro b a hab
    have hba : b ≠ a := fun h => by subst b; exact hab (hrefl a)
    ext x
    change P.proj b (c • (x : X)) = 0
    rw [map_smul]
    have hx : P.proj b (x : X) = 0 := by
      rcases x.property with ⟨y, hy⟩
      rw [← hy]
      exact P.orthogonal hba y
    rw [hx, smul_zero]

/-- Both hard converses are transported back to the ambient operator space. -/
theorem support_pattern_algebra_criterion
    (P : LinearProjectorFamily K X I)
    [∀ i, Nontrivial (LinearMap.range (P.proj i))] (rel : I → I → Prop) :
    (∃ A : Subalgebra K (Module.End K X),
      ∀ T, T ∈ A ↔ OperatorSupported P rel T) ↔
    (∀ a, rel a a) ∧ (∀ a c b, rel a c → rel c b → rel a b) := by
  constructor
  · rintro ⟨A, hA⟩
    refine ⟨(identity_blocks_supported_iff_reflexive P rel).mp ((hA 1).mp A.one_mem), ?_⟩
    apply (blockMulClosed_iff_transitive P rel).mp
    apply (support_mul_closed_iff P rel).mp
    intro S T hS hT
    exact (hA (S*T)).mp (A.mul_mem ((hA S).mpr hS) ((hA T).mpr hT))
  · rintro ⟨hrefl, htrans⟩
    exact ⟨supportSubalgebra P rel hrefl htrans, fun _ => Iff.rfl⟩

end Komorebi.PaperIRelease
