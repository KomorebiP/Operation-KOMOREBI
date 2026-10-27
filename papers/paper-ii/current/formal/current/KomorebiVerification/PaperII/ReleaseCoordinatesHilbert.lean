import KomorebiVerification.PaperII.NestedRefinement
import Mathlib.Analysis.InnerProductSpace.PiL2
import Mathlib.Analysis.InnerProductSpace.Symmetric

/-!
Finite Hilbert packet coordinates use the L2 norm, not the default supremum
norm on a function product. Orthogonality is the usual self-adjointness of
each idempotent. The maps below retain the independent range and sum maps.
-/
set_option autoImplicit false
noncomputable section
namespace Komorebi.PaperII.HilbertCoordinates
open Komorebi.Foundation Komorebi.Foundation.LinearProjectorFamily
universe u v w x
variable {𝕜 : Type u} [RCLike 𝕜]
variable {E : Type v} [NormedAddCommGroup E] [InnerProductSpace 𝕜 E]
variable {ι : Type w} {κ : Type x} [Fintype ι] [Fintype κ]

/-- The actual finite Hilbert direct sum of projector ranges. -/
abbrev HilbertPacketSpace (P : LinearProjectorFamily 𝕜 E ι) :=
  PiLp 2 (fun i => LinearMap.range (P.proj i))

/-- The algebraic packet equivalence, with its codomain carrying the L2 norm. -/
def hilbertPacketEquiv (P : LinearProjectorFamily 𝕜 E ι) :
    E ≃ₗ[𝕜] HilbertPacketSpace P :=
  P.exactPacketCoordinates.trans (WithLp.linearEquiv 2 𝕜 (PacketSpace P)).symm

@[simp] theorem hilbertPacketEquiv_apply (P : LinearProjectorFamily 𝕜 E ι)
    (x : E) (i : ι) :
    ((hilbertPacketEquiv P x i : LinearMap.range (P.proj i)) : E) = P.proj i x := rfl

@[simp] theorem hilbertPacketEquiv_symm_apply (P : LinearProjectorFamily 𝕜 E ι)
    (x : HilbertPacketSpace P) :
    (hilbertPacketEquiv P).symm x = ∑ i, (x i : E) := rfl

/-- Self-adjoint idempotents preserve the full inner product under analysis. -/
theorem hilbertPacketEquiv_inner (P : LinearProjectorFamily 𝕜 E ι)
    (hP : ∀ i, (P.proj i).IsSymmetric) (x y : E) :
    inner 𝕜 (hilbertPacketEquiv P x) (hilbertPacketEquiv P y) = inner 𝕜 x y := by
  change (∑ i, inner 𝕜 (P.proj i x) (P.proj i y)) = inner 𝕜 x y
  calc
    (∑ i, inner 𝕜 (P.proj i x) (P.proj i y)) =
        ∑ i, inner 𝕜 x (P.proj i y) := by
      apply Finset.sum_congr rfl
      intro i _
      rw [hP i, P.idempotent]
    _ = inner 𝕜 x (∑ i, P.proj i y) := (inner_sum _ _ _).symm
    _ = inner 𝕜 x y := by rw [P.complete]

/-- Analysis and synthesis are inverse linear isometries for the Hilbert sum. -/
def hilbertPacketUnitary (P : LinearProjectorFamily 𝕜 E ι)
    (hP : ∀ i, (P.proj i).IsSymmetric) : E ≃ₗᵢ[𝕜] HilbertPacketSpace P :=
  (hilbertPacketEquiv P).isometryOfInner (hilbertPacketEquiv_inner P hP)

/-- Parseval's identity in the exact manuscript normalization. -/
theorem packet_parseval (P : LinearProjectorFamily 𝕜 E ι)
    (hP : ∀ i, (P.proj i).IsSymmetric) (x : E) :
    ‖x‖ ^ 2 = ∑ i, ‖P.proj i x‖ ^ 2 := by
  have h := (hilbertPacketUnitary P hP).norm_map x
  rw [← h]
  exact PiLp.norm_sq_eq_of_L2 _ _

/-- Coordinate change is a genuine unitary between the two finite Hilbert sums. -/
def hilbertCoordinateChange (P : LinearProjectorFamily 𝕜 E ι)
    (Q : LinearProjectorFamily 𝕜 E κ)
    (hP : ∀ i, (P.proj i).IsSymmetric) (hQ : ∀ j, (Q.proj j).IsSymmetric) :
    HilbertPacketSpace P ≃ₗᵢ[𝕜] HilbertPacketSpace Q :=
  (hilbertPacketUnitary P hP).symm.trans (hilbertPacketUnitary Q hQ)

/-- This unitary has the same synthesis-then-analysis formula as the algebraic map. -/
theorem hilbertCoordinateChange_apply (P : LinearProjectorFamily 𝕜 E ι)
    (Q : LinearProjectorFamily 𝕜 E κ)
    (hP : ∀ i, (P.proj i).IsSymmetric) (hQ : ∀ j, (Q.proj j).IsSymmetric)
    (x : HilbertPacketSpace P) (j : κ) :
    ((hilbertCoordinateChange P Q hP hQ x j : LinearMap.range (Q.proj j)) : E) =
      Q.proj j (∑ i, (x i : E)) := rfl

end Komorebi.PaperII.HilbertCoordinates
#print axioms Komorebi.PaperII.HilbertCoordinates.hilbertPacketUnitary
#print axioms Komorebi.PaperII.HilbertCoordinates.hilbertCoordinateChange
