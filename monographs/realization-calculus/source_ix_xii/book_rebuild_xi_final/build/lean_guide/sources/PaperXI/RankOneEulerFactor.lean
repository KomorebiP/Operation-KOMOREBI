import PaperXI.UnramifiedConductorZero
import Mathlib.LinearAlgebra.Dimension.Free
import Mathlib.Algebra.Polynomial.Reverse

/-! # Rank-one Euler factors for irreducible unramified representations -/

set_option autoImplicit false
noncomputable section

namespace PaperXI.FiniteUnramifiedWeil

open ValuativeRel
open scoped Classical Polynomial
open Polynomial

variable (K : Type*) [Field K] [ValuativeRel K] [UniformSpace K]
  [IsUniformAddGroup K] [IsNonarchimedeanLocalField K]
variable (s : Type*) [Field s] [Algebra 𝓀[K] s]
  [FiniteDimensional 𝓀[K] s]

section Polynomial

variable {V : Type*} [AddCommGroup V] [Module ℂ V] [FiniteDimensional ℂ V]

/-- Reversal of a monic linear characteristic polynomial in the convention used
throughout Paper XI. -/
theorem reverse_X_sub_C (c : ℂ) :
    (X - C c).reverse = 1 - C c * X := by
  have hX : (X : ℂ[X]).reverse = 1 := by
    rw [show (X : ℂ[X]) = X * 1 by simp, Polynomial.reverse_X_mul]
    simpa using (Polynomial.reverse_C (R := ℂ) (1 : ℂ))
  rw [sub_eq_add_neg, ← Polynomial.C_neg]
  rw [Polynomial.reverse_add_C, hX]
  simp [sub_eq_add_neg]

/-- In dimension one, the reverse characteristic polynomial of a homothety is
`1 - cX`. -/
theorem reverse_charpoly_smul_id (h : Module.finrank ℂ V = 1) (c : ℂ) :
    ((c • LinearMap.id : Module.End ℂ V).charpoly).reverse = 1 - C c * X := by
  have hchar : (c • LinearMap.id : Module.End ℂ V).charpoly = X - C c := by
    rw [show (c • LinearMap.id : Module.End ℂ V) =
      (0 : Module.End ℂ V) - (-c) • 1 by ext x; simp]
    rw [LinearMap.charpoly_sub_smul]
    simp [h, sub_eq_add_neg]
  rw [hchar]
  exact reverse_X_sub_C c

end Polynomial

section Irreducible

variable {V : Type*} [AddCommGroup V] [Module ℂ V] [FiniteDimensional ℂ V]
variable (ρ : Representation ℂ (UnramifiedWeil K s) V)
variable [Representation.IsIrreducible ρ]

/-- Scalar by which the distinguished geometric-Frobenius lift acts on an
irreducible representation. Irreducibility makes the representation space
one-dimensional because the unramified Weil model is commutative. -/
noncomputable def frobeniusEigenvalue : ℂ :=
  (LinearEquiv.smul_id_of_finrank_eq_one
    (irreducible_finrank_eq_one K s ρ)).symm (ρ (geometricLift K s))

/-- The geometric-Frobenius operator is exactly scalar multiplication by the
chosen eigenvalue. -/
theorem geometricFrobenius_action_eq_smul_id :
    ρ (geometricLift K s) =
      frobeniusEigenvalue K s ρ • LinearMap.id := by
  exact ((LinearEquiv.smul_id_of_finrank_eq_one
    (irreducible_finrank_eq_one K s ρ)).apply_symm_apply
      (ρ (geometricLift K s))).symm

/-- Frobenius acts invertibly, so its scalar eigenvalue is nonzero. -/
theorem frobeniusEigenvalue_ne_zero : frobeniusEigenvalue K s ρ ≠ 0 := by
  have hdim : 0 < Module.finrank ℂ V := by
    rw [irreducible_finrank_eq_one K s ρ]
    exact Nat.zero_lt_one
  obtain ⟨x, hx⟩ :=
    (Module.finrank_pos_iff_exists_ne_zero (R := ℂ)).mp hdim
  intro hzero
  have hF : ρ (geometricLift K s) = 0 := by
    rw [geometricFrobenius_action_eq_smul_id K s ρ, hzero]
    simp
  have hinv : ρ (geometricLift K s) * ρ ((geometricLift K s)⁻¹) = 1 := by
    rw [← map_mul]
    simp
  rw [hF, zero_mul] at hinv
  have hpoint := congrArg (fun f : Module.End ℂ V => f x) hinv
  simp at hpoint
  exact hx hpoint.symm

/-- Explicit linear Euler polynomial for an irreducible representation. -/
theorem frobeniusPolynomial_eq_linear :
    frobeniusPolynomial K s ρ =
      1 - C (frobeniusEigenvalue K s ρ) * X := by
  rw [frobeniusPolynomial, geometricFrobenius_action_eq_smul_id K s ρ]
  exact reverse_charpoly_smul_id
    (irreducible_finrank_eq_one K s ρ) (frobeniusEigenvalue K s ρ)

/-- Reciprocal linear Euler factor associated to a nonzero scalar. -/
noncomputable def rankOneEulerFactor (α : ℂ) : RatFunc ℂ :=
  (algebraMap ℂ[X] (RatFunc ℂ) (1 - C α * X))⁻¹

/-- The unramified local factor of an irreducible representation is the expected
rank-one Euler factor. -/
theorem unramifiedLocalFactor_eq_rankOneEulerFactor :
    unramifiedLocalFactor K s ρ =
      rankOneEulerFactor (frobeniusEigenvalue K s ρ) := by
  rw [unramifiedLocalFactor, rankOneEulerFactor,
    frobeniusPolynomial_eq_linear K s ρ]

end Irreducible

end PaperXI.FiniteUnramifiedWeil
