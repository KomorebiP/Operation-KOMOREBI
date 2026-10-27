module
public import PaperX.ExponentialBoundary
public import Mathlib.Analysis.SpecialFunctions.Complex.LogBounds
public import Mathlib.Analysis.SpecialFunctions.Log.Summable
public import Mathlib.Analysis.Normed.Group.FunctionSeries
public import Mathlib.Analysis.SpecialFunctions.Pow.Continuity
public import Mathlib.Tactic.Positivity
public import Mathlib.Tactic.GCongr

/-! A boundary theorem for complex Euler products with unit-modulus weights.
The logarithmic lift and the absolutely convergent quadratic remainder are
constructed. Continuity, not a derivative estimate, controls the branch. -/
@[expose] public section
noncomputable section
open Filter Set Complex
open scoped Topology
namespace PaperX.EulerLogBoundary
variable {ι : Type*} (N : ι → ℕ) (c : ι → ℂ)

def term (s : ℝ) (i : ι) : ℂ := c i * (N i : ℂ) ^ (-(s : ℂ))
def logTerm (s : ℝ) (i : ι) : ℂ := -Complex.log (1 - term N c s i)
def logSum (s : ℝ) : ℂ := ∑' i, logTerm N c s i
def primeSum (s : ℝ) : ℂ := ∑' i, term N c s i
def remainder (s : ℝ) : ℂ := ∑' i, (logTerm N c s i - term N c s i)
def eulerProduct (s : ℝ) : ℂ := ∏' i, (1 - term N c s i)⁻¹

variable (hN : ∀ i, 2 ≤ N i) (hc : ∀ i, ‖c i‖ = 1)
include hN hc

theorem norm_term (s : ℝ) (i : ι) : ‖term N c s i‖ = (N i : ℝ) ^ (-s) := by
  rw [term, norm_mul, hc, one_mul, Complex.norm_natCast_cpow_of_pos (by have := hN i; omega),
    Complex.neg_re, Complex.ofReal_re]

theorem norm_term_le_inv {s : ℝ} (hs : 1 ≤ s) (i : ι) :
    ‖term N c s i‖ ≤ (N i : ℝ)⁻¹ := by
  rw [norm_term N c hN hc, ← Real.rpow_neg_one]
  exact Real.rpow_le_rpow_of_exponent_le (by exact_mod_cast (hN i).trans' (by omega))
    (neg_le_neg hs)

theorem norm_term_le_half {s : ℝ} (hs : 1 ≤ s) (i : ι) :
    ‖term N c s i‖ ≤ 1 / 2 := by
  refine (norm_term_le_inv N c hN hc hs i).trans ?_
  have hi : (2 : ℝ) ≤ N i := by exact_mod_cast hN i
  calc (N i : ℝ)⁻¹ ≤ (2 : ℝ)⁻¹ := inv_anti₀ (by norm_num) hi
    _ = 1 / 2 := by norm_num

theorem term_slit {s : ℝ} (hs : 1 ≤ s) (i : ι) :
    1 - term N c s i ∈ Complex.slitPlane := by
  apply Complex.mem_slitPlane_iff.mpr
  left
  have ht := norm_term_le_half N c hN hc hs i
  have hre := Complex.re_le_norm (term N c s i)
  simp only [Complex.sub_re, Complex.one_re]
  linarith

theorem norm_logTerm_le {s : ℝ} (hs : 1 ≤ s) (i : ι) :
    ‖logTerm N c s i‖ ≤ 2 * (N i : ℝ) ^ (-s) := by
  have h := Complex.norm_log_one_add_half_le_self
    (z := -term N c s i) (by simpa using norm_term_le_half N c hN hc hs i)
  rw [logTerm, norm_neg]
  calc ‖Complex.log (1 - term N c s i)‖ ≤ (3 / 2) * ‖term N c s i‖ := by
        simpa only [norm_neg, sub_eq_add_neg] using h
    _ ≤ 2 * ‖term N c s i‖ := by nlinarith [norm_nonneg (term N c s i)]
    _ = _ := by rw [norm_term N c hN hc]

omit hc in
theorem term_continuous (i : ι) : Continuous (fun s : ℝ ↦ term N c s i) := by
  have hn : (N i : ℂ) ≠ 0 := by exact_mod_cast (by have := hN i; omega : N i ≠ 0)
  have : NeZero (N i : ℂ) := ⟨hn⟩
  exact continuous_const.mul ((continuous_const_cpow (N i : ℂ)).comp Complex.continuous_ofReal.neg)

theorem logTerm_continuousOn (i : ι) : ContinuousOn (fun s ↦ logTerm N c s i) (Ici 1) :=
  ((continuousOn_const.sub (term_continuous N c hN i).continuousOn).clog
    (fun _ hs ↦ term_slit N c hN hc hs i)).neg

theorem norm_remainder_term_le {s : ℝ} (hs : 1 ≤ s) (i : ι) :
    ‖logTerm N c s i - term N c s i‖ ≤ (N i : ℝ) ^ (-(2 : ℝ)) := by
  let z := term N c s i
  have hz : ‖z‖ ≤ 1 / 2 := norm_term_le_half N c hN hc hs i
  have hi : (1 - ‖z‖)⁻¹ ≤ (2 : ℝ) := by
    rw [inv_le_comm₀ (by linarith) (by norm_num)]; linarith
  have h := Complex.norm_log_one_add_sub_self_le (z := -z) (by simpa using (by linarith : ‖z‖ < 1))
  have ht : ‖logTerm N c s i - term N c s i‖ = ‖Complex.log (1 + -z) - -z‖ := by
    rw [← norm_neg]; congr 1; dsimp [logTerm, z]; ring_nf
  rw [ht]
  calc ‖Complex.log (1 + -z) - -z‖ ≤ ‖z‖ ^ 2 * (1 - ‖z‖)⁻¹ / 2 := by simpa using h
    _ ≤ ‖z‖ ^ 2 := by nlinarith [sq_nonneg ‖z‖]
    _ ≤ ((N i : ℝ)⁻¹) ^ 2 := pow_le_pow_left₀ (norm_nonneg z) (norm_term_le_inv N c hN hc hs i) _
    _ = (N i : ℝ) ^ (-(2 : ℝ)) := by rw [Real.rpow_neg (by positivity), Real.rpow_two, inv_pow]

variable (hsumm : ∀ s : ℝ, 1 < s → Summable (fun i ↦ (N i : ℝ) ^ (-s)))
include hsumm

theorem summable_term {s : ℝ} (hs : 1 < s) : Summable (term N c s) :=
  Summable.of_norm ((hsumm s hs).congr (fun i ↦ (norm_term N c hN hc s i).symm))

theorem summable_logTerm {s : ℝ} (hs : 1 < s) : Summable (logTerm N c s) :=
  Summable.of_norm <| Summable.of_nonneg_of_le (fun _ ↦ norm_nonneg _)
    (norm_logTerm_le N c hN hc hs.le) ((hsumm s hs).mul_left 2)

theorem logSum_continuousOn : ContinuousOn (logSum N c) (Ioi 1) := by
  intro s hs
  obtain ⟨a, ha, has⟩ := exists_between (show (1 : ℝ) < s from hs)
  have hcOn : ContinuousOn (logSum N c) (Ioi a) := by
    apply continuousOn_tsum
      (fun i ↦ (logTerm_continuousOn N c hN hc i).mono (fun _ hx ↦ ha.le.trans hx.le))
      ((hsumm a ha).mul_left 2)
    intro i x hx
    refine (norm_logTerm_le N c hN hc (ha.le.trans hx.le) i).trans ?_
    exact mul_le_mul_of_nonneg_left (Real.rpow_le_rpow_of_exponent_le
      (by have := hN i; exact_mod_cast (by omega : 1 ≤ N i)) (neg_le_neg hx.le)) (by norm_num)
  exact (hcOn.continuousAt (Ioi_mem_nhds has)).continuousWithinAt

theorem remainder_continuousOn : ContinuousOn (remainder N c) (Ici 1) :=
  continuousOn_tsum (fun i ↦ (logTerm_continuousOn N c hN hc i).sub
    (term_continuous N c hN i).continuousOn) (hsumm 2 (by norm_num))
    (fun i _ hs ↦ norm_remainder_term_le N c hN hc hs i)

theorem exp_logSum {s : ℝ} (hs : 1 < s) :
    Complex.exp (logSum N c s) = eulerProduct N c s := by
  have hsum := summable_logTerm N c hN hc hsumm hs
  have hprod := hsum.hasSum.cexp
  have heach : ∀ i, Complex.exp (logTerm N c s i) = (1 - term N c s i)⁻¹ := by
    intro i
    rw [logTerm, Complex.exp_neg, Complex.exp_log (Complex.slitPlane_ne_zero (term_slit N c hN hc hs.le i))]
  exact (hprod.congr_fun (fun i ↦ (heach i).symm)).tprod_eq.symm

theorem primeSum_eq {s : ℝ} (hs : 1 < s) :
    primeSum N c s = logSum N c s - remainder N c s := by
  rw [remainder, (summable_logTerm N c hN hc hsumm hs).tsum_sub
    (summable_term N c hN hc hsumm hs)]
  simp only [primeSum, logSum, sub_sub_cancel]

/-- Finite nonzero Euler-product boundary values construct finite complex
boundary values for the weighted prime sum. All branch control is internal. -/
theorem primeSum_boundary_of_euler_boundary {v : ℂ} (hv : v ≠ 0)
    (hlimit : Tendsto (eulerProduct N c) (𝓝[>] 1) (𝓝 v)) :
    ∃ w : ℂ, Tendsto (primeSum N c) (𝓝[>] 1) (𝓝 w) := by
  have he : Tendsto (fun s ↦ Complex.exp (logSum N c s)) (𝓝[>] 1) (𝓝 v) := by
    apply hlimit.congr'
    filter_upwards [self_mem_nhdsWithin] with s hs
    exact (exp_logSum N c hN hc hsumm hs).symm
  obtain ⟨g, _, hg⟩ := PaperX.ExponentialBoundary.exists_limit_of_exp_limit
    (logSum N c) (logSum_continuousOn N c hN hc hsumm) hv he
  have hr : Tendsto (remainder N c) (𝓝[>] 1) (𝓝 (remainder N c 1)) :=
    ((remainder_continuousOn N c hN hc hsumm) 1 (by simp)).tendsto.mono_left
      (nhdsWithin_mono _ Ioi_subset_Ici_self)
  refine ⟨g - remainder N c 1, ?_⟩
  apply (hg.sub hr).congr'
  filter_upwards [self_mem_nhdsWithin] with s hs
  exact (primeSum_eq N c hN hc hsumm hs).symm

end PaperX.EulerLogBoundary
