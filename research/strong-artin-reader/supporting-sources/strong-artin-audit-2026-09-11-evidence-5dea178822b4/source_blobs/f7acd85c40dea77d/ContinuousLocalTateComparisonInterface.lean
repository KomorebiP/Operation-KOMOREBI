import FiniteCyclicArithmeticComparison
import Mathlib.RepresentationTheory.Homological.ContCohomology.Basic

/-!
# Continuous local Tate comparison interface

This module states the exact comparison datum still required from arithmetic
local cohomology.  It uses Mathlib's actual `continuousCohomology 1 X` type and
proves that, once comparison maps and unit normalization are supplied, all
perfectness and nonvanishing consequences follow from the checked finite cyclic
Frobenius model.

The structure is intentionally an interface, not a proof that a local Galois
representation satisfies it.  Mathlib presently does not provide the required
H¹ comparison between continuous and ordinary group cohomology or local Tate
duality in this form.
-/

namespace Komorebi.StrongArtin.ContinuousLocalTateComparisonInterface

open Komorebi.StrongArtin.FrobeniusCyclicH1Model
open Komorebi.StrongArtin.FiniteCyclicArithmeticComparison

universe u
noncomputable section

variable {k L G n T : Type u}
  [Field k] [TopologicalSpace k]
  [Group L] [TopologicalSpace L] [IsTopologicalGroup L]
  [CommGroup G] [Fintype G]
  [Fintype n] [DecidableEq n]
  [AddCommGroup T] [Module k T]

/-- Exact comparison data relating continuous local degree-one cohomology and
its arithmetic Tate pairing to the finite cyclic Frobenius model. -/
structure Datum
    (X : TopRep.{u} k L)
    (D : Model (k := k) (G := G) (n := n)) where
  tameComparison : T ≃ₗ[k]
    Komorebi.StrongArtin.LocalFrobeniusPerfectPairing.frobeniusCentralizer
      D.frobenius
  h1Comparison :
    (continuousCohomology 1 X : Type u) ≃ₗ[k]
      groupCohomology D.coeff 1
  localTatePairing :
    T →ₗ[k] Module.Dual k (continuousCohomology 1 X : Type u)
  scale : kˣ
  pairing_compatibility :
    localTatePairing =
      (scale • transportedModelPairingEquiv
        D tameComparison h1Comparison).toLinearMap

/-- Forgetting the topological origin gives the already checked arithmetic
comparison structure. -/
def Datum.toArithmeticComparison
    {X : TopRep.{u} k L}
    {D : Model (k := k) (G := G) (n := n)}
    (C : Datum (T := T) X D) :
    ArithmeticComparison
      (T := T) (H := (continuousCohomology 1 X : Type u)) D where
  tameComparison := C.tameComparison
  h1Comparison := C.h1Comparison
  arithmeticPairing := C.localTatePairing
  scale := C.scale
  pairing_compatibility := C.pairing_compatibility

/-- The continuous local pairing is a linear equivalence onto the complete
dual whenever the comparison datum exists. -/
def Datum.localTatePairingEquiv
    {X : TopRep.{u} k L}
    {D : Model (k := k) (G := G) (n := n)}
    (C : Datum (T := T) X D) :
    T ≃ₗ[k] Module.Dual k (continuousCohomology 1 X : Type u) :=
  C.toArithmeticComparison.arithmeticPairingEquiv

@[simp]
theorem Datum.localTatePairingEquiv_toLinearMap
    {X : TopRep.{u} k L}
    {D : Model (k := k) (G := G) (n := n)}
    (C : Datum (T := T) X D) :
    C.localTatePairingEquiv.toLinearMap = C.localTatePairing :=
  C.toArithmeticComparison.arithmeticPairingEquiv_toLinearMap

/-- Continuous arithmetic nonvanishing is equivalent to nonvanishing of the
finite cyclic Frobenius trace model. -/
theorem Datum.localTatePairing_ne_zero_iff_model
    {X : TopRep.{u} k L}
    {D : Model (k := k) (G := G) (n := n)}
    (C : Datum (T := T) X D)
    (t : T) (h : continuousCohomology 1 X) :
    C.localTatePairing t h ≠ 0 ↔
      D.centralizerEquivH1Dual
        (C.tameComparison t) (C.h1Comparison h) ≠ 0 :=
  C.toArithmeticComparison.apply_ne_zero_iff_model t h

/-- Every nonzero continuous degree-one class is detected by a tame direction
once the comparison datum exists. -/
theorem Datum.detects_every_nonzero_continuous_h1
    {X : TopRep.{u} k L}
    {D : Model (k := k) (G := G) (n := n)}
    (C : Datum (T := T) X D) :
    ∀ h : continuousCohomology 1 X, h ≠ 0 →
      ∃ t : T, C.localTatePairing t h ≠ 0 :=
  C.toArithmeticComparison.detects_every_nonzero_h1

/-- Every continuous local functional has a unique tame representative. -/
theorem Datum.exists_unique_tame_representative
    {X : TopRep.{u} k L}
    {D : Model (k := k) (G := G) (n := n)}
    (C : Datum (T := T) X D)
    (φ : Module.Dual k (continuousCohomology 1 X : Type u)) :
    ∃! t : T, C.localTatePairing t = φ :=
  C.toArithmeticComparison.exists_unique_tame_representative φ

end
end Komorebi.StrongArtin.ContinuousLocalTateComparisonInterface

#print axioms Komorebi.StrongArtin.ContinuousLocalTateComparisonInterface.Datum.localTatePairing_ne_zero_iff_model
#print axioms Komorebi.StrongArtin.ContinuousLocalTateComparisonInterface.Datum.detects_every_nonzero_continuous_h1
#print axioms Komorebi.StrongArtin.ContinuousLocalTateComparisonInterface.Datum.exists_unique_tame_representative
