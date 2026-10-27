import PaperXI.HyperbolicDeterminant
import PaperXI.OddPhase

/-! Source 12.8 for the literal hyperbolic action. The calculation also holds
for the defined determinant phase in characteristic two; no Weil trace
interpretation or normalization is asserted here. -/
set_option autoImplicit false
noncomputable section
namespace PaperXI.HyperbolicPhase

variable {p : ℕ} [Fact p.Prime]
variable {U : Type*} [AddCommGroup U] [Module (ZMod p) U]
variable [FiniteDimensional (ZMod p) U]

/-- The actual constructed hyperbolic action satisfies the phase-domain condition. -/
theorem fixedPointFree (a : U ≃ₗ[ZMod p] U) (ha : OddPhase.FixedPointFree a) :
    OddPhase.FixedPointFree (HyperbolicSpace.action a) :=
  HyperbolicSpace.action_fixedPointFree a ha

/-- Source 12.8: the determinant phase of the actual hyperbolic action is the
quadratic character of the determinant on the original space. -/
theorem source (a : U ≃ₗ[ZMod p] U) (ha : OddPhase.FixedPointFree a) :
    OddPhase.phase (HyperbolicSpace.action a) =
      quadraticChar (ZMod p) (LinearMap.det a.toLinearMap) := by
  have hd : LinearMap.det (a.toLinearMap - 1) ≠ 0 :=
    (OddPhase.fixedPointFree_iff_det_ne_zero a).mp ha
  have hdim : Module.finrank (ZMod p) (HyperbolicSpace.Space (ZMod p) U) / 2 =
      Module.finrank (ZMod p) U := by
    rw [HyperbolicSpace.finrank]
    omega
  rw [OddPhase.phase, hdim]
  change quadraticChar (ZMod p) (-1) ^ Module.finrank (ZMod p) U *
      quadraticChar (ZMod p) (LinearMap.det ((HyperbolicSpace.action a).toLinearMap - 1)) = _
  rw [HyperbolicDeterminant.total_difference_det, map_mul, map_mul,
    quadraticChar_sq_one' hd, map_pow, ← MulChar.inv_apply',
    (quadraticChar_isQuadratic (ZMod p)).inv, mul_one]
  have hsign : (quadraticChar (ZMod p) (-1) ^ Module.finrank (ZMod p) U) ^ 2 = 1 := by
    rw [← pow_mul, Nat.mul_comm _ 2, pow_mul,
      quadraticChar_sq_one (neg_ne_zero.mpr one_ne_zero), one_pow]
  calc
    _ = (quadraticChar (ZMod p) (-1) ^ Module.finrank (ZMod p) U) ^ 2 *
        quadraticChar (ZMod p) (LinearMap.det a.toLinearMap) := by ring
    _ = _ := by rw [hsign, one_mul]

/-- All symplectic and fixed-point-free hypotheses are proved for the same
carrier and action appearing in the source phase formula. -/
theorem symplectic_fixedPointFree (a : U ≃ₗ[ZMod p] U) (ha : OddPhase.FixedPointFree a) :
    (HyperbolicSpace.form (ZMod p) U).IsAlt ∧
    (HyperbolicSpace.form (ZMod p) U).Nondegenerate ∧
    (∀ x y, HyperbolicSpace.form (ZMod p) U (HyperbolicSpace.action a x)
      (HyperbolicSpace.action a y) = HyperbolicSpace.form (ZMod p) U x y) ∧
    OddPhase.FixedPointFree (HyperbolicSpace.action a) :=
  ⟨HyperbolicSpace.form_isAlt (ZMod p) U, HyperbolicSpace.form_nondegenerate (ZMod p) U,
    HyperbolicSpace.action_form a, fixedPointFree a ha⟩

end PaperXI.HyperbolicPhase
