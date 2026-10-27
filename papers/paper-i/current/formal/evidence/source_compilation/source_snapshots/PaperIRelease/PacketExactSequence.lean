import PaperIRelease.PacketDescent

set_option autoImplicit false

namespace Komorebi.Foundation.LinearProjectorFamily

universe u v w

variable {R : Type u} {M : Type v} {ι : Type w}
variable [Ring R] [AddCommGroup M] [Module R M] [Fintype ι]

/-- Exact coordinates in the literal finite direct sum of the actual packet
ranges, using the standard finite-product/direct-sum equivalence. -/
noncomputable def exactPacketDirectSumCoordinates
    (P : LinearProjectorFamily R M ι) :
    M ≃ₗ[R] DirectSum ι (fun i ↦ LinearMap.range (P.proj i)) := by
  classical
  exact P.exactPacketCoordinates.trans
    (DirectSum.linearEquivFunOnFintype R ι (fun i ↦ LinearMap.range (P.proj i))).symm

/-- Inclusion of the actual restricted packet into its ambient packet. -/
def packetInclusion (P : LinearProjectorFamily R M ι) (K : Submodule R M)
    (hK : P.Preserves K) (i : ι) :
    LinearMap.range ((P.restrictTo K hK).proj i) →ₗ[R]
      LinearMap.range (P.proj i) where
  toFun x := ⟨(x : K), by
    obtain ⟨y, hy⟩ := x.property
    exact ⟨(y : M), congrArg (fun z : K ↦ (z : M)) hy⟩⟩
  map_add' _ _ := rfl
  map_smul' _ _ := rfl

theorem packetInclusion_injective
    (P : LinearProjectorFamily R M ι) (K : Submodule R M)
    (hK : P.Preserves K) (i : ι) :
    Function.Injective (P.packetInclusion K hK i) := by
  intro x y h
  apply Subtype.ext
  apply Subtype.ext
  exact congrArg (fun z : LinearMap.range (P.proj i) ↦ (z : M)) h

/-- The packet sequence is exact at its middle term. -/
theorem packet_sequence_exact
    (P : LinearProjectorFamily R M ι) (K : Submodule R M)
    (hK : P.Preserves K) (i : ι) :
    LinearMap.range (P.packetInclusion K hK i) =
      LinearMap.ker (P.packetQuotientMap K hK i) := by
  rw [P.packetQuotientMap_ker]
  ext x
  constructor
  · rintro ⟨y, rfl⟩
    exact (y : K).property
  · intro hx
    let y : K := ⟨(x : M), hx⟩
    have hy : y ∈ LinearMap.range ((P.restrictTo K hK).proj i) := by
      rw [P.restrictTo_range]
      exact x.property
    exact ⟨⟨y, hy⟩, rfl⟩

/-- All three conditions for the actual short exact sequence of one packet. -/
theorem packet_shortExact
    (P : LinearProjectorFamily R M ι) (K : Submodule R M)
    (hK : P.Preserves K) (i : ι) :
    Function.Injective (P.packetInclusion K hK i) ∧
      LinearMap.range (P.packetInclusion K hK i) =
        LinearMap.ker (P.packetQuotientMap K hK i) ∧
      Function.Surjective (P.packetQuotientMap K hK i) :=
  ⟨P.packetInclusion_injective K hK i, P.packet_sequence_exact K hK i,
    P.packetQuotientMap_surjective K hK i⟩

/-- The finite product of the packet inclusions (equal to the finite direct
sum under the canonical finite-product/direct-sum equivalence). -/
def packetCoordinateInclusion
    (P : LinearProjectorFamily R M ι) (K : Submodule R M)
    (hK : P.Preserves K) :
    (P.restrictTo K hK).PacketSpace →ₗ[R] P.PacketSpace where
  toFun x i := P.packetInclusion K hK i (x i)
  map_add' x y := by funext i; exact (P.packetInclusion K hK i).map_add _ _
  map_smul' a x := by funext i; exact (P.packetInclusion K hK i).map_smul _ _

/-- The finite product of the actual packet quotient maps. -/
def packetCoordinateQuotient
    (P : LinearProjectorFamily R M ι) (K : Submodule R M)
    (hK : P.Preserves K) :
    P.PacketSpace →ₗ[R] (P.descendTo K hK).PacketSpace where
  toFun x i := P.packetQuotientMap K hK i (x i)
  map_add' x y := by funext i; exact (P.packetQuotientMap K hK i).map_add _ _
  map_smul' a x := by funext i; exact (P.packetQuotientMap K hK i).map_smul _ _

/-- Exact packet coordinates identify the original inclusion with the product
of the packetwise inclusions. -/
theorem packetCoordinateInclusion_natural
    (P : LinearProjectorFamily R M ι) (K : Submodule R M)
    (hK : P.Preserves K) :
    (P.packetCoordinateInclusion K hK).comp (P.restrictTo K hK).rangeAnalysis =
      P.rangeAnalysis.comp K.subtype := by
  ext x i
  rfl

/-- Exact packet coordinates identify the original quotient map with the
product of the packetwise quotient maps. -/
theorem packetCoordinateQuotient_natural
    (P : LinearProjectorFamily R M ι) (K : Submodule R M)
    (hK : P.Preserves K) :
    (P.packetCoordinateQuotient K hK).comp P.rangeAnalysis =
      (P.descendTo K hK).rangeAnalysis.comp K.mkQ := by
  ext x i
  rfl

/-- The finite product of the packet sequences is itself short exact. Together
with the two naturality identities and `exactPacketCoordinates`, this is the
decomposition of the entire exact sequence into its packet sequences. -/
theorem packetCoordinate_shortExact
    (P : LinearProjectorFamily R M ι) (K : Submodule R M)
    (hK : P.Preserves K) :
    Function.Injective (P.packetCoordinateInclusion K hK) ∧
      LinearMap.range (P.packetCoordinateInclusion K hK) =
        LinearMap.ker (P.packetCoordinateQuotient K hK) ∧
      Function.Surjective (P.packetCoordinateQuotient K hK) := by
  classical
  refine ⟨?_, ?_, ?_⟩
  · intro x y h
    funext i
    exact P.packetInclusion_injective K hK i (congrFun h i)
  · ext x
    constructor
    · rintro ⟨y, rfl⟩
      change (P.packetCoordinateQuotient K hK)
        ((P.packetCoordinateInclusion K hK) y) = 0
      funext i
      have hi : P.packetInclusion K hK i (y i) ∈
          LinearMap.ker (P.packetQuotientMap K hK i) := by
        rw [← P.packet_sequence_exact]
        exact ⟨y i, rfl⟩
      exact hi
    · intro hx
      have hi (i : ι) : ∃ y, P.packetInclusion K hK i y = x i := by
        have hz : P.packetQuotientMap K hK i (x i) = 0 :=
          congrFun hx i
        have hm : x i ∈ LinearMap.range (P.packetInclusion K hK i) := by
          rw [P.packet_sequence_exact]
          exact hz
        exact hm
      exact ⟨fun i ↦ Classical.choose (hi i),
        funext (fun i ↦ Classical.choose_spec (hi i))⟩
  · intro y
    choose x hx using fun i ↦ P.packetQuotientMap_surjective K hK i (y i)
    exact ⟨x, funext hx⟩

end Komorebi.Foundation.LinearProjectorFamily

#print axioms Komorebi.Foundation.LinearProjectorFamily.packet_shortExact
#print axioms Komorebi.Foundation.LinearProjectorFamily.packetCoordinate_shortExact
#print axioms Komorebi.Foundation.LinearProjectorFamily.packetCoordinateInclusion_natural
#print axioms Komorebi.Foundation.LinearProjectorFamily.packetCoordinateQuotient_natural
