import PaperX.GeneralArithmeticCoverage
import PaperX.CompatibleSystemSeparation

/-!
# Arithmetic Frobenius coverage to finite compatible-system separation

This module composes the existing arithmetic-coverage bridge with the common
compatible-system separator.  The only arithmetic existence premise retained is
`ExistentialArithmeticCoverage`: prescribed Frobenius conjugacy must occur at an
unramified rational prime outside every finite forbidden set.
-/

set_option autoImplicit false
noncomputable section

namespace PaperX.ArithmeticSystemSeparation

open PaperX.AbsoluteFrobeniusWitnesses
open PaperX.AbsoluteIntegralFrobenius
open PaperX.GeneralArithmeticCoverage
open PaperX.CompatibleSystemRigidity
open PaperX.FiniteSeparation PaperX.TraceRecovery

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
/-- Full finite trace-separator conclusion from the single choice-free
prescribed-Frobenius occurrence premise.  All selected rational primes can avoid
an arbitrary finite forbidden set. -/
theorem finite_arithmetic_system_separator
    (hcov : ExistentialArithmeticCoverage)
    (l₀ : Λ) (bad : Finset RationalPrime) :
    ∃ v : I → RationalPrime, Function.Injective v ∧
      (∀ i, good l₀ (v i)) ∧ (∀ i, v i ∉ bad) ∧
      (sampleMatrix t v).det ≠ 0 ∧
      (∀ l, ((emb l).mapMatrix (sampleMatrix t v)).det ≠ 0) ∧
      ∀ l j i, good l (v j) →
        (emb l).mapMatrix (sampleMatrix t v) j i =
          (ρ l i).character (chosenWitness (v j)).element := by
  apply PaperX.CompatibleSystemSeparation.finite_system_separator
    ρ hc emb t good hgood
    (fun p : RationalPrime => (chosenWitness p).element)
    (cofiniteQuotientCoverage_of_existentialArithmeticCoverage hcov chosenWitness)
    compat hne l₀ bad

end PaperX.ArithmeticSystemSeparation
