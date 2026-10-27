import PaperXI.FiniteUnramifiedWeil
import Mathlib.FieldTheory.RatFunc.Basic
import Mathlib.RepresentationTheory.Invariants
import Mathlib.LinearAlgebra.Charpoly.ToMatrix
import Mathlib.LinearAlgebra.Matrix.Charpoly.Coeff

/-! # Unramified local factors for the finite Weil model -/

set_option autoImplicit false
noncomputable section

namespace PaperXI.FiniteUnramifiedWeil

open ValuativeRel
open PaperXI.ResidueWeil
open scoped Classical Polynomial
open Polynomial

variable (K : Type*) [Field K] [ValuativeRel K] [UniformSpace K]
  [IsUniformAddGroup K] [IsNonarchimedeanLocalField K]
variable (s : Type*) [Field s] [Algebra 𝓀[K] s]
  [FiniteDimensional 𝓀[K] s]

section Representation

variable {V : Type*} [AddCommGroup V] [Module ℂ V]

abbrev Inertia : Subgroup (UnramifiedWeil K s) :=
  (degree (MonoidHom.id (ResidueGalois K s)) (geometricFrobenius K s)).ker

/-- Every representation is trivial on the actual inertia subgroup because this
finite unramified Weil model has trivial inertia. -/
theorem inertia_le_kernel (ρ : Representation ℂ (UnramifiedWeil K s) V) :
    Inertia K s ≤ ρ.ker := by
  rw [Inertia, inertia_eq_bot K s]
  exact bot_le

/-- The inertia-fixed subspace is the whole representation space. -/
theorem inertia_invariants_eq_top (ρ : Representation ℂ (UnramifiedWeil K s) V) :
    Representation.invariants (ρ.comp (Inertia K s).subtype) = ⊤ :=
  (PaperXI.NormalInertia.fixed_top_iff_le_kernel ρ (Inertia K s)).2
    (inertia_le_kernel K s ρ)

/-- Frobenius polynomial of a representation of the finite unramified Weil model.
It is the same reverse characteristic-polynomial convention used by the existing
Paper XI local-factor modules. -/
noncomputable def frobeniusPolynomial [FiniteDimensional ℂ V]
    (ρ : Representation ℂ (UnramifiedWeil K s) V) : ℂ[X] :=
  (ρ (geometricLift K s)).charpoly.reverse

/-- Rational unramified local factor: reciprocal of the full geometric-Frobenius polynomial. -/
noncomputable def unramifiedLocalFactor [FiniteDimensional ℂ V]
    (ρ : Representation ℂ (UnramifiedWeil K s) V) : RatFunc ℂ :=
  (algebraMap ℂ[X] (RatFunc ℂ) (frobeniusPolynomial K s ρ))⁻¹


/-- The canonical linear equivalence from inertia-fixed vectors to the full
space, available because inertia is trivial in the finite unramified model. -/
noncomputable def inertiaFixedEquiv (ρ : Representation ℂ (UnramifiedWeil K s) V) :
    Representation.invariants (ρ.comp (Inertia K s).subtype) ≃ₗ[ℂ] V :=
  LinearEquiv.ofTop _ (inertia_invariants_eq_top K s ρ)

/-- Geometric Frobenius restricted to the actual inertia-fixed subspace. -/
noncomputable def fixedGeometricFrobenius
    (ρ : Representation ℂ (UnramifiedWeil K s) V) :
    Module.End ℂ (Representation.invariants (ρ.comp (Inertia K s).subtype)) :=
  (inertiaFixedEquiv K s ρ).symm.conj (ρ (geometricLift K s))

@[simp]
theorem fixedGeometricFrobenius_charpoly [FiniteDimensional ℂ V]
    (ρ : Representation ℂ (UnramifiedWeil K s) V) :
    (fixedGeometricFrobenius K s ρ).charpoly =
      (ρ (geometricLift K s)).charpoly := by
  exact (inertiaFixedEquiv K s ρ).symm.charpoly_conj _

/-- The local polynomial formed on the literal inertia-fixed subspace. -/
noncomputable def inertiaFrobeniusPolynomial [FiniteDimensional ℂ V]
    (ρ : Representation ℂ (UnramifiedWeil K s) V) : ℂ[X] :=
  (fixedGeometricFrobenius K s ρ).charpoly.reverse

/-- Trivial inertia makes the invariant-space and full-space Frobenius
polynomials literally equal. -/
theorem inertiaFrobeniusPolynomial_eq [FiniteDimensional ℂ V]
    (ρ : Representation ℂ (UnramifiedWeil K s) V) :
    inertiaFrobeniusPolynomial K s ρ = frobeniusPolynomial K s ρ := by
  unfold inertiaFrobeniusPolynomial frobeniusPolynomial
  rw [fixedGeometricFrobenius_charpoly]

/-- Local factor formed from Frobenius on actual inertia invariants. -/
noncomputable def inertiaLocalFactor [FiniteDimensional ℂ V]
    (ρ : Representation ℂ (UnramifiedWeil K s) V) : RatFunc ℂ :=
  (algebraMap ℂ[X] (RatFunc ℂ) (inertiaFrobeniusPolynomial K s ρ))⁻¹

/-- The invariant-space local factor is the full unramified local factor. -/
theorem inertiaLocalFactor_eq [FiniteDimensional ℂ V]
    (ρ : Representation ℂ (UnramifiedWeil K s) V) :
    inertiaLocalFactor K s ρ = unramifiedLocalFactor K s ρ := by
  unfold inertiaLocalFactor unramifiedLocalFactor
  rw [inertiaFrobeniusPolynomial_eq]

set_option maxHeartbeats 800000 in
/-- Determinant form of the reverse characteristic polynomial. -/
theorem frobeniusPolynomial_eq_det [FiniteDimensional ℂ V]
    (ρ : Representation ℂ (UnramifiedWeil K s) V)
    {ι : Type*} [Fintype ι] [DecidableEq ι] (b : Module.Basis ι ℂ V) :
    frobeniusPolynomial K s ρ =
      Matrix.det (1 - (X : ℂ[X]) •
        (LinearMap.toMatrix b b (ρ (geometricLift K s))).map Polynomial.C) := by
  rw [frobeniusPolynomial, ← LinearMap.charpoly_toMatrix (ρ (geometricLift K s)) b,
    Matrix.reverse_charpoly]
  rfl

/-- The Frobenius polynomial has constant coefficient one. -/
theorem frobeniusPolynomial_coeff_zero [FiniteDimensional ℂ V]
    (ρ : Representation ℂ (UnramifiedWeil K s) V) :
    (frobeniusPolynomial K s ρ).coeff 0 = 1 := by
  rw [frobeniusPolynomial, Polynomial.coeff_zero_reverse]
  exact (ρ (geometricLift K s)).charpoly_monic.leadingCoeff

/-- Evaluation at zero is one. -/
theorem frobeniusPolynomial_eval_zero [FiniteDimensional ℂ V]
    (ρ : Representation ℂ (UnramifiedWeil K s) V) :
    Polynomial.eval 0 (frobeniusPolynomial K s ρ) = 1 := by
  rw [← Polynomial.coeff_zero_eq_eval_zero, frobeniusPolynomial_coeff_zero]

/-- The Frobenius polynomial is nonzero. -/
theorem frobeniusPolynomial_ne_zero [FiniteDimensional ℂ V]
    (ρ : Representation ℂ (UnramifiedWeil K s) V) :
    frobeniusPolynomial K s ρ ≠ 0 := by
  intro h
  have h0 := frobeniusPolynomial_coeff_zero K s ρ
  rw [h] at h0
  simp at h0

/-- Its image in the rational-function field is nonzero. -/
theorem mappedFrobeniusPolynomial_ne_zero [FiniteDimensional ℂ V]
    (ρ : Representation ℂ (UnramifiedWeil K s) V) :
    algebraMap ℂ[X] (RatFunc ℂ) (frobeniusPolynomial K s ρ) ≠ 0 :=
  (map_ne_zero_iff _ (RatFunc.algebraMap_injective ℂ)).2
    (frobeniusPolynomial_ne_zero K s ρ)

/-- The local factor is a genuine reciprocal of the Frobenius polynomial. -/
theorem unramifiedLocalFactor_mul_polynomial [FiniteDimensional ℂ V]
    (ρ : Representation ℂ (UnramifiedWeil K s) V) :
    unramifiedLocalFactor K s ρ *
      algebraMap ℂ[X] (RatFunc ℂ) (frobeniusPolynomial K s ρ) = 1 := by
  rw [unramifiedLocalFactor]
  exact inv_mul_cancel₀ (mappedFrobeniusPolynomial_ne_zero K s ρ)

/-- The reciprocal identity also holds in the opposite order. -/
theorem polynomial_mul_unramifiedLocalFactor [FiniteDimensional ℂ V]
    (ρ : Representation ℂ (UnramifiedWeil K s) V) :
    algebraMap ℂ[X] (RatFunc ℂ) (frobeniusPolynomial K s ρ) *
      unramifiedLocalFactor K s ρ = 1 := by
  rw [unramifiedLocalFactor]
  exact mul_inv_cancel₀ (mappedFrobeniusPolynomial_ne_zero K s ρ)

/-- The unramified local factor is nonzero. -/
theorem unramifiedLocalFactor_ne_zero [FiniteDimensional ℂ V]
    (ρ : Representation ℂ (UnramifiedWeil K s) V) :
    unramifiedLocalFactor K s ρ ≠ 0 := by
  rw [unramifiedLocalFactor]
  exact inv_ne_zero (mappedFrobeniusPolynomial_ne_zero K s ρ)


end Representation

end PaperXI.FiniteUnramifiedWeil
