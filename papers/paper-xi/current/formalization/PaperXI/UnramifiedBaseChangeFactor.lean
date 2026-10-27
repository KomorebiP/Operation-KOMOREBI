import PaperXI.RankOneEulerFactor

/-! # Integer-degree base change for the finite unramified Weil model

The finite unramified model is canonically equivalent to `Multiplicative ℤ`.
Multiplication of the degree by `n` therefore gives the restriction map that
models unramified base change of residue degree `n`. This module proves the
resulting Frobenius-power and Euler-factor formulas.

No actual tower of local fields is constructed here; the theorem is scoped to
this integer-degree Weil model.
-/

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

/-- Multiplication by a natural residue degree on the integral degree group. -/
def integerDegreeDilation (n : ℕ) : Multiplicative ℤ →* Multiplicative ℤ where
  toFun z := Multiplicative.ofAdd ((n : ℤ) * Multiplicative.toAdd z)
  map_one' := by simp
  map_mul' a b := by
    apply Multiplicative.toAdd.injective
    simp [mul_add]

/-- Degree dilation on the finite unramified Weil model. -/
def degreeDilation (n : ℕ) : UnramifiedWeil K s →* UnramifiedWeil K s :=
  (degreeEquiv K s).symm.toMonoidHom.comp
    ((integerDegreeDilation n).comp (degreeEquiv K s).toMonoidHom)

@[simp]
theorem degreeEquiv_degreeDilation (n : ℕ) (w : UnramifiedWeil K s) :
    degreeEquiv K s (degreeDilation K s n w) =
      integerDegreeDilation n (degreeEquiv K s w) := by
  simp [degreeDilation]

@[simp]
theorem degree_degreeDilation (n : ℕ) (w : UnramifiedWeil K s) :
    Multiplicative.toAdd
      (degree (MonoidHom.id (ResidueGalois K s)) (geometricFrobenius K s)
        (degreeDilation K s n w)) =
      (n : ℤ) * Multiplicative.toAdd
        (degree (MonoidHom.id (ResidueGalois K s)) (geometricFrobenius K s) w) := by
  change Multiplicative.toAdd (degreeEquiv K s (degreeDilation K s n w)) = _
  rw [degreeEquiv_degreeDilation]
  rfl

/-- Degree dilation sends the distinguished Frobenius lift to its `n`-th power. -/
@[simp]
theorem degreeDilation_geometricLift (n : ℕ) :
    degreeDilation K s n (geometricLift K s) = (geometricLift K s) ^ n := by
  have hdeg : degreeEquiv K s (geometricLift K s) = Multiplicative.ofAdd 1 := by
    simpa only [degreeEquiv_apply] using degree_geometricLift K s
  apply (degreeEquiv K s).injective
  rw [degreeEquiv_degreeDilation, map_pow, hdeg]
  apply Multiplicative.toAdd.injective
  simp [integerDegreeDilation]

/-- Successive degree dilations multiply their residue degrees. -/
theorem degreeDilation_comp (m n : ℕ) :
    (degreeDilation K s m).comp (degreeDilation K s n) =
      degreeDilation K s (m * n) := by
  apply MonoidHom.ext
  intro w
  apply (degreeEquiv K s).injective
  simp [degreeDilation, integerDegreeDilation, mul_assoc]

section Representation

variable {V : Type*} [AddCommGroup V] [Module ℂ V]

/-- Restriction of a representation along degree dilation. -/
def baseChangeRepresentation (n : ℕ)
    (ρ : Representation ℂ (UnramifiedWeil K s) V) :
    Representation ℂ (UnramifiedWeil K s) V :=
  ρ.comp (degreeDilation K s n)

/-- Geometric Frobenius after degree-`n` base change acts by the `n`-th power
of the original Frobenius operator. -/
theorem baseChange_geometricFrobenius (n : ℕ)
    (ρ : Representation ℂ (UnramifiedWeil K s) V) :
    baseChangeRepresentation K s n ρ (geometricLift K s) =
      (ρ (geometricLift K s)) ^ n := by
  change ρ (degreeDilation K s n (geometricLift K s)) = _
  rw [degreeDilation_geometricLift]
  exact map_pow ρ (geometricLift K s) n

/-- Base changes compose according to multiplication of residue degrees. -/
theorem baseChangeRepresentation_comp (m n : ℕ)
    (ρ : Representation ℂ (UnramifiedWeil K s) V) :
    baseChangeRepresentation K s m (baseChangeRepresentation K s n ρ) =
      baseChangeRepresentation K s (n * m) ρ := by
  ext w
  simp [baseChangeRepresentation, degreeDilation, integerDegreeDilation,
    mul_comm, mul_left_comm, mul_assoc]

variable [FiniteDimensional ℂ V]
variable (ρ : Representation ℂ (UnramifiedWeil K s) V)

/-- Frobenius polynomial transforms by replacing Frobenius with its `n`-th
power. -/
theorem baseChange_frobeniusPolynomial (n : ℕ)
    (ρ : Representation ℂ (UnramifiedWeil K s) V) :
    frobeniusPolynomial K s (baseChangeRepresentation K s n ρ) =
      ((ρ (geometricLift K s)) ^ n).charpoly.reverse := by
  rw [frobeniusPolynomial, baseChange_geometricFrobenius]

/-- The local factor after degree dilation is the reciprocal characteristic
polynomial of the Frobenius power. -/
theorem baseChange_localFactor (n : ℕ)
    (ρ : Representation ℂ (UnramifiedWeil K s) V) :
    unramifiedLocalFactor K s (baseChangeRepresentation K s n ρ) =
      (algebraMap ℂ[X] (RatFunc ℂ)
        (((ρ (geometricLift K s)) ^ n).charpoly.reverse))⁻¹ := by
  rw [unramifiedLocalFactor, baseChange_frobeniusPolynomial]

variable [Representation.IsIrreducible ρ]

/-- Rank-one base change raises the Frobenius eigenvalue to the residue degree. -/
theorem irreducible_baseChange_frobeniusPolynomial (n : ℕ) :
    frobeniusPolynomial K s (baseChangeRepresentation K s n ρ) =
      1 - C ((frobeniusEigenvalue K s ρ) ^ n) * X := by
  rw [baseChange_frobeniusPolynomial]
  have hpow : (ρ (geometricLift K s)) ^ n =
      (frobeniusEigenvalue K s ρ) ^ n • LinearMap.id := by
    rw [geometricFrobenius_action_eq_smul_id K s ρ]
    induction n with
    | zero =>
        ext x
        simp
    | succ n ih =>
        rw [pow_succ, ih]
        ext x
        simp [pow_succ, mul_smul, mul_comm]
  rw [hpow]
  exact reverse_charpoly_smul_id
    (irreducible_finrank_eq_one K s ρ) ((frobeniusEigenvalue K s ρ) ^ n)

/-- Explicit Euler-factor base-change law in the irreducible rank-one case. -/
theorem irreducible_baseChange_localFactor (n : ℕ) :
    unramifiedLocalFactor K s (baseChangeRepresentation K s n ρ) =
      rankOneEulerFactor ((frobeniusEigenvalue K s ρ) ^ n) := by
  rw [unramifiedLocalFactor, rankOneEulerFactor,
    irreducible_baseChange_frobeniusPolynomial K s ρ]

end Representation

end PaperXI.FiniteUnramifiedWeil
