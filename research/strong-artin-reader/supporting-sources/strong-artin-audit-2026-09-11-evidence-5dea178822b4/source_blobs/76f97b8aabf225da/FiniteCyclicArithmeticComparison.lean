import FrobeniusCyclicH1Model
import UnitMultiplePairing
import Mathlib.LinearAlgebra.Dual.Lemmas

/-!
# Finite cyclic arithmetic pairing comparison

This module packages the exact comparison needed to transport a normalized
arithmetic local pairing to the genuine finite cyclic `H¹` model.  The
arithmetic pairing is allowed to differ from the model trace pairing by a unit,
which is the strongest normalization-independent statement required by
Taylor--Wiles detection.

The comparison maps themselves remain explicit hypotheses.  In particular,
this file does not identify continuous local Galois cohomology with the finite
cyclic model and does not prove arithmetic local Tate duality.
-/

namespace Komorebi.StrongArtin.FiniteCyclicArithmeticComparison

open Komorebi.StrongArtin.FrobeniusCyclicH1Model
open Komorebi.StrongArtin.LocalFrobeniusPerfectPairing
open Komorebi.StrongArtin.UnitMultiplePairing

universe u
noncomputable section

variable {k G n T H : Type u}
  [Field k] [CommGroup G] [Fintype G]
  [Fintype n] [DecidableEq n]
  [AddCommGroup T] [Module k T]
  [AddCommGroup H] [Module k H]

/-- The model pairing after transporting arithmetic tame directions and
arithmetic degree-one classes to the finite cyclic Frobenius model. -/
def transportedModelPairingEquiv
    (D : Model (k := k) (G := G) (n := n))
    (tameComparison : T ≃ₗ[k] frobeniusCentralizer D.frobenius)
    (h1Comparison : H ≃ₗ[k] groupCohomology D.coeff 1) :
    T ≃ₗ[k] Module.Dual k H :=
  (tameComparison.trans D.centralizerEquivH1Dual).trans h1Comparison.dualMap

@[simp]
theorem transportedModelPairingEquiv_apply
    (D : Model (k := k) (G := G) (n := n))
    (tameComparison : T ≃ₗ[k] frobeniusCentralizer D.frobenius)
    (h1Comparison : H ≃ₗ[k] groupCohomology D.coeff 1)
    (t : T) (h : H) :
    transportedModelPairingEquiv D tameComparison h1Comparison t h =
      D.centralizerEquivH1Dual (tameComparison t) (h1Comparison h) := rfl

/-- Exact data asserting that an arithmetic local pairing is a unit multiple of
the transported finite cyclic Frobenius trace pairing. -/
structure ArithmeticComparison
    (D : Model (k := k) (G := G) (n := n)) where
  tameComparison : T ≃ₗ[k] frobeniusCentralizer D.frobenius
  h1Comparison : H ≃ₗ[k] groupCohomology D.coeff 1
  arithmeticPairing : T →ₗ[k] Module.Dual k H
  scale : kˣ
  pairing_compatibility :
    arithmeticPairing =
      (scale • transportedModelPairingEquiv D tameComparison h1Comparison).toLinearMap

/-- The comparison as a generic unit-multiple pairing datum. -/
def ArithmeticComparison.toUnitMultiple
    {D : Model (k := k) (G := G) (n := n)}
    (C : ArithmeticComparison (T := T) (H := H) D) :
    UnitMultiplePairing.Comparison (k := k) (T := T) (H := H) where
  model := (transportedModelPairingEquiv D C.tameComparison C.h1Comparison).toLinearMap
  arithmetic := C.arithmeticPairing
  scale := C.scale
  compatibility := by
    rw [C.pairing_compatibility, LinearEquiv.toLinearMap_smul]

/-- The arithmetic pairing itself is represented by a linear equivalence. -/
def ArithmeticComparison.arithmeticPairingEquiv
    {D : Model (k := k) (G := G) (n := n)}
    (C : ArithmeticComparison (T := T) (H := H) D) :
    T ≃ₗ[k] Module.Dual k H :=
  C.scale • transportedModelPairingEquiv D C.tameComparison C.h1Comparison

@[simp]
theorem ArithmeticComparison.arithmeticPairingEquiv_toLinearMap
    {D : Model (k := k) (G := G) (n := n)}
    (C : ArithmeticComparison (T := T) (H := H) D) :
    C.arithmeticPairingEquiv.toLinearMap = C.arithmeticPairing := by
  exact C.pairing_compatibility.symm

@[simp]
theorem ArithmeticComparison.arithmeticPairing_apply
    {D : Model (k := k) (G := G) (n := n)}
    (C : ArithmeticComparison (T := T) (H := H) D)
    (t : T) (h : H) :
    C.arithmeticPairing t h =
      (C.scale : k) *
        D.centralizerEquivH1Dual
          (C.tameComparison t) (C.h1Comparison h) := by
  rw [← C.arithmeticPairingEquiv_toLinearMap]
  rfl

/-- Arithmetic nonvanishing is exactly model trace-pairing nonvanishing. -/
theorem ArithmeticComparison.apply_ne_zero_iff_model
    {D : Model (k := k) (G := G) (n := n)}
    (C : ArithmeticComparison (T := T) (H := H) D)
    (t : T) (h : H) :
    C.arithmeticPairing t h ≠ 0 ↔
      D.centralizerEquivH1Dual
        (C.tameComparison t) (C.h1Comparison h) ≠ 0 := by
  rw [C.arithmeticPairing_apply]
  exact mul_ne_zero_iff_left C.scale.ne_zero

/-- The arithmetic pairing is injective in the tame direction. -/
theorem ArithmeticComparison.pairing_injective
    {D : Model (k := k) (G := G) (n := n)}
    (C : ArithmeticComparison (T := T) (H := H) D) :
    Function.Injective C.arithmeticPairing := by
  rw [← C.arithmeticPairingEquiv_toLinearMap]
  exact C.arithmeticPairingEquiv.injective

/-- The arithmetic pairing is surjective onto the full dual. -/
theorem ArithmeticComparison.pairing_surjective
    {D : Model (k := k) (G := G) (n := n)}
    (C : ArithmeticComparison (T := T) (H := H) D) :
    Function.Surjective C.arithmeticPairing := by
  rw [← C.arithmeticPairingEquiv_toLinearMap]
  exact C.arithmeticPairingEquiv.surjective

/-- Every arithmetic functional has a unique tame representative. -/
theorem ArithmeticComparison.exists_unique_tame_representative
    {D : Model (k := k) (G := G) (n := n)}
    (C : ArithmeticComparison (T := T) (H := H) D)
    (φ : Module.Dual k H) :
    ∃! t : T, C.arithmeticPairing t = φ := by
  let t := C.arithmeticPairingEquiv.symm φ
  have ht : C.arithmeticPairing t = φ := by
    rw [← C.arithmeticPairingEquiv_toLinearMap]
    exact C.arithmeticPairingEquiv.apply_symm_apply φ
  refine ⟨t, ht, ?_⟩
  intro s hs
  apply C.pairing_injective
  exact hs.trans ht.symm

/-- In finite dimension, every nonzero arithmetic degree-one class is detected
by an arithmetic tame direction. -/
theorem ArithmeticComparison.detects_every_nonzero_h1
    {D : Model (k := k) (G := G) (n := n)}
    (C : ArithmeticComparison (T := T) (H := H) D) :
    ∀ h : H, h ≠ 0 → ∃ t : T, C.arithmeticPairing t h ≠ 0 := by
  intro h hh
  obtain ⟨φ, hφ⟩ := Module.Projective.exists_dual_ne_zero k hh
  obtain ⟨t, ht⟩ := C.pairing_surjective φ
  refine ⟨t, ?_⟩
  rw [ht]
  exact hφ

end
end Komorebi.StrongArtin.FiniteCyclicArithmeticComparison

#print axioms Komorebi.StrongArtin.FiniteCyclicArithmeticComparison.transportedModelPairingEquiv
#print axioms Komorebi.StrongArtin.FiniteCyclicArithmeticComparison.ArithmeticComparison.apply_ne_zero_iff_model
#print axioms Komorebi.StrongArtin.FiniteCyclicArithmeticComparison.ArithmeticComparison.pairing_injective
#print axioms Komorebi.StrongArtin.FiniteCyclicArithmeticComparison.ArithmeticComparison.pairing_surjective
#print axioms Komorebi.StrongArtin.FiniteCyclicArithmeticComparison.ArithmeticComparison.exists_unique_tame_representative
#print axioms Komorebi.StrongArtin.FiniteCyclicArithmeticComparison.ArithmeticComparison.detects_every_nonzero_h1
