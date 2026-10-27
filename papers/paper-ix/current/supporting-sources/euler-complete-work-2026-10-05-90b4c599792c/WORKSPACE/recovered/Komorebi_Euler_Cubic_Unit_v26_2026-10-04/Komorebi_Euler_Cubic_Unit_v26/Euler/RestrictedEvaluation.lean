module
public import Euler.HenselLifting
public import Mathlib.RingTheory.PowerSeries.Restricted
public import Mathlib.Topology.Algebra.InfiniteSum.Nonarchimedean
public import Mathlib.Analysis.Normed.Group.Ultra
public import Mathlib.Topology.Instances.ZMod
public import Mathlib.Analysis.Calculus.Deriv.Pow
@[expose] public section
noncomputable section
namespace Komorebi.Euler
open Filter PowerSeries
open scoped Topology

/-- Genuine restrictedness on the closed dyadic unit disc. -/
abbrev Restricted (f : PowerSeries D) : Prop := PowerSeries.IsRestricted 1 f

lemma restricted_iff (f : PowerSeries D) :
    Restricted f ↔ Tendsto (fun n => ‖coeff n f‖) atTop (𝓝 0) := by
  simp only [Restricted, PowerSeries.isRestricted_iff', one_pow, mul_one]

/-- A restricted coefficient sequence remains summable after arbitrary integral weights. -/
lemma summable_weighted {f : PowerSeries D} (hf : Restricted f) (w : ℕ → D) :
    Summable (fun n => coeff n f * w n) := by
  apply NonarchimedeanAddGroup.summable_of_tendsto_cofinite_zero
  rw [Nat.cofinite_eq_atTop, tendsto_zero_iff_norm_tendsto_zero]
  apply squeeze_zero (g := fun n => ‖coeff n f‖) (fun n => norm_nonneg _)
  · intro n
    rw [norm_mul]
    exact mul_le_of_le_one_right (norm_nonneg _) (PadicInt.norm_le_one _)
  · exact (restricted_iff f).mp hf

/-- Evaluation is the actual convergent sum in the complete ring of dyadic integers. -/
def reval (f : PowerSeries D) (x : D) : D := ∑' n, coeff n f * x^n

lemma summable_reval {f : PowerSeries D} (hf : Restricted f) (x : D) :
    Summable (fun n => coeff n f * x^n) := summable_weighted hf _

lemma hasSum_reval {f : PowerSeries D} (hf : Restricted f) (x : D) :
    HasSum (fun n => coeff n f * x^n) (reval f x) := (summable_reval hf x).hasSum

lemma reval_add {f g : PowerSeries D} (hf : Restricted f) (hg : Restricted g) (x : D) :
    reval (f+g) x = reval f x+reval g x := by
  simp only [reval, map_add, add_mul]
  exact (summable_reval hf x).tsum_add (summable_reval hg x)

lemma reval_sub {f g : PowerSeries D} (hf : Restricted f) (hg : Restricted g) (x : D) :
    reval (f-g) x = reval f x-reval g x := by
  simp only [reval, map_sub, sub_mul]
  exact (summable_reval hf x).tsum_sub (summable_reval hg x)

/-- Hasse coefficient series: its evaluation gives the kth Taylor coefficient. -/
def hasseSeries (k : ℕ) (f : PowerSeries D) : PowerSeries D :=
  PowerSeries.mk fun n => (Nat.choose (n+k) k : D) * coeff (n+k) f

@[simp] lemma coeff_hasseSeries (k n : ℕ) (f : PowerSeries D) :
    coeff n (hasseSeries k f) = (Nat.choose (n+k) k : D)*coeff (n+k) f := by
  simp [hasseSeries]

lemma restricted_hasseSeries {f : PowerSeries D} (hf : Restricted f) (k : ℕ) :
    Restricted (hasseSeries k f) := by
  rw [restricted_iff]
  apply squeeze_zero (g := fun n => ‖coeff (n+k) f‖) (fun n => norm_nonneg _)
  · intro n
    rw [coeff_hasseSeries, norm_mul]
    exact mul_le_of_le_one_left (norm_nonneg _) (PadicInt.norm_le_one _)
  · exact ((restricted_iff f).mp hf).comp (tendsto_add_atTop_nat k)

/-- Evaluated Hasse jet, with the full infinite coefficient tail retained. -/
def rjet (k : ℕ) (f : PowerSeries D) (x : D) : D := reval (hasseSeries k f) x

@[simp] lemma hasseSeries_zero (f : PowerSeries D) : hasseSeries 0 f=f := by
  ext n
  simp

@[simp] lemma rjet_zero (f : PowerSeries D) (x : D) : rjet 0 f x=reval f x := by
  simp [rjet]

/-- Actual reduction modulo an arbitrary power of two. -/
abbrev redPow (k : ℕ) : D →+* ZMod (2^k) := PadicInt.toZModPow k

lemma redPow_zero_iff_norm (k : ℕ) (x : D) :
    redPow k x=0 ↔ ‖x‖ ≤ (2:ℝ)^(-(k:ℤ)) := by
  rw [← RingHom.mem_ker, PadicInt.ker_toZModPow,
    ← PadicInt.norm_le_pow_iff_mem_span_pow]
  norm_num

lemma redPow_eq_of_norm_sub_le (k : ℕ) {x y : D}
    (h : ‖x-y‖ ≤ (2:ℝ)^(-(k:ℤ))) : redPow k x=redPow k y := by
  have hz := (redPow_zero_iff_norm k (x-y)).mpr h
  simpa only [map_sub, sub_eq_zero] using hz

/-- The residue map is locally constant, hence continuous. -/
lemma continuous_redPow (k : ℕ) : Continuous (redPow k) := by
  rw [continuous_iff_continuousAt]
  intro x
  have hpos : (0:ℝ)<(2:ℝ)^(-(k:ℤ)) := zpow_pos (by norm_num) _
  have he : ∀ᶠ y in 𝓝 x, redPow k y=redPow k x := by
    filter_upwards [Metric.ball_mem_nhds x hpos] with y hy
    exact redPow_eq_of_norm_sub_le k (le_of_lt (by simpa only [Metric.mem_ball, dist_eq_norm] using hy))
  exact continuousAt_const.congr_of_eventuallyEq he

/-- Reduction of a convergent evaluation is the sum of its reduced coefficients. -/
lemma hasSum_redPow_reval {f : PowerSeries D} (hf : Restricted f) (k : ℕ) (x : D) :
    HasSum (fun n => redPow k (coeff n f)*(redPow k x)^n) (redPow k (reval f x)) := by
  have h := (hasSum_reval hf x).map (redPow k) (continuous_redPow k)
  simpa only [Function.comp_def, map_mul, map_pow] using h

/-- Any coefficientwise polynomial certificate transfers to the actual infinite evaluation. -/
theorem reval_residue_polynomial {f : PowerSeries D} (hf : Restricted f)
    (k : ℕ) (p : Polynomial (ZMod (2^k)))
    (hc : ∀ n, redPow k (coeff n f)=p.coeff n) (x : D) :
    redPow k (reval f x)=p.eval (redPow k x) := by
  have h := hasSum_redPow_reval hf k x
  simp_rw [hc] at h
  have hp : HasSum (fun n => p.coeff n*(redPow k x)^n) (p.eval (redPow k x)) := by
    classical
    have hs : HasSum (fun n => p.coeff n*(redPow k x)^n)
        (∑ n ∈ p.support, p.coeff n*(redPow k x)^n) := by
      apply hasSum_sum_of_ne_finset_zero
      intro n hn
      simp only [Polynomial.mem_support_iff, not_not] at hn
      simp [hn]
    simpa only [Polynomial.eval, Polynomial.eval₂, Polynomial.sum, RingHom.id_apply] using hs
  exact h.unique hp


/-- Every evaluated Hasse jet respects a coefficientwise finite residue certificate. -/
theorem rjet_residue_polynomial {f : PowerSeries D} (hf : Restricted f)
    (k : ℕ) (p : Polynomial (ZMod (2^k)))
    (hc : ∀ n, redPow k (coeff n f)=p.coeff n) (d : ℕ) (x : D) :
    redPow k (rjet d f x)=(Polynomial.hasseDeriv d p).eval (redPow k x) := by
  apply reval_residue_polynomial (restricted_hasseSeries hf d)
  intro n
  simp only [coeff_hasseSeries, map_mul, map_natCast, hc, Polynomial.hasseDeriv_coeff]

/-- Soundness for root-free certificates of genuine restricted series. -/
theorem restricted_rootfree_of_residue {f : PowerSeries D} (hf : Restricted f)
    (k : ℕ) (p : Polynomial (ZMod (2^k)))
    (hc : ∀ n, redPow k (coeff n f)=p.coeff n)
    (hp : ∀ y, p.eval y ≠ 0) : ∀ x, reval f x ≠ 0 := by
  intro x hx
  apply hp (redPow k x)
  rw [← reval_residue_polynomial hf k p hc x, hx, map_zero]

/-- Simultaneous Hasse-jet nonvanishing transfers to the infinite series. -/
theorem restricted_no_jet_zero_of_residue {f : PowerSeries D} (hf : Restricted f)
    (k m : ℕ) (p : Polynomial (ZMod (2^k)))
    (hc : ∀ n, redPow k (coeff n f)=p.coeff n)
    (hp : ∀ y, ¬ ∀ d : Fin m, (Polynomial.hasseDeriv d.val p).eval y=0) :
    ∀ x, ¬ ∀ d : Fin m, rjet d.val f x=0 := by
  intro x hx
  apply hp (redPow k x)
  intro d
  rw [← rjet_residue_polynomial hf k p hc d.val x, hx d, map_zero]

end Komorebi.Euler
