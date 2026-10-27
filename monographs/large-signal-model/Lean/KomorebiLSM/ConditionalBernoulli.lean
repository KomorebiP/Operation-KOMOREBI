import Mathlib.Probability.Moments.SubGaussian
import Mathlib.Probability.Distributions.Bernoulli
import Mathlib.Analysis.Convex.SpecificFunctions.Basic
import Mathlib.Tactic

/-! Scalar exponential bounds used for a conditional Hoeffding argument.
The auxiliary Bernoulli measure is explicit and finite; no conditional law on
the sample space is assumed. -/
set_option autoImplicit false
namespace Komorebi.LSM.ConditionalBernoulli
open MeasureTheory ProbabilityTheory Real

/-- The secant bound for the exponential holds for either sign of θ. -/
theorem exp_secant (θ x : ℝ) (hx : x∈Set.Icc (0:ℝ) 1) :
    exp (θ*x)≤(1-x)+x*exp θ := by
  have h := convexOn_exp.2 (Set.mem_univ (0:ℝ)) (Set.mem_univ θ)
    (sub_nonneg.mpr hx.2) hx.1 (by ring : (1-x)+x=1)
  have he : (1-x) • (0:ℝ)+x • θ=θ*x := by simp [smul_eq_mul,mul_comm]
  rw [he] at h
  simpa only [smul_eq_mul,exp_zero,mul_one] using h

/-- The exact centered Bernoulli exponential envelope, proved from the
ordinary Hoeffding theorem on an actual two-point probability measure. -/
theorem centered_bernoulli_bound (θ p : ℝ) (hp : p∈Set.Icc (0:ℝ) 1) :
    exp (-θ*p)*((1-p)+p*exp θ)≤exp (θ^2/8) := by
  let ν : Measure Bool := bernoulliMeasure true false ⟨p,hp⟩
  let X : Bool → ℝ := fun b => if b then 1 else 0
  have hX : Measurable X := measurable_of_countable X
  have hb : ∀ᵐ b∂ν,X b∈Set.Icc (0:ℝ) 1 := by
    exact Filter.Eventually.of_forall (fun b => by cases b <;> norm_num [X])
  have hm : (∫ b,X b∂ν)=p := by
    change (∫ b,X b∂bernoulliMeasure true false ⟨p,hp⟩)=p
    rw [integral_bernoulliMeasure]
    simp [X,smul_eq_mul]
  have hs := (hasSubgaussianMGF_of_mem_Icc (μ := ν) hX.aemeasurable hb).mgf_le θ
  rw [hm] at hs
  have hformula : mgf (fun b => X b-p) ν θ=
      p*exp (θ*(1-p))+(1-p)*exp (θ*(0-p)) := by
    change (∫ b,exp (θ*(X b-p))∂bernoulliMeasure true false ⟨p,hp⟩)=_
    rw [integral_bernoulliMeasure]
    simp [X,smul_eq_mul]
  rw [hformula] at hs
  have hconst : (((‖(1:ℝ)-0‖₊/2)^2 : NNReal):ℝ)=(1:ℝ)/4 := by norm_num
  have hparam : (1/4:ℝ)*θ^2/2=θ^2/8 := by ring
  rw [hconst,hparam] at hs
  calc
    _ = p*exp (θ*(1-p))+(1-p)*exp (θ*(0-p)) := by
      rw [show θ*(1-p)=θ+(-θ*p) by ring,exp_add,
        show θ*(0-p)=-θ*p by ring]
      ring
    _ ≤ _ := hs

end Komorebi.LSM.ConditionalBernoulli
