module
public import Euler.ResidualError
@[expose] public section
noncomputable section
namespace Komorebi.Euler
open PowerSeries

/-- At terminal index zero the actual normalized residual is a unit at every dyadic argument. -/
theorem eulerNormalizedResidual_norm_one_of_terminal_zero (r : ℕ) (hr : 0<r)
    (hj : residualTerminalIndex r=0) (x : D) :
    ‖reval (eulerNormalizedResidual r hr) x‖=1 := by
  have hl := eulerNormalizedResidual_lastOdd r hr
  rw [hj] at hl
  have hc : ∀ n, res (coeff n (eulerNormalizedResidual r hr))=
      (1:Polynomial F₂).coeff n := by
    intro n
    rw [res_eq_red,Polynomial.coeff_one]
    rcases Nat.eq_zero_or_pos n with rfl | hn
    · simpa using hl.1
    · rw [ite_eq_right (by omega)]
      exact hl.2 n hn
  have hv := reval_residue_polynomial (eulerNormalizedResidual_restricted r hr) 1
    (1:Polynomial F₂) hc x
  have he : res (reval (eulerNormalizedResidual r hr) x)=1 := by simpa using hv
  exact res_nonzero_norm_one _ (by rw [he]; decide)

lemma residualTerminalIndex_zero_of_sparse (r : ℕ) (hs : binaryDigitSum r≤3) :
    residualTerminalIndex r=0 := by
  have h := residualTerminalIndex_bound r
  omega

lemma residualCarryMinimum_zero_of_terminal_zero (r : ℕ) (hj : residualTerminalIndex r=0) :
    residualCarryMinimum r=0 := by
  have h := residualTerminalIndex_cost r
  rw [hj,residualCarryCost_zero] at h
  exact h.symm

/-- A first end-to-end exact row law from the constructed G_r, with no residual valuation left. -/
theorem signedEuler_error_sparse_norm (r N : ℕ) (hr : 0<r) (hN : r≤N)
    (hs : binaryDigitSum r≤3) :
    ‖signedEulerEven N-reconstructionTrunc (r-1) N‖=
      (2:ℝ)^(-(4*(r:ℤ)-1))*‖(N.choose r:ℚ_[2])‖ := by
  have hj := residualTerminalIndex_zero_of_sparse r hs
  rw [signedEuler_error_normalized_norm r N hr hN,
    eulerNormalizedResidual_norm_one_of_terminal_zero r hr hj,
    residualCarryMinimum_zero_of_terminal_zero r hj,add_zero,mul_one]

/-- At terminal index one the full actual normalized series has a complete affine certificate. -/
lemma eulerNormalizedResidual_affine_certificate (r : ℕ) (hr : 0<r)
    (hj : residualTerminalIndex r=1) (n : ℕ) :
    res (coeff n (eulerNormalizedResidual r hr))=
      (Polynomial.X+Polynomial.C (res (coeff 0 (eulerNormalizedResidual r hr))):Polynomial F₂).coeff n := by
  have hl := eulerNormalizedResidual_lastOdd r hr
  rw [hj] at hl
  rw [res_eq_red,Polynomial.coeff_add,Polynomial.coeff_X,Polynomial.coeff_C]
  rcases n with _ | n
  · simp [res_eq_red]
  · rcases n with _ | n
    · simpa using hl.1
    · rw [ite_eq_right (by omega),ite_eq_right (by omega),add_zero]
      exact hl.2 _ (by omega)

/-- A genuine simple root of the Euler-defined infinite residual, not an arbitrary polynomial model. -/
theorem eulerNormalizedResidual_one_simple_root (r : ℕ) (hr : 0<r)
    (hj : residualTerminalIndex r=1) :
    ∃ α:D, reval (eulerNormalizedResidual r hr) α=0 ∧
      deriv (qeval (eulerNormalizedResidual r hr)) (α:ℚ_[2])≠0 ∧
      ∀ x:D, reval (eulerNormalizedResidual r hr) x=0 ↔ x=α := by
  let f := eulerNormalizedResidual r hr
  let p : Polynomial F₂ := Polynomial.X+Polynomial.C (res (coeff 0 f))
  have hp : ∀ n, res (coeff n f)=p.coeff n := eulerNormalizedResidual_affine_certificate r hr hj
  let a : D := -coeff 0 f
  have hval : p.eval (res a)=0 := by
    simp only [p,a,Polynomial.eval_add,Polynomial.eval_X,Polynomial.eval_C,map_neg,neg_add_cancel]
  have hd (z:F₂) : p.derivative.eval z≠0 := by simp [p]
  obtain ⟨α,ha,har,hda,hu⟩ := restricted_hensel_simple_residue
    (eulerNormalizedResidual_restricted r hr) p hp a hval (hd _)
  refine ⟨α,ha,hda,?_⟩
  intro x
  constructor
  · intro hx
    apply hu x hx
    have hv := reval_residue_polynomial (eulerNormalizedResidual_restricted r hr) 1 p hp x
    rw [hx,map_zero] at hv
    have he : res x=-res (coeff 0 f) := by
      have : res x+res (coeff 0 f)=0 := by simpa [p] using hv.symm
      exact eq_neg_of_add_eq_zero_left this
    simpa only [a,map_neg] using he
  · rintro rfl
    exact ha

end Komorebi.Euler
