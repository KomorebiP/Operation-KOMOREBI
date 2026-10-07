import KomorebiVerification.ProjectorCore

/-!
# Exact packet coordinates for a complete projector family

The packet space below is defined independently as the finite product of the
actual ranges of the projectors.  It is not defined as the image of analysis,
and synthesis is the direct sum of the packet values rather than an
inverse-by-definition.  Idempotence, pairwise orthogonality, and completeness
therefore do the mathematical work in the two inverse laws.
-/

set_option autoImplicit false

namespace Komorebi.Foundation.LinearProjectorFamily

universe u v w

variable {R : Type u} {M : Type v} {ι : Type w}
variable [Semiring R] [AddCommMonoid M] [Module R M] [Fintype ι]

/-- The explicit product of the projector ranges. -/
abbrev PacketSpace (P : LinearProjectorFamily R M ι) : Type max v w :=
  (i : ι) → LinearMap.range (P.proj i)

/-- Analysis, with each projected value certified to lie in its projector range. -/
def rangeAnalysis (P : LinearProjectorFamily R M ι) : M →ₗ[R] PacketSpace P where
  toFun x i := ⟨P.proj i x, ⟨x, rfl⟩⟩
  map_add' x y := by
    funext i
    apply Subtype.ext
    exact (P.proj i).map_add x y
  map_smul' c x := by
    funext i
    apply Subtype.ext
    exact (P.proj i).map_smul c x

/-- Synthesis is the direct finite sum of packet values. -/
def rangeSynthesis (P : LinearProjectorFamily R M ι) : PacketSpace P →ₗ[R] M where
  toFun packets := ∑ i, (packets i : M)
  map_add' packets packets' := by
    simp only [Pi.add_apply, Submodule.coe_add, Finset.sum_add_distrib]
  map_smul' c packets := by
    simp only [Pi.smul_apply, SetLike.val_smul, Finset.smul_sum, RingHom.id_apply]

@[simp] theorem proj_packet_self
    (P : LinearProjectorFamily R M ι) (packets : PacketSpace P) (i : ι) :
    P.proj i (packets i : M) = (packets i : M) := by
  rcases (packets i).property with ⟨x, hx⟩
  rw [← hx]
  exact P.idempotent i x

theorem proj_packet_eq_zero
    (P : LinearProjectorFamily R M ι) (packets : PacketSpace P)
    {i j : ι} (hij : i ≠ j) :
    P.proj i (packets j : M) = 0 := by
  rcases (packets j).property with ⟨x, hx⟩
  rw [← hx]
  exact P.orthogonal hij x

/-- Completeness proves that synthesizing analyzed coordinates returns the input. -/
@[simp] theorem rangeSynthesis_rangeAnalysis
    (P : LinearProjectorFamily R M ι) (x : M) :
    P.rangeSynthesis (P.rangeAnalysis x) = x := by
  change (∑ i, P.proj i x) = x
  exact P.complete x

/-- Idempotence and orthogonality prove that analysis recovers every range packet. -/
@[simp] theorem rangeAnalysis_rangeSynthesis
    (P : LinearProjectorFamily R M ι) (packets : PacketSpace P) :
    P.rangeAnalysis (P.rangeSynthesis packets) = packets := by
  classical
  funext i
  apply Subtype.ext
  change P.proj i (∑ j, (packets j : M)) = (packets i : M)
  rw [map_sum, Finset.sum_eq_single i]
  · exact P.proj_packet_self packets i
  · intro j _ hji
    exact P.proj_packet_eq_zero packets hji.symm
  · simp

/-- Exact linear coordinates in the independent product of projector ranges. -/
def exactPacketCoordinates
    (P : LinearProjectorFamily R M ι) : M ≃ₗ[R] PacketSpace P where
  toFun := P.rangeAnalysis
  invFun := P.rangeSynthesis
  left_inv := P.rangeSynthesis_rangeAnalysis
  right_inv := P.rangeAnalysis_rangeSynthesis
  map_add' := (P.rangeAnalysis).map_add
  map_smul' := (P.rangeAnalysis).map_smul

@[simp] theorem exactPacketCoordinates_apply
    (P : LinearProjectorFamily R M ι) (x : M) :
    P.exactPacketCoordinates x = P.rangeAnalysis x := rfl

@[simp] theorem exactPacketCoordinates_symm_apply
    (P : LinearProjectorFamily R M ι) (packets : PacketSpace P) :
    P.exactPacketCoordinates.symm packets = P.rangeSynthesis packets := rfl

end Komorebi.Foundation.LinearProjectorFamily

#print axioms Komorebi.Foundation.LinearProjectorFamily.rangeSynthesis_rangeAnalysis
#print axioms Komorebi.Foundation.LinearProjectorFamily.rangeAnalysis_rangeSynthesis
#print axioms Komorebi.Foundation.LinearProjectorFamily.exactPacketCoordinates
