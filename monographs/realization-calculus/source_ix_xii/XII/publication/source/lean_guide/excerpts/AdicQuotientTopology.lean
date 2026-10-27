import PaperXII.AdicModel

/-! The quotient topology of an adic ring is the mapped-ideal adic topology. -/
noncomputable section
open Filter Topology UniformSpace
open scoped Uniformity
set_option autoImplicit false
namespace PaperXII.AdicModel

/-- Continuity from control of the actual defining ideals. -/
theorem continuous_of_map_le {R S : Type*} [CommRing R] [CommRing S]
    [TopologicalSpace R] [TopologicalSpace S] [IsTopologicalRing R] [IsTopologicalRing S]
    {I : Ideal R} {J : Ideal S} (hR : IsAdic I) (hS : IsAdic J)
    (f : R →+* S) (h : I.map f ≤ J) : Continuous f := by
  apply continuous_of_continuousAt_zero f
  rw [ContinuousAt, map_zero, hR.hasBasis_nhds_zero.tendsto_iff hS.hasBasis_nhds_zero]
  refine fun n _ ↦ ⟨n, trivial, ?_⟩
  exact Ideal.map_le_iff_le_comap.mp (by simpa [Ideal.map_pow] using Ideal.pow_right_mono h n)

/-- Actual quotient neighborhoods have the expected adic basis. -/
theorem quotient_isAdic {R : Type*} [CommRing R] [TopologicalSpace R]
    [IsTopologicalRing R] {I : Ideal R} (hR : IsAdic I) (J : Ideal R) :
    IsAdic (I.map (Ideal.Quotient.mk J)) := by
  rw [isAdic_iff]
  constructor
  · intro n
    rw [← Ideal.map_pow, Ideal.map_eq_image_of_surjective _ Ideal.Quotient.mk_surjective]
    exact (QuotientRing.isOpenMap_coe J) _ ((isAdic_iff.mp hR).1 n)
  · intro V hV
    have hb := hR.hasBasis_nhds_zero.map (Ideal.Quotient.mk J)
    rw [(QuotientRing.isOpenQuotientMap_mk J).map_nhds_eq, map_zero] at hb
    obtain ⟨n, _, hn⟩ := hb.mem_iff.mp hV
    refine ⟨n, ?_⟩
    rw [← Ideal.map_pow, Ideal.map_eq_image_of_surjective _ Ideal.Quotient.mk_surjective]
    exact hn

/-- Retag an ideal on the carrier without changing its elements. -/
def carrierIdeal {R : Type*} [CommRing R] (I J : Ideal R) : Ideal (Carrier R I) :=
  J.map (rawEquiv R I).symm.toRingHom

@[simp] theorem carrierIdeal_mem {R : Type*} [CommRing R] (I J : Ideal R) (x : Carrier R I) :
    x ∈ carrierIdeal I J ↔ rawEquiv R I x ∈ J := by
  change x ∈ J.map (RingHom.id R) ↔ x ∈ J
  simp

/-- The ring quotient of the actual adic carrier and the adic quotient carrier agree. -/
def quotientCarrierEquiv {R : Type*} [CommRing R] (I J : Ideal R) :
    (Carrier R I ⧸ carrierIdeal I J) ≃+* Carrier (R ⧸ J) (I.map (Ideal.Quotient.mk J)) :=
  (Ideal.quotientEquiv _ _ (rawEquiv R I) (by simp [carrierIdeal, Ideal.map_map])).trans
    (rawEquiv (R ⧸ J) (I.map (Ideal.Quotient.mk J))).symm

/-- The quotient carrier equivalence preserves the ideal controlling its topology. -/
theorem quotientCarrierEquiv_map {R : Type*} [CommRing R] (I J : Ideal R) :
    ((WithIdeal.i : Ideal (Carrier R I)).map (Ideal.Quotient.mk (carrierIdeal I J))).map
      (quotientCarrierEquiv I J).toRingHom =
      (WithIdeal.i : Ideal (Carrier (R ⧸ J) (I.map (Ideal.Quotient.mk J)))) := by
  rw [Ideal.map_map]
  rfl

theorem quotientCarrierEquiv_continuous {R : Type*} [CommRing R] (I J : Ideal R) :
    Continuous (quotientCarrierEquiv I J) :=
  continuous_of_map_le (quotient_isAdic (carrier_isAdic R I) _)
    (carrier_isAdic _ _) (quotientCarrierEquiv I J).toRingHom
    (quotientCarrierEquiv_map I J).le

theorem quotientCarrierEquiv_symm_continuous {R : Type*} [CommRing R] (I J : Ideal R) :
    Continuous (quotientCarrierEquiv I J).symm := by
  apply continuous_of_map_le (carrier_isAdic _ _)
    (quotient_isAdic (carrier_isAdic R I) _) (quotientCarrierEquiv I J).symm.toRingHom
  rw [← quotientCarrierEquiv_map I J, Ideal.map_map]
  simp

@[simp] theorem quotientCarrierEquiv_mk {R : Type*} [CommRing R] (I J : Ideal R) (x : R) :
    quotientCarrierEquiv I J (Ideal.Quotient.mk _ ((rawEquiv R I).symm x)) =
      (rawEquiv (R ⧸ J) (I.map (Ideal.Quotient.mk J))).symm (Ideal.Quotient.mk J x) := rfl

attribute [local instance] CompletionQuotient.quotientUniformSpace

/-- Quotienting commutes with actual adic completion, including both topologies. -/
def quotientCompletionEquiv {R : Type*} [CommRing R] (I J : Ideal R) :
    (Completed R I ⧸ CompletionQuotient.closedExtension (carrierIdeal I J)) ≃+*
      Completed (R ⧸ J) (I.map (Ideal.Quotient.mk J)) :=
  (CompletionQuotient.equiv (carrierIdeal I J)).trans
    (Completion.mapRingEquiv (quotientCarrierEquiv I J)
      (quotientCarrierEquiv_continuous I J) (quotientCarrierEquiv_symm_continuous I J))

theorem quotientCompletionEquiv_continuous {R : Type*} [CommRing R] (I J : Ideal R) :
    Continuous (quotientCompletionEquiv I J) :=
  Completion.continuous_extension.comp (CompletionQuotient.equiv_continuous _)

theorem quotientCompletionEquiv_symm_continuous {R : Type*} [CommRing R] (I J : Ideal R) :
    Continuous (quotientCompletionEquiv I J).symm :=
  (CompletionQuotient.equiv_symm_continuous _).comp Completion.continuous_extension

@[simp] theorem quotientCompletionEquiv_mk_embed {R : Type*} [CommRing R]
    (I J : Ideal R) (x : R) :
    quotientCompletionEquiv I J (Ideal.Quotient.mk _ (embed R I x)) =
      embed (R ⧸ J) (I.map (Ideal.Quotient.mk J)) (Ideal.Quotient.mk J x) := by
  change Completion.mapRingEquiv (quotientCarrierEquiv I J)
    (quotientCarrierEquiv_continuous I J) (quotientCarrierEquiv_symm_continuous I J)
    (CompletionQuotient.equiv _ (Ideal.Quotient.mk _ ((rawEquiv R I).symm x : Completed R I))) = _
  rw [CompletionQuotient.equiv_mk_coe]
  exact Completion.mapRingHom_coe (quotientCarrierEquiv_continuous I J) _

end PaperXII.AdicModel
