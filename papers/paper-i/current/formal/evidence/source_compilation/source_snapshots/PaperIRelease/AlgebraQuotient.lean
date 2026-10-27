import PaperIRelease.AlgebraPreorder
import Mathlib.RingTheory.Ideal.Quotient.Operations

set_option autoImplicit false
set_option linter.unusedSectionVars false
set_option maxHeartbeats 3000000
noncomputable section

namespace Komorebi.PaperIRelease
open Komorebi.Foundation
open Komorebi.PacketNaturalityCompletion.FullBlocks

universe u v w
variable {K : Type u} [Field K]
variable {X : Type v} [AddCommGroup X] [Module K X]
variable {I : Type w} [Fintype I] [DecidableEq I] [PartialOrder I]

/-- Diagonal packets are multiplicative for a partial-order support pattern. -/
theorem restrict_diagonal_mul (P : LinearProjectorFamily K X I)
    (S T : preorderSupportAlgebra P) (i : I) :
    restrictBlocks P (S.1 * T.1) i i =
      (restrictBlocks P S.1 i i).comp (restrictBlocks P T.1 i i) := by
  change restrictBlocks P (S.1.comp T.1) i i = _
  rw [restrictBlocks_comp]
  change (∑ j, (restrictBlocks P S.1 i j).comp (restrictBlocks P T.1 j i)) = _
  rw [Finset.sum_eq_single i]
  · intro j _ hji
    by_cases hij : i ≤ j
    · have hji' : ¬ j ≤ i := fun h => hji (le_antisymm h hij)
      rw [S.property i j hji']
      simp
    · rw [T.property j i hij]
      simp
  · simp

/-- Projection to all diagonal packet endomorphisms is an algebra homomorphism. -/
def diagonalClassHom (P : LinearProjectorFamily K X I) :
    preorderSupportAlgebra P →ₐ[K] ((i : I) → Module.End K (LinearMap.range (P.proj i))) where
  toFun T i := restrictBlocks P T.1 i i
  map_one' := by
    ext i x
    exact congrArg Subtype.val (packetProjection_apply_coe P i x)
  map_mul' S T := by
    funext i
    exact restrict_diagonal_mul P S T i
  map_zero' := by
    ext i x
    simp [restrictBlocks, packetProjection, packetInclusion]
  map_add' S T := by
    ext i x
    simp [restrictBlocks, packetProjection, packetInclusion]
  commutes' c := by
    ext i x
    change P.proj i (c • (x : X)) = c • (x : X)
    rw [map_smul]
    congr 1
    exact congrArg Subtype.val (packetProjection_apply_coe P i x)

/-- Every prescribed diagonal-class operator family has a supported ambient lift. -/
theorem diagonalClassHom_surjective (P : LinearProjectorFamily K X I) :
    Function.Surjective (diagonalClassHom P) := by
  intro f
  let B : PacketBlocks P := ∑ i, singleBlock P i i (f i)
  have hB : BlocksSupported P (· ≤ ·) B := by
    intro b a hab
    change (∑ i, singleBlock P i i (f i)) b a = 0
    simp only [Finset.sum_apply]
    apply Finset.sum_eq_zero
    intro i _
    exact singleBlock_supported P (· ≤ ·) le_rfl (f i) b a hab
  refine ⟨⟨synthesizeBlocks P B, ?_⟩, ?_⟩
  · change BlocksSupported P (· ≤ ·) (restrictBlocks P (synthesizeBlocks P B))
    rw [restrictBlocks_synthesizeBlocks]
    exact hB
  · funext i
    change restrictBlocks P (synthesizeBlocks P B) i i = f i
    rw [restrictBlocks_synthesizeBlocks]
    dsimp only [B]
    simp only [Finset.sum_apply]
    rw [Finset.sum_eq_single i]
    · simp [singleBlock]
    · intro j _ hji
      simp [singleBlock, Ne.symm hji]
    · simp

/-- The kernel consists exactly of the strict-class support ideal. -/
theorem diagonalClassHom_eq_zero_iff (P : LinearProjectorFamily K X I)
    (T : preorderSupportAlgebra P) :
    diagonalClassHom P T = 0 ↔ OperatorSupported P (· < ·) T.1 := by
  rw [strictSupport_iff_same_class_zero]
  constructor
  · intro h a b hab
    have hab' : a = b := le_antisymm hab.1 hab.2
    subst b
    apply (restricted_block_zero_iff P T.1 a a).mp
    exact congrFun h a
  · intro h
    funext i
    apply (restricted_block_zero_iff P T.1 i i).mpr
    exact h i i ⟨le_rfl, le_rfl⟩

/-- The diagonal-class quotient is the full product of packet endomorphism algebras. -/
def diagonalClassQuotientEquiv (P : LinearProjectorFamily K X I) :
    (preorderSupportAlgebra P ⧸ RingHom.ker (diagonalClassHom P).toRingHom) ≃ₐ[K]
      ((i : I) → Module.End K (LinearMap.range (P.proj i))) :=
  Ideal.quotientKerAlgEquivOfSurjective (diagonalClassHom_surjective P)

end Komorebi.PaperIRelease
