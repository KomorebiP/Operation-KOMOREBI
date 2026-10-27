/-
Fixed-field fibre assembly for the Paper X continuation.
Builds on the attributed AINTLIB arithmetic extraction in FixedFieldCore and FixedFieldTower.
-/
module
public import CebotarevDensity.FixedFieldTower

@[expose] public section
noncomputable section
open NumberField
namespace Chebotarev.FixedFieldFibres

variable (K L : Type*) [Field K] [NumberField K] [Field L] [NumberField L]
  [Algebra K L] [IsGalois K L]

/-- Primes of the top field with a specified arithmetic Frobenius over a fixed base prime. -/
def TopFibre (σ : Gal(L/K)) (𝔭 : Ideal (𝓞 K)) :=
  {𝔓 : Ideal (𝓞 L) // ∃ (_ : 𝔓.IsPrime) (_ : 𝔓.LiesOver 𝔭) (_ : 𝔓 ≠ ⊥),
    IsArithFrobAt (𝓞 K) σ 𝔓}

/-- Relative Frobenius primes of residue degree one over the fixed base prime. -/
def MiddleFibre (E : IntermediateField K L) (σE : Gal(L/↥E)) (𝔭 : Ideal (𝓞 K)) :=
  {P : Ideal (𝓞 ↥E) // P.IsPrime ∧ P.LiesOver 𝔭 ∧ UnramifiedIn (↥E) L P ∧
    frobeniusClass (↥E) L P = ConjClasses.mk σE ∧ P.inertiaDeg (𝓞 K) = 1}

/-- Contraction is a bijection, not merely a comparison of cardinalities. -/
def contractionEquiv
    (σ : Gal(L/K)) (E : IntermediateField K L) (σE : Gal(L/↥E))
    (hE : E = IntermediateField.fixedField (Subgroup.zpowers σ))
    (hσE : σE.restrictScalars K = σ)
    (𝔭 : Ideal (𝓞 K)) [𝔭.IsPrime] (hunr : UnramifiedIn K L 𝔭) :
    TopFibre K L σ 𝔭 ≃ MiddleFibre K L E σE 𝔭 := by
  have : IsScalarTower K ↥E L := E.isScalarTower_mid'
  have : IsGalois (↥E) L := IsGalois.tower_top_intermediateField E
  let F : TopFibre K L σ 𝔭 → MiddleFibre K L E σE 𝔭 := fun Q ↦ ⟨Q.1.under (𝓞 ↥E), by
    obtain ⟨hQp, hQlo, hQne, hQfr⟩ := Q.2
    have := hQp
    have := hQlo
    have hQunder : Q.1.under (𝓞 K) = 𝔭 := hQlo.over.symm
    have hQu : UnramifiedIn K L (Q.1.under (𝓞 K)) := by rwa [hQunder]
    obtain ⟨hu, hf, hd⟩ := fixedField_frobenius_degree_one K L σ E σE hE hσE Q.1
      hQu (Ideal.over_under (A := 𝓞 K) (P := Q.1)) hQfr
    have hmiddle : (Q.1.under (𝓞 ↥E)).LiesOver 𝔭 := by
      have : (Q.1.under (𝓞 ↥E)).LiesOver (Q.1.under (𝓞 K)) := inferInstance
      rwa [hQunder] at this
    exact ⟨inferInstance, hmiddle, hu, hf, hd⟩⟩
  refine Equiv.ofBijective F ⟨?_, ?_⟩
  · intro Q R hQR
    obtain ⟨hQp, hQlo, hQne, hQfr⟩ := Q.2
    obtain ⟨hRp, hRlo, hRne, hRfr⟩ := R.2
    have := hQp
    have := hRp
    have := hQlo
    have := hRlo
    have hUnder : Q.1.under (𝓞 ↥E) = R.1.under (𝓞 ↥E) := congrArg Subtype.val hQR
    have hQmiddle : Q.1.LiesOver (Q.1.under (𝓞 ↥E)) := Ideal.over_under (A := 𝓞 ↥E) (P := Q.1)
    have hRmiddle : R.1.LiesOver (Q.1.under (𝓞 ↥E)) := ⟨hUnder⟩
    have hm := (F Q).2
    have huK : UnramifiedIn K L ((Q.1.under (𝓞 ↥E)).under (𝓞 K)) := by
      rw [Ideal.under_under, ← hQlo.over]
      exact hunr
    obtain ⟨P₀, _, huniq⟩ := existsUnique_prime_above_fixedField K L σ E σE hE hσE
      (Q.1.under (𝓞 ↥E)) huK hm.2.2.1 hm.2.2.2.1 hm.2.2.2.2
    exact Subtype.ext ((huniq Q.1 ⟨hQp, hQmiddle, hQne, hQfr⟩).trans
      (huniq R.1 ⟨hRp, hRmiddle, hRne, hRfr⟩).symm)
  · intro P
    obtain ⟨hPp, hPlo, hPu, hPf, hPd⟩ := P.2
    have := hPp
    have := hPlo
    have huK : UnramifiedIn K L (P.1.under (𝓞 K)) := by rw [← hPlo.over]; exact hunr
    obtain ⟨Q, ⟨hQp, hQlo, hQne, hQfr⟩, _⟩ := existsUnique_prime_above_fixedField
      K L σ E σE hE hσE P.1 huK hPu hPf hPd
    have := hQp
    have := hQlo
    have hQbase : Q.LiesOver 𝔭 := Ideal.LiesOver.trans Q P.1 𝔭
    exact ⟨⟨Q, hQp, hQbase, hQne, hQfr⟩, Subtype.ext hQlo.over.symm⟩

/-- The forward map is the actual contraction of prime ideals. -/
@[simp] theorem contractionEquiv_apply
    (σ : Gal(L/K)) (E : IntermediateField K L) (σE : Gal(L/↥E))
    (hE : E = IntermediateField.fixedField (Subgroup.zpowers σ))
    (hσE : σE.restrictScalars K = σ)
    (𝔭 : Ideal (𝓞 K)) [𝔭.IsPrime] (hunr : UnramifiedIn K L 𝔭)
    (Q : TopFibre K L σ 𝔭) :
    ((contractionEquiv K L σ E σE hE hσE 𝔭 hunr) Q).1 = Q.1.under (𝓞 ↥E) := rfl

/-- The chosen relative generator is constructed by Galois correspondence. -/
def generator (σ : Gal(L/K)) :
    Gal(L/↥(IntermediateField.fixedField (Subgroup.zpowers σ))) :=
  IntermediateField.subgroupEquivAlgEquiv (Subgroup.zpowers σ) ⟨σ, Subgroup.mem_zpowers σ⟩

omit [IsGalois K L] in
@[simp] theorem generator_restrict (σ : Gal(L/K)) :
    (generator K L σ).restrictScalars K = σ := rfl

/-- Exact middle-field fibre count at a supplied unramified base prime.
The relative field and relative Frobenius are constructed, not additional hypotheses. -/
theorem middle_fibre_count (σ : Gal(L/K))
    (𝔭 : Ideal (𝓞 K)) [𝔭.IsPrime] (hunr : UnramifiedIn K L 𝔭)
    (hfrob : frobeniusClass K L 𝔭 = ConjClasses.mk σ) :
    Nat.card (MiddleFibre K L (IntermediateField.fixedField (Subgroup.zpowers σ))
        (generator K L σ) 𝔭) * orderOf σ * Nat.card (ConjClasses.mk σ).carrier
      = Nat.card Gal(L/K) := by
  have hc := Nat.card_congr (contractionEquiv K L σ
    (IntermediateField.fixedField (Subgroup.zpowers σ)) (generator K L σ)
    rfl (generator_restrict K L σ) 𝔭 hunr).symm
  rw [hc]
  exact count_primes_above_with_frobenius_eq_sigma K L σ (ConjClasses.mk σ) rfl 𝔭 hunr hfrob

end Chebotarev.FixedFieldFibres
