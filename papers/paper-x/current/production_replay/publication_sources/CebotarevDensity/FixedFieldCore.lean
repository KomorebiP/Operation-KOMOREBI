module

public import Mathlib.RingTheory.Ideal.Over
public import Mathlib.LinearAlgebra.Dimension.DivisionRing
public import Mathlib.NumberTheory.RamificationInertia.Inertia
public import Mathlib.NumberTheory.RamificationInertia.Ramification
public import Mathlib.RingTheory.Ideal.Norm.AbsNorm
public import Mathlib.RingTheory.SimpleModule.Basic
public import CebotarevDensity.Frobenius
public import CebotarevDensity.Density

/-!
# Fixed-field arithmetic core

Selected proofs from CBirkbeck/AINTLIB, commit
c62aa9dd4638d86b50f46d4000cf87157e333a6f,
projects/Chebotarev/CebotarevDensity/FixedFieldDensity.lean.
Apache-2.0; see LICENSE.AINTLIB.txt. This is a scoped source extraction,
not an authenticated copy or complete port of that upstream file.
The import of Cyclotomic is replaced by the already checked Frobenius
and Density modules. No density occurrence theorem is assumed here.
-/

@[expose] public section

noncomputable section

open Filter NumberField Topology Set
open scoped ENNReal

namespace Chebotarev

variable {K L : Type*} [Field K] [NumberField K] [Field L] [NumberField L]
  [Algebra K L] [IsGalois K L]

open scoped Pointwise in
/-- Conjugation gives an equivalence between arithmetic Frobenius fibres. -/
theorem frobeniusFibre_card_eq_of_isConj
    (K L : Type*) [Field K] [NumberField K] [Field L] [NumberField L] [Algebra K L] [IsGalois K L]
    (𝔭 : Ideal (𝓞 K)) [𝔭.IsPrime] (_hunr : UnramifiedIn K L 𝔭)
    (σ σ' : Gal(L/K)) (hc : IsConj σ σ') :
    Nat.card {𝔓 : Ideal (𝓞 L) // ∃ (_ : 𝔓.IsPrime) (_ : 𝔓.LiesOver 𝔭) (_ : 𝔓 ≠ ⊥),
        IsArithFrobAt (𝓞 K) σ 𝔓}
      = Nat.card {𝔓 : Ideal (𝓞 L) // ∃ (_ : 𝔓.IsPrime) (_ : 𝔓.LiesOver 𝔭) (_ : 𝔓 ≠ ⊥),
        IsArithFrobAt (𝓞 K) σ' 𝔓} := by
  obtain ⟨c, hc⟩ := isConj_iff.mp hc
  let f : Equiv.Perm (Ideal (𝓞 L)) := MulAction.toPerm c
  have hp : ∀ 𝔓 : Ideal (𝓞 L),
      (∃ (_ : 𝔓.IsPrime) (_ : 𝔓.LiesOver 𝔭) (_ : 𝔓 ≠ ⊥), IsArithFrobAt (𝓞 K) σ 𝔓)
        ↔ (∃ (_ : (f 𝔓).IsPrime) (_ : (f 𝔓).LiesOver 𝔭) (_ : f 𝔓 ≠ ⊥),
          IsArithFrobAt (𝓞 K) σ' (f 𝔓)) := by
    intro 𝔓
    change (∃ (_ : 𝔓.IsPrime) (_ : 𝔓.LiesOver 𝔭) (_ : 𝔓 ≠ ⊥),
        IsArithFrobAt (𝓞 K) σ 𝔓) ↔
      (∃ (_ : (c • 𝔓).IsPrime) (_ : (c • 𝔓).LiesOver 𝔭) (_ : c • 𝔓 ≠ ⊥),
        IsArithFrobAt (𝓞 K) σ' (c • 𝔓))
    constructor
    · rintro ⟨hp, hP, hne, hfrob⟩
      have := hp
      have := hP
      have : (c • 𝔓).IsPrime := Ideal.IsPrime.smul (I := 𝔓) c
      have hLc : (c • 𝔓).LiesOver 𝔭 := Ideal.LiesOver.smul (P := 𝔓) (p := 𝔭) c
      have hcne : c • 𝔓 ≠ ⊥ := by
        simpa only [Ideal.smul_bot] using (MulAction.injective c).ne hne
      refine ⟨inferInstance, hLc, hcne, ?_⟩
      rw [← hc]
      exact hfrob.conj c
    · rintro ⟨hp, hP, hne, hfrob⟩
      have := hp
      have := hP
      have hp' : 𝔓.IsPrime := by
        simpa only [inv_smul_smul] using (Ideal.IsPrime.smul (I := c • 𝔓) c⁻¹)
      have hP' : 𝔓.LiesOver 𝔭 := by
        simpa only [inv_smul_smul] using (Ideal.LiesOver.smul (P := c • 𝔓) (p := 𝔭) c⁻¹)
      have hne' : 𝔓 ≠ ⊥ := by
        simpa only [inv_smul_smul, Ideal.smul_bot] using (MulAction.injective c⁻¹).ne hne
      refine ⟨hp', hP', hne', ?_⟩
      have hf := hfrob.conj c⁻¹
      have hx : c⁻¹ * σ' * c⁻¹⁻¹ = σ := by rw [← hc]; group
      simpa only [hx, inv_smul_smul] using hf
  exact Nat.card_congr (Equiv.subtypeEquiv f hp)

set_option backward.isDefEq.respectTransparency false in
/-- Partition primes above a base prime into equipotent conjugacy-class fibres. -/
theorem card_primesAbove_eq_card_carrier_mul_frobeniusFibre
    (K L : Type*) [Field K] [NumberField K] [Field L] [NumberField L] [Algebra K L] [IsGalois K L]
    (σ : Gal(L/K)) (C : ConjClasses Gal(L/K)) (hσ : ConjClasses.mk σ = C)
    (𝔭 : Ideal (𝓞 K)) [𝔭.IsPrime] (hunr : UnramifiedIn K L 𝔭) (hCfrob : frobeniusClass K L 𝔭 = C)
    (hequi : ∀ σ' : Gal(L/K), IsConj σ σ' →
      Nat.card {𝔓 : Ideal (𝓞 L) // ∃ (_ : 𝔓.IsPrime) (_ : 𝔓.LiesOver 𝔭) (_ : 𝔓 ≠ ⊥),
          IsArithFrobAt (𝓞 K) σ 𝔓}
        = Nat.card {𝔓 : Ideal (𝓞 L) // ∃ (_ : 𝔓.IsPrime) (_ : 𝔓.LiesOver 𝔭) (_ : 𝔓 ≠ ⊥),
          IsArithFrobAt (𝓞 K) σ' 𝔓}) :
    Nat.card {𝔓 : Ideal (𝓞 L) // 𝔓.IsPrime ∧ 𝔓.LiesOver 𝔭 ∧ 𝔓 ≠ ⊥}
      = Nat.card C.carrier
        * Nat.card {𝔓 : Ideal (𝓞 L) // ∃ (_ : 𝔓.IsPrime) (_ : 𝔓.LiesOver 𝔭) (_ : 𝔓 ≠ ⊥),
          IsArithFrobAt (𝓞 K) σ 𝔓} := by
  have hpbot : 𝔭 ≠ ⊥ := UnramifiedIn.ne_bot K L hunr
  have : 𝔭.IsMaximal := ‹𝔭.IsPrime›.isMaximal hpbot
  have : Finite (𝔭.primesOver (𝓞 L)) := (IsDedekindDomain.primesOver_finite 𝔭 (𝓞 L)).to_subtype
  have : Finite {𝔓 : Ideal (𝓞 L) // 𝔓.IsPrime ∧ 𝔓.LiesOver 𝔭 ∧ 𝔓 ≠ ⊥} :=
    Finite.of_injective
      (fun 𝔓 : {𝔓 : Ideal (𝓞 L) // 𝔓.IsPrime ∧ 𝔓.LiesOver 𝔭 ∧ 𝔓 ≠ ⊥} ↦
        (⟨𝔓.1, 𝔓.2.1, 𝔓.2.2.1⟩ : 𝔭.primesOver (𝓞 L)))
      fun _ _ hab ↦ Subtype.ext (by simpa using hab)
  have : Fintype C.carrier := Fintype.ofFinite _
  have hfinP : ∀ (𝔓 : Ideal (𝓞 L)) [𝔓.IsPrime] (hP : 𝔓.LiesOver 𝔭), Finite (𝓞 L ⧸ 𝔓) :=
    fun 𝔓 _ hP ↦ UnramifiedIn.finite_quotient K L hunr 𝔓 hP
  have hmem : ∀ (𝔓 : Ideal (𝓞 L)) [𝔓.IsPrime] (hP : 𝔓.LiesOver 𝔭),
      haveI := hfinP 𝔓 hP
      arithFrobAt (𝓞 K) Gal(L/K) 𝔓 ∈ C.carrier := by
    intro 𝔓 _ hP
    have := hfinP 𝔓 hP
    rw [ConjClasses.mem_carrier_iff_mk_eq, ← frobeniusClass_eq_mk_of_isArithFrobAt K L 𝔭 hunr _ 𝔓
      (IsArithFrobAt.arithFrobAt (𝓞 K) Gal(L/K) 𝔓) hP, hCfrob]
  have hconj : ∀ g : C.carrier, IsConj σ g.1 := by
    rintro ⟨g, hg⟩
    rw [ConjClasses.mem_carrier_iff_mk_eq] at hg
    exact ConjClasses.mk_eq_mk_iff_isConj.mp (hσ.trans hg.symm)
  let F : {𝔓 : Ideal (𝓞 L) // 𝔓.IsPrime ∧ 𝔓.LiesOver 𝔭 ∧ 𝔓 ≠ ⊥} → C.carrier := fun 𝔓 ↦
    haveI := 𝔓.2.1
    haveI := hfinP 𝔓.1 𝔓.2.2.1
    ⟨arithFrobAt (𝓞 K) Gal(L/K) 𝔓.1, hmem 𝔓.1 𝔓.2.2.1⟩
  rw [← Nat.card_congr (Equiv.sigmaFiberEquiv F), Nat.card_sigma]
  have hfib : ∀ g : C.carrier,
      Nat.card {𝔓 // F 𝔓 = g}
        = Nat.card {𝔓 : Ideal (𝓞 L) // ∃ (_ : 𝔓.IsPrime) (_ : 𝔓.LiesOver 𝔭) (_ : 𝔓 ≠ ⊥),
            IsArithFrobAt (𝓞 K) σ 𝔓} := by
    intro g
    rw [hequi g.1 (hconj g)]
    refine Nat.card_congr ⟨fun x ↦ ⟨x.1.1, x.1.2.1, x.1.2.2.1, x.1.2.2.2, ?_⟩,
      fun x ↦ ⟨⟨x.1, by obtain ⟨hp, hP, hne, _⟩ := x.2; exact ⟨hp, hP, hne⟩⟩, ?_⟩,
      fun _ ↦ rfl, fun _ ↦ rfl⟩
    · have := x.1.2.1
      have := hfinP x.1.1 x.1.2.2.1
      rw [← Subtype.ext_iff.mp x.2]
      exact IsArithFrobAt.arithFrobAt (𝓞 K) Gal(L/K) x.1.1
    · obtain ⟨hp, hP, hne, hg⟩ := x.2
      have := hp
      have := hP
      have := hfinP x.1 hP
      have : Algebra.IsUnramifiedAt (𝓞 K) x.1 :=
        Ideal.ramificationIdx_eq_one_iff.mp
          ((Ideal.ramificationIdx'_eq_ramificationIdx (x.1.under (𝓞 K)) x.1
            (Ideal.IsIntegral.comap_ne_bot (𝓞 K) hne)).symm.trans
            (UnramifiedIn.ramificationIdx_eq_one K L hunr x.1 hP))
      exact Subtype.ext (eq_arithFrobAt_of_isArithFrobAt K L x.1 g.1 hg).symm
  simp_rw [hfib]
  rw [Finset.sum_const, Finset.card_univ, smul_eq_mul, ← Nat.card_eq_fintype_card]

/-- The Frobenius fibres occur evenly within the conjugacy class of a base prime. -/
theorem count_frobenius_eq_sigma_mul_card_carrier
    (K L : Type*) [Field K] [NumberField K] [Field L] [NumberField L] [Algebra K L] [IsGalois K L]
    (σ : Gal(L/K)) (C : ConjClasses Gal(L/K)) (_hσ : ConjClasses.mk σ = C)
    (𝔭 : Ideal (𝓞 K)) [𝔭.IsPrime] (hunr : UnramifiedIn K L 𝔭)
    (_hCfrob : frobeniusClass K L 𝔭 = C) :
    Nat.card {𝔓 : Ideal (𝓞 L) // ∃ (_ : 𝔓.IsPrime) (_ : 𝔓.LiesOver 𝔭)
        (_ : 𝔓 ≠ ⊥), IsArithFrobAt (𝓞 K) σ 𝔓}
      * Nat.card C.carrier
      = Nat.card {𝔓 : Ideal (𝓞 L) // 𝔓.IsPrime ∧ 𝔓.LiesOver 𝔭 ∧ 𝔓 ≠ ⊥} :=
  (mul_comm _ _).trans (card_primesAbove_eq_card_carrier_mul_frobeniusFibre K L σ C _hσ 𝔭 hunr
    _hCfrob fun σ' hc ↦ frobeniusFibre_card_eq_of_isConj K L 𝔭 hunr σ σ' hc).symm

/-- Exact arithmetic count; no occurrence assertion for an unprovided base prime. -/
theorem count_primes_above_with_frobenius_eq_sigma
    (K L : Type*) [Field K] [NumberField K] [Field L] [NumberField L] [Algebra K L] [IsGalois K L]
    (σ : Gal(L/K)) (C : ConjClasses Gal(L/K)) (_hσ : ConjClasses.mk σ = C)
    (𝔭 : Ideal (𝓞 K)) [𝔭.IsPrime] (hunr : UnramifiedIn K L 𝔭)
    (_hCfrob : frobeniusClass K L 𝔭 = C) :
    Nat.card {𝔓 : Ideal (𝓞 L) // ∃ (_ : 𝔓.IsPrime) (_ : 𝔓.LiesOver 𝔭)
        (_ : 𝔓 ≠ ⊥), IsArithFrobAt (𝓞 K) σ 𝔓}
      * orderOf σ * Nat.card C.carrier
      = Nat.card Gal(L/K) := by
  rw [mul_right_comm,
    count_frobenius_eq_sigma_mul_card_carrier K L σ C _hσ 𝔭 hunr _hCfrob]
  exact card_primesAbove_mul_orderOf_eq K L σ C _hσ 𝔭 hunr _hCfrob

omit [IsGalois K L] in
/-- Prime-ideal zeta sums in the two fields have the same logarithmic leading term. -/
private theorem univ_ratio_E_K_tendsto_one (E : IntermediateField K L) :
    Tendsto (fun s : ℝ ↦ primeIdealZetaSum (univ : Set (Ideal (𝓞 ↥E))) s
        / primeIdealZetaSum (univ : Set (Ideal (𝓞 K))) s) (𝓝[>] 1) (𝓝 1) := by
  have hcancel := (primeIdealZetaSum_univ_tendsto_log (↥E)).div
    (primeIdealZetaSum_univ_tendsto_log K) one_ne_zero
  rw [one_div_one] at hcancel
  refine hcancel.congr' ?_
  filter_upwards [tendsto_log_one_div_sub_one_atTop.eventually_gt_atTop 0] with s hs
  simp only [Pi.div_apply]
  rw [div_div_div_cancel_right₀ hs.ne']

open scoped Pointwise in
/-- Equality of residue norms identifies the restricted arithmetic Frobenius. -/
theorem arithFrobAt_restrictScalars_eq (E : IntermediateField K L)
    (𝔓 : Ideal (𝓞 L)) [𝔓.IsPrime] (hunrK : Ideal.ramificationIdx' (𝔓.under (𝓞 K)) 𝔓 = 1)
    (_hunrE : Ideal.ramificationIdx' (𝔓.under (𝓞 ↥E)) 𝔓 = 1)
    (hnorm : Nat.card (𝓞 ↥E ⧸ 𝔓.under (𝓞 ↥E)) = Nat.card (𝓞 K ⧸ 𝔓.under (𝓞 K))) :
    haveI : IsScalarTower K ↥E L := E.isScalarTower_mid'
    haveI : Finite (𝓞 L ⧸ 𝔓) :=
      Ideal.finiteQuotientOfFreeOfNeBot 𝔓 (ne_bot_of_ramificationIdx_eq_one K L hunrK)
    haveI : IsGalois (↥E) L := IsGalois.tower_top_intermediateField E
    (arithFrobAt (𝓞 ↥E) Gal(L/(↥E)) 𝔓).restrictScalars K = arithFrobAt (𝓞 K) Gal(L/K) 𝔓 := by
  have : IsScalarTower K ↥E L := E.isScalarTower_mid'
  have : IsGalois (↥E) L := IsGalois.tower_top_intermediateField E
  have : IsGaloisGroup Gal(L/(↥E)) (↥E) L := IsGaloisGroup.of_isGalois (↥E) L
  have hPbot : 𝔓 ≠ ⊥ := ne_bot_of_ramificationIdx_eq_one K L hunrK
  have : Finite (𝓞 L ⧸ 𝔓) := Ideal.finiteQuotientOfFreeOfNeBot 𝔓 hPbot
  set σE := arithFrobAt (𝓞 ↥E) Gal(L/(↥E)) 𝔓 with hσE
  have hKfrob1 : IsArithFrobAt (𝓞 K) (σE.restrictScalars K) 𝔓 := by
    intro x
    have hact : (σE.restrictScalars K) • x = σE • x := Subtype.ext (by
      change (σE.restrictScalars K) • (x : L) = σE • (x : L)
      rw [AlgEquiv.smul_def, AlgEquiv.smul_def, AlgEquiv.restrictScalars_apply])
    change (MulSemiringAction.toAlgHom (𝓞 K) (𝓞 L) (σE.restrictScalars K)) x
      - x ^ Nat.card (𝓞 K ⧸ 𝔓.under (𝓞 K)) ∈ 𝔓
    rw [show x ^ Nat.card (𝓞 K ⧸ 𝔓.under (𝓞 K))
          = x ^ Nat.card (𝓞 ↥E ⧸ 𝔓.under (𝓞 ↥E)) by rw [hnorm],
      show (MulSemiringAction.toAlgHom (𝓞 K) (𝓞 L) (σE.restrictScalars K)) x = σE • x by
        rw [← hact]
        rfl]
    exact IsArithFrobAt.arithFrobAt (𝓞 ↥E) Gal(L/(↥E)) 𝔓 x
  have hmem := hKfrob1.mul_inv_mem_inertia (IsArithFrobAt.arithFrobAt (𝓞 K) Gal(L/K) 𝔓)
  rw [inertiaGroup_trivial_of_unramified K L 𝔓 hunrK, Subgroup.mem_bot] at hmem
  exact mul_inv_eq_one.mp hmem

open scoped Pointwise in
/-- In the cyclic fixed field, every relative automorphism fixes the prime. -/
theorem stabilizer_intermediate_eq_top_of_frobenius
    (σ : Gal(L/K)) (𝔓 : Ideal (𝓞 L)) [𝔓.IsPrime]
    (hunrK : UnramifiedIn K L (𝔓.under (𝓞 K))) (hPK : 𝔓.LiesOver (𝔓.under (𝓞 K)))
    (hfrob : IsArithFrobAt (𝓞 K) σ 𝔓)
    (_horderE : orderOf σ = Nat.card Gal(L/(IntermediateField.fixedField (Subgroup.zpowers σ)))) :
    haveI : IsScalarTower K ↥(IntermediateField.fixedField (Subgroup.zpowers σ)) L :=
      (IntermediateField.fixedField (Subgroup.zpowers σ)).isScalarTower_mid'
    MulAction.stabilizer
        Gal(L/↥(IntermediateField.fixedField (Subgroup.zpowers σ))) 𝔓 = ⊤ := by
  have : IsScalarTower K ↥(IntermediateField.fixedField (Subgroup.zpowers σ)) L :=
    (IntermediateField.fixedField (Subgroup.zpowers σ)).isScalarTower_mid'
  have hraK := UnramifiedIn.ramificationIdx_eq_one K L hunrK 𝔓 hPK
  have hPbot : 𝔓 ≠ ⊥ := ne_bot_of_ramificationIdx_eq_one K L hraK
  have hpbot : 𝔓.under (𝓞 K) ≠ ⊥ := UnramifiedIn.ne_bot K L hunrK
  have : 𝔓.IsMaximal := ‹𝔓.IsPrime›.isMaximal hPbot
  have : (𝔓.under (𝓞 K)).IsMaximal :=
    (inferInstance : (𝔓.under (𝓞 K)).IsPrime).isMaximal hpbot
  have : Finite (𝓞 L ⧸ 𝔓) := Ideal.finiteQuotientOfFreeOfNeBot 𝔓 hPbot
  have : Algebra.IsSeparable (𝓞 K ⧸ 𝔓.under (𝓞 K)) (𝓞 L ⧸ 𝔓) := by
    let : Field (𝓞 K ⧸ 𝔓.under (𝓞 K)) := Ideal.Quotient.field _
    let : Field (𝓞 L ⧸ 𝔓) := Ideal.Quotient.field _
    exact IsGalois.to_isSeparable
  have hmem : σ ∈ MulAction.stabilizer Gal(L/K) 𝔓 := hfrob.mem_stabilizer
  have hinertK : 𝔓.inertiaDeg (𝓞 K) = orderOf σ := by
    rw [Ideal.inertiaDeg_eq_of_isMaximal (𝔓.under (𝓞 K)) 𝔓, orderOf_eq_finrank_of_isArithFrobAt K L σ 𝔓 hraK hfrob]
  have hcardstab' : Nat.card (MulAction.stabilizer Gal(L/K) 𝔓) = orderOf σ := by
    rw [Ideal.card_stabilizer_eq (𝔓.under (𝓞 K)) 𝔓,
      Ideal.ramificationIdxIn_eq_ramificationIdx (𝔓.under (𝓞 K)) 𝔓 Gal(L/K),
      ← Ideal.ramificationIdx'_eq_ramificationIdx (𝔓.under (𝓞 K)) 𝔓 hpbot, hraK, one_mul,
      Ideal.inertiaDegIn_eq_inertiaDeg (𝔓.under (𝓞 K)) 𝔓 Gal(L/K),
      hinertK]
  have hstab : Subgroup.zpowers σ = MulAction.stabilizer Gal(L/K) 𝔓 :=
    Subgroup.eq_of_le_of_card_ge (by rwa [Subgroup.zpowers_le])
      (by rw [Nat.card_zpowers, hcardstab'])
  rw [eq_top_iff]
  intro τ _
  rw [MulAction.mem_stabilizer_iff]
  change τ • 𝔓 = 𝔓
  have hmemfix : τ.restrictScalars K
      ∈ IntermediateField.fixingSubgroup (IntermediateField.fixedField (Subgroup.zpowers σ)) :=
    fun x ↦ τ.commutes x
  rw [IntermediateField.fixingSubgroup_fixedField (Subgroup.zpowers σ)] at hmemfix
  have hstabmem : τ.restrictScalars K ∈ MulAction.stabilizer Gal(L/K) 𝔓 := hstab ▸ hmemfix
  exact MulAction.mem_stabilizer_iff.mp hstabmem

end Chebotarev
