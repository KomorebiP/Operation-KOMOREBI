import Mathlib.Analysis.SpecialFunctions.Bernstein
import Mathlib.Analysis.Calculus.Deriv.Polynomial
import Mathlib.Analysis.SpecialFunctions.Integrals.Basic
import Mathlib.MeasureTheory.Integral.Prod
import Mathlib.MeasureTheory.Measure.ProbabilityMeasure
import Mathlib.MeasureTheory.Function.LocallyIntegrable

/-! The actual positive Bernstein–Durrmeyer kernel on the unit interval. -/
set_option autoImplicit false
open MeasureTheory Polynomial
open scoped BigOperators ENNReal

namespace Komorebi.LSM.BernsteinKernel
noncomputable section

/-- Lebesgue measure on [0,1], already normalized to total mass one. -/
def measure : Measure ℝ := volume.restrict (Set.Icc 0 1)

instance measure_probability : IsProbabilityMeasure measure := by
  constructor
  norm_num [measure]

theorem support_ae : ∀ᵐ x ∂measure, x ∈ Set.Icc (0 : ℝ) 1 :=
  ae_restrict_mem measurableSet_Icc

theorem integral_eq_interval (f : ℝ → ℝ) :
    (∫ x, f x ∂measure) = ∫ x in (0 : ℝ)..1, f x := by
  rw [intervalIntegral.integral_of_le (by norm_num)]
  exact integral_Icc_eq_integral_Ioc

theorem continuous_integrable {F : Type*} [NormedAddCommGroup F] [NormedSpace ℝ F]
    {f : ℝ → F} (hf : Continuous f) : Integrable f measure := hf.integrableOn_Icc

/-- The basis is defined by the literal polynomial, on all real inputs. -/
def basis (n k : ℕ) (x : ℝ) : ℝ := (bernsteinPolynomial ℝ n k).eval x

theorem basis_formula (n k : ℕ) (x : ℝ) :
    basis n k x = (n.choose k : ℝ) * x^k * (1-x)^(n-k) := by
  simp [basis, bernsteinPolynomial]

theorem basis_continuous (n k : ℕ) : Continuous (basis n k) := (bernsteinPolynomial ℝ n k).continuous

theorem basis_nonneg (n k : ℕ) {x : ℝ} (hx : x ∈ Set.Icc (0 : ℝ) 1) : 0 ≤ basis n k x := by
  rw [basis_formula]
  exact mul_nonneg (mul_nonneg (Nat.cast_nonneg _) (pow_nonneg hx.1 _))
    (pow_nonneg (sub_nonneg.mpr hx.2) _)

theorem sum_basis (n : ℕ) (x : ℝ) : (∑ k : Fin (n+1), basis n k x) = 1 := by
  have h := congrArg (Polynomial.eval x) (bernsteinPolynomial.sum ℝ n)
  simpa [basis, Polynomial.eval_finsetSum, Finset.sum_range] using h

theorem basis_le_one (n : ℕ) (k : Fin (n+1)) {x : ℝ} (hx : x ∈ Set.Icc (0 : ℝ) 1) :
    basis n k x ≤ 1 := by
  rw [← sum_basis n x]
  exact Finset.single_le_sum (s := Finset.univ) (f := fun j : Fin (n+1) => basis n j x)
    (fun j _ => basis_nonneg n j hx) (Finset.mem_univ k)

/-- The derivative ladder equates the integrals of adjacent basis elements. -/
theorem basis_integral_adjacent (n k : ℕ) (hk : k < n) :
    (∫ x, basis n k x ∂measure) = ∫ x, basis n (k+1) x ∂measure := by
  let p := bernsteinPolynomial ℝ (n+1) (k+1)
  have h := intervalIntegral.integral_eq_sub_of_hasDerivAt
    (fun x _ => p.hasDerivAt x) (p.derivative.continuous.intervalIntegrable 0 1)
  have he : p.eval 1 - p.eval 0 = 0 := by
    simp [p, bernsteinPolynomial.eval_at_0, bernsteinPolynomial.eval_at_1,
      Nat.ne_of_lt hk]
  rw [he] at h
  have hd : (fun x => p.derivative.eval x) =
      (fun x => ((n : ℝ)+1) * (basis n k x - basis n (k+1) x)) := by
    funext x
    simp [p, bernsteinPolynomial.derivative_succ_aux, basis]
  rw [hd, intervalIntegral.integral_const_mul,
    intervalIntegral.integral_sub ((basis_continuous n k).intervalIntegrable 0 1)
      ((basis_continuous n (k+1)).intervalIntegrable 0 1)] at h
  rw [integral_eq_interval, integral_eq_interval]
  have hn : (n : ℝ)+1 ≠ 0 := by positivity
  exact sub_eq_zero.mp ((mul_eq_zero.mp h).resolve_left hn)

theorem basis_integral_eq_zero_index (n k : ℕ) (hk : k ≤ n) :
    (∫ x, basis n k x ∂measure) = ∫ x, basis n 0 x ∂measure := by
  induction k with
  | zero => rfl
  | succ k ih =>
    exact (basis_integral_adjacent n k (by omega)).symm.trans (ih (by omega))

/-- Every basis element has exact integral 1/(n+1), proved by the ladder and sum identity. -/
theorem basis_integral (n : ℕ) (k : Fin (n+1)) :
    (∫ x, basis n k x ∂measure) = 1 / ((n : ℝ)+1) := by
  have hs : (∑ j : Fin (n+1), ∫ x, basis n j x ∂measure) = 1 := by
    rw [← integral_finsetSum (f := fun (j : Fin (n+1)) x => basis n j x) _
      (fun j _ => continuous_integrable (basis_continuous n j))]
    simp_rw [sum_basis]
    simp
  have hz : ((n : ℝ)+1) * (∫ x, basis n 0 x ∂measure) = 1 := by
    simpa only [basis_integral_eq_zero_index n _ (Fin.is_le _), Finset.sum_const,
      Finset.card_univ, Fintype.card_fin, nsmul_eq_mul, Nat.cast_add, Nat.cast_one] using hs
  rw [basis_integral_eq_zero_index n k k.is_le]
  exact (eq_div_iff (by positivity : (n : ℝ)+1 ≠ 0)).mpr (by nlinarith [hz])

/-- Degree elevation supplies the exact first weighted beta moment. -/
theorem basis_mul_x (n : ℕ) (k : Fin (n+1)) (x : ℝ) :
    basis n k x * x = ((k : ℝ)+1) / ((n : ℝ)+1) * basis (n+1) ((k : ℕ)+1) x := by
  have hc : ((n : ℝ)+1) * (n.choose k : ℝ) =
      ((n+1).choose ((k : ℕ)+1) : ℝ) * ((k : ℝ)+1) := by
    exact_mod_cast Nat.add_one_mul_choose_eq n (k : ℕ)
  rw [basis_formula, basis_formula, Nat.add_sub_add_right]
  field_simp
  rw [pow_succ]
  linear_combination (x^(k : ℕ) * x * (1-x)^(n-(k : ℕ))) * hc

theorem basis_first_moment (n : ℕ) (k : Fin (n+1)) :
    (∫ x, basis n k x * x ∂measure) =
      ((k : ℝ)+1) / (((n : ℝ)+1) * ((n : ℝ)+2)) := by
  simp_rw [basis_mul_x]
  rw [integral_const_mul, basis_integral (n+1) ⟨(k : ℕ)+1, by omega⟩]
  push_cast
  field_simp
  ring

/-- The classical Bernstein–Durrmeyer kernel. -/
def kernel (n : ℕ) (x v : ℝ) : ℝ :=
  ((n : ℝ)+1) * ∑ k : Fin (n+1), basis n k x * basis n k v

theorem kernel_nonneg (n : ℕ) {x v : ℝ}
    (hx : x ∈ Set.Icc (0 : ℝ) 1) (hv : v ∈ Set.Icc (0 : ℝ) 1) : 0 ≤ kernel n x v := by
  exact mul_nonneg (by positivity) (Finset.sum_nonneg fun k _ =>
    mul_nonneg (basis_nonneg n k hx) (basis_nonneg n k hv))

theorem kernel_symmetric (n : ℕ) (x v : ℝ) : kernel n x v = kernel n v x := by
  simp only [kernel, mul_comm]

theorem kernel_continuous (n : ℕ) : Continuous (Function.uncurry (kernel n)) := by
  unfold kernel basis bernsteinPolynomial
  fun_prop

/-- Both marginal kernel integrals equal one exactly. -/
theorem kernel_integral_right (n : ℕ) (x : ℝ) : (∫ v, kernel n x v ∂measure) = 1 := by
  simp only [kernel]
  rw [integral_const_mul, integral_finsetSum (f := fun (k : Fin (n+1)) v => basis n k x * basis n k v) _ (fun k _ =>
    continuous_integrable (continuous_const.mul (basis_continuous n k)))]
  simp_rw [integral_const_mul, basis_integral]
  rw [← Finset.sum_mul, sum_basis]
  field_simp

theorem kernel_integral_left (n : ℕ) (v : ℝ) : (∫ x, kernel n x v ∂measure) = 1 := by
  simp_rw [kernel_symmetric n _ v]
  exact kernel_integral_right n v

/-- Continuous functions have actual integrals on the unit square. -/
theorem continuous_joint_integrable {F : Type*} [NormedAddCommGroup F] [NormedSpace ℝ F]
    {f : ℝ × ℝ → F} (hf : Continuous f) : Integrable f (measure.prod measure) := by
  unfold measure
  rw [Measure.prod_restrict]
  exact hf.continuousOn.integrableOn_compact (isCompact_Icc.prod isCompact_Icc)

/-- Joint averaging separates a product test into the exact basis moments. -/
theorem kernel_product_integral (n : ℕ) (f g : ℝ → ℝ) (hf : Continuous f) (hg : Continuous g) :
    (∫ x, ∫ v, kernel n x v * (f x * g v) ∂measure ∂measure) =
      ((n : ℝ)+1) * ∑ k : Fin (n+1),
        (∫ x, basis n k x * f x ∂measure) * (∫ v, basis n k v * g v ∂measure) := by
  have hi (x : ℝ) : (∫ v, kernel n x v * (f x * g v) ∂measure) =
      ((n : ℝ)+1) * ∑ k : Fin (n+1), (basis n k x * f x) *
        (∫ v, basis n k v * g v ∂measure) := by
    have heq : (fun v => kernel n x v * (f x * g v)) =
        (fun v => ((n : ℝ)+1) * ∑ k : Fin (n+1), (basis n k x * f x) * (basis n k v * g v)) := by
      funext v
      simp only [kernel, Finset.sum_mul, Finset.mul_sum]
      congr 1
      funext k
      ring
    rw [heq, integral_const_mul, integral_finsetSum (f := fun (k : Fin (n+1)) v =>
      (basis n k x * f x) * (basis n k v * g v)) _ (fun k _ =>
        continuous_integrable (continuous_const.mul ((basis_continuous n k).mul hg)))]
    simp only [integral_const_mul]
  simp_rw [hi]
  rw [integral_const_mul, integral_finsetSum (f := fun (k : Fin (n+1)) x =>
    (basis n k x * f x) * (∫ v, basis n k v * g v ∂measure)) _
    (fun k _ => continuous_integrable (((basis_continuous n k).mul hf).mul continuous_const))]
  simp only [integral_mul_const]

/-- The sum of the first squares, stated directly over real casts. -/
theorem sum_succ_squares (m : ℕ) :
    (∑ k ∈ Finset.range m, ((k : ℝ)+1)^2) = (m : ℝ) * (m+1) * (2*m+1) / 6 := by
  induction m with
  | zero => simp
  | succ m ih =>
    rw [Finset.sum_range_succ, ih]
    push_cast
    ring

/-- The exact mixed moment under the actual joint kernel density. -/
theorem kernel_mixed_moment (n : ℕ) :
    (∫ x, ∫ v, kernel n x v * (x*v) ∂measure ∂measure) =
      (2*(n : ℝ)+3) / (6*((n : ℝ)+2)) := by
  rw [kernel_product_integral n (fun x : ℝ => x) (fun v : ℝ => v) continuous_id continuous_id]
  simp_rw [basis_first_moment, ← pow_two, div_pow]
  rw [← Finset.sum_div, ← Finset.sum_range (fun k : ℕ => ((k : ℝ)+1)^2), sum_succ_squares]
  push_cast
  field_simp
  ring

/-- Each marginal is uniform, so its second moment is exactly one third. -/
theorem kernel_first_square (n : ℕ) :
    (∫ x, ∫ v, kernel n x v * x^2 ∂measure ∂measure) = 1/3 := by
  simp_rw [integral_mul_const, kernel_integral_right, one_mul]
  rw [integral_eq_interval, integral_pow]
  norm_num

theorem kernel_second_square (n : ℕ) :
    (∫ x, ∫ v, kernel n x v * v^2 ∂measure ∂measure) = 1/3 := by
  have hj : Integrable (fun p : ℝ × ℝ => kernel n p.1 p.2 * p.2^2) (measure.prod measure) :=
    continuous_joint_integrable ((kernel_continuous n).mul (continuous_snd.pow 2))
  rw [integral_integral_swap (f := fun x v => kernel n x v * v^2) hj]
  simp_rw [integral_mul_const, kernel_integral_left, one_mul]
  rw [integral_eq_interval, integral_pow]
  norm_num

/-- The genuine joint squared-distance integral, including the exact constant. -/
theorem kernel_squared_distance (n : ℕ) :
    (∫ x, ∫ v, kernel n x v * (v-x)^2 ∂measure ∂measure) = 1 / (3*((n : ℝ)+2)) := by
  have hi (x : ℝ) : (∫ v, kernel n x v * (v-x)^2 ∂measure) =
      (∫ v, kernel n x v * v^2 ∂measure) +
        (∫ v, kernel n x v * x^2 ∂measure) -
          2 * (∫ v, kernel n x v * (x*v) ∂measure) := by
    have heq : (fun v => kernel n x v * (v-x)^2) =
        (fun v => kernel n x v * v^2 + kernel n x v * x^2 - 2 * (kernel n x v * (x*v))) := by
      funext v
      ring
    have hc : Continuous (fun v => kernel n x v) :=
      (kernel_continuous n).comp (continuous_const.prodMk continuous_id)
    rw [heq, integral_sub
      (f := fun v => kernel n x v * v^2 + kernel n x v * x^2)
      (g := fun v => 2 * (kernel n x v * (x*v)))
      ((continuous_integrable (hc.mul (continuous_id.pow 2))).add
        (continuous_integrable (hc.mul continuous_const)))
      (continuous_integrable (continuous_const.mul (hc.mul (continuous_const.mul continuous_id)))),
      integral_add (f := fun v => kernel n x v * v^2) (g := fun v => kernel n x v * x^2)
        (continuous_integrable (hc.mul (continuous_id.pow 2)))
        (continuous_integrable (hc.mul continuous_const)), integral_const_mul]
  simp_rw [hi]
  have h1 : Integrable (fun x => ∫ v, kernel n x v * v^2 ∂measure) measure :=
    (continuous_joint_integrable ((kernel_continuous n).mul (continuous_snd.pow 2))).integral_prod_left
  have h2 : Integrable (fun x => ∫ v, kernel n x v * x^2 ∂measure) measure :=
    (continuous_joint_integrable ((kernel_continuous n).mul (continuous_fst.pow 2))).integral_prod_left
  have h3 : Integrable (fun x => ∫ v, kernel n x v * (x*v) ∂measure) measure :=
    (continuous_joint_integrable ((kernel_continuous n).mul (continuous_fst.mul continuous_snd))).integral_prod_left
  rw [integral_sub
    (f := fun x => (∫ v, kernel n x v * v^2 ∂measure) + (∫ v, kernel n x v * x^2 ∂measure))
    (g := fun x => 2 * (∫ v, kernel n x v * (x*v) ∂measure)) (h1.add h2) (h3.const_mul 2),
    integral_add (f := fun x => ∫ v, kernel n x v * v^2 ∂measure)
      (g := fun x => ∫ v, kernel n x v * x^2 ∂measure) h1 h2, integral_const_mul,
    kernel_first_square, kernel_second_square, kernel_mixed_moment]
  field_simp
  ring

/-- The genuine joint density is supported on the unit square. -/
theorem joint_support_ae : ∀ᵐ p ∂measure.prod measure,
    p ∈ Set.Icc (0 : ℝ) 1 ×ˢ Set.Icc (0 : ℝ) 1 := by
  apply (Measure.ae_prod_iff_ae_ae (measurableSet_Icc.prod measurableSet_Icc)).mpr
  filter_upwards [support_ae] with x hx
  filter_upwards [support_ae] with v hv
  exact ⟨hx,hv⟩

theorem kernel_nonneg_ae (n : ℕ) :
    ∀ᵐ p ∂measure.prod measure, 0 ≤ kernel n p.1 p.2 :=
  joint_support_ae.mono fun _ hp => kernel_nonneg n hp.1 hp.2

theorem kernel_joint_integrable (n : ℕ) :
    Integrable (fun p : ℝ × ℝ => kernel n p.1 p.2) (measure.prod measure) :=
  continuous_joint_integrable (kernel_continuous n)

theorem joint_kernel_integral (n : ℕ) :
    (∫ p : ℝ × ℝ, kernel n p.1 p.2 ∂measure.prod measure) = 1 := by
  rw [integral_prod (fun p : ℝ × ℝ => kernel n p.1 p.2) (kernel_joint_integrable n)]
  simp_rw [kernel_integral_right]
  simp

/-- An actual probability measure, not an assumed coupling. -/
def jointLaw (n : ℕ) : Measure (ℝ × ℝ) :=
  (measure.prod measure).withDensity (fun p => ENNReal.ofReal (kernel n p.1 p.2))

instance jointLaw_probability (n : ℕ) : IsProbabilityMeasure (jointLaw n) := by
  constructor
  rw [jointLaw, withDensity_apply _ MeasurableSet.univ, Measure.restrict_univ,
    ← ofReal_integral_eq_lintegral_ofReal (kernel_joint_integrable n)
      (kernel_nonneg_ae n), joint_kernel_integral, ENNReal.ofReal_one]

theorem jointLaw_integral (n : ℕ) (f : ℝ × ℝ → ℝ) :
    (∫ p, f p ∂jointLaw n) = ∫ p, kernel n p.1 p.2 * f p ∂measure.prod measure := by
  have hm : Measurable (fun p : ℝ × ℝ => ENNReal.ofReal (kernel n p.1 p.2)) :=
    (kernel_continuous n).measurable.ennreal_ofReal
  rw [jointLaw, integral_withDensity_eq_integral_toReal_smul hm
    (ae_of_all _ fun _ => ENNReal.ofReal_lt_top)]
  apply integral_congr_ae
  filter_upwards [kernel_nonneg_ae n] with p hp
  rw [ENNReal.toReal_ofReal hp, smul_eq_mul]

theorem jointLaw_support (n : ℕ) : ∀ᵐ p ∂jointLaw n,
    p ∈ Set.Icc (0 : ℝ) 1 ×ˢ Set.Icc (0 : ℝ) 1 :=
  (withDensity_absolutelyContinuous _ _).ae_le joint_support_ae

def distance (p : ℝ × ℝ) : ℝ := |p.2-p.1|

theorem distance_continuous : Continuous distance := (continuous_snd.sub continuous_fst).abs

theorem distance_le_one {p : ℝ × ℝ} (hp : p ∈ Set.Icc (0 : ℝ) 1 ×ˢ Set.Icc (0 : ℝ) 1) :
    distance p ≤ 1 := by
  apply abs_le.mpr
  constructor <;> linarith [hp.1.1,hp.1.2,hp.2.1,hp.2.2]

theorem distance_integrable (n : ℕ) : Integrable distance (jointLaw n) := by
  apply Integrable.of_bound distance_continuous.aestronglyMeasurable 1
  filter_upwards [jointLaw_support n] with p hp
  change ‖|p.2-p.1|‖ ≤ 1
  rw [Real.norm_eq_abs, abs_abs]
  exact distance_le_one hp

theorem distance_square_integrable (n : ℕ) : Integrable (fun p => distance p ^ 2) (jointLaw n) := by
  apply Integrable.of_bound (distance_continuous.pow 2).aestronglyMeasurable 1
  filter_upwards [jointLaw_support n] with p hp
  rw [Real.norm_eq_abs, abs_of_nonneg (sq_nonneg _)]
  exact pow_le_one₀ (abs_nonneg _) (distance_le_one hp)

theorem jointLaw_squared_distance (n : ℕ) :
    (∫ p, distance p ^ 2 ∂jointLaw n) = 1 / (3*((n : ℝ)+2)) := by
  have hi : Integrable (fun p : ℝ × ℝ => kernel n p.1 p.2 * distance p ^ 2) (measure.prod measure) :=
    continuous_joint_integrable ((kernel_continuous n).mul (distance_continuous.pow 2))
  rw [jointLaw_integral, integral_prod (fun p : ℝ × ℝ => kernel n p.1 p.2 * distance p ^ 2) hi]
  simp only [distance, sq_abs]
  exact kernel_squared_distance n

/-- Cauchy–Schwarz for the actual joint law, proved by its nonnegative variance. -/
theorem jointLaw_distance_bound (n : ℕ) :
    (∫ p, distance p ∂jointLaw n) ≤ 1 / Real.sqrt (3*((n : ℝ)+2)) := by
  let m := ∫ p, distance p ∂jointLaw n
  have hvar : 0 ≤ ∫ p, distance p ^ 2 - 2*m*distance p + m^2 ∂jointLaw n := by
    apply integral_nonneg
    intro p
    change (0 : ℝ) ≤ distance p ^ 2 - 2*m*distance p + m^2
    nlinarith [sq_nonneg (distance p-m)]
  rw [integral_add (f := fun p => distance p^2 - 2*m*distance p) (g := fun _ => m^2)
      ((distance_square_integrable n).sub ((distance_integrable n).const_mul (2*m)))
      (integrable_const _), integral_sub (f := fun p => distance p^2) (g := fun p => 2*m*distance p)
      (distance_square_integrable n)
      ((distance_integrable n).const_mul (2*m)), integral_const_mul, integral_const] at hvar
  simp only [probReal_univ, one_smul] at hvar
  rw [jointLaw_squared_distance] at hvar
  have hm : m^2 ≤ 1 / (3*((n : ℝ)+2)) := by nlinarith [hvar]
  have hpos : 0 ≤ 1 / (3*((n : ℝ)+2)) := by positivity
  have hbound : m ≤ Real.sqrt (1 / (3*((n : ℝ)+2))) := by
    nlinarith [Real.sq_sqrt hpos, Real.sqrt_nonneg (1 / (3*((n : ℝ)+2)))]
  simpa only [one_div, Real.sqrt_inv] using hbound

/-- The integrated absolute kernel displacement has the stated exact-rate bound. -/
theorem kernel_distance_bound (n : ℕ) :
    (∫ x, ∫ v, kernel n x v * |v-x| ∂measure ∂measure) ≤
      1 / Real.sqrt (3*((n : ℝ)+2)) := by
  have h := jointLaw_distance_bound n
  have hi : Integrable (fun p : ℝ × ℝ => kernel n p.1 p.2 * distance p) (measure.prod measure) :=
    continuous_joint_integrable ((kernel_continuous n).mul distance_continuous)
  rw [jointLaw_integral, integral_prod (fun p : ℝ × ℝ => kernel n p.1 p.2 * distance p) hi] at h
  exact h

end
end Komorebi.LSM.BernsteinKernel
