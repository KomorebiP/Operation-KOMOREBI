import PaperX.IdealClassQuantitativeAttachment

/-! Exact normalization of the ordinary ideal-class counting coefficient. -/

set_option autoImplicit false
noncomputable section

open Ideal MeasureTheory
open scoped nonZeroDivisors Real Classical
open NumberField NumberField.InfinitePlace NumberField.mixedEmbedding
open NumberField.mixedEmbedding.euclidean NumberField.mixedEmbedding.fundamentalCone
open NumberField.Units

namespace PaperX.IdealClassQuantitative

variable (K : Type*) [Field K] [NumberField K]

/-- The classical coefficient of the count in one ordinary ideal class. -/
def classResidue : ℝ :=
  (2 ^ nrRealPlaces K * (2 * Real.pi) ^ nrComplexPlaces K * regulator K) /
    (torsionOrder K * Real.sqrt |discr K|)

/-- The cone volume divided by its ideal-lattice covolume. -/
def latticeDensity (J : (Ideal (𝓞 K))⁰) : ℝ :=
  volume.real (coneRegion K 1) / ZLattice.covolume (idealEuclideanLattice K J)

/-- Scaling by the norm of the representative and dividing by the roots of unity
recovers the coefficient independent of the chosen ideal class. -/
theorem latticeDensity_normalization (J : (Ideal (𝓞 K))⁰) :
    latticeDensity K J * absNorm (J : Ideal (𝓞 K)) * (torsionOrder K : ℝ)⁻¹ =
      classResidue K := by
  classical
  have hJ : (absNorm (J : Ideal (𝓞 K)) : ℝ) ≠ 0 :=
    Nat.cast_ne_zero.mpr (absNorm_ne_zero_of_nonZeroDivisors J)
  rw [latticeDensity, classResidue, coneRegion_one, MeasureTheory.measureReal_def,
    (volumePreserving_toMixed K).measure_preimage (measurableSet_normLeOne K).nullMeasurableSet,
    volume_normLeOne, ZLattice.covolume_comap _ _ _ (volumePreserving_toMixed K),
    covolume_idealLattice, ENNReal.toReal_mul, ENNReal.toReal_mul, ENNReal.toReal_pow,
    ENNReal.toReal_pow, ENNReal.toReal_ofNat, ENNReal.coe_toReal, NNReal.coe_real_pi,
    ENNReal.toReal_ofReal (regulator_pos K).le, FractionalIdeal.coe_mk0,
    FractionalIdeal.coeIdeal_absNorm, Rat.cast_natCast, div_eq_mul_inv, div_eq_mul_inv,
    mul_inv, mul_inv, mul_inv, inv_pow, inv_inv]
  ring_nf
  rw [mul_inv_cancel_right₀ hJ]

/-- Positivity of the torsion divisor, used for honest division of the count. -/
theorem torsionOrder_cast_pos : (0 : ℝ) < torsionOrder K :=
  Nat.cast_pos.mpr (Nat.pos_of_ne_zero (torsionOrder_ne_zero K))

/-- An exact real-valued error identity before any geometric estimate is assumed. -/
theorem class_error_eq_lattice_error {C : ClassGroup (𝓞 K)}
    {J : (Ideal (𝓞 K))⁰} (hJ : ClassGroup.mk0 J = C⁻¹) (s : ℝ) :
    (classCount K C s : ℝ) - classResidue K * s =
      ((latticeCount K J (s * absNorm (J : Ideal (𝓞 K))) : ℝ) -
        latticeDensity K J * (s * absNorm (J : Ideal (𝓞 K)))) /
          torsionOrder K := by
  rw [latticeCount_eq_classCount_mul_torsion K hJ, Nat.cast_mul,
    ← latticeDensity_normalization K J]
  have ht : (torsionOrder K : ℝ) ≠ 0 := (torsionOrder_cast_pos K).ne'
  field_simp [ht]

end PaperX.IdealClassQuantitative
