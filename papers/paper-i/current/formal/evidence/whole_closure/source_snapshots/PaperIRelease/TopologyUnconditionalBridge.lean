import PaperIRelease.TopologyUnconditional
import PaperIRelease.TopologyCountablePackets

/-! # Identification of countable packet coordinates with the general sum space -/

noncomputable section
open Set

namespace PaperIRelease.TopologyCountablePackets.Projectors

open PaperIRelease.TopologyUnconditional

variable {𝕜 X : Type*} [RCLike 𝕜] [NormedAddCommGroup X] [NormedSpace 𝕜 X]
variable (P : Projectors 𝕜 X)

/-- The closed ranges of the countable bounded idempotents. -/
def closedPackets : ClosedPackets 𝕜 X where
  packet n := (P.proj n).range
  closed n := by
    apply ContinuousLinearMap.IsIdempotentElem.isClosed_range
    apply ContinuousLinearMap.ext
    exact P.idempotent n

/-- Both carriers are the same summable coordinate families. -/
def generalSpaceLinearEquiv : P.PacketSpace ≃ₗ[𝕜] P.closedPackets.Space where
  toFun x := ⟨x.val, x.property⟩
  invFun x := ⟨x.val, x.property⟩
  left_inv _ := rfl
  right_inv _ := rfl
  map_add' _ _ := rfl
  map_smul' _ _ := rfl

/-- The two literal signed-sum supremum norms agree. -/
def generalSpaceIsometry : P.PacketSpace ≃ₗᵢ[𝕜] P.closedPackets.Space where
  toLinearEquiv := P.generalSpaceLinearEquiv
  norm_map' x := by
    change sSup (P.closedPackets.signedValues (P.generalSpaceLinearEquiv x)) =
      sSup (P.signedValues x)
    congr 1
    ext r
    constructor
    · rintro ⟨⟨F, ⟨a, ha⟩⟩, hr⟩
      exact ⟨F, a, ha, hr.symm⟩
    · rintro ⟨F, a, ha, hr⟩
      exact ⟨⟨F, ⟨a, ha⟩⟩, hr.symm⟩

/-- The countable theorem targets exactly the general unconditional sum
space of the closed packet ranges. -/
def countableUnconditionalPacketEquiv : X ≃L[𝕜] P.closedPackets.Space :=
  P.packetEquiv.trans P.generalSpaceIsometry.toContinuousLinearEquiv

/-- Its analysis norm is at most the declared multiplier constant. -/
theorem countable_analysis_norm_le :
    ‖P.countableUnconditionalPacketEquiv.toContinuousLinearMap‖ ≤ P.K := by
  apply ContinuousLinearMap.opNorm_le_bound _ P.nonneg_K
  intro x
  change ‖P.generalSpaceIsometry (P.packetEquiv x)‖ ≤ _
  rw [P.generalSpaceIsometry.norm_map]
  exact ContinuousLinearMap.le_of_opNorm_le _ P.analysis_opNorm_le x

/-- Its synthesis norm is at most one. -/
theorem countable_synthesis_norm_le :
    ‖P.countableUnconditionalPacketEquiv.symm.toContinuousLinearMap‖ ≤ 1 := by
  apply ContinuousLinearMap.opNorm_le_bound _ zero_le_one
  intro x
  change ‖P.synthesis (P.generalSpaceIsometry.symm x)‖ ≤ _
  calc
    ‖P.synthesis (P.generalSpaceIsometry.symm x)‖ ≤ ‖P.generalSpaceIsometry.symm x‖ :=
      P.synthesis_norm_le _
    _ = 1 * ‖x‖ := by rw [P.generalSpaceIsometry.symm.norm_map, one_mul]

end PaperIRelease.TopologyCountablePackets.Projectors
