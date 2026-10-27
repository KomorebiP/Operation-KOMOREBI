/-
Copyright (c) 2026 Komorebi P. All rights reserved.
Authors: Komorebi P.
-/
import KomorebiPaperIII.PacketCoordinates
import Mathlib.Algebra.DirectSum.Module

/-! # Literal finite direct-sum form of the constructed packet coordinates -/
set_option autoImplicit false
noncomputable section
open scoped BigOperators
namespace Komorebi.PaperIII.PacketCoordinates.System
universe u v w
variable {R : Type u} {M : Type v} {I : Type w}
variable [Semiring R] [AddCommMonoid M] [Module R M]
variable [Fintype I] [DecidableEq I]
variable (P : Komorebi.PaperIII.PacketCoordinates.System R M I)

/-- The literal algebraic direct sum printed in Paper III, Section 16. -/
abbrev DirectCoordinates := DirectSum I (fun i => LinearMap.range (P.projector i))

/-- The pinned finite direct-sum/product equivalence, on the actual packet ranges. -/
def directSumToCoordinates : P.DirectCoordinates ≃ₗ[R] P.Coordinates :=
  DirectSum.linearEquivFunOnFintype R I (fun i => LinearMap.range (P.projector i))

/-- Analysis as an equivalence to the literal direct sum, without a supplied coordinate certificate. -/
def directSumEquiv : M ≃ₗ[R] P.DirectCoordinates :=
  P.coordinateEquiv.trans P.directSumToCoordinates.symm

/-- The finite product bridge takes literal direct-sum analysis to the same actual tuple. -/
omit [DecidableEq I] in
@[simp] theorem directSumToCoordinates_analysis (x : M) :
    P.directSumToCoordinates (P.directSumEquiv x) = P.analysis x := by
  change P.directSumToCoordinates (P.directSumToCoordinates.symm (P.analysis x)) = P.analysis x
  exact P.directSumToCoordinates.apply_symm_apply (P.analysis x)

/-- Every direct-sum component is the original projected ambient vector. -/
@[simp] theorem directSumEquiv_component (x : M) (i : I) :
    (P.directSumEquiv x i : M) = P.projector i x := by
  exact congrArg (fun y : P.Coordinates => (y i : M)) (P.directSumToCoordinates_analysis x)

/-- The inverse of literal direct-sum analysis is the finite ambient sum. -/
omit [DecidableEq I] in
@[simp] theorem directSumEquiv_symm_apply (x : P.DirectCoordinates) :
    P.directSumEquiv.symm x = ∑ i, (x i : M) := rfl

end Komorebi.PaperIII.PacketCoordinates.System
