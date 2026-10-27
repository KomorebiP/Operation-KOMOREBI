/-
Copyright (c) 2026 Komorebi P. All rights reserved.
Authors: Komorebi P.
-/
import KomorebiPaperIV.CanonicalPartialFractions
import KomorebiPaperIV.AnalyticCycles

namespace Komorebi.PaperIV
open Set Filter
open scoped Topology
noncomputable section

/-- An actual analytic logarithm on a stated domain. -/
def IsLogarithmOn (f L : ℂ → ℂ) (s : Set ℂ) : Prop :=
  DifferentiableOn ℂ L s ∧ ∀ z ∈ s, Complex.exp (L z) = f z

/-- Reciprocal powers using one fixed logarithm on the whole domain. -/
def logarithmPower (L : ℂ → ℂ) (r : ℂ) (z : ℂ) : ℂ :=
  Complex.exp (-r * L z)

theorem logarithmPower_add (L : ℂ → ℂ) (r t z : ℂ) :
    logarithmPower L r z * logarithmPower L t z = logarithmPower L (r + t) z := by
  unfold logarithmPower
  rw [← Complex.exp_add]
  congr 1
  ring

theorem IsLogarithmOn.nonzero {f L : ℂ → ℂ} {s : Set ℂ}
    (hL : IsLogarithmOn f L s) {z : ℂ} (hz : z ∈ s) : f z ≠ 0 := by
  rw [← hL.2 z hz]
  exact Complex.exp_ne_zero _

theorem IsLogarithmOn.deriv {f L : ℂ → ℂ} {s : Set ℂ}
    (hs : IsOpen s) (hL : IsLogarithmOn f L s) {z : ℂ} (hz : z ∈ s) :
    deriv L z = logDeriv f z := by
  have hd := (hL.1 z hz).differentiableAt (hs.mem_nhds hz)
  have he : (fun w => Complex.exp (L w)) =ᶠ[𝓝 z] f :=
    eventually_of_mem (hs.mem_nhds hz) (fun w hw => hL.2 w hw)
  have h := he.deriv_eq
  rw [hd.hasDerivAt.cexp.deriv, hL.2 z hz] at h
  rw [logDeriv_apply]
  apply (eq_div_iff (hL.nonzero hz)).mpr
  simpa [mul_comm] using h

theorem hasDerivAt_logarithmPower {f L : ℂ → ℂ} {s : Set ℂ}
    (hs : IsOpen s) (hL : IsLogarithmOn f L s) (r : ℂ) {z : ℂ} (hz : z ∈ s) :
    HasDerivAt (logarithmPower L r)
      (r * (-logDeriv f z) * logarithmPower L r z) z := by
  change HasDerivAt (fun w => Complex.exp (-r * L w))
    (r * (-logDeriv f z) * Complex.exp (-r * L z)) z
  have hd := (hL.1 z hz).differentiableAt (hs.mem_nhds hz)
  have h := (hd.hasDerivAt.const_mul (-r)).cexp
  rw [hL.deriv hs hz] at h
  simpa only [logarithmPower, neg_mul, mul_neg, mul_assoc, mul_left_comm, mul_comm] using h

theorem reciprocal_fixed_log_derivative {N : ℕ} {L : ℂ → ℂ} {s : Set ℂ}
    (hs : IsOpen s) (hL : IsLogarithmOn (canonicalSignedDenominator N) L s)
    (r : ℂ) {z : ℂ} (hz : z ∈ s) :
    deriv (logarithmPower L r) z =
      r * analyticTransferTangent N z * logarithmPower L r z :=
  (hasDerivAt_logarithmPower hs hL r hz).deriv

/-- Evaluation of the complete differential Bell polynomial on successive
derivatives of a function. Its defining recurrence is Y_(n+1)=Y_n'+gY_n. -/
def analyticDifferentialBell (g : ℂ → ℂ) : ℕ → ℂ → ℂ
  | 0 => fun _ => 1
  | n + 1 => fun z => deriv (analyticDifferentialBell g n) z + g z * analyticDifferentialBell g n z

theorem analyticOnNhd_differentialBell {g : ℂ → ℂ} {s : Set ℂ}
    (hg : AnalyticOnNhd ℂ g s) (n : ℕ) : AnalyticOnNhd ℂ (analyticDifferentialBell g n) s := by
  induction n with
  | zero => intro z _; exact analyticAt_const
  | succ n ih => exact ih.deriv.add (hg.mul ih)

theorem iteratedDeriv_eq_analyticDifferentialBell {f g : ℂ → ℂ} {s : Set ℂ}
    (hs : IsOpen s) (hf : AnalyticOnNhd ℂ f s) (hg : AnalyticOnNhd ℂ g s)
    (hfg : ∀ z ∈ s, deriv f z = g z * f z) (n : ℕ) :
    ∀ z ∈ s, iteratedDeriv n f z = analyticDifferentialBell g n z * f z := by
  induction n with
  | zero => intro z _; simp [analyticDifferentialBell]
  | succ n ih =>
    intro z hz
    have he : iteratedDeriv n f =ᶠ[𝓝 z]
        (fun w => analyticDifferentialBell g n w * f w) :=
      eventually_of_mem (hs.mem_nhds hz) (fun w hw => ih w hw)
    rw [iteratedDeriv_succ, he.deriv_eq,
      ((analyticOnNhd_differentialBell hg n z hz).differentiableAt.hasDerivAt.fun_mul
        (hf z hz).differentiableAt.hasDerivAt).deriv,
      hfg z hz]
    simp only [analyticDifferentialBell]
    ring

theorem analytic_higher_riccati {N : ℕ} (hN : 0 < N) {z : ℂ}
    (hz : canonicalSignedDenominator N z ≠ 0) :
    analyticDifferentialBell (fun w => -analyticTransferTangent N w) N z = -1 := by
  let f := canonicalSignedDenominator N
  let s := {w : ℂ | f w ≠ 0}
  have hf : Differentiable ℂ f := fun w =>
    (analyticAt_entireSigned N 0 (canonicalPrimitiveRoot N) (canonicalSignedRoot N) w).differentiableAt
  have hs : IsOpen s := isOpen_ne_fun hf.continuous continuous_const
  have hg : AnalyticOnNhd ℂ (fun w => -analyticTransferTangent N w) s := by
    intro w hw
    change AnalyticAt ℂ (fun w => -(-logDeriv f w)) w
    simp only [neg_neg, logDeriv_apply]
    have hfa := hf.analyticAt w
    have hfd := hfa.deriv
    exact hfd.fun_div hfa (show f w ≠ 0 from hw)
  have hfg : ∀ w ∈ s, deriv f w = (-analyticTransferTangent N w) * f w := by
    intro w hw
    change deriv f w = -(-logDeriv f w) * f w
    simp only [neg_neg, logDeriv_apply]
    exact (div_mul_cancel₀ _ hw).symm
  have he := iteratedDeriv_eq_analyticDifferentialBell hs (fun w _ => hf.analyticAt w) hg hfg N z hz
  have hode := entireSigned_ode (canonicalPrimitiveRoot_isPrimitive hN) (canonicalSignedRoot_pow hN) 0 z
  change deriv^[N] f z = -f z at hode
  rw [iteratedDeriv_eq_iterate, hode] at he
  apply mul_right_cancel₀ hz
  calc
    _ = -f z := he.symm
    _ = _ := by ring

end
end Komorebi.PaperIV
