import PaperIRelease.PacketExactSequence
import KomorebiVerification.TopologicalCompletion

/-!
# Closed invariant subspaces and Banach packet exact sequences

The continuous maps bundle the same algebraic maps constructed in
`PacketDescent`, and their exactness is proved by those literal identifications.
The quotient carries its quotient norm; closedness supplies separation.
-/

noncomputable section
set_option autoImplicit false
set_option linter.style.haveILetI false

namespace Komorebi.Foundation.LinearProjectorFamily

universe u v w

variable {𝕜 : Type u} {X : Type v} {ι : Type w}
variable [NontriviallyNormedField 𝕜] [NormedAddCommGroup X] [NormedSpace 𝕜 X]
variable [Fintype ι]

/-- Bundle the original projector with its asserted continuity. -/
def boundedProjector (P : LinearProjectorFamily 𝕜 X ι)
    (hP : ∀ i, Continuous (P.proj i)) (i : ι) : X →L[𝕜] X :=
  ⟨P.proj i, hP i⟩

theorem isClosed_range_of_bounded (P : LinearProjectorFamily 𝕜 X ι)
    (hP : ∀ i, Continuous (P.proj i)) (i : ι) :
    IsClosed (LinearMap.range (P.proj i) : Set X) := by
  apply ContinuousLinearMap.IsIdempotentElem.isClosed_range
    (p := P.boundedProjector hP i)
  apply ContinuousLinearMap.ext
  intro x
  exact P.idempotent i x

variable (P : LinearProjectorFamily 𝕜 X ι)
variable (hP : ∀ i, Continuous (P.proj i))
variable (K : Submodule 𝕜 X) (hK : P.Preserves K)

/-- The original restricted projector, with inherited continuity. -/
def restrictedProjectorCLM (i : ι) : K →L[𝕜] K where
  toLinearMap := (P.restrictTo K hK).proj i
  cont := ((hP i).comp continuous_subtype_val).subtype_mk _

@[simp] theorem restrictedProjectorCLM_toLinearMap (i : ι) :
    (P.restrictedProjectorCLM hP K hK i).toLinearMap =
      (P.restrictTo K hK).proj i := rfl

/-- The quotient projector is the continuous quotient lift of `π ∘ P_i`. -/
def quotientProjectorCLM (i : ι) : (X ⧸ K) →L[𝕜] (X ⧸ K) :=
  K.liftQL (K.mkQL.comp (P.boundedProjector hP i)) (by
    intro x hx
    change K.mkQ (P.proj i x) = 0
    exact (Submodule.Quotient.mk_eq_zero K).mpr (hK i x hx))

@[simp] theorem quotientProjectorCLM_toLinearMap (i : ι) :
    (P.quotientProjectorCLM hP K hK i).toLinearMap =
      (P.descendTo K hK).proj i := rfl

@[simp] theorem quotientProjectorCLM_mkQ (i : ι) (x : X) :
    P.quotientProjectorCLM hP K hK i (K.mkQ x) = K.mkQ (P.proj i x) := rfl

/-- Quotient projectors satisfy the sharp inherited operator bound. -/
theorem quotientProjector_norm_apply_le (i : ι) (z : X ⧸ K) :
    ‖P.quotientProjectorCLM hP K hK i z‖ ≤ ‖P.boundedProjector hP i‖ * ‖z‖ := by
  let C := ‖P.boundedProjector hP i‖
  have hC : 0 ≤ C := norm_nonneg _
  apply le_of_forall_pos_le_add
  intro ε hε
  obtain ⟨x, hx, hnorm⟩ := Submodule.Quotient.norm_mk_lt z
    (show 0 < ε / (C + 1) by positivity)
  have hbase : ‖P.quotientProjectorCLM hP K hK i z‖ ≤ C * ‖x‖ := by
    rw [← hx]
    exact (Submodule.Quotient.norm_mk_le K (P.proj i x)).trans
      ((P.boundedProjector hP i).le_opNorm x)
  have hmul : C * ‖x‖ ≤ C * (‖z‖ + ε / (C + 1)) :=
    mul_le_mul_of_nonneg_left hnorm.le hC
  have hsmall : C * (ε / (C + 1)) ≤ ε := by
    have hpos : 0 < C + 1 := by positivity
    rw [← mul_div_assoc]
    apply (div_le_iff₀ hpos).mpr
    nlinarith
  exact hbase.trans (hmul.trans (by nlinarith))

/-- The quotient operator norm cannot exceed that of the original projector. -/
theorem quotientProjector_norm_le (i : ι) :
    ‖P.quotientProjectorCLM hP K hK i‖ ≤ ‖P.boundedProjector hP i‖ :=
  ContinuousLinearMap.opNorm_le_bound _ (norm_nonneg _)
    (P.quotientProjector_norm_apply_le hP K hK i)

/-- The actual packet inclusion is bounded as a composition of subtype maps. -/
def packetInclusionCLM (i : ι) :
    LinearMap.range ((P.restrictTo K hK).proj i) →L[𝕜]
      LinearMap.range (P.proj i) :=
  (K.subtypeL.comp (LinearMap.range ((P.restrictTo K hK).proj i)).subtypeL).codRestrict
    (LinearMap.range (P.proj i)) (fun x ↦ (P.packetInclusion K hK i x).property)

@[simp] theorem packetInclusionCLM_toLinearMap (i : ι) :
    (P.packetInclusionCLM K hK i).toLinearMap = P.packetInclusion K hK i := rfl

/-- The actual packet quotient map is bounded as the restriction and
corestriction of the ambient quotient map. -/
def packetQuotientCLM (i : ι) :
    LinearMap.range (P.proj i) →L[𝕜]
      LinearMap.range ((P.descendTo K hK).proj i) :=
  (K.mkQL.comp (LinearMap.range (P.proj i)).subtypeL).codRestrict
    (LinearMap.range ((P.descendTo K hK).proj i))
    (fun x ↦ (P.packetQuotientMap K hK i x).property)

@[simp] theorem packetQuotientCLM_toLinearMap (i : ι) :
    (P.packetQuotientCLM K hK i).toLinearMap = P.packetQuotientMap K hK i := rfl

theorem packetQuotientCLM_norm_le_one (i : ι) :
    ‖P.packetQuotientCLM K hK i‖ ≤ 1 := by
  apply ContinuousLinearMap.opNorm_le_bound _ zero_le_one
  intro x
  change ‖(Submodule.Quotient.mk (x : X) : X ⧸ K)‖ ≤ 1 * ‖x‖
  simpa using (Submodule.Quotient.norm_mk_le K (x : X))

/-- The submodule `X_i ∩ K`, expressed inside `X_i`. -/
abbrev packetIntersection (i : ι) : Submodule 𝕜 (LinearMap.range (P.proj i)) :=
  K.comap (LinearMap.range (P.proj i)).subtype

/-- Factor the actual continuous packet quotient map through its kernel. -/
def packetQuotientLiftCLM (i : ι) :
    (LinearMap.range (P.proj i) ⧸ P.packetIntersection K i) →L[𝕜]
      LinearMap.range ((P.descendTo K hK).proj i) :=
  (P.packetIntersection K i).liftQL (P.packetQuotientCLM K hK i) (by
    rw [packetQuotientCLM_toLinearMap, P.packetQuotientMap_ker])

/-- Project and then take the quotient of the source packet. -/
def projectToPacketQuotient (i : ι) :
    X →L[𝕜] (LinearMap.range (P.proj i) ⧸ P.packetIntersection K i) :=
  (P.packetIntersection K i).mkQL.comp
    ((P.boundedProjector hP i).codRestrict (LinearMap.range (P.proj i))
      (fun x ↦ ⟨x, rfl⟩))

/-- This inverse is induced from the actual bounded projector, using
invariance to prove that the projected map vanishes on `K`. -/
def packetQuotientInverseAmbient (i : ι) :
    (X ⧸ K) →L[𝕜] (LinearMap.range (P.proj i) ⧸ P.packetIntersection K i) :=
  K.liftQL (P.projectToPacketQuotient hP K i) (by
    intro x hx
    change Submodule.Quotient.mk (⟨P.proj i x, ⟨x, rfl⟩⟩ : LinearMap.range (P.proj i)) = 0
    apply (Submodule.Quotient.mk_eq_zero (P.packetIntersection K i)).mpr
    exact hK i x hx)

def packetQuotientInverseCLM (i : ι) :
    LinearMap.range ((P.descendTo K hK).proj i) →L[𝕜]
      (LinearMap.range (P.proj i) ⧸ P.packetIntersection K i) :=
  (P.packetQuotientInverseAmbient hP K hK i).comp
    (LinearMap.range ((P.descendTo K hK).proj i)).subtypeL

/-- The quotient identification is a bounded linear equivalence. Its inverse
is constructed from `P_i`, so no open-mapping hypothesis or supplied inverse
is being smuggled into the statement. -/
def packetQuotientEquivL (i : ι) :
    (LinearMap.range (P.proj i) ⧸ P.packetIntersection K i) ≃L[𝕜]
      LinearMap.range ((P.descendTo K hK).proj i) :=
  ContinuousLinearEquiv.equivOfInverse
    (P.packetQuotientLiftCLM K hK i) (P.packetQuotientInverseCLM hP K hK i)
    (by
      intro z
      obtain ⟨x, rfl⟩ := (P.packetIntersection K i).mkQ_surjective z
      change Submodule.Quotient.mk
        (⟨P.proj i (x : X), ⟨(x : X), rfl⟩⟩ : LinearMap.range (P.proj i)) =
        Submodule.Quotient.mk x
      congr 1
      exact Subtype.ext (P.proj_eq_self_of_mem_range i x.property))
    (by
      intro z
      apply Subtype.ext
      obtain ⟨x, hx⟩ := K.mkQ_surjective (z : X ⧸ K)
      have hz := (P.descendTo K hK).proj_eq_self_of_mem_range i z.property
      rw [← hx] at hz
      change K.mkQ (P.proj i x) = K.mkQ x at hz
      change (P.packetQuotientLiftCLM K hK i
        (P.packetQuotientInverseAmbient hP K hK i (z : X ⧸ K)) : X ⧸ K) = _
      rw [← hx]
      exact hz)

@[simp] theorem packetQuotientEquivL_mk (i : ι)
    (x : LinearMap.range (P.proj i)) :
    (P.packetQuotientEquivL hP K hK i (Submodule.Quotient.mk x) : X ⧸ K) =
      K.mkQ (x : X) := rfl

include hK in
/-- The projector is the identity modulo `K` on the sum `X_i + K`. -/
theorem packetSum_proj_modK (i : ι) (x : ↥(LinearMap.range (P.proj i) ⊔ K)) :
    K.mkQ (P.proj i (x : X)) = K.mkQ (x : X) := by
  obtain ⟨a, ha, b, hb, hab⟩ := Submodule.mem_sup.mp x.property
  have hb0 : K.mkQ b = 0 := (Submodule.Quotient.mk_eq_zero K).mpr hb
  have hPb0 : K.mkQ (P.proj i b) = 0 :=
    (Submodule.Quotient.mk_eq_zero K).mpr (hK i b hb)
  rw [← hab, map_add, P.proj_eq_self_of_mem_range i ha, map_add, map_add, hb0, hPb0]

/-- Restrict the quotient map to `X_i + K` and corestrict to the quotient packet. -/
def packetSumQuotientMapCLM (i : ι) :
    ↥(LinearMap.range (P.proj i) ⊔ K) →L[𝕜]
      LinearMap.range ((P.descendTo K hK).proj i) :=
  (K.mkQL.comp (LinearMap.range (P.proj i) ⊔ K).subtypeL).codRestrict
    (LinearMap.range ((P.descendTo K hK).proj i))
    (fun x ↦ ⟨K.mkQ (x : X), P.packetSum_proj_modK K hK i x⟩)

def packetSumQuotientLiftCLM (i : ι) :
    (↥(LinearMap.range (P.proj i) ⊔ K) ⧸
      K.comap (LinearMap.range (P.proj i) ⊔ K).subtype) →L[𝕜]
        LinearMap.range ((P.descendTo K hK).proj i) :=
  (K.comap (LinearMap.range (P.proj i) ⊔ K).subtype).liftQL
    (P.packetSumQuotientMapCLM K hK i) (by
      intro x hx
      apply Subtype.ext
      exact (Submodule.Quotient.mk_eq_zero K).mpr hx)

/-- Project from the ambient quotient into the sum quotient. -/
def packetSumQuotientInverseAmbient (i : ι) :
    (X ⧸ K) →L[𝕜]
      (↥(LinearMap.range (P.proj i) ⊔ K) ⧸
        K.comap (LinearMap.range (P.proj i) ⊔ K).subtype) :=
  K.liftQL
    ((K.comap (LinearMap.range (P.proj i) ⊔ K).subtype).mkQL.comp
      ((P.boundedProjector hP i).codRestrict (LinearMap.range (P.proj i) ⊔ K)
        (fun x ↦ Submodule.mem_sup.mpr ⟨P.proj i x, ⟨x, rfl⟩, 0, K.zero_mem, add_zero _⟩)))
    (by
      intro x hx
      apply (Submodule.Quotient.mk_eq_zero
        (K.comap (LinearMap.range (P.proj i) ⊔ K).subtype)).mpr
      exact hK i x hx)

/-- The quotient packet is also boundedly isomorphic to `(X_i + K)/K`. -/
def packetSumQuotientEquivL (i : ι) :
    (↥(LinearMap.range (P.proj i) ⊔ K) ⧸
      K.comap (LinearMap.range (P.proj i) ⊔ K).subtype) ≃L[𝕜]
        LinearMap.range ((P.descendTo K hK).proj i) :=
  ContinuousLinearEquiv.equivOfInverse
    (P.packetSumQuotientLiftCLM K hK i)
    ((P.packetSumQuotientInverseAmbient hP K hK i).comp
      (LinearMap.range ((P.descendTo K hK).proj i)).subtypeL)
    (by
      intro z
      obtain ⟨x, rfl⟩ :=
        (K.comap (LinearMap.range (P.proj i) ⊔ K).subtype).mkQ_surjective z
      apply (Submodule.Quotient.eq
        (K.comap (LinearMap.range (P.proj i) ⊔ K).subtype)).mpr
      exact (Submodule.Quotient.eq K).mp (P.packetSum_proj_modK K hK i x))
    (by
      intro z
      apply Subtype.ext
      obtain ⟨x, hx⟩ := K.mkQ_surjective (z : X ⧸ K)
      have hz := (P.descendTo K hK).proj_eq_self_of_mem_range i z.property
      rw [← hx] at hz
      change K.mkQ (P.proj i x) = K.mkQ x at hz
      change (P.packetSumQuotientLiftCLM K hK i
        (P.packetSumQuotientInverseAmbient hP K hK i (z : X ⧸ K)) : X ⧸ K) = _
      rw [← hx]
      exact hz)

include hP

theorem isClosed_restricted_packet (i : ι) :
    IsClosed (LinearMap.range ((P.restrictTo K hK).proj i) : Set K) :=
  (P.restrictTo K hK).isClosed_range_of_bounded
    (fun j ↦ (P.restrictedProjectorCLM hP K hK j).continuous) i

variable [hclosed : IsClosed (K : Set X)]

theorem isClosed_quotient_packet (i : ι) :
    IsClosed (LinearMap.range ((P.descendTo K hK).proj i) : Set (X ⧸ K)) :=
  (P.descendTo K hK).isClosed_range_of_bounded
    (fun j ↦ (P.quotientProjectorCLM hP K hK j).continuous) i

include hK in
/-- Invariance makes `X_i + K` closed: it is the inverse image of the closed
quotient packet. This is stronger than closedness of two arbitrary summands. -/
theorem isClosed_packet_sum (i : ι) :
    IsClosed ((LinearMap.range (P.proj i) ⊔ K : Submodule 𝕜 X) : Set X) := by
  have h := (P.isClosed_quotient_packet hP K hK i).preimage K.mkQL.continuous
  change IsClosed ((LinearMap.range ((P.descendTo K hK).proj i)).comap K.mkQ : Set X) at h
  rwa [P.descendTo_range_preimage] at h

/-- Every term of the packet sequence is complete under the inherited norm. -/
theorem packet_sequence_complete [CompleteSpace X] (i : ι) :
    CompleteSpace (LinearMap.range ((P.restrictTo K hK).proj i)) ∧
      CompleteSpace (LinearMap.range (P.proj i)) ∧
      CompleteSpace (LinearMap.range ((P.descendTo K hK).proj i)) := by
  letI : IsClosed (LinearMap.range ((P.restrictTo K hK).proj i) : Set K) :=
    P.isClosed_restricted_packet hP K hK i
  letI : IsClosed (LinearMap.range (P.proj i) : Set X) :=
    P.isClosed_range_of_bounded hP i
  letI : IsClosed (LinearMap.range ((P.descendTo K hK).proj i) : Set (X ⧸ K)) :=
    P.isClosed_quotient_packet hP K hK i
  exact ⟨inferInstance, inferInstance, inferInstance⟩

/-- Paper I's topological packet exact sequence: the actual packet maps are
bounded, injective/exact/surjective, their three spaces are Banach, and the
constructed quotient projector has norm at most the original projector. -/
theorem banach_packet_shortExact [CompleteSpace X] (i : ι) :
    CompleteSpace (LinearMap.range ((P.restrictTo K hK).proj i)) ∧
      CompleteSpace (LinearMap.range (P.proj i)) ∧
      CompleteSpace (LinearMap.range ((P.descendTo K hK).proj i)) ∧
      Function.Injective (P.packetInclusionCLM K hK i) ∧
      LinearMap.range (P.packetInclusionCLM K hK i).toLinearMap =
        LinearMap.ker (P.packetQuotientCLM K hK i).toLinearMap ∧
      Function.Surjective (P.packetQuotientCLM K hK i) ∧
      ‖P.quotientProjectorCLM hP K hK i‖ ≤ ‖P.boundedProjector hP i‖ := by
  obtain ⟨h1, h2, h3⟩ := P.packet_sequence_complete hP K hK i
  obtain ⟨hinj, hexact, hsurj⟩ := P.packet_shortExact K hK i
  exact ⟨h1, h2, h3, hinj, hexact, hsurj, P.quotientProjector_norm_le hP K hK i⟩

end Komorebi.Foundation.LinearProjectorFamily

#print axioms Komorebi.Foundation.LinearProjectorFamily.banach_packet_shortExact
#print axioms Komorebi.Foundation.LinearProjectorFamily.quotientProjector_norm_le
#print axioms Komorebi.Foundation.LinearProjectorFamily.packetQuotientEquivL
#print axioms Komorebi.Foundation.LinearProjectorFamily.packetSumQuotientEquivL
