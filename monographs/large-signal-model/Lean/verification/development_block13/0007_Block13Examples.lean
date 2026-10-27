import KomorebiLSM.SpectralSharpness

set_option autoImplicit false
namespace Komorebi.LSM.Block13Examples
open Komorebi.LSM.Spectral Komorebi.LSM.Identification

/-- The scalar factor two has the actual singular value two. -/
theorem double_leastPositive : leastPositive ((2:ℝ) • (LinearMap.id : ℝ →ₗ[ℝ] ℝ)) = 2 := by
  let A : ℝ →ₗ[ℝ] ℝ := (2:ℝ) • LinearMap.id
  have hsur : Function.Surjective A := by
    intro y
    refine ⟨y/2, ?_⟩
    simp only [A, LinearMap.smul_apply, LinearMap.id_apply, ContinuousLinearMap.coe_smul, ContinuousLinearMap.id_apply, ContinuousLinearMap.coe_coe, Pi.smul_apply, smul_eq_mul]
    ring
  have hr : 0 < Module.finrank ℝ A.range := by
    rw [LinearMap.range_eq_top.mpr hsur]
    simp
  obtain ⟨v,_,hn,ha⟩ := exists_unit_minimizer A hr
  change ‖(2:ℝ)*v‖ = leastPositive A at ha
  rw [norm_mul, Real.norm_of_nonneg (by norm_num : (0:ℝ) ≤ 2), hn, mul_one] at ha
  exact ha.symm

theorem double_inverse_norm :
    ‖pinvL ((2:ℝ) • ContinuousLinearMap.id ℝ ℝ)‖ = (1/2:ℝ) := by
  let A : ℝ →L[ℝ] ℝ := (2:ℝ) • ContinuousLinearMap.id ℝ ℝ
  have hsur : Function.Surjective A.toLinearMap := by
    intro y
    refine ⟨y/2, ?_⟩
    simp only [A, LinearMap.smul_apply, LinearMap.id_apply, ContinuousLinearMap.coe_smul, ContinuousLinearMap.id_apply, ContinuousLinearMap.coe_coe, Pi.smul_apply, smul_eq_mul]
    ring
  have hr : 0 < Module.finrank ℝ A.toLinearMap.range := by
    rw [LinearMap.range_eq_top.mpr hsur]
    simp
  have h := pinv_operator_norm_eq A hr
  have hs : leastPositive A.toLinearMap = 2 := double_leastPositive
  rw [hs] at h
  simpa only [A, inv_eq_one_div] using h

theorem zero_has_no_positive_singular_value : leastPositive (0 : ℝ →ₗ[ℝ] ℝ) = 0 := by
  simp [leastPositive]

noncomputable def firstCoordinate : EuclideanSpace ℝ (Fin 2) →ₗ[ℝ] ℝ :=
  (LinearMap.proj (0:Fin 2)).comp (WithLp.linearEquiv 2 ℝ (Fin 2 → ℝ)).toLinearMap

/-- A rank-one table cannot have a positive lower bound on its whole domain. -/
theorem global_lower_fails_for_projection :
    ∃ v : EuclideanSpace ℝ (Fin 2),
      ‖firstCoordinate v‖ < leastPositive firstCoordinate * ‖v‖ := by
  have hsur : Function.Surjective firstCoordinate := by
    intro y
    exact ⟨WithLp.toLp 2 (fun _ => y), rfl⟩
  have hr : 0 < Module.finrank ℝ firstCoordinate.range := by
    rw [LinearMap.range_eq_top.mpr hsur]
    simp
  let v : EuclideanSpace ℝ (Fin 2) := WithLp.toLp 2 ![0,1]
  have hv : v ≠ 0 := by
    intro h
    have h' := congrArg (fun w : EuclideanSpace ℝ (Fin 2) => w 1) h
    norm_num [v] at h'
  have hz : firstCoordinate v = 0 := by rfl
  refine ⟨v, ?_⟩
  rw [hz, norm_zero]
  exact mul_pos (leastPositive_pos firstCoordinate hr) (norm_pos_iff.mpr hv)

end Komorebi.LSM.Block13Examples
