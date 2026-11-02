import CoupledUniqueness
import Mathlib.Analysis.Analytic.OfScalars

/-! # Recovering labeled scale parameters from canonical analytic germs

The coefficients use the ordinary odd series, not exponential generating series.
The comparison with Mathlib's formal multilinear series inserts zero even terms.
-/

set_option autoImplicit false
set_option maxHeartbeats 1000000

noncomputable section

open Filter
open scoped Topology

namespace Komorebi.SpecialFunctions.Coupled.Scales

def denseOdd (c : ℕ → ℝ) (k : ℕ) : ℂ :=
  if k % 2 = 1 then (c (k / 2) : ℂ) else 0

theorem denseOdd_odd (c : ℕ → ℝ) (n : ℕ) :
    denseOdd c (2 * n + 1) = (c n : ℂ) := by
  have hm : (2 * n + 1) % 2 = 1 := by omega
  have hd : (2 * n + 1) / 2 = n := by omega
  simp [denseOdd, hm, hd]

theorem denseOdd_even (c : ℕ → ℝ) (n : ℕ) :
    denseOdd c (2 * n) = 0 := by
  have hm : (2 * n) % 2 = 0 := by omega
  simp [denseOdd, hm]

theorem odd_hasSum_dense {c : ℕ → ℝ} {z w : ℂ}
    (h : HasSum (fun n => (c n : ℂ) * z ^ (2 * n + 1)) w) :
    HasSum (fun k => denseOdd c k * z ^ k) w := by
  have hi : Function.Injective (fun n : ℕ => 2 * n + 1) := by
    intro a b hab
    change 2 * a + 1 = 2 * b + 1 at hab
    omega
  apply (hi.hasSum_iff (f := fun k => denseOdd c k * z ^ k) ?_).mp
  · simpa only [Function.comp_def, denseOdd_odd] using h
  · intro k hk
    have hm : k % 2 ≠ 1 := by
      intro hm
      apply hk
      refine ⟨k / 2, ?_⟩
      change 2 * (k / 2) + 1 = k
      omega
    simp [denseOdd, hm]

theorem odd_series_hasFPowerSeriesAt {c : ℕ → ℝ} {f : ℂ → ℂ}
    (h : ∀ᶠ z in 𝓝 (0 : ℂ),
      HasSum (fun n => (c n : ℂ) * z ^ (2 * n + 1)) (f z)) :
    HasFPowerSeriesAt f (FormalMultilinearSeries.ofScalars ℂ (denseOdd c)) 0 := by
  apply hasFPowerSeriesAt_iff.mpr
  filter_upwards [h] with z hz
  simpa only [FormalMultilinearSeries.coeff_ofScalars, zero_add, smul_eq_mul,
    mul_comm] using odd_hasSum_dense hz

theorem odd_coefficients_eq_of_germ_eq {c d : ℕ → ℝ} {f g : ℂ → ℂ}
    (hc : ∀ᶠ z in 𝓝 (0 : ℂ),
      HasSum (fun n => (c n : ℂ) * z ^ (2 * n + 1)) (f z))
    (hd : ∀ᶠ z in 𝓝 (0 : ℂ),
      HasSum (fun n => (d n : ℂ) * z ^ (2 * n + 1)) (g z))
    (hfg : f =ᶠ[𝓝 0] g) : c = d := by
  have hp := (odd_series_hasFPowerSeriesAt hc).eq_formalMultilinearSeries_of_eventually
    (odd_series_hasFPowerSeriesAt hd) hfg
  funext n
  have hn := congrArg (fun p : FormalMultilinearSeries ℂ ℂ ℂ => p.coeff (2 * n + 1)) hp
  simpa only [FormalMultilinearSeries.coeff_ofScalars, denseOdd_odd,
    Complex.ofReal_inj] using hn

theorem odd_series_Taylor_coefficients {c : ℕ → ℝ} {f : ℂ → ℂ}
    {p : FormalMultilinearSeries ℂ ℂ ℂ} (hp : HasFPowerSeriesAt f p 0)
    (hc : ∀ᶠ z in 𝓝 (0 : ℂ),
      HasSum (fun n => (c n : ℂ) * z ^ (2 * n + 1)) (f z)) (k : ℕ) :
    p.coeff k = denseOdd c k := by
  have he := hp.eq_formalMultilinearSeries (odd_series_hasFPowerSeriesAt hc)
  simpa only [FormalMultilinearSeries.coeff_ofScalars] using
    congrArg (fun q : FormalMultilinearSeries ℂ ℂ ℂ => q.coeff k) he

theorem coupled_hasFPowerSeriesAt (s : Scales) (hs : s.positive)
    (hstrict : s.q < 1 ∧ s.r < 1 ∧ s.a < 1 ∧ s.b < 1) :
    HasFPowerSeriesAt s.U
      (FormalMultilinearSeries.ofScalars ℂ (denseOdd (fun n => (s.coefficients n).1))) 0 ∧
    HasFPowerSeriesAt s.V
      (FormalMultilinearSeries.ofScalars ℂ (denseOdd (fun n => (s.coefficients n).2))) 0 := by
  exact ⟨odd_series_hasFPowerSeriesAt (Eventually.of_forall fun z =>
      (s.coefficient_series_entire hs hstrict z).1.of_norm.hasSum),
    odd_series_hasFPowerSeriesAt (Eventually.of_forall fun z =>
      (s.coefficient_series_entire hs hstrict z).2.of_norm.hasSum)⟩

theorem coefficients_eq_of_analytic_germs {s t : Scales}
    (hs : s.positive) (ht : t.positive)
    (hstricts : s.q < 1 ∧ s.r < 1 ∧ s.a < 1 ∧ s.b < 1)
    (hstrictt : t.q < 1 ∧ t.r < 1 ∧ t.a < 1 ∧ t.b < 1)
    (hU : s.U =ᶠ[𝓝 0] t.U) (hV : s.V =ᶠ[𝓝 0] t.V) :
    s.coefficients = t.coefficients := by
  have h1 := odd_coefficients_eq_of_germ_eq
    (Eventually.of_forall fun z => (s.coefficient_series_entire hs hstricts z).1.of_norm.hasSum)
    (Eventually.of_forall fun z => (t.coefficient_series_entire ht hstrictt z).1.of_norm.hasSum) hU
  have h2 := odd_coefficients_eq_of_germ_eq
    (Eventually.of_forall fun z => (s.coefficient_series_entire hs hstricts z).2.of_norm.hasSum)
    (Eventually.of_forall fun z => (t.coefficient_series_entire ht hstrictt z).2.of_norm.hasSum) hV
  funext n
  exact Prod.ext (congrFun h1 n) (congrFun h2 n)

theorem sameJet_of_analytic_germs {s t : Scales}
    (hs : s.positive) (ht : t.positive)
    (hstricts : s.q < 1 ∧ s.r < 1 ∧ s.a < 1 ∧ s.b < 1)
    (hstrictt : t.q < 1 ∧ t.r < 1 ∧ t.a < 1 ∧ t.b < 1)
    (hU : s.U =ᶠ[𝓝 0] t.U) (hV : s.V =ᶠ[𝓝 0] t.V) : s.sameJet t := by
  apply sameJet_of_coefficients_eq
  intro n _ _
  exact congrFun (coefficients_eq_of_analytic_germs hs ht hstricts hstrictt hU hV) n

/-- The guarded analytic-germ parameter-recovery implication of Theorem G.2. -/
theorem parameters_of_analytic_germs {s t : Scales}
    (hs : s.positive) (ht : t.positive)
    (hstricts : s.q < 1 ∧ s.r < 1 ∧ s.a < 1 ∧ s.b < 1)
    (hstrictt : t.q < 1 ∧ t.r < 1 ∧ t.a < 1 ∧ t.b < 1)
    (hD : s.defect ≠ 0)
    (hU : s.U =ᶠ[𝓝 0] t.U) (hV : s.V =ᶠ[𝓝 0] t.V) : s = t :=
  parameters_of_formal_pair_eq hs ht hD
    (coefficients_eq_of_analytic_germs hs ht hstricts hstrictt hU hV)

theorem parameters_of_entire_pair_eq {s t : Scales}
    (hs : s.positive) (ht : t.positive)
    (hstricts : s.q < 1 ∧ s.r < 1 ∧ s.a < 1 ∧ s.b < 1)
    (hstrictt : t.q < 1 ∧ t.r < 1 ∧ t.a < 1 ∧ t.b < 1)
    (hD : s.defect ≠ 0) (hU : s.U = t.U) (hV : s.V = t.V) : s = t :=
  parameters_of_analytic_germs hs ht hstricts hstrictt hD
    (Eventually.of_forall fun z => congrFun hU z)
    (Eventually.of_forall fun z => congrFun hV z)

theorem analytic_solution_Taylor_coefficients (s : Scales) (hs : s.positive)
    (hstrict : s.q < 1 ∧ s.r < 1 ∧ s.a < 1 ∧ s.b < 1)
    {f g : ℂ → ℂ} {p q : FormalMultilinearSeries ℂ ℂ ℂ}
    (hp : HasFPowerSeriesAt f p 0) (hq : HasFPowerSeriesAt g q 0)
    (hzero : f 0 = 0 ∧ g 0 = 0) (heq : s.GermEquations f g) (k : ℕ) :
    p.coeff k = denseOdd (fun n => (s.coefficients n).1) k ∧
    q.coeff k = denseOdd (fun n => (s.coefficients n).2) k := by
  have hc := s.analytic_solution_hasSum hs hstrict hp.analyticAt hq.analyticAt hzero heq
  exact ⟨odd_series_Taylor_coefficients hp (hc.mono fun _ hz => hz.1) k,
    odd_series_Taylor_coefficients hq (hc.mono fun _ hz => hz.2) k⟩

theorem parameters_of_shared_solution_germ {s t : Scales}
    (hs : s.positive) (ht : t.positive)
    (hstricts : s.q < 1 ∧ s.r < 1 ∧ s.a < 1 ∧ s.b < 1)
    (hstrictt : t.q < 1 ∧ t.r < 1 ∧ t.a < 1 ∧ t.b < 1)
    (hD : s.defect ≠ 0) {f g : ℂ → ℂ}
    (hf : AnalyticAt ℂ f 0) (hg : AnalyticAt ℂ g 0)
    (hzero : f 0 = 0 ∧ g 0 = 0)
    (heqs : s.GermEquations f g) (heqt : t.GermEquations f g) : s = t := by
  have hsc := s.analytic_solution_germ_eq hs hstricts hf hg hzero heqs
  have htc := t.analytic_solution_germ_eq ht hstrictt hf hg hzero heqt
  exact parameters_of_analytic_germs hs ht hstricts hstrictt hD
    (hsc.1.symm.trans htc.1) (hsc.2.symm.trans htc.2)

end Komorebi.SpecialFunctions.Coupled.Scales
