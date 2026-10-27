import Mathlib.Probability.Distributions.Gaussian.Real
import Mathlib.Probability.Kernel.Posterior

open MeasureTheory ProbabilityTheory
open scoped ENNReal NNReal

namespace Komorebi.GaussianBayesBridge

theorem completing_square_real
    (m y x p r : ℝ) (hp : p ≠ 0) (hr : r ≠ 0) (hpr : p + r ≠ 0) :
    (x - m)^2 / p + (y - x)^2 / r =
      (y - m)^2 / (p + r) +
        (x - (r*m + p*y)/(p+r))^2 / (p*r/(p+r)) := by
  field_simp
  ring

end Komorebi.GaussianBayesBridge

namespace Komorebi.GaussianBayesBridge

theorem gaussian_norm_product_real
    (p r : ℝ) (hp : 0 < p) (hr : 0 < r) :
    (Real.sqrt (2 * Real.pi * p))⁻¹ * (Real.sqrt (2 * Real.pi * r))⁻¹ =
      (Real.sqrt (2 * Real.pi * (p+r)))⁻¹ *
        (Real.sqrt (2 * Real.pi * (p*r/(p+r))))⁻¹ := by
  have h2pi : 0 ≤ 2 * Real.pi := by positivity
  have hp0 : 0 ≤ p := hp.le
  have hr0 : 0 ≤ r := hr.le
  have hsum : 0 < p + r := add_pos hp hr
  have hv : 0 ≤ p * r / (p+r) := by positivity
  have hL : Real.sqrt (2 * Real.pi * p) * Real.sqrt (2 * Real.pi * r) =
      Real.sqrt ((2 * Real.pi * p) * (2 * Real.pi * r)) := by
    rw [← Real.sqrt_mul (by positivity : 0 ≤ 2 * Real.pi * p)]
  have hR : Real.sqrt (2 * Real.pi * (p+r)) * Real.sqrt (2 * Real.pi * (p*r/(p+r))) =
      Real.sqrt ((2 * Real.pi * (p+r)) * (2 * Real.pi * (p*r/(p+r)))) := by
    rw [← Real.sqrt_mul (by positivity : 0 ≤ 2 * Real.pi * (p+r))]
  have hrad : (2 * Real.pi * p) * (2 * Real.pi * r) =
      (2 * Real.pi * (p+r)) * (2 * Real.pi * (p*r/(p+r))) := by
    field_simp [ne_of_gt hsum]
  have hprod : Real.sqrt (2 * Real.pi * p) * Real.sqrt (2 * Real.pi * r) =
      Real.sqrt (2 * Real.pi * (p+r)) * Real.sqrt (2 * Real.pi * (p*r/(p+r))) := by
    rw [hL, hR, hrad]
  rw [← mul_inv, ← mul_inv]
  exact congrArg Inv.inv hprod

end Komorebi.GaussianBayesBridge

namespace Komorebi.GaussianBayesBridge

noncomputable def scalarPosteriorVar (p r : ℝ≥0) : ℝ≥0 := p * r / (p + r)

noncomputable def scalarPosteriorMean (m y : ℝ) (p r : ℝ≥0) : ℝ :=
  ((r : ℝ) * m + (p : ℝ) * y) / ((p : ℝ) + (r : ℝ))

theorem gaussian_exponent_identity_real
    (m y x p r : ℝ) (hp : p ≠ 0) (hr : r ≠ 0) (hpr : p + r ≠ 0) :
    (-(x - m)^2 / (2*p)) + (-(y - x)^2 / (2*r)) =
      (-(y - m)^2 / (2*(p+r))) +
        (-(x - (r*m+p*y)/(p+r))^2 / (2*(p*r/(p+r)))) := by
  field_simp
  ring

/-- Scalar linear-Gaussian Bayes/Kalman density factorization. -/
theorem gaussian_prior_likelihood_factorization
    (m y x : ℝ) (p r : ℝ≥0) (hp : p ≠ 0) (hr : r ≠ 0) :
    gaussianPDFReal m p x * gaussianPDFReal x r y =
      gaussianPDFReal m (p + r) y *
        gaussianPDFReal (scalarPosteriorMean m y p r) (scalarPosteriorVar p r) x := by
  have hpR : 0 < (p : ℝ) := NNReal.coe_pos.mpr (pos_iff_ne_zero.mpr hp)
  have hrR : 0 < (r : ℝ) := NNReal.coe_pos.mpr (pos_iff_ne_zero.mpr hr)
  have hsumR : 0 < (p : ℝ) + (r : ℝ) := add_pos hpR hrR
  have hnorm := gaussian_norm_product_real (p : ℝ) (r : ℝ) hpR hrR
  have hexp := gaussian_exponent_identity_real m y x (p : ℝ) (r : ℝ)
    (ne_of_gt hpR) (ne_of_gt hrR) (ne_of_gt hsumR)
  simp only [gaussianPDFReal, scalarPosteriorMean, scalarPosteriorVar,
    NNReal.coe_add, NNReal.coe_mul, NNReal.coe_div]
  let ap : ℝ := (Real.sqrt (2 * Real.pi * (p : ℝ)))⁻¹
  let ar : ℝ := (Real.sqrt (2 * Real.pi * (r : ℝ)))⁻¹
  let asum : ℝ := (Real.sqrt (2 * Real.pi * ((p : ℝ) + (r : ℝ))))⁻¹
  let av : ℝ := (Real.sqrt (2 * Real.pi * ((p : ℝ) * (r : ℝ) / ((p : ℝ) + (r : ℝ)))))⁻¹
  let ep : ℝ := -(x - m)^2 / (2 * (p : ℝ))
  let er : ℝ := -(y - x)^2 / (2 * (r : ℝ))
  let es : ℝ := -(y - m)^2 / (2 * ((p : ℝ) + (r : ℝ)))
  let ev : ℝ := -(x - ((r : ℝ)*m + (p : ℝ)*y)/((p : ℝ)+(r : ℝ)))^2 /
    (2 * ((p : ℝ)*(r : ℝ)/((p : ℝ)+(r : ℝ))))
  change ap * Real.exp ep * (ar * Real.exp er) = asum * Real.exp es * (av * Real.exp ev)
  calc
    ap * Real.exp ep * (ar * Real.exp er)
        = (ap * ar) * (Real.exp ep * Real.exp er) := by ring
    _ = (asum * av) * Real.exp (ep + er) := by
      rw [Real.exp_add]
      rw [show ap * ar = asum * av by simpa [ap, ar, asum, av] using hnorm]
    _ = (asum * av) * Real.exp (es + ev) := by
      rw [show ep + er = es + ev by simpa [ep, er, es, ev] using hexp]
    _ = asum * Real.exp es * (av * Real.exp ev) := by
      rw [Real.exp_add]
      ring

end Komorebi.GaussianBayesBridge

namespace Komorebi.GaussianBayesBridge

noncomputable def gaussianLocationKernel (v : ℝ≥0) : Kernel ℝ ℝ :=
  ⟨fun m => gaussianReal m v, by
    exact (measurable_gaussianReal.comp measurable_prodMk_right).comp measurable_id⟩

-- simpler direct constructor for the posterior Gaussian family
noncomputable def scalarKalmanPosteriorKernel (m : ℝ) (p r : ℝ≥0) : Kernel ℝ ℝ :=
  ⟨fun y => gaussianReal (scalarPosteriorMean m y p r) (scalarPosteriorVar p r), by
    have hmean : Measurable (fun y : ℝ => scalarPosteriorMean m y p r) := by
      simp only [scalarPosteriorMean]
      fun_prop
    have hpair : Measurable (fun y : ℝ =>
        (scalarPosteriorMean m y p r, scalarPosteriorVar p r)) :=
      hmean.prodMk measurable_const
    exact measurable_gaussianReal.comp hpair⟩

@[simp] theorem gaussianLocationKernel_apply (v : ℝ≥0) (x : ℝ) :
    gaussianLocationKernel v x = gaussianReal x v := rfl

@[simp] theorem scalarKalmanPosteriorKernel_apply (m : ℝ) (p r : ℝ≥0) (y : ℝ) :
    scalarKalmanPosteriorKernel m p r y =
      gaussianReal (scalarPosteriorMean m y p r) (scalarPosteriorVar p r) := rfl

instance gaussianLocationKernel_isMarkov (v : ℝ≥0) :
    IsMarkovKernel (gaussianLocationKernel v) := by
  constructor
  intro x
  change IsProbabilityMeasure (gaussianReal x v)
  infer_instance

instance scalarKalmanPosteriorKernel_isMarkov (m : ℝ) (p r : ℝ≥0) :
    IsMarkovKernel (scalarKalmanPosteriorKernel m p r) := by
  constructor
  intro y
  change IsProbabilityMeasure
    (gaussianReal (scalarPosteriorMean m y p r) (scalarPosteriorVar p r))
  infer_instance

end Komorebi.GaussianBayesBridge

namespace Komorebi.GaussianBayesBridge

/-- Marginal of `Y = X + ε` for Gaussian prior and Gaussian noise. -/
theorem gaussianLocationKernel_comp_prior (m : ℝ) (p r : ℝ≥0) :
    gaussianLocationKernel r ∘ₘ gaussianReal m p = gaussianReal m (p + r) := by
  rw [← show gaussianReal m p ∗ gaussianReal 0 r = gaussianReal m (p + r) by
    simpa using (gaussianReal_conv_gaussianReal (m₁ := m) (m₂ := 0) (v₁ := p) (v₂ := r))]
  refine Measure.ext_of_lintegral _ fun f hf => ?_
  rw [Measure.lintegral_bind (Kernel.measurable _).aemeasurable hf.aemeasurable]
  rw [Measure.lintegral_conv hf]
  refine lintegral_congr fun x => ?_
  change (∫⁻ y, f y ∂gaussianReal x r) = ∫⁻ z, f (x + z) ∂gaussianReal 0 r
  have hmap : (gaussianReal 0 r).map (x + ·) = gaussianReal x r := by
    simpa using (gaussianReal_map_const_add (μ := 0) (v := r) x)
  rw [← hmap, lintegral_map hf (by fun_prop)]

end Komorebi.GaussianBayesBridge

namespace Komorebi.GaussianBayesBridge

theorem gaussian_prior_likelihood_factorization_ennreal
    (m y x : ℝ) (p r : ℝ≥0) (hp : p ≠ 0) (hr : r ≠ 0) :
    gaussianPDF m p x * gaussianPDF x r y =
      gaussianPDF m (p + r) y *
        gaussianPDF (scalarPosteriorMean m y p r) (scalarPosteriorVar p r) x := by
  simp only [gaussianPDF]
  rw [← ENNReal.ofReal_mul (gaussianPDFReal_nonneg m p x)]
  rw [gaussian_prior_likelihood_factorization m y x p r hp hr]
  rw [ENNReal.ofReal_mul (gaussianPDFReal_nonneg m (p + r) y)]

end Komorebi.GaussianBayesBridge

namespace Komorebi.GaussianBayesBridge

lemma scalarPosteriorVar_ne_zero (p r : ℝ≥0) (hp : p ≠ 0) (hr : r ≠ 0) :
    scalarPosteriorVar p r ≠ 0 := by
  simp [scalarPosteriorVar, hp, hr]

lemma measurable_likelihood_pdf (r : ℝ≥0) :
    Measurable (Function.uncurry (fun x y : ℝ => gaussianPDF x r y)) := by
  fun_prop

lemma measurable_posterior_pdf (m : ℝ) (p r : ℝ≥0) :
    Measurable (Function.uncurry (fun y x : ℝ =>
      gaussianPDF (scalarPosteriorMean m y p r) (scalarPosteriorVar p r) x)) := by
  simp only [Function.uncurry_def, scalarPosteriorMean]
  fun_prop

/-- The Gaussian location kernel is the Gaussian density kernel over Lebesgue measure. -/
theorem gaussianLocationKernel_eq_withDensity (r : ℝ≥0) (hr : r ≠ 0) :
    gaussianLocationKernel r =
      (Kernel.const ℝ volume).withDensity (fun x y => gaussianPDF x r y) := by
  apply Kernel.ext
  intro x
  rw [Kernel.withDensity_apply _ (measurable_likelihood_pdf r)]
  simp only [Kernel.const_apply, gaussianLocationKernel_apply]
  exact gaussianReal_of_var_ne_zero x hr

/-- The scalar Kalman posterior family is a Gaussian density kernel over Lebesgue measure. -/
theorem scalarKalmanPosteriorKernel_eq_withDensity
    (m : ℝ) (p r : ℝ≥0) (hp : p ≠ 0) (hr : r ≠ 0) :
    scalarKalmanPosteriorKernel m p r =
      (Kernel.const ℝ volume).withDensity (fun y x =>
        gaussianPDF (scalarPosteriorMean m y p r) (scalarPosteriorVar p r) x) := by
  have hv : scalarPosteriorVar p r ≠ 0 := scalarPosteriorVar_ne_zero p r hp hr
  apply Kernel.ext
  intro y
  rw [Kernel.withDensity_apply _ (measurable_posterior_pdf m p r)]
  simp only [Kernel.const_apply, scalarKalmanPosteriorKernel_apply]
  exact gaussianReal_of_var_ne_zero (scalarPosteriorMean m y p r) hv


instance likelihoodWithDensity_isSFinite (r : ℝ≥0) : IsSFiniteKernel
    ((Kernel.const ℝ volume).withDensity (fun x y => gaussianPDF x r y)) :=
  Kernel.IsSFiniteKernel.withDensity (Kernel.const ℝ volume)
    (fun _ _ => ne_of_lt gaussianPDF_lt_top)

instance posteriorWithDensity_isSFinite (m : ℝ) (p r : ℝ≥0) : IsSFiniteKernel
    ((Kernel.const ℝ volume).withDensity (fun y x =>
      gaussianPDF (scalarPosteriorMean m y p r) (scalarPosteriorVar p r) x)) :=
  Kernel.IsSFiniteKernel.withDensity (Kernel.const ℝ volume)
    (fun _ _ => ne_of_lt gaussianPDF_lt_top)

/-- State-data joint law as a density on product Lebesgue measure. -/
theorem prior_likelihood_joint_density
    (m : ℝ) (p r : ℝ≥0) (hp : p ≠ 0) (hr : r ≠ 0) :
    gaussianReal m p ⊗ₘ gaussianLocationKernel r =
      (volume.prod volume).withDensity
        (fun z : ℝ × ℝ => gaussianPDF m p z.1 * gaussianPDF z.1 r z.2) := by
  rw [gaussianReal_of_var_ne_zero m hp, gaussianLocationKernel_eq_withDensity r hr]
  rw [Measure.withDensity_compProd_withDensity
    (μ := volume) (κ := Kernel.const ℝ volume)
    (measurable_gaussianPDF m p) (measurable_likelihood_pdf r)]
  rw [Measure.compProd_const]

/-- Data-state evidence/posterior joint law as a density on product Lebesgue measure. -/
theorem evidence_posterior_joint_density
    (m : ℝ) (p r : ℝ≥0) (hp : p ≠ 0) (hr : r ≠ 0) :
    gaussianReal m (p + r) ⊗ₘ scalarKalmanPosteriorKernel m p r =
      (volume.prod volume).withDensity
        (fun z : ℝ × ℝ => gaussianPDF m (p + r) z.1 *
          gaussianPDF (scalarPosteriorMean m z.1 p r) (scalarPosteriorVar p r) z.2) := by
  have hsum : p + r ≠ 0 := by simp [hp, hr]
  rw [gaussianReal_of_var_ne_zero m hsum,
    scalarKalmanPosteriorKernel_eq_withDensity m p r hp hr]
  rw [Measure.withDensity_compProd_withDensity
    (μ := volume) (κ := Kernel.const ℝ volume)
    (measurable_gaussianPDF m (p+r)) (measurable_posterior_pdf m p r)]
  rw [Measure.compProd_const]

end Komorebi.GaussianBayesBridge

namespace Komorebi.GaussianBayesBridge

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
  let h : ℝ × ℝ → ℝ≥0∞ := fun z => f z.swap * g z
  have hh : Measurable h := (hf.comp measurable_swap).mul hg
  have hswap : (∫⁻ z, h z.swap ∂volume.prod volume) = ∫⁻ z, h z ∂volume.prod volume := by
    rw [← lintegral_map hh measurable_swap, Measure.prod_swap]
  simpa [h, mul_comm] using hswap

end Komorebi.GaussianBayesBridge

namespace Komorebi.GaussianBayesBridge

/-- The evidence/Kalman-posterior joint law is exactly the coordinate-swapped
prior/likelihood joint law. This is the disintegration identity needed for
Bayesian posterior uniqueness. -/
theorem evidence_posterior_joint_eq_swapped_prior_likelihood
    (m : ℝ) (p r : ℝ≥0) (hp : p ≠ 0) (hr : r ≠ 0) :
    gaussianReal m (p + r) ⊗ₘ scalarKalmanPosteriorKernel m p r =
      (gaussianReal m p ⊗ₘ gaussianLocationKernel r).map Prod.swap := by
  rw [evidence_posterior_joint_density m p r hp hr,
      prior_likelihood_joint_density m p r hp hr]
  rw [map_swap_prod_volume_withDensity]
  · apply MeasureTheory.withDensity_congr_ae
    filter_upwards with z
    exact (gaussian_prior_likelihood_factorization_ennreal
      m z.1 z.2 p r hp hr).symm
  · exact (measurable_gaussianPDF m p).comp measurable_fst |>.mul
      (measurable_likelihood_pdf r)

end Komorebi.GaussianBayesBridge

namespace Komorebi.GaussianBayesBridge

open scoped ProbabilityTheory

/-- **Scalar Gaussian Bayes = Kalman conditioning.**  For positive prior and
observation variances, the explicit scalar Kalman Gaussian kernel agrees,
for evidence-almost every observation, with Mathlib's canonical Bayesian
posterior kernel obtained by disintegration. -/
theorem scalarKalmanPosterior_ae_eq_canonicalPosterior
    (m : ℝ) (p r : ℝ≥0) (hp : p ≠ 0) (hr : r ≠ 0) :
    (fun y => scalarKalmanPosteriorKernel m p r y) =ᵐ[gaussianReal m (p + r)]
      (fun y => ProbabilityTheory.posterior (gaussianLocationKernel r)
        (gaussianReal m p) y) := by
  have hjoint :
      (gaussianLocationKernel r ∘ₘ gaussianReal m p) ⊗ₘ
          scalarKalmanPosteriorKernel m p r =
        (gaussianReal m p ⊗ₘ gaussianLocationKernel r).map Prod.swap := by
    rw [gaussianLocationKernel_comp_prior]
    exact evidence_posterior_joint_eq_swapped_prior_likelihood m p r hp hr
  have huniq := ProbabilityTheory.ae_eq_posterior_of_compProd_eq
    (κ := gaussianLocationKernel r) (μ := gaussianReal m p)
    (η := scalarKalmanPosteriorKernel m p r) hjoint
  rw [gaussianLocationKernel_comp_prior] at huniq
  exact huniq

end Komorebi.GaussianBayesBridge

namespace Komorebi.GaussianBayesBridge

/-- Pointwise normalized Bayes density equals the scalar Kalman Gaussian density. -/
theorem normalized_bayes_density_eq_kalman
    (m y x : ℝ) (p r : ℝ≥0) (hp : p ≠ 0) (hr : r ≠ 0) :
    (gaussianPDF m p x * gaussianPDF x r y) / gaussianPDF m (p + r) y =
      gaussianPDF (scalarPosteriorMean m y p r) (scalarPosteriorVar p r) x := by
  rw [gaussian_prior_likelihood_factorization_ennreal m y x p r hp hr]
  have hsum : p + r ≠ 0 := by simp [hp, hr]
  have hne : gaussianPDF m (p + r) y ≠ 0 :=
    (gaussianPDF_pos m hsum y).ne'
  have htop : gaussianPDF m (p + r) y ≠ ⊤ := ne_of_lt gaussianPDF_lt_top
  simpa [div_eq_mul_inv, mul_assoc, mul_left_comm, mul_comm] using
    (ENNReal.mul_div_cancel (a := gaussianPDF m (p + r) y)
      (b := gaussianPDF (scalarPosteriorMean m y p r) (scalarPosteriorVar p r) x) hne htop)

end Komorebi.GaussianBayesBridge

namespace Komorebi.GaussianBayesBridge

/-- For every observation `y`, the explicitly normalized Bayes measure equals
exactly the scalar Kalman Gaussian posterior measure. -/
theorem normalized_bayes_measure_eq_kalman
    (m y : ℝ) (p r : ℝ≥0) (hp : p ≠ 0) (hr : r ≠ 0) :
    volume.withDensity (fun x : ℝ =>
      (gaussianPDF m p x * gaussianPDF x r y) / gaussianPDF m (p + r) y) =
      scalarKalmanPosteriorKernel m p r y := by
  rw [scalarKalmanPosteriorKernel_apply]
  have hv : scalarPosteriorVar p r ≠ 0 := scalarPosteriorVar_ne_zero p r hp hr
  rw [gaussianReal_of_var_ne_zero _ hv]
  apply MeasureTheory.withDensity_congr_ae
  filter_upwards with x
  exact normalized_bayes_density_eq_kalman m y x p r hp hr

end Komorebi.GaussianBayesBridge

#print axioms Komorebi.GaussianBayesBridge.gaussian_prior_likelihood_factorization_ennreal
#print axioms Komorebi.GaussianBayesBridge.gaussianLocationKernel_comp_prior
#print axioms Komorebi.GaussianBayesBridge.evidence_posterior_joint_eq_swapped_prior_likelihood
#print axioms Komorebi.GaussianBayesBridge.scalarKalmanPosterior_ae_eq_canonicalPosterior
#print axioms Komorebi.GaussianBayesBridge.normalized_bayes_measure_eq_kalman
