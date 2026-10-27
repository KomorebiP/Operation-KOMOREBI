import FiniteCyclicArithmeticComparison
import UnitMultipleOnePrimeInterface

/-!
# Finite cyclic local comparison to Taylor--Wiles selection

This capstone transports admissible nonzero detection from the genuine finite
cyclic `H¹` Frobenius model to a unit-normalized arithmetic pairing and then
invokes the v0.15 exact auxiliary-selection theorem.

The theorem is conditional only on the explicit arithmetic comparison and
admissibility data.  It does not assert that number-field primes furnish those
data; Chebotarev and continuous local Tate duality remain separate arithmetic
inputs.
-/

namespace Komorebi.StrongArtin.FiniteCyclicTaylorWilesComparisonCapstone

open Komorebi.StrongArtin.FrobeniusCyclicH1Model
open Komorebi.StrongArtin.FiniteCyclicArithmeticComparison
open Komorebi.StrongArtin.UnitMultipleOnePrimeInterface
open Komorebi.StrongArtin.AdaptiveAuxiliarySelection

universe u
noncomputable section

variable {k G n T H : Type u}
  [Field k] [CommGroup G] [Fintype G]
  [Fintype n] [DecidableEq n]
  [AddCommGroup T] [Module k T]
  [AddCommGroup H] [Module k H]

/-- An arithmetic local comparison together with the admissible tame directions
needed to detect every nonzero finite cyclic degree-one class. -/
structure AdmissibleComparison
    (D : Model (k := k) (G := G) (n := n))
    extends ArithmeticComparison (T := T) (H := H) D where
  admissible : T → Prop
  model_detects : ∀ h : H, h ≠ 0 →
    ∃ t : T, admissible t ∧
      D.centralizerEquivH1Dual
        (toArithmeticComparison.tameComparison t)
        (toArithmeticComparison.h1Comparison h) ≠ 0

/-- The pointwise family comparison supplied by an admissible arithmetic local
comparison. -/
def AdmissibleComparison.toFamilyComparison
    {D : Model (k := k) (G := G) (n := n)}
    (C : AdmissibleComparison (T := T) (H := H) D) :
    FamilyComparison (k := k) (H := H) (Aux := T) where
  admissible := C.admissible
  modelFunctional := fun t =>
    (transportedModelPairingEquiv D
      C.toArithmeticComparison.tameComparison
      C.toArithmeticComparison.h1Comparison).toLinearMap t
  arithmeticFunctional := C.toArithmeticComparison.arithmeticPairing
  scale := fun _ => C.toArithmeticComparison.scale
  compatibility := fun t => by
    ext h
    rw [C.toArithmeticComparison.arithmeticPairing_apply]
    rfl

/-- Model detection in the capstone has the exact shape required by the generic
unit-multiple family theorem. -/
theorem AdmissibleComparison.family_model_detects
    {D : Model (k := k) (G := G) (n := n)}
    (C : AdmissibleComparison (T := T) (H := H) D) :
    ∀ h : H, h ≠ 0 →
      ∃ t : T,
        C.toFamilyComparison.admissible t ∧
        C.toFamilyComparison.modelFunctional t h ≠ 0 := by
  intro h hh
  obtain ⟨t, ht, hdetect⟩ := C.model_detects h hh
  refine ⟨t, ht, ?_⟩
  simpa [AdmissibleComparison.toFamilyComparison,
    transportedModelPairingEquiv_apply] using hdetect

/-- **Finite cyclic local-comparison selection theorem.** A unit-normalized
arithmetic pairing with admissible model detection yields exactly `dim H`
admissible arithmetic local conditions whose simultaneous evaluation is
injective. -/
theorem AdmissibleComparison.exists_exact_arithmetic_TaylorWiles_set
    {D : Model (k := k) (G := G) (n := n)}
    [DecidableEq T] [FiniteDimensional k H]
    (C : AdmissibleComparison (T := T) (H := H) D) :
    ∃ Q : Finset T,
      (∀ t ∈ Q, C.admissible t) ∧
      Q.card = Module.finrank k H ∧
      selectedKernel C.toArithmeticComparison.arithmeticPairing Q = ⊥ ∧
      Function.Injective
        (evaluationMap C.toArithmeticComparison.arithmeticPairing Q) := by
  simpa [AdmissibleComparison.toFamilyComparison] using
    C.toFamilyComparison.exists_exact_arithmetic_auxiliary_set
      C.family_model_detects

end
end Komorebi.StrongArtin.FiniteCyclicTaylorWilesComparisonCapstone

#print axioms Komorebi.StrongArtin.FiniteCyclicTaylorWilesComparisonCapstone.AdmissibleComparison.family_model_detects
#print axioms Komorebi.StrongArtin.FiniteCyclicTaylorWilesComparisonCapstone.AdmissibleComparison.exists_exact_arithmetic_TaylorWiles_set
