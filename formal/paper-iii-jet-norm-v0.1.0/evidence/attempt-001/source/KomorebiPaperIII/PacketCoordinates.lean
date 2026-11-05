/-
Copyright (c) 2026 Komorebi P. All rights reserved.
Authors: Komorebi P.
-/
import Mathlib.LinearAlgebra.Pi

/-!
# Actual coordinates of a finite orthogonal projector family

The coordinate type is the dependent product of the actual projector ranges.
Analysis and synthesis are constructed from the projectors, not supplied as an
invertibility certificate. Finiteness identifies this product with the finite
algebraic direct sum used in Paper III, Section 16. Zero projectors and the empty
index type are allowed; completeness then imposes the appropriate degeneracy.
-/
set_option autoImplicit false
noncomputable section
open scoped BigOperators

namespace Komorebi.PaperIII.PacketCoordinates
universe u v w

/-- A complete, pairwise orthogonal family of idempotent linear endomorphisms. -/
structure System (R : Type u) (M : Type v) (I : Type w)
    [Semiring R] [AddCommMonoid M] [Module R M] [Fintype I] where
  projector : I → M →ₗ[R] M
  complete : ∑ i, projector i = LinearMap.id
  idempotent : ∀ i, (projector i).comp (projector i) = projector i
  orthogonal : ∀ i j, i ≠ j → (projector i).comp (projector j) = 0

namespace System
variable {R : Type u} {M : Type v} {I : Type w}
variable [Semiring R] [AddCommMonoid M] [Module R M] [Fintype I]
variable (P : System R M I)

/-- The coordinate in slot `i` belongs to the actual range of projector `i`. -/
abbrev Coordinates := (i : I) → LinearMap.range (P.projector i)

/-- A vector in a projector range is fixed by that projector. -/
theorem projector_range_self (i : I) (x : LinearMap.range (P.projector i)) :
    P.projector i (x : M) = (x : M) := by
  rcases x.property with ⟨y, hy⟩
  rw [← hy]
  exact LinearMap.congr_fun (P.idempotent i) y

/-- Distinct projectors annihilate vectors in each other's ranges. -/
theorem projector_range_other (i j : I) (h : i ≠ j)
    (x : LinearMap.range (P.projector j)) : P.projector i (x : M) = 0 := by
  rcases x.property with ⟨y, hy⟩
  rw [← hy]
  exact LinearMap.congr_fun (P.orthogonal i j h) y

/-- Split an ambient vector into its projected components. -/
def analysis : M →ₗ[R] P.Coordinates where
  toFun x i := ⟨P.projector i x, ⟨x, rfl⟩⟩
  map_add' x y := by
    funext i
    apply Subtype.ext
    exact (P.projector i).map_add x y
  map_smul' r x := by
    funext i
    apply Subtype.ext
    exact (P.projector i).map_smul r x

/-- Reconstruct an ambient vector by summing the complete packet tuple. -/
def synthesis : P.Coordinates →ₗ[R] M where
  toFun x := ∑ i, (x i : M)
  map_add' x y := by
    change (∑ i, ((x i : M) + (y i : M))) = _
    exact Finset.sum_add_distrib
  map_smul' r x := by
    change (∑ i, r • (x i : M)) = r • (∑ i, (x i : M))
    exact Finset.smul_sum.symm

@[simp] theorem analysis_apply (x : M) (i : I) :
    (P.analysis x i : M) = P.projector i x := rfl

@[simp] theorem synthesis_apply (x : P.Coordinates) :
    P.synthesis x = ∑ i, (x i : M) := rfl

/-- Completeness proves synthesis after analysis is the ambient identity. -/
@[simp] theorem synthesis_analysis (x : M) : P.synthesis (P.analysis x) = x := by
  change (∑ i, P.projector i x) = x
  simpa only [LinearMap.sum_apply, LinearMap.id_apply] using
    LinearMap.congr_fun P.complete x

/-- Idempotence and orthogonality prove analysis after synthesis is the tuple identity. -/
@[simp] theorem analysis_synthesis (x : P.Coordinates) : P.analysis (P.synthesis x) = x := by
  classical
  funext i
  apply Subtype.ext
  change P.projector i (∑ j, (x j : M)) = (x i : M)
  rw [map_sum]
  rw [Finset.sum_eq_single i]
  · exact P.projector_range_self i (x i)
  · intro j _ hji
    exact P.projector_range_other i j hji.symm (x j)
  · simp

/-- The coordinate linear equivalence is constructed from the projector axioms. -/
def coordinateEquiv : M ≃ₗ[R] P.Coordinates :=
  { P.analysis with
    invFun := P.synthesis
    left_inv := P.synthesis_analysis
    right_inv := P.analysis_synthesis }

@[simp] theorem coordinateEquiv_apply (x : M) : P.coordinateEquiv x = P.analysis x := rfl
@[simp] theorem coordinateEquiv_symm_apply (x : P.Coordinates) :
    P.coordinateEquiv.symm x = P.synthesis x := rfl

/-- Range membership and being fixed are literally the same packet condition. -/
theorem mem_range_iff_fixed (i : I) (x : M) :
    x ∈ LinearMap.range (P.projector i) ↔ P.projector i x = x := by
  constructor
  · intro hx
    exact P.projector_range_self i ⟨x, hx⟩
  · intro hx
    exact ⟨x, hx⟩

/-- Complete projected data distinguish ambient vectors. -/
theorem analysis_injective : Function.Injective P.analysis := by
  intro x y h
  have hh := congrArg P.synthesis h
  simpa only [P.synthesis_analysis] using hh

/-- Every legal packet tuple is realized by its actual finite sum. -/
theorem analysis_surjective : Function.Surjective P.analysis := by
  intro x
  exact ⟨P.synthesis x, P.analysis_synthesis x⟩

end System
end Komorebi.PaperIII.PacketCoordinates
