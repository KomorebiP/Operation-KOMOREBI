module
public import CebotarevDensity.FixedFieldCore

/-! Arithmetic tower proofs extracted and adapted from CBirkbeck/AINTLIB's
FixedFieldDensity.lean at c62aa9dd4638d86b50f46d4000cf87157e333a6f.
Apache-2.0. These are actual rings of integers and intermediate fields.
This source does not assert existence of a base prime with prescribed Frobenius. -/

@[expose] public section
noncomputable section
open Filter NumberField Topology Set
open scoped ENNReal
namespace Chebotarev
variable {K L : Type*} [Field K] [NumberField K] [Field L] [NumberField L]
  [Algebra K L] [IsGalois K L]

open scoped Pointwise in
theorem inertiaDeg_under_E_eq_one_of_frobenius
    (σ : Gal(L/K)) (𝔓 : Ideal (𝓞 L)) [𝔓.IsPrime]
    (hunrK : UnramifiedIn K L (𝔓.under (𝓞 K))) (hPK : 𝔓.LiesOver (𝔓.under (𝓞 K)))
    (hfrob : IsArithFrobAt (𝓞 K) σ 𝔓)
    (horderE : orderOf σ = Nat.card Gal(L/(IntermediateField.fixedField (Subgroup.zpowers σ)))) :
    have : IsScalarTower K ↥(IntermediateField.fixedField (Subgroup.zpowers σ)) L :=
      (IntermediateField.fixedField (Subgroup.zpowers σ)).isScalarTower_mid'
    Ideal.ramificationIdx'
        (𝔓.under (𝓞 ↥(IntermediateField.fixedField (Subgroup.zpowers σ)))) 𝔓 = 1
      ∧ (𝔓.under (𝓞 ↥(IntermediateField.fixedField (Subgroup.zpowers σ)))).inertiaDeg (𝓞 K) = 1
      ∧ Nat.card (𝓞 ↥(IntermediateField.fixedField (Subgroup.zpowers σ))
            ⧸ 𝔓.under (𝓞 ↥(IntermediateField.fixedField (Subgroup.zpowers σ))))
          = Nat.card (𝓞 K ⧸ 𝔓.under (𝓞 K)) := by
  set E := IntermediateField.fixedField (Subgroup.zpowers σ) with hE
  have : IsScalarTower K ↥E L := E.isScalarTower_mid'
  have : IsGalois (↥E) L := IsGalois.tower_top_intermediateField _
  have hraK := UnramifiedIn.ramificationIdx_eq_one K L hunrK 𝔓 hPK
  have hPbot : 𝔓 ≠ ⊥ := ne_bot_of_ramificationIdx_eq_one K L hraK
  have hpbot : 𝔓.under (𝓞 K) ≠ ⊥ := UnramifiedIn.ne_bot K L hunrK
  have : 𝔓.IsMaximal := ‹𝔓.IsPrime›.isMaximal hPbot
  have : (𝔓.under (𝓞 K)).IsMaximal :=
    (inferInstance : (𝔓.under (𝓞 K)).IsPrime).isMaximal hpbot
  have : Finite (𝓞 L ⧸ 𝔓) := Ideal.finiteQuotientOfFreeOfNeBot 𝔓 hPbot
  have hPEp : (𝔓.under (𝓞 ↥E)).IsPrime := inferInstance
  have hPK' : 𝔓.LiesOver (𝔓.under (𝓞 K)) := Ideal.over_under (A := 𝓞 K) (P := 𝔓)
  have hPEK : (𝔓.under (𝓞 ↥E)).LiesOver (𝔓.under (𝓞 K)) := inferInstance
  have hPEL : 𝔓.LiesOver (𝔓.under (𝓞 ↥E)) := Ideal.over_under (A := 𝓞 ↥E) (P := 𝔓)
  have hPEbot : 𝔓.under (𝓞 ↥E) ≠ ⊥ := Ideal.IsIntegral.comap_ne_bot (𝓞 ↥E) hPbot
  have : (𝔓.under (𝓞 ↥E)).IsMaximal := hPEp.isMaximal hPEbot
  have hraE : (𝔓.under (𝓞 ↥E)).ramificationIdx' 𝔓 = 1 := by
    have hmul := Ideal.ramificationIdx'_algebra_tower' (𝔓.under (𝓞 K)) (𝔓.under (𝓞 ↥E)) 𝔓
    rw [hraK] at hmul
    exact Nat.eq_one_of_mul_eq_one_left hmul.symm
  have : Algebra.IsSeparable (𝓞 ↥E ⧸ 𝔓.under (𝓞 ↥E)) (𝓞 L ⧸ 𝔓) := by
    let : Field (𝓞 ↥E ⧸ 𝔓.under (𝓞 ↥E)) := Ideal.Quotient.field _
    let : Field (𝓞 L ⧸ 𝔓) := Ideal.Quotient.field _
    exact IsGalois.to_isSeparable
  have hstab := stabilizer_intermediate_eq_top_of_frobenius σ 𝔓 hunrK hPK hfrob horderE
  have hcardE : Nat.card (MulAction.stabilizer Gal(L/↥E) 𝔓) = Nat.card Gal(L/↥E) := by
    rw [hstab, Subgroup.card_top]
  have hfinE : 𝔓.inertiaDeg (𝓞 ↥E) = orderOf σ := by
    rw [Ideal.card_stabilizer_eq (𝔓.under (𝓞 ↥E)) 𝔓,
      Ideal.ramificationIdxIn_eq_ramificationIdx (𝔓.under (𝓞 ↥E)) 𝔓 Gal(L/↥E),
      ← Ideal.ramificationIdx'_eq_ramificationIdx (𝔓.under (𝓞 ↥E)) 𝔓 hPEbot, hraE, one_mul,
      Ideal.inertiaDegIn_eq_inertiaDeg (𝔓.under (𝓞 ↥E)) 𝔓 Gal(L/↥E)] at hcardE
    exact hcardE.trans horderE.symm
  have hfinK : 𝔓.inertiaDeg (𝓞 K) = orderOf σ := by
    rw [Ideal.inertiaDeg_eq_of_isMaximal (𝔓.under (𝓞 K)) 𝔓, orderOf_eq_finrank_of_isArithFrobAt K L σ 𝔓 hraK hfrob]
  have hdegree1 : (𝔓.under (𝓞 ↥E)).inertiaDeg (𝓞 K) = 1 := by
    have hmul := Ideal.inertiaDeg_tower (R := 𝓞 K) (𝔓.under (𝓞 ↥E)) 𝔓
    rw [hfinK, hfinE] at hmul
    have hpos : 0 < orderOf σ := orderOf_pos_iff.mpr (isOfFinOrder_of_finite σ)
    exact Nat.eq_of_mul_eq_mul_right hpos (by simpa using hmul.symm)
  refine ⟨hraE, hdegree1, ?_⟩
  have hn := Ideal.absNorm_pow_inertiaDeg (𝔓.under (𝓞 K)) (𝔓.under (𝓞 ↥E))
  rw [hdegree1, pow_one] at hn
  simpa only [Ideal.absNorm_apply, Submodule.cardQuot_apply] using hn.symm

open scoped Pointwise in
theorem unique_prime_above_of_full_order_frobenius (E : IntermediateField K L)
    (σE : Gal(L/↥E)) (P : Ideal (𝓞 ↥E)) [P.IsPrime]
    (hP : UnramifiedIn (↥E) L P) (hPfrob : frobeniusClass (↥E) L P = ConjClasses.mk σE)
    (hgen : orderOf σE = Nat.card Gal(L/↥E)) :
    ∃! 𝔓 : Ideal (𝓞 L), 𝔓.IsPrime ∧ 𝔓.LiesOver P ∧ 𝔓 ≠ ⊥ := by
  have : IsScalarTower K ↥E L := E.isScalarTower_mid'
  have : IsGalois (↥E) L := IsGalois.tower_top_intermediateField _
  have hmul := card_primesAbove_mul_orderOf_eq (↥E) L σE (ConjClasses.mk σE) rfl P hP hPfrob
  rw [hgen] at hmul
  have hcard : Nat.card {𝔓 : Ideal (𝓞 L) // 𝔓.IsPrime ∧ 𝔓.LiesOver P ∧ 𝔓 ≠ ⊥} = 1 :=
    Nat.eq_of_mul_eq_mul_right (Nat.card_pos (α := Gal(L/↥E))) (by simpa only [one_mul] using hmul)
  obtain ⟨hsub, hnonempty⟩ := Nat.card_eq_one_iff_unique.mp hcard
  let _ := hsub
  obtain ⟨𝔓₀⟩ := hnonempty
  exact ⟨𝔓₀.1, 𝔓₀.2, fun 𝔓 h ↦ congrArg Subtype.val
    (Subsingleton.elim (⟨𝔓, h⟩ : {Q : Ideal (𝓞 L) // Q.IsPrime ∧ Q.LiesOver P ∧ Q ≠ ⊥}) 𝔓₀)⟩

private theorem sigmaE_eq_arithFrobAt (σ : Gal(L/K))
    (σE : Gal(L/(IntermediateField.fixedField (Subgroup.zpowers σ))))
    (hσE : σE.restrictScalars K = σ)
    (𝔓 : Ideal (𝓞 L)) [𝔓.IsPrime] (hunrK : UnramifiedIn K L (𝔓.under (𝓞 K)))
    (hPK : 𝔓.LiesOver (𝔓.under (𝓞 K))) (hfrob : IsArithFrobAt (𝓞 K) σ 𝔓)
    (horderE : orderOf σ = Nat.card Gal(L/(IntermediateField.fixedField (Subgroup.zpowers σ)))) :
    have : IsScalarTower K ↥(IntermediateField.fixedField (Subgroup.zpowers σ)) L :=
      (IntermediateField.fixedField (Subgroup.zpowers σ)).isScalarTower_mid'
    have : IsGalois (↥(IntermediateField.fixedField (Subgroup.zpowers σ))) L :=
      IsGalois.tower_top_intermediateField _
    have : Finite (𝓞 L ⧸ 𝔓) := Ideal.finiteQuotientOfFreeOfNeBot 𝔓
      (ne_bot_of_ramificationIdx_eq_one K L
        (UnramifiedIn.ramificationIdx_eq_one K L hunrK 𝔓 hPK))
    σE = arithFrobAt (𝓞 ↥(IntermediateField.fixedField (Subgroup.zpowers σ)))
      Gal(L/↥(IntermediateField.fixedField (Subgroup.zpowers σ))) 𝔓 := by
  set E := IntermediateField.fixedField (Subgroup.zpowers σ)
  have : IsScalarTower K ↥E L := E.isScalarTower_mid'
  have : IsGalois (↥E) L := IsGalois.tower_top_intermediateField _
  have hraK := UnramifiedIn.ramificationIdx_eq_one K L hunrK 𝔓 hPK
  have : Finite (𝓞 L ⧸ 𝔓) :=
    Ideal.finiteQuotientOfFreeOfNeBot 𝔓 (ne_bot_of_ramificationIdx_eq_one K L hraK)
  obtain ⟨hraE, _, hnorm⟩ := inertiaDeg_under_E_eq_one_of_frobenius σ 𝔓 hunrK hPK hfrob horderE
  apply AlgEquiv.restrictScalars_injective K
  rw [hσE, arithFrobAt_restrictScalars_eq E 𝔓 hraK hraE hnorm]
  have hmem := hfrob.mul_inv_mem_inertia (IsArithFrobAt.arithFrobAt (𝓞 K) Gal(L/K) 𝔓)
  rw [inertiaGroup_trivial_of_unramified K L 𝔓 hraK, Subgroup.mem_bot] at hmem
  exact mul_inv_eq_one.mp hmem

open scoped Pointwise in
theorem fixedField_frobenius_degree_one
    (K L : Type*) [Field K] [NumberField K] [Field L] [NumberField L] [Algebra K L] [IsGalois K L]
    (σ : Gal(L/K)) (E : IntermediateField K L) (σE : Gal(L/↥E))
    (hE : E = IntermediateField.fixedField (Subgroup.zpowers σ))
    (hσE : σE.restrictScalars K = σ)
    (𝔓 : Ideal (𝓞 L)) [𝔓.IsPrime] (hunrK : UnramifiedIn K L (𝔓.under (𝓞 K)))
    (hPK : 𝔓.LiesOver (𝔓.under (𝓞 K))) (hfrob : IsArithFrobAt (𝓞 K) σ 𝔓) :
    have : IsScalarTower K ↥E L := E.isScalarTower_mid'
    have : IsGalois (↥E) L := IsGalois.tower_top_intermediateField _
    UnramifiedIn (↥E) L (𝔓.under (𝓞 ↥E)) ∧
      frobeniusClass (↥E) L (𝔓.under (𝓞 ↥E)) = ConjClasses.mk σE ∧
      (𝔓.under (𝓞 ↥E)).inertiaDeg (𝓞 K) = 1 := by
  revert σE
  subst E
  intro σE hσE
  let E : IntermediateField K L := IntermediateField.fixedField (Subgroup.zpowers σ)
  have : IsScalarTower K ↥E L := E.isScalarTower_mid'
  have : IsGalois (↥E) L := IsGalois.tower_top_intermediateField _
  have horderE : orderOf σ = Nat.card Gal(L/↥E) := by
    rw [← Nat.card_zpowers σ]
    exact Nat.card_congr (IntermediateField.subgroupEquivAlgEquiv (Subgroup.zpowers σ)).toEquiv
  obtain ⟨hraE, hdegree1, _hnorm⟩ := inertiaDeg_under_E_eq_one_of_frobenius σ 𝔓 hunrK hPK hfrob horderE
  have hraK := UnramifiedIn.ramificationIdx_eq_one K L hunrK 𝔓 hPK
  have hPbot : 𝔓 ≠ ⊥ := ne_bot_of_ramificationIdx_eq_one K L hraK
  have : 𝔓.IsMaximal := ‹𝔓.IsPrime›.isMaximal hPbot
  have : Finite (𝓞 L ⧸ 𝔓) := Ideal.finiteQuotientOfFreeOfNeBot 𝔓 hPbot
  have : (𝔓.under (𝓞 ↥E)).IsPrime := inferInstance
  have hpEbot : 𝔓.under (𝓞 ↥E) ≠ ⊥ := Ideal.IsIntegral.comap_ne_bot (𝓞 ↥E) hPbot
  have : (𝔓.under (𝓞 ↥E)).IsMaximal :=
    (inferInstance : (𝔓.under (𝓞 ↥E)).IsPrime).isMaximal hpEbot
  have hPEL : 𝔓.LiesOver (𝔓.under (𝓞 ↥E)) := Ideal.over_under (A := 𝓞 ↥E) (P := 𝔓)
  have hUnrE : UnramifiedIn (↥E) L (𝔓.under (𝓞 ↥E)) := by
    refine ⟨hpEbot, fun 𝔔 h𝔔max h𝔔lo ↦ ?_⟩
    have := h𝔔max.isPrime
    have := h𝔔lo
    have : Algebra.IsUnramifiedAt (𝓞 ↥E) 𝔓 :=
      Ideal.ramificationIdx_eq_one_iff.mp
        ((Ideal.ramificationIdx'_eq_ramificationIdx (𝔓.under (𝓞 ↥E)) 𝔓 hpEbot).symm.trans hraE)
    have heq : (𝔓.under (𝓞 ↥E)).ramificationIdx' 𝔔 = (𝔓.under (𝓞 ↥E)).ramificationIdx' 𝔓 := by
      rw [Ideal.ramificationIdx'_eq_ramificationIdx (𝔓.under (𝓞 ↥E)) 𝔔 hpEbot,
        Ideal.ramificationIdx'_eq_ramificationIdx (𝔓.under (𝓞 ↥E)) 𝔓 hpEbot]
      exact Ideal.ramificationIdx_eq_of_isGaloisGroup (𝔓.under (𝓞 ↥E)) 𝔔 𝔓 Gal(L/↥E)
    exact Ideal.ramificationIdx_eq_one_iff.mp
      ((Ideal.ramificationIdx'_eq_ramificationIdx (𝔓.under (𝓞 ↥E)) 𝔔 hpEbot).symm.trans (heq.trans hraE))
  refine ⟨hUnrE, ?_, hdegree1⟩
  have hsigmaEq := sigmaE_eq_arithFrobAt σ σE hσE 𝔓 hunrK hPK hfrob horderE
  have hσEfrob : IsArithFrobAt (𝓞 ↥E) σE 𝔓 :=
    hsigmaEq ▸ IsArithFrobAt.arithFrobAt (𝓞 ↥E) Gal(L/↥E) 𝔓
  exact frobeniusClass_eq_mk_of_isArithFrobAt (↥E) L (𝔓.under (𝓞 ↥E)) hUnrE σE 𝔓 hσEfrob hPEL

open scoped Pointwise in
theorem existsUnique_prime_above_fixedField
    (K L : Type*) [Field K] [NumberField K] [Field L] [NumberField L] [Algebra K L] [IsGalois K L]
    (σ : Gal(L/K)) (E : IntermediateField K L) (σE : Gal(L/↥E))
    (hE : E = IntermediateField.fixedField (Subgroup.zpowers σ))
    (hσE : σE.restrictScalars K = σ)
    (P : Ideal (𝓞 ↥E)) [P.IsPrime]
    (hunrK : UnramifiedIn K L (P.under (𝓞 K)))
    (hP : UnramifiedIn (↥E) L P) (hPfrob : frobeniusClass (↥E) L P = ConjClasses.mk σE)
    (hdeg : P.inertiaDeg (𝓞 K) = 1) :
    have : IsScalarTower K ↥E L := E.isScalarTower_mid'
    have : IsGalois (↥E) L := IsGalois.tower_top_intermediateField _
    ∃! 𝔓 : Ideal (𝓞 L), ∃ (_ : 𝔓.IsPrime) (_ : 𝔓.LiesOver P) (_ : 𝔓 ≠ ⊥),
      IsArithFrobAt (𝓞 K) σ 𝔓 := by
  have : IsScalarTower K ↥E L := E.isScalarTower_mid'
  have : IsGalois (↥E) L := IsGalois.tower_top_intermediateField _
  have hgen : orderOf σE = Nat.card Gal(L/↥E) := by
    have horderE : orderOf σ = Nat.card Gal(L/↥E) := by
      rw [hE, ← Nat.card_zpowers σ]
      exact Nat.card_congr (IntermediateField.subgroupEquivAlgEquiv (Subgroup.zpowers σ)).toEquiv
    rw [← horderE, ← hσE]
    exact (orderOf_injective (AlgEquiv.restrictScalarsHom K) (AlgEquiv.restrictScalars_injective K) σE).symm
  obtain ⟨𝔓₀, ⟨hprime, hlies, hne⟩, hunique⟩ :=
    unique_prime_above_of_full_order_frobenius E σE P hP hPfrob hgen
  have := hprime
  have := hlies
  have : Finite (𝓞 L ⧸ 𝔓₀) := Ideal.finiteQuotientOfFreeOfNeBot 𝔓₀ hne
  have hPE : 𝔓₀.under (𝓞 ↥E) = P := hlies.over.symm
  have hPK : 𝔓₀.under (𝓞 K) = P.under (𝓞 K) := by
    rw [← hPE, Ideal.under_under]
  have : 𝔓₀.LiesOver (P.under (𝓞 K)) := hPK ▸ (Ideal.over_under (A := 𝓞 K) (P := 𝔓₀))
  have hpbot : P.under (𝓞 K) ≠ ⊥ := UnramifiedIn.ne_bot K L hunrK
  have hnorm : Nat.card (𝓞 ↥E ⧸ 𝔓₀.under (𝓞 ↥E)) = Nat.card (𝓞 K ⧸ 𝔓₀.under (𝓞 K)) := by
    rw [hPE, hPK]
    have hn := Ideal.absNorm_pow_inertiaDeg (P.under (𝓞 K)) P
    rw [hdeg, pow_one] at hn
    simpa only [Ideal.absNorm_apply, Submodule.cardQuot_apply] using hn.symm
  have hraK : (𝔓₀.under (𝓞 K)).ramificationIdx' 𝔓₀ = 1 := by
    exact UnramifiedIn.ramificationIdx_eq_one K L hunrK 𝔓₀ inferInstance
  have hraE : (𝔓₀.under (𝓞 ↥E)).ramificationIdx' 𝔓₀ = 1 := by
    exact UnramifiedIn.ramificationIdx_eq_one (↥E) L hP 𝔓₀ hlies
  have hcommE : IsMulCommutative Gal(L/↥E) := by
    have : IsCyclic Gal(L/↥E) := isCyclic_iff_exists_orderOf_eq_natCard.mpr ⟨σE, hgen⟩
    infer_instance
  have hsigmaE : σE = arithFrobAt (𝓞 ↥E) Gal(L/↥E) 𝔓₀ := by
    let : CommGroup Gal(L/↥E) := { mul_comm := mul_comm' }
    have hclass := frobeniusClass_eq_mk_of_isArithFrobAt (↥E) L P hP
      (arithFrobAt (𝓞 ↥E) Gal(L/↥E) 𝔓₀) 𝔓₀ (IsArithFrobAt.arithFrobAt (𝓞 ↥E) Gal(L/↥E) 𝔓₀) hlies
    have hc : IsConj σE (arithFrobAt (𝓞 ↥E) Gal(L/↥E) 𝔓₀) :=
      ConjClasses.mk_eq_mk_iff_isConj.mp (hPfrob.symm.trans hclass)
    exact isConj_iff_eq.mp hc
  have hsigmaK : σ = arithFrobAt (𝓞 K) Gal(L/K) 𝔓₀ := by
    rw [← hσE, hsigmaE, arithFrobAt_restrictScalars_eq E 𝔓₀ hraK hraE hnorm]
  refine ⟨𝔓₀, ⟨hprime, hlies, hne, hsigmaK ▸ IsArithFrobAt.arithFrobAt (𝓞 K) Gal(L/K) 𝔓₀⟩, ?_⟩
  intro 𝔓 h
  obtain ⟨hpr, hL, h0, _⟩ := h
  exact hunique 𝔓 ⟨hpr, hL, h0⟩

end Chebotarev
