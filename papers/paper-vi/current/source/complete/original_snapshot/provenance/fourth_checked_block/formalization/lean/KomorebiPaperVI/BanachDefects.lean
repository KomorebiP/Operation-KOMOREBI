import KomorebiPaperVI.Semigroups

/-! Author: Komorebi P. Duhamel defects in a real Banach algebra. -/
namespace KomorebiPaperVI.BanachDefects
open KomorebiPaperVI.Semigroups
variable {R : Type*} [NormedRing R] [NormedAlgebra ℝ R] [CompleteSpace R]

theorem duhamel_derivative (A B C : R) (t r : ℝ) :
    HasDerivAt (fun u => transfer B (t-u)*C*transfer A u)
      (transfer B (t-r)*(C*A-B*C)*transfer A r) r := by
  have hsub : HasDerivAt (fun u : ℝ => t-u) (-1) r := by
    convert! (hasDerivAt_const r t).sub (hasDerivAt_id r) using 1
    simp
  have hB : HasDerivAt (fun u : ℝ => transfer B (t-u))
      ((-1:ℝ) • (transfer B (t-r)*B)) r := (transfer_derivative_right B (t-r)).scomp r
    hsub
  convert! (hB.mul_const C).mul (transfer_derivative_left A r) using 1
  simp only [neg_smul,one_smul]
  noncomm_ring

theorem duhamel (A B C : R) (t : ℝ) :
    C*transfer A t-transfer B t*C=
      ∫ r in 0..t,transfer B (t-r)*(C*A-B*C)*transfer A r := by
  have hc : Continuous (fun r => transfer B (t-r)*(C*A-B*C)*transfer A r) := by fun_prop
  have h := intervalIntegral.integral_eq_sub_of_hasDerivAt
    (fun r _ => duhamel_derivative A B C t r) (hc.intervalIntegrable 0 t)
  simpa only [sub_self,transfer_zero,zero_sub,sub_zero,one_mul,mul_one] using h.symm

theorem contraction_bound (A B C : R) (t : ℝ) (ht : 0 ≤ t)
    (hA : ∀ r,0 ≤ r → ‖transfer A r‖ ≤ 1)
    (hB : ∀ r,0 ≤ r → ‖transfer B r‖ ≤ 1) :
    ‖C*transfer A t-transfer B t*C‖ ≤ t*‖C*A-B*C‖ := by
  rw [duhamel]
  have hc : Continuous (fun r => transfer B (t-r)*(C*A-B*C)*transfer A r) := by fun_prop
  calc
    _ ≤ ∫ r in 0..t,‖transfer B (t-r)*(C*A-B*C)*transfer A r‖ :=
      intervalIntegral.norm_integral_le_integral_norm ht
    _ ≤ ∫ _ in 0..t,‖C*A-B*C‖ := by
      apply intervalIntegral.integral_mono_on ht (hc.norm.intervalIntegrable 0 t) intervalIntegrable_const
      intro r hr
      calc
        _ ≤ ‖transfer B (t-r)‖*‖C*A-B*C‖*‖transfer A r‖ := norm_mul_le_of_le (norm_mul_le _ _) le_rfl
        _ ≤ 1*‖C*A-B*C‖*1 := by gcongr; exact hB (t-r) (by linarith [hr.2]); exact hA r hr.1
        _ = _ := by ring
    _ = _ := by simp [smul_eq_mul]

end KomorebiPaperVI.BanachDefects
