import Mathlib.Probability.Distributions.Gaussian.Real
import Mathlib.Probability.Kernel.Posterior

open MeasureTheory ProbabilityTheory
open scoped ENNReal NNReal

namespace Komorebi.GeneralScalarGaussianBayes

noncomputable def innovationVar (h : ℝ) (p r : ℝ≥0) : ℝ≥0 :=
  .mk (h^2) (sq_nonneg h) * p + r

noncomputable def kalmanGain (h : ℝ) (p r : ℝ≥0) : ℝ :=
  (p : ℝ) * h / (h^2 * (p : ℝ) + (r : ℝ))

noncomputable def posteriorMean (h m y : ℝ) (p r : ℝ≥0) : ℝ :=
  m + kalmanGain h p r * (y - h*m)

noncomputable def posteriorVar (h : ℝ) (p r : ℝ≥0) : ℝ≥0 :=
  p * r / innovationVar h p r

@[simp] theorem coe_innovationVar (h : ℝ) (p r : ℝ≥0) :
    (innovationVar h p r : ℝ) = h^2 * (p : ℝ) + (r : ℝ) := by
  simp [innovationVar]

theorem innovationVar_ne_zero (h : ℝ) (p r : ℝ≥0) (hr : r ≠ 0) :
    innovationVar h p r ≠ 0 := by
  rw [← NNReal.coe_ne_zero]
  simp only [coe_innovationVar]
  have hrR : 0 < (r : ℝ) := NNReal.coe_pos.mpr (pos_iff_ne_zero.mpr hr)
  positivity

theorem posteriorVar_ne_zero (h : ℝ) (p r : ℝ≥0) (hp : p ≠ 0) (hr : r ≠ 0) :
    posteriorVar h p r ≠ 0 := by
  simp [posteriorVar, hp, hr, innovationVar_ne_zero h p r hr]

theorem completing_square_real
    (h m y x p r : ℝ) (hp : p ≠ 0) (hr : r ≠ 0)
    (hS : h^2 * p + r ≠ 0) :
    (x - m)^2 / p + (y - h*x)^2 / r =
      (y - h*m)^2 / (h^2*p + r) +
        (x - (m + (p*h/(h^2*p+r))*(y-h*m)))^2 /
          (p*r/(h^2*p+r)) := by
  have hS1 : p*h^2 + r ≠ 0 := by simpa [mul_comm] using hS
  have hS2 : r + p*h^2 ≠ 0 := by simpa [add_comm, mul_comm] using hS
  field_simp [hp, hr, hS, hS1, hS2]
  ring

theorem gaussian_exponent_identity_real
    (h m y x p r : ℝ) (hp : p ≠ 0) (hr : r ≠ 0)
    (hS : h^2 * p + r ≠ 0) :
    (-(x - m)^2 / (2*p)) + (-(y - h*x)^2 / (2*r)) =
      (-(y - h*m)^2 / (2*(h^2*p+r))) +
        (-(x - (m + (p*h/(h^2*p+r))*(y-h*m)))^2 /
          (2*(p*r/(h^2*p+r)))) := by
  have hS1 : p*h^2 + r ≠ 0 := by simpa [mul_comm] using hS
  have hS2 : r + p*h^2 ≠ 0 := by simpa [add_comm, mul_comm] using hS
  field_simp [hp, hr, hS, hS1, hS2]
  ring

theorem gaussian_norm_product_real
    (h p r : ℝ) (hp : 0 < p) (hr : 0 < r) :
    (Real.sqrt (2 * Real.pi * p))⁻¹ * (Real.sqrt (2 * Real.pi * r))⁻¹ =
      (Real.sqrt (2 * Real.pi * (h^2*p+r)))⁻¹ *
        (Real.sqrt (2 * Real.pi * (p*r/(h^2*p+r))))⁻¹ := by
  have hS : 0 < h^2*p+r := by positivity
  have hL : Real.sqrt (2 * Real.pi * p) * Real.sqrt (2 * Real.pi * r) =
      Real.sqrt ((2 * Real.pi * p) * (2 * Real.pi * r)) := by
    rw [← Real.sqrt_mul (by positivity : 0 ≤ 2 * Real.pi * p)]
  have hR : Real.sqrt (2 * Real.pi * (h^2*p+r)) *
      Real.sqrt (2 * Real.pi * (p*r/(h^2*p+r))) =
      Real.sqrt ((2 * Real.pi * (h^2*p+r)) *
        (2 * Real.pi * (p*r/(h^2*p+r)))) := by
    rw [← Real.sqrt_mul (by positivity : 0 ≤ 2 * Real.pi * (h^2*p+r))]
  have hrad : (2 * Real.pi * p) * (2 * Real.pi * r) =
      (2 * Real.pi * (h^2*p+r)) * (2 * Real.pi * (p*r/(h^2*p+r))) := by
    field_simp [ne_of_gt hS]
  have hprod : Real.sqrt (2 * Real.pi * p) * Real.sqrt (2 * Real.pi * r) =
      Real.sqrt (2 * Real.pi * (h^2*p+r)) *
        Real.sqrt (2 * Real.pi * (p*r/(h^2*p+r))) := by
    rw [hL, hR, hrad]
  rw [← mul_inv, ← mul_inv]
  exact congrArg Inv.inv hprod

/-- Pointwise real-density factorization for `Y = h X + ε`. -/
theorem gaussian_prior_likelihood_factorization_real
    (h m y x : ℝ) (p r : ℝ≥0) (hp : p ≠ 0) (hr : r ≠ 0) :
    gaussianPDFReal m p x * gaussianPDFReal (h*x) r y =
      gaussianPDFReal (h*m) (innovationVar h p r) y *
        gaussianPDFReal (posteriorMean h m y p r) (posteriorVar h p r) x := by
  have hpR : 0 < (p : ℝ) := NNReal.coe_pos.mpr (pos_iff_ne_zero.mpr hp)
  have hrR : 0 < (r : ℝ) := NNReal.coe_pos.mpr (pos_iff_ne_zero.mpr hr)
  have hSR : 0 < h^2 * (p : ℝ) + (r : ℝ) := by positivity
  have hnorm := gaussian_norm_product_real h (p : ℝ) (r : ℝ) hpR hrR
  have hexp := gaussian_exponent_identity_real h m y x (p : ℝ) (r : ℝ)
    (ne_of_gt hpR) (ne_of_gt hrR) (ne_of_gt hSR)
  simp only [gaussianPDFReal, posteriorMean, posteriorVar, kalmanGain,
    innovationVar]
  let ap : ℝ := (Real.sqrt (2 * Real.pi * (p : ℝ)))⁻¹
  let ar : ℝ := (Real.sqrt (2 * Real.pi * (r : ℝ)))⁻¹
  let aS : ℝ := (Real.sqrt (2 * Real.pi * (h^2*(p : ℝ)+(r : ℝ))))⁻¹
  let av : ℝ := (Real.sqrt (2 * Real.pi *
    ((p : ℝ)*(r : ℝ)/(h^2*(p : ℝ)+(r : ℝ)))))⁻¹
  let ep : ℝ := -(x-m)^2/(2*(p : ℝ))
  let er : ℝ := -(y-h*x)^2/(2*(r : ℝ))
  let eS : ℝ := -(y-h*m)^2/(2*(h^2*(p : ℝ)+(r : ℝ)))
  let ev : ℝ := -(x-(m+((p : ℝ)*h/(h^2*(p : ℝ)+(r : ℝ)))*(y-h*m)))^2 /
    (2*((p : ℝ)*(r : ℝ)/(h^2*(p : ℝ)+(r : ℝ))))
  change ap * Real.exp ep * (ar * Real.exp er) = aS * Real.exp eS * (av * Real.exp ev)
  calc
    ap * Real.exp ep * (ar * Real.exp er)
        = (ap * ar) * (Real.exp ep * Real.exp er) := by ring
    _ = (aS * av) * Real.exp (ep + er) := by
      rw [Real.exp_add]
      rw [show ap * ar = aS * av by simpa [ap, ar, aS, av] using hnorm]
    _ = (aS * av) * Real.exp (eS + ev) := by
      rw [show ep + er = eS + ev by simpa [ep, er, eS, ev] using hexp]
    _ = aS * Real.exp eS * (av * Real.exp ev) := by
      rw [Real.exp_add]
      ring



/-- Observation kernel for `Y = h X + ε`, `ε ~ N(0,r)`. -/
noncomputable def linearObservationKernel (h : ℝ) (r : ℝ≥0) : Kernel ℝ ℝ :=
  ⟨fun x => gaussianReal (h*x) r, by
    have hpair : Measurable (fun x : ℝ => (h*x, r)) := by fun_prop
    exact measurable_gaussianReal.comp hpair⟩

/-- Explicit Kalman posterior kernel for the scalar linear observation model. -/
noncomputable def kalmanPosteriorKernel (h m : ℝ) (p r : ℝ≥0) : Kernel ℝ ℝ :=
  ⟨fun y => gaussianReal (posteriorMean h m y p r) (posteriorVar h p r), by
    have hmean : Measurable (fun y : ℝ => posteriorMean h m y p r) := by
      simp only [posteriorMean, kalmanGain]
      fun_prop
    have hpair : Measurable (fun y : ℝ =>
        (posteriorMean h m y p r, posteriorVar h p r)) :=
      hmean.prodMk measurable_const
    exact measurable_gaussianReal.comp hpair⟩

@[simp] theorem linearObservationKernel_apply (h : ℝ) (r : ℝ≥0) (x : ℝ) :
    linearObservationKernel h r x = gaussianReal (h*x) r := rfl

@[simp] theorem kalmanPosteriorKernel_apply
    (h m : ℝ) (p r : ℝ≥0) (y : ℝ) :
    kalmanPosteriorKernel h m p r y =
      gaussianReal (posteriorMean h m y p r) (posteriorVar h p r) := rfl

instance linearObservationKernel_isMarkov (h : ℝ) (r : ℝ≥0) :
    IsMarkovKernel (linearObservationKernel h r) := by
  constructor
  intro x
  change IsProbabilityMeasure (gaussianReal (h*x) r)
  infer_instance

instance kalmanPosteriorKernel_isMarkov (h m : ℝ) (p r : ℝ≥0) :
    IsMarkovKernel (kalmanPosteriorKernel h m p r) := by
  constructor
  intro y
  change IsProbabilityMeasure
    (gaussianReal (posteriorMean h m y p r) (posteriorVar h p r))
  infer_instance

/-- Exact evidence marginal: `Y ~ N(hm, h²p+r)`. -/
theorem linearObservationKernel_comp_prior (h m : ℝ) (p r : ℝ≥0) :
    linearObservationKernel h r ∘ₘ gaussianReal m p =
      gaussianReal (h*m) (innovationVar h p r) := by
  rw [← show gaussianReal (h*m) (.mk (h^2) (sq_nonneg h) * p) ∗ gaussianReal 0 r =
      gaussianReal (h*m) (innovationVar h p r) by
    simpa [innovationVar] using (gaussianReal_conv_gaussianReal
      (m₁ := h*m) (m₂ := 0) (v₁ := .mk (h^2) (sq_nonneg h) * p) (v₂ := r))]
  rw [← show (gaussianReal m p).map (h * ·) =
      gaussianReal (h*m) (.mk (h^2) (sq_nonneg h) * p) by
    simpa using (gaussianReal_map_const_mul (μ := m) (v := p) h)]
  refine Measure.ext_of_lintegral _ fun f hf => ?_
  rw [Measure.lintegral_bind (Kernel.measurable _).aemeasurable hf.aemeasurable]
  rw [Measure.lintegral_conv hf]
  let g : ℝ → ℝ≥0∞ := fun u => ∫⁻ z, f (u + z) ∂gaussianReal 0 r
  have hg : Measurable g := by
    simp only [g]
    fun_prop
  rw [lintegral_map hg (by fun_prop : Measurable (h * ·))]
  refine lintegral_congr fun x => ?_
  change (∫⁻ y, f y ∂gaussianReal (h*x) r) = ∫⁻ z, f (h*x + z) ∂gaussianReal 0 r
  have hmap : (gaussianReal 0 r).map (h*x + ·) = gaussianReal (h*x) r := by
    simpa using (gaussianReal_map_const_add (μ := 0) (v := r) (h*x))
  rw [← hmap, lintegral_map hf (by fun_prop)]

/-- ENNReal density factorization for the scalar linear observation model. -/
theorem gaussian_prior_likelihood_factorization_ennreal
    (h m y x : ℝ) (p r : ℝ≥0) (hp : p ≠ 0) (hr : r ≠ 0) :
    gaussianPDF m p x * gaussianPDF (h*x) r y =
      gaussianPDF (h*m) (innovationVar h p r) y *
        gaussianPDF (posteriorMean h m y p r) (posteriorVar h p r) x := by
  simp only [gaussianPDF]
  rw [← ENNReal.ofReal_mul (gaussianPDFReal_nonneg m p x)]
  rw [gaussian_prior_likelihood_factorization_real h m y x p r hp hr]
  rw [ENNReal.ofReal_mul (gaussianPDFReal_nonneg (h*m) (innovationVar h p r) y)]

lemma measurable_likelihood_pdf (h : ℝ) (r : ℝ≥0) :
    Measurable (Function.uncurry (fun x y : ℝ => gaussianPDF (h*x) r y)) := by
  fun_prop

lemma measurable_posterior_pdf (h m : ℝ) (p r : ℝ≥0) :
    Measurable (Function.uncurry (fun y x : ℝ =>
      gaussianPDF (posteriorMean h m y p r) (posteriorVar h p r) x)) := by
  simp only [Function.uncurry_def, posteriorMean, kalmanGain]
  fun_prop

/-- The observation kernel is its Gaussian density kernel over Lebesgue measure. -/
theorem linearObservationKernel_eq_withDensity
    (h : ℝ) (r : ℝ≥0) (hr : r ≠ 0) :
    linearObservationKernel h r =
      (Kernel.const ℝ volume).withDensity (fun x y => gaussianPDF (h*x) r y) := by
  apply Kernel.ext
  intro x
  rw [Kernel.withDensity_apply _ (measurable_likelihood_pdf h r)]
  simp only [Kernel.const_apply, linearObservationKernel_apply]
  exact gaussianReal_of_var_ne_zero (h*x) hr

/-- The explicit posterior family is its Gaussian density kernel over Lebesgue measure. -/
theorem kalmanPosteriorKernel_eq_withDensity
    (h m : ℝ) (p r : ℝ≥0) (hp : p ≠ 0) (hr : r ≠ 0) :
    kalmanPosteriorKernel h m p r =
      (Kernel.const ℝ volume).withDensity (fun y x =>
        gaussianPDF (posteriorMean h m y p r) (posteriorVar h p r) x) := by
  have hv : posteriorVar h p r ≠ 0 := posteriorVar_ne_zero h p r hp hr
  apply Kernel.ext
  intro y
  rw [Kernel.withDensity_apply _ (measurable_posterior_pdf h m p r)]
  simp only [Kernel.const_apply, kalmanPosteriorKernel_apply]
  exact gaussianReal_of_var_ne_zero (posteriorMean h m y p r) hv

instance likelihoodWithDensity_isSFinite (h : ℝ) (r : ℝ≥0) : IsSFiniteKernel
    ((Kernel.const ℝ volume).withDensity (fun x y => gaussianPDF (h*x) r y)) :=
  Kernel.IsSFiniteKernel.withDensity (Kernel.const ℝ volume)
    (fun _ _ => ne_of_lt gaussianPDF_lt_top)

instance posteriorWithDensity_isSFinite (h m : ℝ) (p r : ℝ≥0) : IsSFiniteKernel
    ((Kernel.const ℝ volume).withDensity (fun y x =>
      gaussianPDF (posteriorMean h m y p r) (posteriorVar h p r) x)) :=
  Kernel.IsSFiniteKernel.withDensity (Kernel.const ℝ volume)
    (fun _ _ => ne_of_lt gaussianPDF_lt_top)

/-- State-data joint law as a density on product Lebesgue measure. -/
theorem prior_likelihood_joint_density
    (h m : ℝ) (p r : ℝ≥0) (hp : p ≠ 0) (hr : r ≠ 0) :
    gaussianReal m p ⊗ₘ linearObservationKernel h r =
      (volume.prod volume).withDensity
        (fun z : ℝ × ℝ => gaussianPDF m p z.1 * gaussianPDF (h*z.1) r z.2) := by
  rw [gaussianReal_of_var_ne_zero m hp, linearObservationKernel_eq_withDensity h r hr]
  rw [Measure.withDensity_compProd_withDensity
    (μ := volume) (κ := Kernel.const ℝ volume)
    (measurable_gaussianPDF m p) (measurable_likelihood_pdf h r)]
  rw [Measure.compProd_const]

/-- Data-state evidence/posterior joint law as a density on product Lebesgue measure. -/
theorem evidence_posterior_joint_density
    (h m : ℝ) (p r : ℝ≥0) (hp : p ≠ 0) (hr : r ≠ 0) :
    gaussianReal (h*m) (innovationVar h p r) ⊗ₘ kalmanPosteriorKernel h m p r =
      (volume.prod volume).withDensity
        (fun z : ℝ × ℝ => gaussianPDF (h*m) (innovationVar h p r) z.1 *
          gaussianPDF (posteriorMean h m z.1 p r) (posteriorVar h p r) z.2) := by
  have hS : innovationVar h p r ≠ 0 := innovationVar_ne_zero h p r hr
  rw [gaussianReal_of_var_ne_zero (h*m) hS,
    kalmanPosteriorKernel_eq_withDensity h m p r hp hr]
  rw [Measure.withDensity_compProd_withDensity
    (μ := volume) (κ := Kernel.const ℝ volume)
    (measurable_gaussianPDF (h*m) (innovationVar h p r))
    (measurable_posterior_pdf h m p r)]
  rw [Measure.compProd_const]

/-- Swapping coordinates transports a density over symmetric product Lebesgue measure
by precomposition with `Prod.swap`. -/
theorem map_swap_prod_volume_withDensity
    (f : ℝ × ℝ → ℝ≥0∞) (hf : Measurable f) :
    ((volume.prod volume).withDensity f).map Prod.swap =
      (volume.prod volume).withDensity (fun z => f z.swap) := by
  refine Measure.ext_of_lintegral _ fun g hg => ?_
  rw [lintegral_map hg measurable_swap]
  change (∫⁻ a, (g ∘ Prod.swap) a ∂(volume.prod volume).withDensity f) = _
  rw [lintegral_withDensity_eq_lintegral_mul _ hf (hg.comp measurable_swap)]
  change _ = (∫⁻ a, g a ∂(volume.prod volume).withDensity (f ∘ Prod.swap))
  rw [lintegral_withDensity_eq_lintegral_mul _ (hf.comp measurable_swap) hg]
  let q : ℝ × ℝ → ℝ≥0∞ := fun z => f z.swap * g z
  have hq : Measurable q := (hf.comp measurable_swap).mul hg
  have hswap : (∫⁻ z, q z.swap ∂volume.prod volume) = ∫⁻ z, q z ∂volume.prod volume := by
    rw [← lintegral_map hq measurable_swap, Measure.prod_swap]
  simpa [q, mul_comm] using hswap

/-- Exact disintegration identity for the explicit scalar linear-Gaussian posterior. -/
theorem evidence_posterior_joint_eq_swapped_prior_likelihood
    (h m : ℝ) (p r : ℝ≥0) (hp : p ≠ 0) (hr : r ≠ 0) :
    gaussianReal (h*m) (innovationVar h p r) ⊗ₘ kalmanPosteriorKernel h m p r =
      (gaussianReal m p ⊗ₘ linearObservationKernel h r).map Prod.swap := by
  rw [evidence_posterior_joint_density h m p r hp hr,
      prior_likelihood_joint_density h m p r hp hr]
  rw [map_swap_prod_volume_withDensity]
  · apply MeasureTheory.withDensity_congr_ae
    filter_upwards with z
    exact (gaussian_prior_likelihood_factorization_ennreal
      h m z.1 z.2 p r hp hr).symm
  · exact (measurable_gaussianPDF m p).comp measurable_fst |>.mul
      (measurable_likelihood_pdf h r)

open scoped ProbabilityTheory

/-- **General scalar Gaussian Bayes = Kalman conditioning.**  For arbitrary real
observation coefficient `h` and positive variances, the explicit Kalman Gaussian
kernel agrees evidence-a.e. with Mathlib's canonical posterior kernel. -/
theorem kalmanPosterior_ae_eq_canonicalPosterior
    (h m : ℝ) (p r : ℝ≥0) (hp : p ≠ 0) (hr : r ≠ 0) :
    (fun y => kalmanPosteriorKernel h m p r y) =ᵐ[gaussianReal (h*m) (innovationVar h p r)]
      (fun y => ProbabilityTheory.posterior (linearObservationKernel h r)
        (gaussianReal m p) y) := by
  have hjoint :
      (linearObservationKernel h r ∘ₘ gaussianReal m p) ⊗ₘ
          kalmanPosteriorKernel h m p r =
        (gaussianReal m p ⊗ₘ linearObservationKernel h r).map Prod.swap := by
    rw [linearObservationKernel_comp_prior]
    exact evidence_posterior_joint_eq_swapped_prior_likelihood h m p r hp hr
  have huniq := ProbabilityTheory.ae_eq_posterior_of_compProd_eq
    (κ := linearObservationKernel h r) (μ := gaussianReal m p)
    (η := kalmanPosteriorKernel h m p r) hjoint
  rw [linearObservationKernel_comp_prior] at huniq
  exact huniq

/-- Pointwise normalized Bayes density equals the explicit Kalman Gaussian density. -/
theorem normalized_bayes_density_eq_kalman
    (h m y x : ℝ) (p r : ℝ≥0) (hp : p ≠ 0) (hr : r ≠ 0) :
    (gaussianPDF m p x * gaussianPDF (h*x) r y) /
        gaussianPDF (h*m) (innovationVar h p r) y =
      gaussianPDF (posteriorMean h m y p r) (posteriorVar h p r) x := by
  rw [gaussian_prior_likelihood_factorization_ennreal h m y x p r hp hr]
  have hS : innovationVar h p r ≠ 0 := innovationVar_ne_zero h p r hr
  have hne : gaussianPDF (h*m) (innovationVar h p r) y ≠ 0 :=
    (gaussianPDF_pos (h*m) hS y).ne'
  have htop : gaussianPDF (h*m) (innovationVar h p r) y ≠ ⊤ :=
    ne_of_lt gaussianPDF_lt_top
  simpa [div_eq_mul_inv, mul_assoc, mul_left_comm, mul_comm] using
    (ENNReal.mul_div_cancel
      (a := gaussianPDF (h*m) (innovationVar h p r) y)
      (b := gaussianPDF (posteriorMean h m y p r) (posteriorVar h p r) x)
      hne htop)

/-- For every observation `y`, normalized Bayes measure equals the explicit
Kalman Gaussian posterior measure. -/
theorem normalized_bayes_measure_eq_kalman
    (h m y : ℝ) (p r : ℝ≥0) (hp : p ≠ 0) (hr : r ≠ 0) :
    volume.withDensity (fun x : ℝ =>
      (gaussianPDF m p x * gaussianPDF (h*x) r y) /
        gaussianPDF (h*m) (innovationVar h p r) y) =
      kalmanPosteriorKernel h m p r y := by
  rw [kalmanPosteriorKernel_apply]
  have hv : posteriorVar h p r ≠ 0 := posteriorVar_ne_zero h p r hp hr
  rw [gaussianReal_of_var_ne_zero _ hv]
  apply MeasureTheory.withDensity_congr_ae
  filter_upwards with x
  exact normalized_bayes_density_eq_kalman h m y x p r hp hr

end Komorebi.GeneralScalarGaussianBayes
