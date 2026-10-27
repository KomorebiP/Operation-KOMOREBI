import KomorebiLSM.CurvedMomentTV
import KomorebiLSM.PolynomialGram
import Mathlib.Analysis.SpecialFunctions.Integrals.Basic
import Mathlib.Tactic

/-! Actual five-node and normalized Lebesgue references, with exact absolute
moments. The finite experiment and continuous experiment remain distinct. -/
set_option autoImplicit false
namespace Komorebi.LSM.CurvedMoment
open MeasureTheory
open scoped BigOperators ENNReal
noncomputable section

namespace FiveNode

def node : Fin 5 → ℝ := ![-1,-1/2,0,1/2,1]
def weight : Fin 5 → ℝ≥0∞ := ![7/90,16/45,2/15,16/45,7/90]
def measure : Measure ℝ := ∑ i : Fin 5, weight i • Measure.dirac (node i)

theorem weight_ne_top (i : Fin 5) : weight i≠∞ := by
  fin_cases i <;> dsimp [weight] <;>
    exact ENNReal.div_ne_top (by norm_num) (by norm_num)

instance measure_probability : IsProbabilityMeasure measure := by
  constructor
  apply (ENNReal.toReal_eq_one_iff _).mp
  have he : measure Set.univ=∑ i : Fin 5,weight i := by
    simp [measure]
  rw [he,ENNReal.toReal_sum (fun i _ => weight_ne_top i)]
  norm_num [Fin.sum_univ_succ,weight]

theorem integral_eq (f : ℝ → ℝ) :
    (∫ u,f u∂measure)=∑ i : Fin 5,(weight i).toReal*f (node i) := by
  rw [measure,integral_finsetSum_measure]
  · simp only [integral_smul_measure,integral_dirac,smul_eq_mul]
  · intro i _
    exact (integrable_dirac (f:=f) (by simp)).smul_measure (weight_ne_top i)

theorem support : ∀ᵐ u∂measure,u∈Set.Icc (-1:ℝ) 1 := by
  rw [measure,ae_finsetSum_measure_iff]
  intro i _
  apply Measure.ae_smul_measure
  apply (ae_dirac_iff (p := fun x : ℝ => x∈Set.Icc (-1:ℝ) 1) measurableSet_Icc).mpr
  fin_cases i <;> norm_num [node]

theorem reference : Reference measure := by
  refine ⟨measure_probability,support,?_,?_,?_,?_⟩ <;>
    norm_num [integral_eq,weight,node,Fin.sum_univ_succ]

theorem absoluteFirst_eq : reference.absoluteFirst=23/45 := by
  norm_num [Reference.absoluteFirst,integral_eq,weight,node,Fin.sum_univ_succ]

theorem absoluteLegendre_eq : reference.absoluteLegendre=14/45 := by
  norm_num [Reference.absoluteLegendre,integral_eq,weight,node,Fin.sum_univ_succ,legendre]

theorem parameterBudget_eq (da db : ℝ) :
    reference.parameterBudget da db=(23*da+14*db)/90 := by
  rw [Reference.parameterBudget,absoluteFirst_eq,absoluteLegendre_eq]
  ring

theorem final_rectangle_budget : reference.parameterBudget (53/1000) (87/1000)=2437/90000 := by
  rw [parameterBudget_eq]
  norm_num

end FiveNode

namespace Uniform

theorem reference : Reference UniformIntervalMoments.measure where
  probability := UniformIntervalMoments.measure_isProbability
  support := PolynomialGram.uniform_ae_interval
  first := by simpa [UniformIntervalMoments.moment] using UniformIntervalMoments.moment_one
  second := UniformIntervalMoments.moment_two
  third := by
    change UniformIntervalMoments.moment 3=0
    norm_num [UniformIntervalMoments.moment_formula]
  fourth := by
    change UniformIntervalMoments.moment 4=1/5
    norm_num [UniformIntervalMoments.moment_formula]

theorem absoluteFirst_eq : reference.absoluteFirst=1/2 := by
  rw [Reference.absoluteFirst,UniformIntervalMoments.integral_eq]
  have hsplit := intervalIntegral.integral_add_adjacent_intervals (μ:=volume)
    (continuous_abs.intervalIntegrable (-1) 0) (continuous_abs.intervalIntegrable 0 1)
  have hn : (∫ u : ℝ in (-1)..0,|u|)=∫ u : ℝ in (-1)..0,-u := by
    apply intervalIntegral.integral_congr
    intro u hu
    rw [Set.uIcc_of_le (by norm_num : (-1:ℝ)≤0)] at hu
    exact abs_of_nonpos hu.2
  have hp : (∫ u : ℝ in 0..1,|u|)=∫ u : ℝ in 0..1,u := by
    apply intervalIntegral.integral_congr
    intro u hu
    rw [Set.uIcc_of_le (by norm_num : (0:ℝ)≤1)] at hu
    exact abs_of_nonneg hu.1
  rw [← hsplit,hn,hp,intervalIntegral.integral_neg]
  norm_num

private theorem integral_legendre (a b : ℝ) :
    (∫ u in a..b,legendre u)=((b^3-b)-(a^3-a))/2 := by
  have hp : IntervalIntegrable (fun u : ℝ => 3*u^2) volume a b :=
    (show Continuous (fun u : ℝ => 3*u^2) by fun_prop).intervalIntegrable a b
  have hc : IntervalIntegrable (fun _ : ℝ => (1:ℝ)) volume a b :=
    continuous_const.intervalIntegrable a b
  simp only [legendre]
  rw [intervalIntegral.integral_div,intervalIntegral.integral_sub hp hc,
    intervalIntegral.integral_const_mul]
  norm_num
  ring

theorem absoluteLegendre_eq : reference.absoluteLegendre=2/(3*Real.sqrt 3) := by
  let q : ℝ := 1/Real.sqrt 3
  have hs : 0<Real.sqrt 3 := Real.sqrt_pos.2 (by norm_num)
  have hs2 : (Real.sqrt 3)^2=3 := Real.sq_sqrt (by norm_num)
  have hq : 0<q := by dsimp [q];positivity
  have hq2 : q^2=1/3 := by dsimp [q];rw [div_pow,hs2];norm_num
  have hq1 : q≤1 := by nlinarith
  have hq3 : q^3=q/3 := by rw [pow_succ,hq2];ring
  have hneg : (∫ u in (-1:ℝ)..(-q),|legendre u|)=∫ u in (-1:ℝ)..(-q),legendre u := by
    apply intervalIntegral.integral_congr
    intro u hu
    rw [Set.uIcc_of_le (by linarith : (-1:ℝ)≤-q)] at hu
    apply abs_of_nonneg
    dsimp [legendre]
    have : q^2≤u^2 := by nlinarith [sq_nonneg (u+q),hu.2]
    nlinarith
  have hmid : (∫ u in (-q)..q,|legendre u|)=∫ u in (-q)..q,-legendre u := by
    apply intervalIntegral.integral_congr
    intro u hu
    rw [Set.uIcc_of_le (by linarith : -q≤q)] at hu
    apply abs_of_nonpos
    dsimp [legendre]
    have : u^2≤q^2 := by nlinarith [mul_nonneg (by linarith [hu.2] : 0≤q-u) (by linarith [hu.1] : 0≤q+u)]
    nlinarith
  have hpos : (∫ u in q..(1:ℝ),|legendre u|)=∫ u in q..(1:ℝ),legendre u := by
    apply intervalIntegral.integral_congr
    intro u hu
    rw [Set.uIcc_of_le hq1] at hu
    apply abs_of_nonneg
    dsimp [legendre]
    have : q^2≤u^2 := by nlinarith [sq_nonneg (u-q),hu.1]
    nlinarith
  have hc : Continuous (fun u => |legendre u|) := by unfold legendre;fun_prop
  have hleft := intervalIntegral.integral_add_adjacent_intervals (μ:=volume)
    (hc.intervalIntegrable (-1) (-q)) (hc.intervalIntegrable (-q) q)
  have hright := intervalIntegral.integral_add_adjacent_intervals (μ:=volume)
    (hc.intervalIntegrable (-1) q) (hc.intervalIntegrable q 1)
  rw [Reference.absoluteLegendre,UniformIntervalMoments.integral_eq,← hright,← hleft,
    hneg,hmid,hpos,intervalIntegral.integral_neg,integral_legendre,integral_legendre,integral_legendre]
  rw [show (-q)^3= -(q^3) by ring]
  norm_num
  rw [hq3]
  dsimp [q]
  field_simp
  ring

end Uniform

end
end Komorebi.LSM.CurvedMoment
