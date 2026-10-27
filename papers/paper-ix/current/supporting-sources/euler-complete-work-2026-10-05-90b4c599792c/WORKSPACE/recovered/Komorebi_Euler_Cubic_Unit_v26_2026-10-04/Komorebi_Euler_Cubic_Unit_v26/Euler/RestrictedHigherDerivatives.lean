module
public import Euler.RestrictedJets
public import Euler.SourceTranslation
public import Mathlib.Analysis.Calculus.Deriv.Mul
public import Mathlib.Analysis.Calculus.IteratedDeriv.Defs
public import Mathlib.RingTheory.PowerSeries.Derivative
@[expose] public section
noncomputable section
namespace Komorebi.Euler
open PowerSeries Filter
open scoped Topology

/-- The integral disc is a neighborhood of each of its points in Q_2. -/
lemma eventually_integral_near (x : D) :
    ∀ᶠ y : ℚ_[2] in 𝓝 (x:ℚ_[2]), ‖y‖≤1 := by
  filter_upwards [Metric.ball_mem_nhds (x:ℚ_[2]) (by norm_num : (0:ℝ)<1)] with y hy
  have hd : ‖y-(x:ℚ_[2])‖<1 := by
    simpa only [Metric.mem_ball,dist_eq_norm] using hy
  calc
    ‖y‖=‖(y-(x:ℚ_[2]))+(x:ℚ_[2])‖ := by rw [sub_add_cancel]
    _ ≤ max ‖y-(x:ℚ_[2])‖ ‖(x:ℚ_[2])‖ := IsUltrametricDist.norm_add_le_max _ _
    _ ≤ 1 := max_le hd.le x.2

lemma eventuallyEq_of_eq_on_dyadic {f g : ℚ_[2] → ℚ_[2]}
    (h : ∀ x : D, f (x:ℚ_[2])=g (x:ℚ_[2])) (x : D) :
    f =ᶠ[𝓝 (x:ℚ_[2])] g := by
  filter_upwards [eventually_integral_near x] with y hy
  exact h ⟨y,hy⟩

/-- All ordinary analytic derivatives equal factorial times the evaluated Hasse jet.
This is proved locally on Q_2, not by a real/complex uniform-derivative theorem. -/
theorem iteratedDeriv_scaled_qeval {f : Series} (hf : Restricted f)
    (c : ℚ_[2]) (k : ℕ) (x : D) :
    iteratedDeriv k (fun y : ℚ_[2] => c*qeval f y) (x:ℚ_[2]) =
      c*(k.factorial:ℚ_[2])*(rjet k f x:ℚ_[2]) := by
  induction k generalizing x with
  | zero =>
    simp only [iteratedDeriv_zero,Nat.factorial_zero,Nat.cast_one,mul_one,rjet_zero]
    rw [coe_reval hf]
  | succ k ih =>
    have he : iteratedDeriv k (fun y : ℚ_[2] => c*qeval f y) =ᶠ[𝓝 (x:ℚ_[2])]
        (fun y : ℚ_[2] => (c*(k.factorial:ℚ_[2]))*qeval (hasseSeries k f) y) := by
      apply eventuallyEq_of_eq_on_dyadic
      intro z
      rw [ih,← coe_reval (restricted_hasseSeries hf k) z]
      rfl
    have hd := ((hasDerivAt_qeval (restricted_hasseSeries hf k) x).const_mul
      (c*(k.factorial:ℚ_[2]))).congr_of_eventuallyEq he
    rw [iteratedDeriv_succ,hd.deriv,rjet_one_hasseSeries hf]
    push_cast
    rw [Nat.factorial_succ]
    push_cast
    ring

theorem iteratedDeriv_qeval {f : Series} (hf : Restricted f) (k : ℕ) (x : D) :
    iteratedDeriv k (qeval f) (x:ℚ_[2])=
      (k.factorial:ℚ_[2])*(rjet k f x:ℚ_[2]) := by
  simpa only [one_mul] using iteratedDeriv_scaled_qeval hf 1 k x

/-- Each member of the jet tower really is differentiable. -/
theorem hasDerivAt_iteratedDeriv_qeval {f : Series} (hf : Restricted f)
    (k : ℕ) (x : D) :
    HasDerivAt (iteratedDeriv k (qeval f))
      (((k+1).factorial:ℚ_[2])*(rjet (k+1) f x:ℚ_[2])) (x:ℚ_[2]) := by
  have he : iteratedDeriv k (qeval f) =ᶠ[𝓝 (x:ℚ_[2])]
      (fun y : ℚ_[2] => (k.factorial:ℚ_[2])*qeval (hasseSeries k f) y) := by
    apply eventuallyEq_of_eq_on_dyadic
    intro z
    rw [iteratedDeriv_qeval hf,← coe_reval (restricted_hasseSeries hf k) z]
    rfl
  have hd := ((hasDerivAt_qeval (restricted_hasseSeries hf k) x).const_mul
    (k.factorial:ℚ_[2])).congr_of_eventuallyEq he
  rw [rjet_one_hasseSeries hf] at hd
  convert hd using 1 <;> first | rfl | (push_cast; rw [Nat.factorial_succ]; push_cast; ring)

lemma hasseSeries_one_eq_derivative (f : Series) : hasseSeries 1 f=d⁄dX D f := by
  ext n
  simp only [coeff_hasseSeries,coeff_derivative,Nat.choose_one_right,Nat.cast_add,Nat.cast_one]
  ring

lemma rjet_one_mul {f g : Series} (hf : Restricted f) (hg : Restricted g) (x : D) :
    rjet 1 (f*g) x=rjet 1 f x*reval g x+reval f x*rjet 1 g x := by
  have h : hasseSeries 1 (f*g)=hasseSeries 1 f*g+f*hasseSeries 1 g := by
    simp only [hasseSeries_one_eq_derivative,Derivation.leibniz,smul_eq_mul]
    ring
  unfold rjet
  rw [h,reval_add
    (PowerSeries.isRestricted.mul 1 (restricted_hasseSeries hf 1) hg)
    (PowerSeries.isRestricted.mul 1 hf (restricted_hasseSeries hg 1)),
    reval_mul (restricted_hasseSeries hf 1) hg,
    reval_mul hf (restricted_hasseSeries hg 1)]

end Komorebi.Euler
