module
public import CebotarevDensity.Frobenius
public import Mathlib.NumberTheory.RamificationInertia.Ramification

/-! Actual normal restriction and unramified descent in K <= L <= M.
Reconstructed from the tower lemmas of the pinned AINTLIB Abelian development.
No Frobenius occurrence is assumed in the projection construction. -/
@[expose] public section
noncomputable section
open NumberField Chebotarev
namespace PaperX.FrobeniusTowerProjection
variable (K L M : Type*) [Field K] [NumberField K] [Field L] [NumberField L]
    [Field M] [NumberField M] [Algebra K L] [Algebra K M] [Algebra L M]
    [IsScalarTower K L M] [IsGalois K L] [IsGalois K M]

omit [NumberField K] [NumberField L] [NumberField M] [IsGalois K M] in
theorem smul_algebraMap (σ : Gal(M/K)) (y : 𝓞 L) :
    σ • (algebraMap (𝓞 L) (𝓞 M) y) =
      algebraMap (𝓞 L) (𝓞 M) ((σ.restrictNormal L) • y) := by
  have : IsScalarTower (𝓞 K) (𝓞 L) (𝓞 M) := inferInstance
  have hM : ∀ (g : M ≃ₐ[K] M) (x : 𝓞 M), ((g • x : 𝓞 M) : M) = g • (x : M) :=
    fun g x ↦ by simpa [Algebra.smul_def] using
      (smul_distrib_smul (G := M ≃ₐ[K] M) (R := 𝓞 M) (S := M) g x 1).symm
  have hL : ∀ (g : L ≃ₐ[K] L) (x : 𝓞 L), ((g • x : 𝓞 L) : L) = g • (x : L) :=
    fun g x ↦ by simpa [Algebra.smul_def] using
      (smul_distrib_smul (G := L ≃ₐ[K] L) (R := 𝓞 L) (S := L) g x 1).symm
  have hcoe : ∀ z : 𝓞 L, ((algebraMap (𝓞 L) (𝓞 M) z : 𝓞 M) : M) = algebraMap L M (z : L) :=
    fun z ↦ by
      rw [RingOfIntegers.coe_eq_algebraMap, ← IsScalarTower.algebraMap_apply (𝓞 L) (𝓞 M) M,
        RingOfIntegers.coe_eq_algebraMap, ← IsScalarTower.algebraMap_apply (𝓞 L) L M]
  rw [RingOfIntegers.ext_iff, hM, hcoe y, hcoe ((σ.restrictNormal L) • y), hL,
    AlgEquiv.smul_def, AlgEquiv.smul_def, AlgEquiv.restrictNormal_commutes]

theorem isArithFrobAt_restrict (σ : Gal(M/K)) (P : Ideal (𝓞 M))
    (hσ : IsArithFrobAt (𝓞 K) σ P) :
    IsArithFrobAt (𝓞 K) (σ.restrictNormal L) (P.under (𝓞 L)) := by
  have : IsScalarTower (𝓞 K) (𝓞 L) (𝓞 M) := inferInstance
  have hunder : (P.under (𝓞 L)).under (𝓞 K) = P.under (𝓞 K) := Ideal.under_under P
  intro y
  rw [hunder, Ideal.under, Ideal.mem_comap, map_sub, map_pow,
    MulSemiringAction.toAlgHom_apply, ← smul_algebraMap K L M σ y]
  exact hσ (algebraMap (𝓞 L) (𝓞 M) y)


/-- Actual unramifiedness descends from M to the intermediate field L. -/
theorem unramified_descend (p : Ideal (𝓞 K)) (hunr : UnramifiedIn K M p) :
    UnramifiedIn K L p := by
  refine ⟨hunr.1, ?_⟩
  intro q hqmax hqlo
  have := hqmax.isPrime
  have := hqlo
  have hqbot : q ≠ ⊥ := Ideal.ne_bot_of_liesOver_of_ne_bot hunr.1 q
  obtain ⟨P, hPp, hPloq, hPbot⟩ := exists_prime_liesOver L M q hqbot
  have := hPp
  have := hPloq
  have hPlop : P.LiesOver p := ⟨by
    rw [hqlo.over, hPloq.over, Ideal.under_under]⟩
  have heP : p.ramificationIdx' P = 1 := by
    have h := UnramifiedIn.ramificationIdx_eq_one K M hunr P hPlop
    rwa [← hPlop.over] at h
  have htower := Ideal.ramificationIdx'_algebra_tower' p q P
  rw [heP] at htower
  have heq : p.ramificationIdx' q = 1 := Nat.eq_one_of_mul_eq_one_right htower.symm
  rw [← Ideal.ramificationIdx_eq_one_iff,
    ← Ideal.ramificationIdx'_eq_ramificationIdx p q hunr.1]
  exact heq

/-- Conjugacy classes of actual arithmetic Frobenius commute with normal restriction. -/
theorem frobeniusClass_project
    (σ : Gal(L/K)) (s : Gal(M/K)) (hrestr : AlgEquiv.restrictNormalHom L s = σ)
    (p : Ideal (𝓞 K)) [p.IsPrime] (hunrM : UnramifiedIn K M p)
    (hfr : frobeniusClass K M p = ConjClasses.mk s) :
    frobeniusClass K L p = ConjClasses.mk σ := by
  have hunrL : UnramifiedIn K L p := unramified_descend K L M p hunrM
  obtain ⟨P, hPp, hPlo, hPbot⟩ := exists_prime_liesOver K M p hunrM.1
  have := hPp
  have := hPlo
  have : Finite (𝓞 M ⧸ P) := Ideal.finiteQuotientOfFreeOfNeBot P hPbot
  let t : Gal(M/K) := arithFrobAt (𝓞 K) Gal(M/K) P
  have ht : IsArithFrobAt (𝓞 K) t P := IsArithFrobAt.arithFrobAt (𝓞 K) Gal(M/K) P
  have hc : IsConj t s := ConjClasses.mk_eq_mk_iff_isConj.mp
    ((frobeniusClass_eq_mk_of_isArithFrobAt K M p hunrM t P ht hPlo).symm.trans hfr)
  have : (P.under (𝓞 L)).IsPrime := Ideal.IsPrime.under (𝓞 L) P
  have : (P.under (𝓞 L)).LiesOver p :=
    ⟨((Ideal.under_under P).trans hPlo.over.symm).symm⟩
  rw [frobeniusClass_eq_mk_of_isArithFrobAt K L p hunrL (t.restrictNormal L)
    (P.under (𝓞 L)) (isArithFrobAt_restrict K L M t P ht) inferInstance]
  apply ConjClasses.mk_eq_mk_iff_isConj.mpr
  have hcL := MonoidHom.map_isConj (AlgEquiv.restrictNormalHom L) hc
  rwa [hrestr] at hcL

end PaperX.FrobeniusTowerProjection
