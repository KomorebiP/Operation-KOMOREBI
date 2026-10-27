import UnitMultiplePairing
import RelativeTaylorWilesFiniteSet

/-!
# Unit-normalization invariance of the one-prime interface

The arithmetic local Tate pairing may differ from the model trace pairing by a
nonzero local unit.  Taylor--Wiles selection uses only nonvanishing, so the
one-prime interface and the resulting finite auxiliary set are unchanged by
such rescaling.
-/

namespace Komorebi.StrongArtin.UnitMultipleOnePrimeInterface

open Komorebi.StrongArtin.RelativeTaylorWilesFiniteSet

universe u
noncomputable section

variable {k H Aux : Type u} [Field k]
  [AddCommGroup H] [Module k H]

/-- A family of arithmetic local functionals that is pointwise a unit multiple
of a model family. -/
structure FamilyComparison where
  admissible : Aux → Prop
  modelFunctional : Aux → Module.Dual k H
  arithmeticFunctional : Aux → Module.Dual k H
  scale : Aux → kˣ
  compatibility : ∀ a : Aux,
    arithmeticFunctional a = (scale a : k) • modelFunctional a

@[simp]
theorem FamilyComparison.arithmetic_apply
    (C : FamilyComparison (k := k) (H := H) (Aux := Aux))
    (a : Aux) (h : H) :
    C.arithmeticFunctional a h =
      (C.scale a : k) * C.modelFunctional a h := by
  rw [C.compatibility]
  rfl

/-- Local arithmetic and model evaluations vanish on exactly the same classes. -/
theorem FamilyComparison.arithmetic_apply_ne_zero_iff
    (C : FamilyComparison (k := k) (H := H) (Aux := Aux))
    (a : Aux) (h : H) :
    C.arithmeticFunctional a h ≠ 0 ↔
      C.modelFunctional a h ≠ 0 := by
  rw [C.arithmetic_apply]
  exact mul_ne_zero_iff_left (C.scale a).ne_zero

/-- Model one-prime detection transfers to the arithmetic pairing family. -/
theorem FamilyComparison.arithmetic_detects_of_model_detects
    (C : FamilyComparison (k := k) (H := H) (Aux := Aux))
    (hmodel : ∀ h : H, h ≠ 0 →
      ∃ a : Aux, C.admissible a ∧ C.modelFunctional a h ≠ 0) :
    ∀ h : H, h ≠ 0 →
      ∃ a : Aux, C.admissible a ∧ C.arithmeticFunctional a h ≠ 0 := by
  intro h hh
  obtain ⟨a, ha, hdetect⟩ := hmodel h hh
  exact ⟨a, ha, C.arithmetic_apply_ne_zero_iff a h |>.2 hdetect⟩

/-- The arithmetic one-prime selection interface induced by a unit-normalized
model family. -/
def FamilyComparison.arithmeticInterface
    (C : FamilyComparison (k := k) (H := H) (Aux := Aux))
    (hmodel : ∀ h : H, h ≠ 0 →
      ∃ a : Aux, C.admissible a ∧ C.modelFunctional a h ≠ 0) :
    OnePrimeSelectionInterface k H Aux where
  admissible := C.admissible
  localFunctional := C.arithmeticFunctional
  detects := C.arithmetic_detects_of_model_detects hmodel

/-- Unit-normalized arithmetic local pairings produce the same exact finite
Taylor--Wiles set as the model pairings. -/
theorem FamilyComparison.exists_exact_arithmetic_auxiliary_set
    [DecidableEq Aux] [FiniteDimensional k H]
    (C : FamilyComparison (k := k) (H := H) (Aux := Aux))
    (hmodel : ∀ h : H, h ≠ 0 →
      ∃ a : Aux, C.admissible a ∧ C.modelFunctional a h ≠ 0) :
    ∃ Q : Finset Aux,
      (∀ a ∈ Q, C.admissible a) ∧
      Q.card = Module.finrank k H ∧
      Komorebi.StrongArtin.AdaptiveAuxiliarySelection.selectedKernel
        C.arithmeticFunctional Q = ⊥ ∧
      Function.Injective
        (Komorebi.StrongArtin.AdaptiveAuxiliarySelection.evaluationMap
          C.arithmeticFunctional Q) := by
  exact exists_relative_TaylorWiles_set_exact
    (C.arithmeticInterface hmodel)

end
end Komorebi.StrongArtin.UnitMultipleOnePrimeInterface

#print axioms Komorebi.StrongArtin.UnitMultipleOnePrimeInterface.FamilyComparison.arithmetic_apply_ne_zero_iff
#print axioms Komorebi.StrongArtin.UnitMultipleOnePrimeInterface.FamilyComparison.arithmetic_detects_of_model_detects
#print axioms Komorebi.StrongArtin.UnitMultipleOnePrimeInterface.FamilyComparison.exists_exact_arithmetic_auxiliary_set
