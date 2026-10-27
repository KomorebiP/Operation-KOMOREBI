import PaperX.ChebotarevPrimeIdealAdapter

/-!
# External Chebotarev API adapter

This module isolates the exact four properties required from an external
prime-ideal Chebotarev formalization and proves that they imply the qualitative
prime-ideal occurrence contract consumed by Paper X.
-/
set_option autoImplicit false
noncomputable section

namespace PaperX.ChebotarevExternalAPIAdapter

open NumberField
open PaperX.AbsoluteIntegralFrobenius
open PaperX.ChebotarevPrimeIdealAdapter

local instance (L : FiniteGaloisIntermediateField ℚ Qbar) : NumberField L := ⟨⟩

/-- The exact external API needed from a Chebotarev development. -/
structure API where
  UnramifiedIn :
    (L : FiniteGaloisIntermediateField ℚ Qbar) → Ideal (𝓞 ℚ) → Prop
  frobeniusClass :
    (L : FiniteGaloisIntermediateField ℚ Qbar) →
      Ideal (𝓞 ℚ) → ConjClasses Gal(L/ℚ)
  unramified_ne_bot :
    ∀ (L : FiniteGaloisIntermediateField ℚ Qbar) (𝔭 : Ideal (𝓞 ℚ)),
      UnramifiedIn L 𝔭 → 𝔭 ≠ ⊥
  unramified_at :
    ∀ (L : FiniteGaloisIntermediateField ℚ Qbar) (𝔭 : Ideal (𝓞 ℚ)),
      UnramifiedIn L 𝔭 →
      ∀ (P : Ideal (𝓞 L)) (_ : P.IsMaximal), P.LiesOver 𝔭 →
        Algebra.IsUnramifiedAt (𝓞 ℚ) P
  frobeniusClass_eq_mk_of_isArithFrobAt :
    ∀ (L : FiniteGaloisIntermediateField ℚ Qbar)
      (𝔭 : Ideal (𝓞 ℚ)) (_ : 𝔭.IsPrime),
      UnramifiedIn L 𝔭 →
      ∀ (τ : Gal(L/ℚ)) (P : Ideal (𝓞 L)) (_ : P.IsPrime),
        IsArithFrobAt (𝓞 ℚ) τ P → P.LiesOver 𝔭 →
          frobeniusClass L 𝔭 = ConjClasses.mk τ
  infinite_setOf_frobenius_class :
    ∀ (L : FiniteGaloisIntermediateField ℚ Qbar)
      (C : ConjClasses Gal(L/ℚ)),
      Set.Infinite
        {𝔭 : Ideal (𝓞 ℚ) |
          𝔭.IsPrime ∧ UnramifiedIn L 𝔭 ∧ frobeniusClass L 𝔭 = C}

/-- A nonzero prime ideal of `𝓞 ℚ` has a nonzero prime of `𝓞 L` above it. -/
theorem exists_prime_liesOver
    (L : FiniteGaloisIntermediateField ℚ Qbar)
    (𝔭 : Ideal (𝓞 ℚ)) [𝔭.IsPrime] (h𝔭ne : 𝔭 ≠ ⊥) :
    ∃ P : Ideal (𝓞 L), P.IsPrime ∧ P.LiesOver 𝔭 ∧ P ≠ ⊥ := by
  obtain ⟨P, hP, hcomap⟩ :=
    Ideal.exists_ideal_over_prime_of_isIntegral_of_isDomain
      (S := 𝓞 L) 𝔭 (by
        rw [(RingHom.injective_iff_ker_eq_bot _).mp
          (FaithfulSMul.algebraMap_injective (𝓞 ℚ) (𝓞 L))]
        exact bot_le)
  have hPover : P.LiesOver 𝔭 := ⟨hcomap.symm⟩
  exact ⟨P, hP, hPover,
    Ideal.ne_bot_of_liesOver_of_ne_bot h𝔭ne P⟩

/-- Any external implementation satisfying `API` supplies exactly the
prime-ideal occurrence statement needed by the Paper-X adapter. -/
theorem primeIdealChebotarevOccurrence_of_API (A : API) :
    PrimeIdealChebotarevOccurrence := by
  intro L σ
  apply (A.infinite_setOf_frobenius_class L (ConjClasses.mk σ)).mono
  intro 𝔭 h𝔭
  rcases h𝔭 with ⟨h𝔭prime, h𝔭unr, h𝔭class⟩
  have h𝔭ne : 𝔭 ≠ ⊥ := A.unramified_ne_bot L 𝔭 h𝔭unr
  let : 𝔭.IsPrime := h𝔭prime
  obtain ⟨P, hPprime, hPover, hPne⟩ := exists_prime_liesOver L 𝔭 h𝔭ne
  let : P.IsPrime := hPprime
  let : Finite (𝓞 L ⧸ P) := Ideal.finiteQuotientOfFreeOfNeBot P hPne
  let τ : Gal(L/ℚ) := arithFrobAt (𝓞 ℚ) Gal(L/ℚ) P
  have hτfrob : IsArithFrobAt (𝓞 ℚ) τ P :=
    IsArithFrobAt.arithFrobAt (𝓞 ℚ) Gal(L/ℚ) P
  have hτclass : A.frobeniusClass L 𝔭 = ConjClasses.mk τ :=
    A.frobeniusClass_eq_mk_of_isArithFrobAt L 𝔭 h𝔭prime h𝔭unr
      τ P hPprime hτfrob hPover
  have hτσ : IsConj τ σ := by
    apply ConjClasses.mk_eq_mk_iff_isConj.mp
    exact hτclass.symm.trans h𝔭class
  refine ⟨h𝔭prime, h𝔭ne, A.unramified_at L 𝔭 h𝔭unr,
    P, hPprime, hPover, τ, hτfrob, hτσ⟩

/-- The external four-property API implies the exact Paper X arithmetic
coverage obligation. -/
theorem existentialArithmeticCoverage_of_API (A : API) :
    PaperX.GeneralArithmeticCoverage.ExistentialArithmeticCoverage :=
  existentialArithmeticCoverage_of_primeIdealChebotarev
    (primeIdealChebotarevOccurrence_of_API A)

end PaperX.ChebotarevExternalAPIAdapter
