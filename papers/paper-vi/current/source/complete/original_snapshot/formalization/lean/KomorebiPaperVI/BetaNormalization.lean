import Mathlib.Analysis.SpecialFunctions.Gamma.Beta
import Mathlib.Analysis.SpecialFunctions.ContinuousFunctionalCalculus.Rpow.IntegralRepresentation

/-! Author: Komorebi P. Exact sine normalization of the fractional integral. -/
namespace KomorebiPaperVI.BetaNormalization
open Set MeasureTheory
set_option backward.isDefEq.respectTransparency false

noncomputable def betaKernel (a x : ℝ) : ℝ := x^(a-1)*(1-x)^(-a)
noncomputable def changeVariable (x : ℝ) : ℝ := x/(1+x)

theorem beta_value (a : ℝ) (ha : a∈Ioo 0 1) :
    (∫ x in Ioo 0 1,betaKernel a x)=Real.pi/Real.sin (Real.pi*a) := by
  have h := Complex.Gamma_mul_Gamma_eq_betaIntegral (s := (a:ℂ)) (t := 1-(a:ℂ))
    (by simpa using ha.1) (by simpa using sub_pos.mpr ha.2)
  rw [add_sub_cancel,Complex.Gamma_one,one_mul,Complex.Gamma_mul_Gamma_one_sub] at h
  have he : Complex.betaIntegral (a:ℂ) (1-(a:ℂ))=
      ((∫ x in Ioo 0 1,betaKernel a x):ℝ) := by
    rw [Complex.betaIntegral,intervalIntegral.integral_of_le (by norm_num : (0:ℝ) ≤ 1),
      integral_Ioc_eq_integral_Ioo]
    trans ∫ x in Ioo (0:ℝ) 1,(betaKernel a x:ℂ)
    · apply setIntegral_congr_fun measurableSet_Ioo
      intro x hx
      dsimp [betaKernel]
      rw [Complex.ofReal_mul,Complex.ofReal_cpow hx.1.le,Complex.ofReal_cpow (by linarith [hx.2] : 0 ≤ 1-x)]
      push_cast
      congr 2
      ring
    · exact integral_complex_ofReal
  rw [he] at h
  exact_mod_cast h.symm

theorem change_derivative (x : ℝ) (hx : 0 < x) :
    HasDerivAt changeVariable ((1+x)^(-2:ℤ)) x := by
  convert! (hasDerivAt_id x).div ((hasDerivAt_const x 1).add (hasDerivAt_id x)) (by linarith : 1+x≠0) using 1
  simp [zpow_neg,div_eq_mul_inv]

theorem change_injective : InjOn changeVariable (Ioi 0) := by
  intro x hx y hy h
  change 0 < x at hx
  change 0 < y at hy
  dsimp [changeVariable] at h
  have h := (div_eq_div_iff (by linarith : 1+x≠0) (by linarith : 1+y≠0)).mp h
  nlinarith

theorem change_image : changeVariable '' Ioi 0=Ioo 0 1 := by
  ext y
  constructor
  · rintro ⟨x,hx,rfl⟩
    change 0 < x at hx
    dsimp [changeVariable]
    exact ⟨div_pos hx (by linarith), (div_lt_one (by linarith : 0 < 1+x)).mpr (by linarith)⟩
  · intro hy
    refine ⟨y/(1-y),div_pos hy.1 (sub_pos.mpr hy.2),?_⟩
    dsimp [changeVariable]
    have hy0 : 1-y ≠ 0 := ne_of_gt (sub_pos.mpr hy.2)
    field_simp [hy0]
    ring

theorem change_integrand (a x : ℝ) (hx : 0 < x) :
    |(1+x)^(-2:ℤ)| • betaKernel a (changeVariable x)=x^(a-1)/(1+x) := by
  have hd : 0 < 1+x := by linarith
  have hs : 1-x/(1+x)=1/(1+x) := by field_simp; ring
  dsimp [betaKernel,changeVariable]
  rw [hs,Real.div_rpow hx.le hd.le,Real.rpow_neg (by positivity : 0 ≤ 1/(1+x)),Real.div_rpow zero_le_one hd.le]
  simp only [Real.one_rpow,one_div,inv_inv,zpow_neg,zpow_ofNat,abs_inv,abs_of_nonneg (sq_nonneg (1+x))]
  rw [Real.rpow_sub hd,Real.rpow_one]
  field_simp

theorem rational_integral (a : ℝ) (ha : a∈Ioo 0 1) :
    (∫ x in Ioi 0,x^(a-1)/(1+x))=Real.pi/Real.sin (Real.pi*a) := by
  have h := integral_image_eq_integral_abs_deriv_smul measurableSet_Ioi
    (fun x hx => (change_derivative x hx).hasDerivWithinAt) change_injective (betaKernel a)
  rw [change_image] at h
  rw [← beta_value a ha,h]
  apply setIntegral_congr_fun measurableSet_Ioi
  intro x hx
  exact (change_integrand a x hx).symm

theorem normalizer_exact (a : ℝ) (ha : a∈Ioo 0 1) :
    (∫ t in Ioi 0,Real.rpowIntegrand₀₁ a t 1)=Real.pi/Real.sin (Real.pi*a) := by
  rw [← rational_integral a ha]
  apply setIntegral_congr_fun measurableSet_Ioi
  intro t ht
  dsimp only
  rw [Real.rpowIntegrand₀₁_eq_pow_div ha ht.le zero_le_one,mul_one,add_comm]

theorem sine_factor_positive (a : ℝ) (ha : a∈Ioo 0 1) :
    0 < Real.sin (Real.pi*a)/Real.pi := by
  apply div_pos _ Real.pi_pos
  apply Real.sin_pos_of_pos_of_lt_pi
  · exact mul_pos Real.pi_pos ha.1
  · nlinarith [Real.pi_pos,ha.2]

theorem scalar_fractional_integral (a x : ℝ) (ha : a∈Ioo 0 1) (hx : 0 ≤ x) :
    x^a=(Real.sin (Real.pi*a)/Real.pi)*(∫ t in Ioi 0,Real.rpowIntegrand₀₁ a t x) := by
  rw [Real.rpow_eq_const_mul_integral ha hx,normalizer_exact a ha,inv_div]

theorem beta_real_integral (a b : ℝ) (ha : 0 < a) (hb : 0 < b) :
    (∫ x in Ioo 0 1,x^(a-1)*(1-x)^(b-1))=Real.Gamma a*Real.Gamma b/Real.Gamma (a+b) := by
  have h := Complex.betaIntegral_eq_Gamma_mul_div (a:ℂ) (b:ℂ) (by simpa) (by simpa)
  have he : Complex.betaIntegral (a:ℂ) (b:ℂ)=
      ((∫ x in Ioo 0 1,x^(a-1)*(1-x)^(b-1)):ℝ) := by
    rw [Complex.betaIntegral,intervalIntegral.integral_of_le (by norm_num : (0:ℝ) ≤ 1),integral_Ioc_eq_integral_Ioo]
    trans ∫ x in Ioo (0:ℝ) 1,((x^(a-1)*(1-x)^(b-1):ℝ):ℂ)
    · apply setIntegral_congr_fun measurableSet_Ioo
      intro x hx
      dsimp only
      rw [Complex.ofReal_mul,Complex.ofReal_cpow hx.1.le,Complex.ofReal_cpow (by linarith [hx.2] : 0 ≤ 1-x)]
      push_cast
      rfl
    · exact integral_complex_ofReal
  rw [he,← Complex.ofReal_add,Complex.Gamma_ofReal,Complex.Gamma_ofReal,Complex.Gamma_ofReal] at h
  exact_mod_cast h

theorem weighted_beta_value (p : ℝ) (hp : p∈Ioo 0 1) :
    (∫ x in Ioo 0 1,x^p*(1-x)^(-p))=p*Real.pi/Real.sin (Real.pi*p) := by
  have h := beta_real_integral (p+1) (1-p) (by linarith [hp.1]) (sub_pos.mpr hp.2)
  rw [add_sub_cancel_right,show 1-p-1= -p by ring,show p+1+(1-p)=2 by ring,
    Real.Gamma_add_one hp.1.ne',Real.Gamma_two,div_one,mul_assoc,Real.Gamma_mul_Gamma_one_sub] at h
  simpa only [mul_div_assoc] using h

theorem gap_change_integrand (p x : ℝ) (hx : 0 < x) :
    |(1+x)^(-2:ℤ)| • ((changeVariable x)^p*(1-changeVariable x)^(-p))=x^p/(1+x)^2 := by
  have hd : 0 < 1+x := by linarith
  have hs : 1-x/(1+x)=1/(1+x) := by field_simp; ring
  dsimp [changeVariable]
  rw [hs,Real.div_rpow hx.le hd.le,Real.rpow_neg (by positivity : 0 ≤ 1/(1+x)),Real.div_rpow zero_le_one hd.le]
  simp only [Real.one_rpow,one_div,inv_inv,zpow_neg,zpow_ofNat,abs_inv,abs_of_nonneg (sq_nonneg (1+x))]
  field_simp

theorem unit_gap_integral (p : ℝ) (hp : p∈Ioo 0 1) :
    (∫ x in Ioi 0,x^p/(1+x)^2)=p*Real.pi/Real.sin (Real.pi*p) := by
  have h := integral_image_eq_integral_abs_deriv_smul measurableSet_Ioi
    (fun x hx => (change_derivative x hx).hasDerivWithinAt) change_injective
    (fun x : ℝ => x^p*(1-x)^(-p))
  rw [change_image] at h
  rw [← weighted_beta_value p hp,h]
  apply setIntegral_congr_fun measurableSet_Ioi
  intro x hx
  exact (gap_change_integrand p x hx).symm

theorem gap_integral (p m : ℝ) (hp : p∈Ioo 0 1) (hm : 0 < m) :
    (∫ t in Ioi 0,t^p/(t+m)^2)=m^(p-1)*(p*Real.pi/Real.sin (Real.pi*p)) := by
  have h := integral_comp_mul_left_Ioi' (fun t : ℝ => t^p/(t+m)^2) 0 hm
  simp only [mul_zero,smul_eq_mul] at h
  rw [← h]
  have he : EqOn (fun x : ℝ => (m*x)^p/(m*x+m)^2)
      (fun x => m^(p-2)*(x^p/(1+x)^2)) (Ioi 0) := by
    intro x hx
    dsimp only
    rw [Real.mul_rpow hm.le (le_of_lt hx),Real.rpow_sub hm,Real.rpow_two]
    have hd : 1+x ≠ 0 := by linarith [show 0 < x from hx]
    rw [show m*x+m=m*(1+x) by ring,mul_pow]
    field_simp [hm.ne',hd]
  rw [setIntegral_congr_fun measurableSet_Ioi he,integral_const_mul,unit_gap_integral p hp]
  have he : m*m^(p-2)=m^(p-1) := by
    nth_rw 1 [← Real.rpow_one m]
    rw [← Real.rpow_add hm]
    congr 1
    ring
  rw [← mul_assoc,he]

theorem normalized_gap_integral (p m : ℝ) (hp : p∈Ioo 0 1) (hm : 0 < m) :
    (Real.sin (Real.pi*p)/Real.pi)*(∫ t in Ioi 0,t^p/(t+m)^2)=p*m^(p-1) := by
  rw [gap_integral p m hp hm]
  have hs : Real.sin (Real.pi*p) ≠ 0 := by
    intro hs
    have h := sine_factor_positive p hp
    rw [hs,zero_div] at h
    exact (lt_irrefl 0) h
  field_simp

end KomorebiPaperVI.BetaNormalization
