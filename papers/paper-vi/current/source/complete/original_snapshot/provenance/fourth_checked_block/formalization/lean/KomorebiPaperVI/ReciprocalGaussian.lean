import Mathlib.Analysis.SpecialFunctions.Gaussian.GaussianIntegral

/-! Author: Komorebi P. A reciprocal Gaussian substitution for the positive Poisson mode. -/
namespace KomorebiPaperVI.ReciprocalGaussian
open Set MeasureTheory
noncomputable def phi (a x : ℝ) : ℝ := x-a/x

theorem phi_derivative (a x : ℝ) (hx : x≠0) :
    HasDerivAt (phi a) (1+a/x^2) x := by
  convert! (hasDerivAt_id x).sub ((hasDerivAt_const x a).div (hasDerivAt_id x) hx) using 1
  dsimp
  ring

theorem phi_injective (a : ℝ) (ha : 0 < a) : InjOn (phi a) (Ioi 0) := by
  apply StrictMonoOn.injOn
  intro x hx y hy hxy
  unfold phi
  have h : a/y < a/x := div_lt_div_of_pos_left ha hx hxy
  linarith

theorem phi_surjective (a : ℝ) (ha : 0 < a) : phi a '' Ioi 0=univ := by
  apply eq_univ_of_forall
  intro y
  let r := Real.sqrt (y^2+4*a)
  have hr : r^2=y^2+4*a := Real.sq_sqrt (by positivity)
  have hr0 : 0 ≤ r := Real.sqrt_nonneg _
  have hpos : 0 < (y+r)/2 := by nlinarith
  refine ⟨(y+r)/2,hpos,?_⟩
  unfold phi
  apply (sub_eq_iff_eq_add).mpr
  have hne : y+r≠0 := by linarith
  field_simp [hne]
  nlinarith

theorem gaussian_jacobian_integrable (a : ℝ) (ha : 0 < a) :
    IntegrableOn (fun x => (1+a/x^2)*Real.exp (-(phi a x)^2)) (Ioi 0) := by
  have h := (integrableOn_image_iff_integrableOn_abs_deriv_smul measurableSet_Ioi
    (fun x hx => (phi_derivative a x hx.ne').hasDerivWithinAt) (phi_injective a ha)
    (fun u : ℝ => Real.exp (-u^2))).mp
    (by rw [phi_surjective a ha]; simpa using integrable_exp_neg_mul_sq (b := 1) (by norm_num))
  apply h.congr
  filter_upwards [ae_restrict_mem measurableSet_Ioi] with x hx
  simp only [smul_eq_mul,abs_of_pos (by positivity : 0 < 1+a/x^2)]

theorem gaussian_jacobian_integral (a : ℝ) (ha : 0 < a) :
    (∫ x in Ioi 0,(1+a/x^2)*Real.exp (-(phi a x)^2))=Real.sqrt Real.pi := by
  have h := integral_image_eq_integral_abs_deriv_smul measurableSet_Ioi
    (fun x hx => (phi_derivative a x hx.ne').hasDerivWithinAt) (phi_injective a ha)
    (fun u : ℝ => Real.exp (-u^2))
  rw [phi_surjective a ha,setIntegral_univ] at h
  have hg : (∫ u : ℝ,Real.exp (-u^2))=Real.sqrt Real.pi := by
    simpa using integral_gaussian (1:ℝ)
  rw [hg] at h
  rw [h]
  apply setIntegral_congr_fun measurableSet_Ioi
  intro x hx
  simp only [smul_eq_mul,abs_of_pos (by positivity : 0 < 1+a/x^2)]

theorem reciprocal_derivative (a x : ℝ) (hx : x≠0) :
    HasDerivAt (fun u => a/u) (-a/x^2) x := by
  convert! (hasDerivAt_const x a).div (hasDerivAt_id x) hx using 1
  dsimp
  ring

theorem reciprocal_image (a : ℝ) (ha : 0 < a) : (fun x => a/x) '' Ioi 0=Ioi 0 := by
  ext y
  constructor
  · rintro ⟨x,hx,rfl⟩
    exact div_pos ha hx
  · intro hy
    refine ⟨a/y,div_pos ha hy,?_⟩
    field_simp

theorem reciprocal_injective (a : ℝ) (ha : 0 < a) : InjOn (fun x => a/x) (Ioi 0) := by
  intro x hx y hy h
  change 0 < x at hx
  change 0 < y at hy
  have hxy : a*y=a*x := (div_eq_div_iff hx.ne' hy.ne').mp h
  nlinarith

theorem reciprocal_phi (a x : ℝ) (ha : a≠0) (hx : x≠0) : phi a (a/x)= -phi a x := by
  unfold phi
  field_simp
  ring

theorem reciprocal_gaussian_symmetry (a : ℝ) (ha : 0 < a) :
    (∫ x in Ioi 0,a/x^2*Real.exp (-(phi a x)^2))=
      ∫ x in Ioi 0,Real.exp (-(phi a x)^2) := by
  have h := integral_image_eq_integral_abs_deriv_smul measurableSet_Ioi
    (fun x hx => (reciprocal_derivative a x hx.ne').hasDerivWithinAt)
    (reciprocal_injective a ha) (fun x => Real.exp (-(phi a x)^2))
  rw [reciprocal_image a ha] at h
  rw [h]
  apply setIntegral_congr_fun measurableSet_Ioi
  intro x hx
  dsimp only
  rw [reciprocal_phi a x ha.ne' hx.ne',neg_sq]
  simp only [smul_eq_mul,abs_div,abs_neg,abs_of_pos ha,abs_of_nonneg (sq_nonneg x)]

theorem phi_gaussian_integrable (a : ℝ) (ha : 0 < a) :
    IntegrableOn (fun x => Real.exp (-(phi a x)^2)) (Ioi 0) := by
  have hc : ContinuousOn (fun x => Real.exp (-(phi a x)^2)) (Ioi 0) := by
    intro x hx
    apply ContinuousAt.continuousWithinAt
    unfold phi
    fun_prop (disch := exact hx.ne')
  apply (gaussian_jacobian_integrable a ha).mono' (hc.aestronglyMeasurable measurableSet_Ioi)
  filter_upwards [ae_restrict_mem measurableSet_Ioi] with x hx
  rw [Real.norm_of_nonneg (Real.exp_pos _).le]
  have h : 0 ≤ a/x^2 := by positivity
  nlinarith [Real.exp_pos (-(phi a x)^2)]

theorem phi_gaussian_integral (a : ℝ) (ha : 0 < a) :
    (∫ x in Ioi 0,Real.exp (-(phi a x)^2))=Real.sqrt Real.pi/2 := by
  have hi := phi_gaussian_integrable a ha
  have hw : IntegrableOn (fun x => a/x^2*Real.exp (-(phi a x)^2)) (Ioi 0) := by
    convert! (gaussian_jacobian_integrable a ha).sub hi using 1
    funext x
    dsimp only [Pi.sub_apply]
    ring
  have hj := gaussian_jacobian_integral a ha
  have he : (fun x => (1+a/x^2)*Real.exp (-(phi a x)^2))=
      fun x => Real.exp (-(phi a x)^2)+a/x^2*Real.exp (-(phi a x)^2) := by funext x; ring
  rw [he,integral_add hi hw,reciprocal_gaussian_symmetry a ha] at hj
  linarith

theorem reciprocal_square_gaussian (a : ℝ) (ha : 0 ≤ a) :
    (∫ x in Ioi 0,Real.exp (-x^2-a^2/x^2))=Real.exp (-2*a)*Real.sqrt Real.pi/2 := by
  rcases ha.eq_or_lt with he | ha
  · subst a
    simpa using integral_gaussian_Ioi (1:ℝ)
  · have he : EqOn (fun x => Real.exp (-x^2-a^2/x^2))
        (fun x => Real.exp (-2*a)*Real.exp (-(phi a x)^2)) (Ioi 0) := by
      intro x hx
      dsimp only
      rw [← Real.exp_add]
      congr 1
      unfold phi
      have hx0 : x ≠ 0 := ne_of_gt hx
      field_simp [hx0]
      ring
    rw [setIntegral_congr_fun measurableSet_Ioi he,integral_const_mul,phi_gaussian_integral a ha]
    ring

end KomorebiPaperVI.ReciprocalGaussian
