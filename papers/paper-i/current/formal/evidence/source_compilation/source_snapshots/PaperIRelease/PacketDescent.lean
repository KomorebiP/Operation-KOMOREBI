import KomorebiVerification.ExactCoordinates
import KomorebiVerification.PaperITransport

/-!
# Actual restriction, quotient and exact sequences of finite packets

All induced maps are constructed from the given invariant submodule. Zero
projectors can be discarded by the explicit finite subtype `NonzeroIndex`.
The intersections below use comaps along subtype inclusions, so their ambient
module is explicit even where the printed paper suppresses that embedding.
-/

set_option autoImplicit false
set_option linter.unnecessarySimpa false

namespace Komorebi.Foundation.LinearProjectorFamily

universe u v w

variable {R : Type u} {M : Type v} {ι : Type w}
variable [Ring R] [AddCommGroup M] [Module R M] [Fintype ι]

/-- Every projector preserves the actual submodule. -/
def Preserves (P : LinearProjectorFamily R M ι) (K : Submodule R M) : Prop :=
  ∀ i, ∀ x ∈ K, P.proj i x ∈ K

/-- The literal restriction of the given projectors to an invariant submodule. -/
def restrictTo (P : LinearProjectorFamily R M ι) (K : Submodule R M)
    (hK : P.Preserves K) : LinearProjectorFamily R K ι where
  proj i :=
    { toFun := fun x ↦ ⟨P.proj i x, hK i x x.property⟩
      map_add' := fun x y ↦ Subtype.ext ((P.proj i).map_add x y)
      map_smul' := fun a x ↦ Subtype.ext ((P.proj i).map_smul a x) }
  idempotent i x := Subtype.ext (P.idempotent i x)
  orthogonal hij x := Subtype.ext (P.orthogonal hij x)
  complete x := by
    apply Subtype.ext
    simpa using P.complete (x : M)

@[simp] theorem restrictTo_proj_apply
    (P : LinearProjectorFamily R M ι) (K : Submodule R M)
    (hK : P.Preserves K) (i : ι) (x : K) :
    ((P.restrictTo K hK).proj i x : M) = P.proj i x := rfl

/-- The quotient projectors are induced by the original linear maps. -/
def descendTo (P : LinearProjectorFamily R M ι) (K : Submodule R M)
    (hK : P.Preserves K) : LinearProjectorFamily R (M ⧸ K) ι where
  proj i := K.mapQ K (P.proj i) (hK i)
  idempotent i z := by
    obtain ⟨x, rfl⟩ := K.mkQ_surjective z
    change K.mkQ (P.proj i (P.proj i x)) = K.mkQ (P.proj i x)
    rw [P.idempotent]
  orthogonal hij z := by
    obtain ⟨x, rfl⟩ := K.mkQ_surjective z
    change K.mkQ (P.proj _ (P.proj _ x)) = 0
    rw [P.orthogonal hij, map_zero]
  complete z := by
    obtain ⟨x, rfl⟩ := K.mkQ_surjective z
    change (∑ i, K.mkQ (P.proj i x)) = K.mkQ x
    rw [← map_sum, P.complete]

@[simp] theorem descendTo_proj_mkQ
    (P : LinearProjectorFamily R M ι) (K : Submodule R M)
    (hK : P.Preserves K) (i : ι) (x : M) :
    (P.descendTo K hK).proj i (K.mkQ x) = K.mkQ (P.proj i x) := rfl

/-- The literal quotient-map intertwining identity. -/
theorem descendTo_intertwines
    (P : LinearProjectorFamily R M ι) (K : Submodule R M)
    (hK : P.Preserves K) (i : ι) :
    K.mkQ.comp (P.proj i) = ((P.descendTo K hK).proj i).comp K.mkQ := by
  ext x
  rfl

/-- The actual finite subtype of indices whose projectors are nonzero. -/
abbrev NonzeroIndex (P : LinearProjectorFamily R M ι) := {i : ι // P.proj i ≠ 0}

noncomputable instance nonzeroIndexFintype (P : LinearProjectorFamily R M ι) :
    Fintype P.NonzeroIndex := by
  classical
  exact inferInstanceAs (Fintype {i // P.proj i ≠ 0})

/-- Discard zero projectors; the identity sum is retained, including for the
zero module where the remaining index type may be empty. -/
noncomputable def discardZeros (P : LinearProjectorFamily R M ι) :
    LinearProjectorFamily R M P.NonzeroIndex := by
  classical
  exact
    { proj := fun i ↦ P.proj i.val
      idempotent := fun i x ↦ P.idempotent i.val x
      orthogonal := fun hij x ↦ P.orthogonal (fun h ↦ hij (Subtype.ext h)) x
      complete := fun x ↦ by
        have h := Fintype.sum_subtype_add_sum_subtype
          (fun i : ι ↦ P.proj i ≠ 0) (fun i ↦ P.proj i x)
        have hz : (∑ i : {i : ι // ¬ P.proj i ≠ 0}, P.proj i.val x) = 0 := by
          apply Finset.sum_eq_zero
          intro i _
          have hi : P.proj i.val = 0 := not_not.mp i.property
          simp [hi]
        rw [hz, add_zero] at h
        exact h.trans (P.complete x) }

theorem discardZeros_proj_ne_zero (P : LinearProjectorFamily R M ι)
    (i : P.NonzeroIndex) : P.discardZeros.proj i ≠ 0 := i.property

/-- The packet system on the invariant submodule after all zero restricted
packets have been removed. -/
noncomputable def nonzeroRestriction
    (P : LinearProjectorFamily R M ι) (K : Submodule R M)
    (hK : P.Preserves K) :
    LinearProjectorFamily R K (P.restrictTo K hK).NonzeroIndex :=
  (P.restrictTo K hK).discardZeros

/-- The canonical quotient packet system after all zero descended packets
have been removed. Its index type need not equal the original index type. -/
noncomputable def nonzeroQuotient
    (P : LinearProjectorFamily R M ι) (K : Submodule R M)
    (hK : P.Preserves K) :
    LinearProjectorFamily R (M ⧸ K) (P.descendTo K hK).NonzeroIndex :=
  (P.descendTo K hK).discardZeros

/-- The quotient projectors are uniquely determined by intertwining with the
surjective quotient map. -/
theorem descendTo_unique
    (P : LinearProjectorFamily R M ι) (K : Submodule R M)
    (hK : P.Preserves K) (i : ι) (Q : Module.End R (M ⧸ K))
    (hQ : Q.comp K.mkQ = K.mkQ.comp (P.proj i)) :
    Q = (P.descendTo K hK).proj i := by
  apply LinearMap.ext
  intro z
  obtain ⟨x, rfl⟩ := K.mkQ_surjective z
  exact congrArg (fun f : M →ₗ[R] M ⧸ K ↦ f x) hQ

/-- A projector fixes every point in its range. -/
theorem proj_eq_self_of_mem_range (P : LinearProjectorFamily R M ι)
    (i : ι) {x : M} (hx : x ∈ LinearMap.range (P.proj i)) :
    P.proj i x = x := by
  obtain ⟨y, rfl⟩ := hx
  exact P.idempotent i y

/-- The restricted packet is exactly the intersection, as a submodule of `K`. -/
theorem restrictTo_range
    (P : LinearProjectorFamily R M ι) (K : Submodule R M)
    (hK : P.Preserves K) (i : ι) :
    LinearMap.range ((P.restrictTo K hK).proj i) =
      (LinearMap.range (P.proj i)).comap K.subtype := by
  ext x
  constructor
  · rintro ⟨y, rfl⟩
    exact ⟨(y : M), rfl⟩
  · intro hx
    exact ⟨x, Subtype.ext (P.proj_eq_self_of_mem_range i hx)⟩

/-- The same intersection after embedding the restricted packet in `M`. -/
theorem restrictTo_range_in_ambient
    (P : LinearProjectorFamily R M ι) (K : Submodule R M)
    (hK : P.Preserves K) (i : ι) :
    (LinearMap.range ((P.restrictTo K hK).proj i)).map K.subtype =
      K ⊓ LinearMap.range (P.proj i) := by
  rw [P.restrictTo_range]
  ext x
  constructor
  · rintro ⟨y, hy, rfl⟩
    exact ⟨y.property, hy⟩
  · rintro ⟨hxK, hxP⟩
    exact ⟨⟨x, hxK⟩, hxP, rfl⟩

/-- Quotient map restricted to the actual `i`th packet and corestricted to
the actual range of the descended projector. -/
def packetQuotientMap
    (P : LinearProjectorFamily R M ι) (K : Submodule R M)
    (hK : P.Preserves K) (i : ι) :
    LinearMap.range (P.proj i) →ₗ[R]
      LinearMap.range ((P.descendTo K hK).proj i) where
  toFun x := ⟨K.mkQ x, ⟨K.mkQ x, by
    rw [P.descendTo_proj_mkQ, P.proj_eq_self_of_mem_range i x.property]⟩⟩
  map_add' x y := Subtype.ext (K.mkQ.map_add x y)
  map_smul' a x := Subtype.ext (K.mkQ.map_smul a x)

@[simp] theorem packetQuotientMap_coe
    (P : LinearProjectorFamily R M ι) (K : Submodule R M)
    (hK : P.Preserves K) (i : ι) (x : LinearMap.range (P.proj i)) :
    (P.packetQuotientMap K hK i x : M ⧸ K) = K.mkQ x := rfl

theorem packetQuotientMap_surjective
    (P : LinearProjectorFamily R M ι) (K : Submodule R M)
    (hK : P.Preserves K) (i : ι) :
    Function.Surjective (P.packetQuotientMap K hK i) := by
  rintro ⟨z, y, hy⟩
  obtain ⟨x, rfl⟩ := K.mkQ_surjective y
  refine ⟨⟨P.proj i x, ⟨x, rfl⟩⟩, Subtype.ext ?_⟩
  exact hy

/-- The descended packet is exactly the image of the original packet under
the quotient map. -/
theorem descendTo_range
    (P : LinearProjectorFamily R M ι) (K : Submodule R M)
    (hK : P.Preserves K) (i : ι) :
    LinearMap.range ((P.descendTo K hK).proj i) =
      (LinearMap.range (P.proj i)).map K.mkQ := by
  ext z
  constructor
  · rintro ⟨y, rfl⟩
    obtain ⟨x, rfl⟩ := K.mkQ_surjective y
    exact ⟨P.proj i x, ⟨x, rfl⟩, rfl⟩
  · rintro ⟨x, ⟨y, rfl⟩, rfl⟩
    exact ⟨K.mkQ y, rfl⟩

/-- The inverse image of the quotient packet is the literal sum `X_i + K`. -/
theorem descendTo_range_preimage
    (P : LinearProjectorFamily R M ι) (K : Submodule R M)
    (hK : P.Preserves K) (i : ι) :
    (LinearMap.range ((P.descendTo K hK).proj i)).comap K.mkQ =
      LinearMap.range (P.proj i) ⊔ K := by
  rw [P.descendTo_range]
  ext x
  constructor
  · rintro ⟨y, hy, hxy⟩
    have hdiff : x - y ∈ K := by
      apply (Submodule.Quotient.eq K).mp
      exact hxy.symm
    exact Submodule.mem_sup.mpr ⟨y, hy, x - y, hdiff, by abel⟩
  · intro hx
    obtain ⟨y, hy, z, hz, rfl⟩ := Submodule.mem_sup.mp hx
    refine ⟨y, hy, ?_⟩
    rw [map_add, show K.mkQ z = 0 from (Submodule.Quotient.mk_eq_zero K).mpr hz,
      add_zero]

/-- Its kernel is literally the intersection inside the source packet. -/
theorem packetQuotientMap_ker
    (P : LinearProjectorFamily R M ι) (K : Submodule R M)
    (hK : P.Preserves K) (i : ι) :
    LinearMap.ker (P.packetQuotientMap K hK i) =
      K.comap (LinearMap.range (P.proj i)).subtype := by
  ext x
  change (P.packetQuotientMap K hK i x = 0) ↔ (x : M) ∈ K
  rw [← Subtype.val_inj]
  change (Submodule.Quotient.mk (x : M) : M ⧸ K) = Submodule.Quotient.mk 0 ↔ _
  simpa using (Submodule.Quotient.eq K (x := (x : M)) (y := 0))

/-- First-isomorphism equivalence from the actual packet quotient map. -/
noncomputable def packetQuotientEquiv
    (P : LinearProjectorFamily R M ι) (K : Submodule R M)
    (hK : P.Preserves K) (i : ι) :
    (LinearMap.range (P.proj i) ⧸ K.comap (LinearMap.range (P.proj i)).subtype)
      ≃ₗ[R] LinearMap.range ((P.descendTo K hK).proj i) :=
  (Submodule.quotEquivOfEq _ _ (P.packetQuotientMap_ker K hK i).symm).trans
    ((P.packetQuotientMap K hK i).quotKerEquivOfSurjective
      (P.packetQuotientMap_surjective K hK i))

/-- Second-isomorphism equivalence with `(X_i + K)/K`, with the denominator
explicitly pulled back to the sum submodule. -/
noncomputable def descendedPacketEquivSumQuotient
    (P : LinearProjectorFamily R M ι) (K : Submodule R M)
    (hK : P.Preserves K) (i : ι) :
    LinearMap.range ((P.descendTo K hK).proj i) ≃ₗ[R]
      (↥(LinearMap.range (P.proj i) ⊔ K) ⧸
        K.comap (LinearMap.range (P.proj i) ⊔ K).subtype) :=
  (P.packetQuotientEquiv K hK i).symm.trans
    ((Submodule.quotEquivOfEq _ _ (by simp)).trans
      (LinearMap.quotientInfEquivSupQuotient (LinearMap.range (P.proj i)) K))

/-- Transfer blocks preserve the invariant submodule and land in the target
packet, hence map every restricted source packet into the restricted target. -/
theorem transferBlock_preserves_packet
    (P : LinearProjectorFamily R M ι) (K : Submodule R M)
    (hK : P.Preserves K) (T : Module.End R M)
    (hT : ∀ x ∈ K, T x ∈ K) (j i : ι) {x : M}
    (hx : x ∈ K ⊓ LinearMap.range (P.proj i)) :
    transferBlock P P T j i x ∈ K ⊓ LinearMap.range (P.proj j) :=
  ⟨hK j _ (hT _ (hK i x hx.1)), ⟨T (P.proj i x), rfl⟩⟩

/-- Transfer blocks intertwine with the constructed quotient operator. -/
theorem transferBlock_descends
    (P : LinearProjectorFamily R M ι) (K : Submodule R M)
    (hK : P.Preserves K) (T : Module.End R M)
    (hT : ∀ x ∈ K, T x ∈ K) (j i : ι) :
    K.mkQ.comp (transferBlock P P T j i) =
      (transferBlock (P.descendTo K hK) (P.descendTo K hK)
        (K.mapQ K T hT) j i).comp K.mkQ := by
  ext x
  rfl

end Komorebi.Foundation.LinearProjectorFamily

#print axioms Komorebi.Foundation.LinearProjectorFamily.restrictTo
#print axioms Komorebi.Foundation.LinearProjectorFamily.descendTo
#print axioms Komorebi.Foundation.LinearProjectorFamily.discardZeros
#print axioms Komorebi.Foundation.LinearProjectorFamily.packetQuotientEquiv
#print axioms Komorebi.Foundation.LinearProjectorFamily.descendedPacketEquivSumQuotient
#print axioms Komorebi.Foundation.LinearProjectorFamily.transferBlock_descends
