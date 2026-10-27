import PaperXI.UnramifiedFieldTower

/-! # Actual unramified base change through the recursive local-field tower

Block 40 proved Frobenius-power and Euler-factor formulas for an internal degree
dilation of the integer-degree unramified Weil model. Block 41 constructs an
actual recursive local-field tower and its restriction map. This module proves
that the two constructions give the same Frobenius polynomials and local
factors, and records conductor zero on both sides of the actual tower.

This remains scoped to the bounded unramified Weil models, not absolute Weil
groups or automorphic base change.
-/

set_option autoImplicit false
noncomputable section

namespace PaperXI.ActualUnramifiedBaseChange

open PaperXI.UnramifiedFieldTower
open PaperXI.FiniteUnramifiedWeil
open ValuativeRel
open scoped Classical Polynomial
open Polynomial

variable (K : Type*) [Field K] [ValuativeRel K] [UniformSpace K]
  [IsUniformAddGroup K] [IsNonarchimedeanLocalField K]
variable (s : Type*) [Field s] [Algebra 𝓀[K] s]
  [FiniteDimensional 𝓀[K] s]
variable (t : Type*) [Field t] [Algebra s t] [FiniteDimensional s t]

noncomputable local instance : Algebra 𝓀[LowerField K s] t :=
  residueTowerAlgebra K s t

noncomputable local instance : FiniteDimensional 𝓀[LowerField K s] t :=
  residueTowerFinite K s t

variable {V : Type*} [AddCommGroup V] [Module ℂ V] [FiniteDimensional ℂ V]
variable (ρ : Representation ℂ (UnramifiedWeil K s) V)

/-- Actual tower restriction and Block 40's internal degree dilation have the
same Frobenius polynomial. -/
theorem frobeniusPolynomial_eq_modelBaseChange :
    frobeniusPolynomial (LowerField K s) t (restrictRepresentation K s t ρ) =
      frobeniusPolynomial K s
        (baseChangeRepresentation K s (Module.finrank s t) ρ) := by
  rw [restriction_frobeniusPolynomial,
    baseChange_frobeniusPolynomial, map_pow]

/-- Actual tower restriction and the internal degree-dilation model have the
same rational unramified local factor. -/
theorem localFactor_eq_modelBaseChange :
    unramifiedLocalFactor (LowerField K s) t
        (restrictRepresentation K s t ρ) =
      unramifiedLocalFactor K s
        (baseChangeRepresentation K s (Module.finrank s t) ρ) := by
  unfold unramifiedLocalFactor
  rw [frobeniusPolynomial_eq_modelBaseChange K s t ρ]

/-- Inertia codimension remains zero after restriction through the actual
unramified tower. -/
theorem restricted_inertiaCodimension_eq_zero :
    inertiaCodimension (LowerField K s) t
      (restrictRepresentation K s t ρ) = 0 :=
  inertiaCodimension_eq_zero (LowerField K s) t
    (restrictRepresentation K s t ρ)

omit [FiniteDimensional ℂ V] in
/-- Swan conductor remains zero after restriction through the actual
unramified tower. -/
theorem restricted_swanConductorExponent_eq_zero :
    swanConductorExponent (LowerField K s) t
      (restrictRepresentation K s t ρ) = 0 :=
  swanConductorExponent_eq_zero (LowerField K s) t
    (restrictRepresentation K s t ρ)

/-- Artin conductor remains zero after restriction through the actual
unramified tower. -/
theorem restricted_artinConductorExponent_eq_zero :
    artinConductorExponent (LowerField K s) t
      (restrictRepresentation K s t ρ) = 0 :=
  artinConductorExponent_eq_zero (LowerField K s) t
    (restrictRepresentation K s t ρ)

/-- The model Artin exponent is invariant under actual unramified tower
restriction; both sides vanish for the bounded unramified Weil models. -/
theorem artinConductorExponent_restriction :
    artinConductorExponent (LowerField K s) t
        (restrictRepresentation K s t ρ) =
      artinConductorExponent K s ρ := by
  rw [restricted_artinConductorExponent_eq_zero K s t ρ,
    artinConductorExponent_eq_zero K s ρ]

variable [Representation.IsIrreducible ρ]

/-- For an irreducible lower representation, actual field-tower restriction
raises the Frobenius eigenvalue to the relative residue degree. -/
theorem irreducible_restriction_frobeniusPolynomial :
    frobeniusPolynomial (LowerField K s) t
        (restrictRepresentation K s t ρ) =
      1 - C ((frobeniusEigenvalue K s ρ) ^ Module.finrank s t) * X := by
  rw [frobeniusPolynomial_eq_modelBaseChange K s t ρ]
  exact irreducible_baseChange_frobeniusPolynomial K s ρ
    (Module.finrank s t)

/-- Explicit rank-one Euler factor under the actual unramified field tower. -/
theorem irreducible_restriction_localFactor :
    unramifiedLocalFactor (LowerField K s) t
        (restrictRepresentation K s t ρ) =
      rankOneEulerFactor
        ((frobeniusEigenvalue K s ρ) ^ Module.finrank s t) := by
  rw [localFactor_eq_modelBaseChange K s t ρ]
  exact irreducible_baseChange_localFactor K s ρ (Module.finrank s t)

end PaperXI.ActualUnramifiedBaseChange
