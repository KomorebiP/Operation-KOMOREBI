import KomorebiLSM.UniformIntervalMoments
import KomorebiLSM.SequentialLowerCertificate
import Mathlib.MeasureTheory.VectorMeasure.WithDensityVec
import Mathlib.MeasureTheory.Integral.Pi
import Mathlib.Probability.Independence.Basic
import Mathlib.MeasureTheory.Measure.ProbabilityMeasure
import KomorebiLSM.BaseNormModels
import Mathlib.LinearAlgebra.Matrix.Rank

/-! P55: two distinct strictly positive scalar laws with identical low-order
moments, including the exact total-variation distance and product semantics. -/
set_option autoImplicit false
open MeasureTheory Matrix
open scoped BigOperators ENNReal

namespace Komorebi.LSM.LegendreCounterexample

noncomputable section

def L3 (u : ℝ) : ℝ := (5 * u^3 - 3 * u) / 2

@[simp] theorem L3_neg (u : ℝ) : L3 (-u) = -L3 u := by unfold L3; ring

@[simp] theorem L3_zero : L3 0 = 0 := by norm_num [L3]

@[simp] theorem L3_one : L3 1 = 1 := by norm_num [L3]

theorem L3_continuous : Continuous L3 := by unfold L3; fun_prop

/-- A factorization gives the interval bound without presuming it. -/
theorem L3_le_one {u : ℝ} (hu : u ≤ 1) : L3 u ≤ 1 := by
  have hq : 0 ≤ 5 * u^2 + 5 * u + 2 := by nlinarith [sq_nonneg (u + 1/2)]
  have hm := mul_nonpos_of_nonpos_of_nonneg (sub_nonpos.mpr hu) hq
  unfold L3
  nlinarith

theorem L3_abs_le_one {u : ℝ} (hu : u ∈ Set.Icc (-1 : ℝ) 1) : |L3 u| ≤ 1 := by
  apply abs_le.mpr
  constructor
  · have h := L3_le_one (u := -u) (by linarith [hu.1])
    rw [L3_neg] at h
    linarith
  · exact L3_le_one hu.2

def density (ε : ℝ) (u : ℝ) : ℝ := 1 + ε * L3 u

theorem density_continuous (ε : ℝ) : Continuous (density ε) := by
  unfold density L3
  fun_prop

theorem density_positive {ε u : ℝ} (hε : |ε| < 1)
    (hu : u ∈ Set.Icc (-1 : ℝ) 1) : 0 < density ε u := by
  have habs : |ε * L3 u| < 1 := by
    rw [abs_mul]
    exact lt_of_le_of_lt (mul_le_mul_of_nonneg_left (L3_abs_le_one hu) (abs_nonneg ε))
      (by simpa using hε)
  have h := (abs_lt.mp habs).1
  unfold density
  linarith

theorem measure_support : ∀ᵐ u ∂UniformIntervalMoments.measure, u ∈ Set.Icc (-1 : ℝ) 1 := by
  unfold UniformIntervalMoments.measure AveragedCongruence.uniformInterval ProbabilityTheory.cond
  have h : ∀ᵐ u ∂volume.restrict (Set.Ioc (-1 : ℝ) 1), u ∈ Set.Icc (-1 : ℝ) 1 :=
    (ae_restrict_mem measurableSet_Ioc).mono fun _ h => ⟨h.1.le, h.2⟩
  exact Measure.ae_smul_measure h _

/-- Exact orthogonality for any power, derived from the uniform power moments. -/
theorem weighted_L3_integral (j : ℕ) :
    (∫ u, u^j * L3 u ∂UniformIntervalMoments.measure) =
      (5 * UniformIntervalMoments.moment (j + 3) -
        3 * UniformIntervalMoments.moment (j + 1)) / 2 := by
  have heq : (fun u : ℝ => u^j * L3 u) =
      (fun u => (5 * u^(j+3) - 3 * u^(j+1)) / 2) := by
    funext u
    unfold L3
    simp only [pow_add]
    ring
  rw [heq, integral_div, integral_sub
    (UniformIntervalMoments.continuous_integrable (by fun_prop))
    (UniformIntervalMoments.continuous_integrable (by fun_prop)),
    integral_const_mul, integral_const_mul]
  rfl

theorem low_order_orthogonality (j : Fin 3) :
    (∫ u, u^(j : ℕ) * L3 u ∂UniformIntervalMoments.measure) = 0 := by
  rw [weighted_L3_integral]
  fin_cases j <;> norm_num [UniformIntervalMoments.moment_formula]

theorem density_moment (ε : ℝ) (j : Fin 3) :
    (∫ u, u^(j : ℕ) * density ε u ∂UniformIntervalMoments.measure) =
      UniformIntervalMoments.moment j := by
  have heq : (fun u : ℝ => u^(j : ℕ) * density ε u) =
      (fun u => u^(j : ℕ) + ε * (u^(j : ℕ) * L3 u)) := by
    funext u
    unfold density
    ring
  rw [heq, integral_add (UniformIntervalMoments.continuous_integrable (by fun_prop))
    (UniformIntervalMoments.continuous_integrable (by unfold L3; fun_prop)),
    integral_const_mul, low_order_orthogonality]
  simp [UniformIntervalMoments.moment]

theorem density_integral_one (ε : ℝ) :
    (∫ u, density ε u ∂UniformIntervalMoments.measure) = 1 := by
  have h := density_moment ε (0 : Fin 3)
  simpa using h

noncomputable def root : ℝ := Real.sqrt (3/5)

theorem root_nonneg : 0 ≤ root := Real.sqrt_nonneg _

theorem root_sq : root^2 = 3/5 := Real.sq_sqrt (by norm_num)

theorem root_le_one : root ≤ 1 := by
  exact Real.sqrt_le_iff.mpr ⟨by norm_num, by norm_num⟩

theorem L3_nonpos_left {u : ℝ} (hu : u ∈ Set.Icc 0 root) : L3 u ≤ 0 := by
  have hs : u^2 ≤ 3/5 := by nlinarith [root_nonneg, root_sq, hu.1, hu.2]
  have hm := mul_nonpos_of_nonneg_of_nonpos hu.1 (by linarith : 5*u^2-3 ≤ 0)
  unfold L3
  nlinarith

theorem L3_nonneg_right {u : ℝ} (hu : u ∈ Set.Icc root 1) : 0 ≤ L3 u := by
  have hs : 3/5 ≤ u^2 := by nlinarith [root_nonneg, root_sq, hu.1, hu.2]
  have hm := mul_nonneg (root_nonneg.trans hu.1) (by linarith : 0 ≤ 5*u^2-3)
  unfold L3
  nlinarith

/-- The genuine signed polynomial integral on any interval. -/
theorem L3_interval_integral (a b : ℝ) :
    (∫ u in a..b, L3 u) = (5*(b^4-a^4)/4 - 3*(b^2-a^2)/2)/2 := by
  unfold L3
  rw [intervalIntegral.integral_div, intervalIntegral.integral_sub (f := fun u : ℝ => 5 * u^3) (g := fun u : ℝ => 3*u)
    ((continuous_const.mul (continuous_id.pow 3)).intervalIntegrable a b)
    ((continuous_const.mul continuous_id).intervalIntegrable a b),
    intervalIntegral.integral_const_mul, intervalIntegral.integral_const_mul, integral_pow, integral_id]
  norm_num
  ring

/-- The absolute integral is computed by splitting at the actual positive root. -/
theorem L3_abs_integral : (∫ u, |L3 u| ∂UniformIntervalMoments.measure) = 13/40 := by
  have hc : Continuous (fun u => |L3 u|) := L3_continuous.abs
  have hleft : (∫ u in (0 : ℝ)..root, |L3 u|) = -(∫ u in (0 : ℝ)..root, L3 u) := by
    rw [← intervalIntegral.integral_neg]
    apply intervalIntegral.integral_congr
    intro u hu
    rw [Set.uIcc_of_le root_nonneg] at hu
    exact abs_of_nonpos (L3_nonpos_left hu)
  have hright : (∫ u in root..(1 : ℝ), |L3 u|) = ∫ u in root..(1 : ℝ), L3 u := by
    apply intervalIntegral.integral_congr
    intro u hu
    rw [Set.uIcc_of_le root_le_one] at hu
    exact abs_of_nonneg (L3_nonneg_right hu)
  have hhalf : (∫ u in (0 : ℝ)..1, |L3 u|) = 13/40 := by
    rw [← intervalIntegral.integral_add_adjacent_intervals
      (hc.intervalIntegrable 0 root) (hc.intervalIntegrable root 1), hleft, hright,
      L3_interval_integral, L3_interval_integral]
    have h4 : root^4 = 9/25 := by nlinarith [sq_nonneg (root^2 - 3/5), root_sq]
    rw [h4, root_sq]
    norm_num
  have hneg : (∫ u in (-1 : ℝ)..0, |L3 u|) = ∫ u in (0 : ℝ)..1, |L3 u| := by
    have h := intervalIntegral.integral_comp_neg (a := (0 : ℝ)) (b := 1) (fun u => |L3 u|)
    simpa using h.symm
  rw [UniformIntervalMoments.integral_eq,
    ← intervalIntegral.integral_add_adjacent_intervals
      (hc.intervalIntegrable (-1) 0) (hc.intervalIntegrable 0 1), hneg, hhalf]
  norm_num

/-- These are genuine absolutely continuous laws, not just formal densities. -/
def rawLaw (ε : ℝ) : Measure ℝ :=
  UniformIntervalMoments.measure.withDensity (fun u => ENNReal.ofReal (density ε u))

theorem density_ae_positive {ε : ℝ} (hε : |ε| < 1) :
    ∀ᵐ u ∂UniformIntervalMoments.measure, 0 < density ε u :=
  measure_support.mono fun _ hu => density_positive hε hu

theorem density_lintegral_one {ε : ℝ} (hε : |ε| < 1) :
    (∫⁻ u, ENNReal.ofReal (density ε u) ∂UniformIntervalMoments.measure) = 1 := by
  rw [← ofReal_integral_eq_lintegral_ofReal
    (UniformIntervalMoments.continuous_integrable (density_continuous ε))
    ((density_ae_positive hε).mono fun _ h => h.le), density_integral_one, ENNReal.ofReal_one]

theorem rawLaw_isProbability {ε : ℝ} (hε : |ε| < 1) : IsProbabilityMeasure (rawLaw ε) := by
  constructor
  rw [rawLaw, withDensity_apply _ MeasurableSet.univ, Measure.restrict_univ, density_lintegral_one hε]

def law (ε : ℝ) (hε : |ε| < 1) : ProbabilityMeasure ℝ := ⟨rawLaw ε, rawLaw_isProbability hε⟩

/-- Actual law integration agrees with weighted integration under the reference law. -/
theorem law_integral (ε : ℝ) (hε : |ε| < 1) (f : ℝ → ℝ) :
    (∫ u, f u ∂(law ε hε : Measure ℝ)) =
      ∫ u, density ε u * f u ∂UniformIntervalMoments.measure := by
  change (∫ u, f u ∂rawLaw ε) = _
  rw [rawLaw, integral_withDensity_eq_integral_toReal_smul
    (density_continuous ε).measurable.ennreal_ofReal (ae_of_all _ fun _ => ENNReal.ofReal_lt_top)]
  apply integral_congr_ae
  filter_upwards [density_ae_positive hε] with u hu
  rw [ENNReal.toReal_ofReal hu.le, smul_eq_mul]

theorem law_moment (ε : ℝ) (hε : |ε| < 1) (j : Fin 3) :
    (∫ u, u^(j : ℕ) ∂(law ε hε : Measure ℝ)) = UniformIntervalMoments.moment j := by
  rw [law_integral]
  simpa only [mul_comm] using density_moment ε j

/-- Event probabilities are the actual restricted density integrals. -/
theorem law_event_real (ε : ℝ) (hε : |ε| < 1) (event : Set ℝ) (hevent : MeasurableSet event) :
    (law ε hε : Measure ℝ).real event =
      ∫ u in event, density ε u ∂UniformIntervalMoments.measure := by
  change (rawLaw ε event).toReal = _
  rw [rawLaw, withDensity_apply _ hevent]
  exact (integral_eq_lintegral_of_nonneg_ae
    (ae_restrict_of_ae ((density_ae_positive hε).mono fun _ h => h.le))
    (density_continuous ε).aestronglyMeasurable.restrict).symm

/-- The signed measure associated to the actual law has exactly the declared density. -/
theorem law_toSignedMeasure (ε : ℝ) (hε : |ε| < 1) :
    (law ε hε : Measure ℝ).toSignedMeasure =
      UniformIntervalMoments.measure.withDensityᵥ (density ε) := by
  have hf : (∫⁻ u, ENNReal.ofReal (density ε u) ∂UniformIntervalMoments.measure) ≠ ⊤ := by
    rw [density_lintegral_one hε]
    exact ENNReal.one_ne_top
  have hreal := withDensityᵥ_toReal (density_continuous ε).measurable.ennreal_ofReal.aemeasurable hf
  refine hreal.symm.trans (WithDensityᵥEq.congr_ae ?_)
  filter_upwards [density_ae_positive hε] with u hu
  exact ENNReal.toReal_ofReal hu.le

/-- Exact total variation of the actual positive probability laws. -/
theorem law_totalVariation (ε : ℝ) (hε : |ε| < 1) :
    SequentialLowerCertificate.lawTV (law ε hε : Measure ℝ)
      (law (-ε) (by simpa using hε) : Measure ℝ) = 13 * |ε| / 40 := by
  have hdiff : Integrable (fun u => density ε u - density (-ε) u) UniformIntervalMoments.measure :=
    UniformIntervalMoments.continuous_integrable ((density_continuous ε).sub (density_continuous (-ε)))
  rw [SequentialLowerCertificate.lawTV, law_toSignedMeasure, law_toSignedMeasure,
    ← withDensityᵥ_sub' (UniformIntervalMoments.continuous_integrable (density_continuous ε))
      (UniformIntervalMoments.continuous_integrable (density_continuous (-ε))),
    SignedMeasure.totalVariation_eq_variation, Measure.variation_withDensityᵥ hdiff,
    Measure.real, withDensity_apply _ MeasurableSet.univ, Measure.restrict_univ,
    ← integral_norm_eq_lintegral_enorm hdiff.aestronglyMeasurable]
  have heq : (fun u => ‖density ε u - density (-ε) u‖) =
      (fun u => 2 * |ε| * |L3 u|) := by
    funext u
    rw [Real.norm_eq_abs, show density ε u - density (-ε) u = 2 * ε * L3 u by unfold density; ring,
      abs_mul, abs_mul]
    norm_num
  rw [heq, integral_const_mul, L3_abs_integral]
  ring

theorem positive_law_totalVariation {ε : ℝ} (hε0 : 0 < ε) (hε1 : ε < 1) :
    SequentialLowerCertificate.lawTV (law ε (by rwa [abs_of_pos hε0]) : Measure ℝ)
      (law (-ε) (by rwa [abs_neg, abs_of_pos hε0]) : Measure ℝ) = 13 * ε / 40 := by
  simpa only [abs_of_pos hε0] using law_totalVariation ε (by rwa [abs_of_pos hε0])

theorem laws_distinct {ε : ℝ} (hε0 : 0 < ε) (hε1 : ε < 1) :
    (law ε (by rwa [abs_of_pos hε0]) : Measure ℝ) ≠
      (law (-ε) (by rwa [abs_neg, abs_of_pos hε0]) : Measure ℝ) := by
  intro heq
  have h := positive_law_totalVariation hε0 hε1
  simp only [SequentialLowerCertificate.lawTV, heq, sub_self, SignedMeasure.totalVariation_zero,
    Measure.real, Measure.coe_zero, Pi.zero_apply, ENNReal.toReal_zero, mul_zero] at h
  linarith

/-- Taking independent observations means the actual finite product measure. -/
def productLaw (ε : ℝ) (hε : |ε| < 1) (N : ℕ) : Measure (Fin N → ℝ) :=
  Measure.pi (fun _ : Fin N => (law ε hε : Measure ℝ))

instance productLaw_isProbability (ε : ℝ) (hε : |ε| < 1) (N : ℕ) :
    IsProbabilityMeasure (productLaw ε hε N) := by unfold productLaw; infer_instance

theorem productLaw_independent (ε : ℝ) (hε : |ε| < 1) (N : ℕ) :
    ProbabilityTheory.iIndepFun (fun i (x : Fin N → ℝ) => x i) (productLaw ε hε N) :=
  ProbabilityTheory.iIndepFun_pi (fun _ => measurable_id.aemeasurable)

/-- Every low-order product moment factors and is independent of the sign. -/
theorem product_moments (ε : ℝ) (hε : |ε| < 1) (N : ℕ) (j : Fin N → Fin 3) :
    (∫ x, ∏ i, (x i)^(j i : ℕ) ∂productLaw ε hε N) =
      ∏ i, UniformIntervalMoments.moment (j i) := by
  unfold productLaw
  rw [integral_fintype_prod_eq_prod (fun (i : Fin N) (u : ℝ) => u^(j i : ℕ))]
  apply Finset.prod_congr rfl
  intro i _
  exact law_moment ε hε (j i)

theorem product_moments_equal (ε : ℝ) (hε : |ε| < 1) (N : ℕ) (j : Fin N → Fin 3) :
    (∫ x, ∏ i, (x i)^(j i : ℕ) ∂productLaw ε hε N) =
      ∫ x, ∏ i, (x i)^(j i : ℕ) ∂productLaw (-ε) (by simpa using hε) N := by
  rw [product_moments, product_moments]

/-- A one-dimensional positive operator density with identity mass functional. -/
def scalarOperator (ε u : ℝ) : ℝ →ₗ[ℝ] ℝ := density ε u • LinearMap.id

@[simp] theorem scalarOperator_apply (ε u z : ℝ) : scalarOperator ε u z = density ε u * z := rfl

theorem scalarOperator_positive {ε : ℝ} (hε : |ε| < 1) :
    ∀ᵐ u ∂UniformIntervalMoments.measure,
      ∀ z ∈ BaseNorm.scalarCone.carrier, scalarOperator ε u z ∈ BaseNorm.scalarCone.carrier := by
  filter_upwards [density_ae_positive hε] with u hu
  intro z hz
  change 0 ≤ density ε u * z
  exact mul_nonneg hu.le hz

/-- Exact normalization on the whole predictive space. -/
theorem scalarOperator_normalized (ε z : ℝ) :
    (∫ u, scalarOperator ε u z ∂UniformIntervalMoments.measure) = z := by
  simp only [scalarOperator_apply, integral_mul_const, density_integral_one, one_mul]

theorem scalar_initial_and_dimension :
    (1 : ℝ) ∈ BaseNorm.scalarCone.base ∧ Module.finrank ℝ ℝ = 1 := by
  constructor
  · constructor <;> norm_num [BaseNorm.scalarCone]
  · exact Module.finrank_self ℝ

/-- An event acts on the scalar state by its actual law probability. -/
def eventOperator (ε : ℝ) (hε : |ε| < 1) (event : Set ℝ) : ℝ →ₗ[ℝ] ℝ :=
  (law ε hε : Measure ℝ).real event • LinearMap.id

theorem eventOperator_integral (ε : ℝ) (hε : |ε| < 1)
    (event : Set ℝ) (hevent : MeasurableSet event) (z : ℝ) :
    eventOperator ε hε event z = ∫ u in event, scalarOperator ε u z ∂UniformIntervalMoments.measure := by
  simp only [eventOperator, LinearMap.smul_apply, LinearMap.id_apply, smul_eq_mul,
    scalarOperator_apply, integral_mul_const]
  rw [law_event_real ε hε event hevent]

def wordProbability (ε : ℝ) (hε : |ε| < 1) (events : List (Set ℝ)) : ℝ :=
  (events.map (fun event => (law ε hε : Measure ℝ).real event)).prod

theorem event_word_scalar (ε : ℝ) (hε : |ε| < 1) (events : List (Set ℝ)) (z : ℝ) :
    FiniteInstruments.wordAction (eventOperator ε hε) events z = wordProbability ε hε events * z := by
  induction events generalizing z with
  | nil => simp [FiniteInstruments.wordAction, wordProbability]
  | cons event events ih =>
    simp only [FiniteInstruments.wordAction, LinearMap.comp_apply, ih,
      eventOperator, LinearMap.smul_apply, LinearMap.id_apply, smul_eq_mul,
      wordProbability, List.map_cons, List.prod_cons]
    ring

/-- The scalar event representation is exactly the actual independent record law. -/
theorem rankone_event_realization (ε : ℝ) (hε : |ε| < 1) (N : ℕ) (events : Fin N → Set ℝ) :
    (productLaw ε hε N).real (Set.univ.pi events) =
      FiniteInstruments.wordAction (eventOperator ε hε) (List.ofFn events) 1 := by
  rw [event_word_scalar, mul_one]
  simp only [productLaw, Measure.real, Measure.pi_pi, ENNReal.toReal_prod,
    wordProbability, List.map_ofFn, List.prod_ofFn, Function.comp_apply]

/-- Every event-history/core table factors as an outer product. -/
theorem event_hankel_factor {I J : Type*} (ε : ℝ) (hε : |ε| < 1)
    (tests : I → List (Set ℝ)) (histories : J → List (Set ℝ)) :
    (fun i j => wordProbability ε hε (histories j ++ tests i)) =
      Matrix.vecMulVec (fun i => wordProbability ε hε (tests i))
        (fun j => wordProbability ε hε (histories j)) := by
  funext i j
  simp [wordProbability, Matrix.vecMulVec, List.map_append, List.prod_append, mul_comm]

/-- A complete finite table containing empty history and test has rank exactly
one; this rules out a zero-dimensional predictive process. -/
theorem event_hankel_rank_one {I J : Type*} [Fintype J] (ε : ℝ) (hε : |ε| < 1)
    (tests : I → List (Set ℝ)) (histories : J → List (Set ℝ))
    (i₀ : I) (j₀ : J) (ht : tests i₀ = []) (hh : histories j₀ = []) :
    Matrix.rank (fun i j => wordProbability ε hε (histories j ++ tests i)) = 1 := by
  apply le_antisymm
  · rw [event_hankel_factor]
    exact Matrix.rank_vecMulVec_le _ _
  · have hsub : Matrix.submatrix (fun i j => wordProbability ε hε (histories j ++ tests i))
        (fun _ : Fin 1 => i₀) (fun _ : Fin 1 => j₀) = (1 : Matrix (Fin 1) (Fin 1) ℝ) := by
      ext i j
      fin_cases i
      fin_cases j
      simp [Matrix.submatrix, ht, hh, wordProbability]
    have h := Matrix.rank_submatrix_le
      (fun i j => wordProbability ε hε (histories j ++ tests i))
      (fun _ : Fin 1 => i₀) (fun _ : Fin 1 => j₀)
    rw [hsub, Matrix.rank_one, Fintype.card_fin] at h
    exact h

/-- The misspecification is genuine: a nonzero cubic perturbation does not
belong to the quadratic class even when equality is requested only on [-1,1]. -/
theorem density_not_quadratic {ε : ℝ} (hε : ε ≠ 0) :
    ¬ ∃ c : Fin 3 → ℝ, ∀ u ∈ Set.Icc (-1 : ℝ) 1,
      density ε u = ∑ k : Fin 3, c k * u^(k : ℕ) := by
  rintro ⟨c, hc⟩
  let p : Polynomial ℝ := Polynomial.ofFn 4 ![1, -3*ε/2, 0, 5*ε/2]
  have heval (u : ℝ) : p.eval u = density ε u := by
    simp only [p, UniformIntervalMoments.eval_ofFn, Fin.sum_univ_succ]
    norm_num [density, L3, Matrix.cons_val_two]
    ring
  have heq : p = Polynomial.ofFn 3 c := by
    apply Polynomial.eq_of_infinite_eval_eq
    apply (Set.Ioo_infinite (by norm_num : (-1 : ℝ) < 1)).mono
    intro u hu
    change p.eval u = (Polynomial.ofFn 3 c).eval u
    rw [heval, UniformIntervalMoments.eval_ofFn]
    exact hc u ⟨hu.1.le, hu.2.le⟩
  have hcoeff := congrArg (fun q : Polynomial ℝ => q.coeff 3) heq
  norm_num [p, Polynomial.ofFn_coeff_eq_val_of_lt, Polynomial.ofFn_coeff_eq_zero_of_ge] at hcoeff
  apply hε
  linarith

end
end Komorebi.LSM.LegendreCounterexample
