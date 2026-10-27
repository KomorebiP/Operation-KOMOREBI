import PaperX.ConstructedChebotarevBridge
import PaperX.ArithmeticSystemSeparation

/-!
# Constructed Claim 9.1 endpoint
The original Block37 separator statement, with the external API parameter
discharged by the actual general Frobenius occurrence construction.
-/
set_option autoImplicit false
noncomputable section

namespace PaperX.Claim91ConstructedClosure

open PaperX.AbsoluteFrobeniusWitnesses
open PaperX.AbsoluteIntegralFrobenius
open PaperX.ChebotarevExternalAPIAdapter
open PaperX.CompatibleSystemRigidity
open PaperX.FiniteSeparation PaperX.TraceRecovery

/-- The constructed Chebotarev implementation closes the exact
arithmetic occurrence obligation in Paper X Claim 9.1. -/
theorem existentialArithmeticCoverage :
    PaperX.GeneralArithmeticCoverage.ExistentialArithmeticCoverage :=
  PaperX.ConstructedChebotarevBridge.existentialArithmeticCoverage

variable {Λ I E : Type*} [Field E]
variable [Fintype I] [DecidableEq I]
variable {K : Λ → Type*} [∀ l, Field (K l)] [∀ l, CharZero (K l)]
  [∀ l, TopologicalSpace (K l)] [∀ l, IsTopologicalRing (K l)] [∀ l, T2Space (K l)]
variable {W : Λ → I → Type*} [∀ l i, AddCommGroup (W l i)]
  [∀ l i, Module (K l) (W l i)] [∀ l i, FiniteDimensional (K l) (W l i)]
variable (ρ : (l : Λ) → (i : I) → Representation (K l) GQ (W l i))
variable [∀ l i, (ρ l i).IsIrreducible]
variable (hc : ∀ l i, Continuous (ρ l i).character)
variable (emb : (l : Λ) → E →+* K l)
variable (t : I → RationalPrime → E)
variable (good : Λ → RationalPrime → Prop)
variable (hgood : ∀ l, Set.Finite {p | ¬ good l p})
variable (compat : ∀ l i p, good l p →
  (ρ l i).character (chosenWitness p).element = emb l (t i p))
variable (hne : ∀ i j, MemberwiseEquiv ρ i j → i = j)

include hc hgood compat hne in
/-- Full recorded Claim 9.1 separator conclusion with no external API premise.  The selected rational primes avoid every
prescribed finite forbidden set. -/
theorem finite_arithmetic_system_separator
    (l₀ : Λ) (bad : Finset RationalPrime) :
    ∃ v : I → RationalPrime, Function.Injective v ∧
      (∀ i, good l₀ (v i)) ∧ (∀ i, v i ∉ bad) ∧
      (sampleMatrix t v).det ≠ 0 ∧
      (∀ l, ((emb l).mapMatrix (sampleMatrix t v)).det ≠ 0) ∧
      ∀ l j i, good l (v j) →
        (emb l).mapMatrix (sampleMatrix t v) j i =
          (ρ l i).character (chosenWitness (v j)).element := by
  exact PaperX.ArithmeticSystemSeparation.finite_arithmetic_system_separator
    ρ hc emb t good hgood compat hne
    existentialArithmeticCoverage l₀ bad

end PaperX.Claim91ConstructedClosure
