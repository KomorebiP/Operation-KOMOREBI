/-
Copyright (c) 2026 Komorebi P. All rights reserved.
Authors: Komorebi P.

SECTION 17 NORM-ESTIMATE CANDIDATE. NOT COMPILED.
This proves the ambient extension inequality. The literal submodule-range
norm comparison remains a separate outstanding correspondence obligation.
-/
import Mathlib.Analysis.Normed.Module.Multilinear.Basic

set_option autoImplicit false
noncomputable section
open scoped BigOperators

namespace Komorebi.PaperIII.BoundedJet

universe u v w
variable {K : Type u} [NontriviallyNormedField K]
variable {X : Type v} {Y : Type w}
variable [SeminormedAddCommGroup X] [NormedSpace K X]
variable [SeminormedAddCommGroup Y] [NormedSpace K Y]
variable {n : Nat}

/-- Bounded ambient packet jet: input projections followed by an arbitrary
    continuous multilinear map and an output projection. -/
def projectedJet (Q : Y →L[K] Y)
    (P : Fin n → X →L[K] X)
    (B : ContinuousMultilinearMap K (fun (_ : Fin n) => X) Y) :
    ContinuousMultilinearMap K (fun (_ : Fin n) => X) Y :=
  Q.compContinuousMultilinearMap (B.compContinuousLinearMap P)

/-- The exact norm inequality for the projected ambient jet. This uses the
    standard norm estimates for composition of continuous multilinear maps
    with bounded input and output maps. -/
theorem projectedJet_norm_le (Q : Y →L[K] Y)
    (P : Fin n → X →L[K] X)
    (B : ContinuousMultilinearMap K (fun (_ : Fin n) => X) Y) :
    ‖projectedJet Q P B‖ ≤ ‖Q‖ * ‖B‖ * ∏ k, ‖P k‖ := by
  have houtput :
      ‖Q.compContinuousMultilinearMap (B.compContinuousLinearMap P)‖ ≤
        ‖Q‖ * ‖B.compContinuousLinearMap P‖ :=
    ContinuousLinearMap.norm_compContinuousMultilinearMap_le Q _
  have hinput :
      ‖B.compContinuousLinearMap P‖ ≤ ‖B‖ * ∏ k, ‖P k‖ :=
    ContinuousMultilinearMap.norm_compContinuousLinearMap_le B P
  calc
    ‖projectedJet Q P B‖ ≤ ‖Q‖ * ‖B.compContinuousLinearMap P‖ := houtput
    _ ≤ ‖Q‖ * (‖B‖ * ∏ k, ‖P k‖) :=
        mul_le_mul_of_nonneg_left hinput (norm_nonneg _)
    _ = ‖Q‖ * ‖B‖ * ∏ k, ‖P k‖ := by ring

end Komorebi.PaperIII.BoundedJet
