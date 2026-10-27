import KomorebiLSM.EllipsoidGeometry
import Mathlib.Algebra.Order.BigOperators.Ring.Finset

/-! The actual inverse-metric dual Cauchy--Schwarz inequality and the mass
orientation implication used by the full P62 certificate. -/
set_option autoImplicit false
namespace Komorebi.LSM.OrientedEllipsoid
open Matrix
open scoped BigOperators
variable {D : Type*} [Fintype D] [DecidableEq D]

/-- The inverse in the dual quadratic form is the actual nonsingular matrix
inverse. Positivity of the primal metric entails this inequality. -/
theorem metric_dual_cauchy_schwarz (H : Matrix D D ℝ) (hH : H.PosDef)
    (b y : D → ℝ) :
    (b ⬝ᵥ y)^2 ≤ (b ⬝ᵥ (H⁻¹ *ᵥ b)) * (y ⬝ᵥ (H *ᵥ y)) := by
  let L := factor H hH
  let v := H⁻¹ *ᵥ b
  have hL : L.transpose * L=H := factor_square H hH
  have hHv : H *ᵥ v=b := by
    change H *ᵥ (H⁻¹ *ᵥ b)=b
    rw [Matrix.mulVec_mulVec,Matrix.mul_nonsing_inv _
      ((Matrix.isUnit_iff_isUnit_det _).mp hH.isUnit),Matrix.one_mulVec]
  have hcross : (L *ᵥ v) ⬝ᵥ (L *ᵥ y)=b ⬝ᵥ y := by
    rw [← Matrix.dotProduct_transpose_mulVec L y (L *ᵥ v),Matrix.mulVec_mulVec,hL,hHv,
      dotProduct_comm]
  have hleft : (L *ᵥ v) ⬝ᵥ (L *ᵥ v)=b ⬝ᵥ (H⁻¹ *ᵥ b) := by
    rw [← Matrix.dotProduct_transpose_mulVec L v (L *ᵥ v),Matrix.mulVec_mulVec,hL,hHv,
      dotProduct_comm]
  have hright : (L *ᵥ y) ⬝ᵥ (L *ᵥ y)=y ⬝ᵥ (H *ᵥ y) := by
    rw [← Matrix.dotProduct_transpose_mulVec L y (L *ᵥ y),Matrix.mulVec_mulVec,hL]
  have hcs : ((L *ᵥ v) ⬝ᵥ (L *ᵥ y))^2 ≤
      ((L *ᵥ v) ⬝ᵥ (L *ᵥ v)) * ((L *ᵥ y) ⬝ᵥ (L *ᵥ y)) := by
    simpa only [dotProduct,pow_two] using
      Finset.sum_mul_sq_le_sq_mul_sq Finset.univ (L *ᵥ v) (L *ᵥ y)
  rwa [hcross,hleft,hright] at hcs

/-- The complete orientation hypotheses force the desired nonnegative mass
sheet, including zero mass and empty spatial dimension. -/
theorem mass_orientation (H : Matrix D D ℝ) (hH : H.PosDef)
    (b y : D → ℝ) (β m : ℝ) (hm : 0≤m)
    (hy : y ⬝ᵥ (H *ᵥ y)≤m^2) (hβ : 0≤β)
    (hdual : 0≤β^2-b ⬝ᵥ (H⁻¹ *ᵥ b)) : 0≤β*m+b ⬝ᵥ y := by
  have hq : 0≤y ⬝ᵥ (H *ᵥ y) := by
    simpa only [Pi.star_apply,star_trivial] using hH.posSemidef.dotProduct_mulVec_nonneg y
  have hbound : (b ⬝ᵥ y)^2≤(β*m)^2 := by
    calc
      _≤(b ⬝ᵥ (H⁻¹ *ᵥ b)) * (y ⬝ᵥ (H *ᵥ y)) := metric_dual_cauchy_schwarz H hH b y
      _≤β^2*m^2 := mul_le_mul (sub_nonneg.mp hdual) hy hq (sq_nonneg β)
      _=(β*m)^2 := by ring
  have habs : |b ⬝ᵥ y|≤β*m :=
    (sq_le_sq₀ (abs_nonneg _) (mul_nonneg hβ hm)).mp (by simpa only [sq_abs] using hbound)
  linarith [(abs_le.mp habs).1]

end Komorebi.LSM.OrientedEllipsoid
