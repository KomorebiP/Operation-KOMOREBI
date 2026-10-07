/-
Copyright (c) 2026 Komorebi P. All rights reserved.
Authors: Komorebi P.
-/
import KomorebiPaperIV.CanonicalPartialFractions
import Mathlib.Analysis.Calculus.IteratedDeriv.Lemmas

namespace Komorebi.PaperIV
noncomputable section
open Set Filter
open scoped Topology

theorem locally_uniform_sum_deriv {ι : Type*} {F : ι → ℂ → ℂ} {G : ℂ → ℂ} {U : Set ℂ}
    (h : HasSumLocallyUniformlyOn F G U) (hU : IsOpen U)
    (hF : ∀ i, DifferentiableOn ℂ (F i) U) :
    HasSumLocallyUniformlyOn (fun i => deriv (F i)) (deriv G) U := by
  have hh := h.deriv (Eventually.of_forall (fun S => DifferentiableOn.fun_sum (fun i _ => hF i))) hU
  apply hh.congr
  intro S z hz
  exact (deriv_fun_sum (fun i _ => (hF i).differentiableAt (hU.mem_nhds hz)))

def zeroResolventJet (f : ℂ → ℂ) (n : ℕ) (i : ZeroMultiplicityIndex f) (w : ℂ) : ℂ :=
  (n.factorial : ℂ) / (indexedZero i - w) ^ (n + 1)

theorem zeroResolventJet_hasDerivAt {f : ℂ → ℂ} (n : ℕ) (i : ZeroMultiplicityIndex f)
    {w : ℂ} (hw : w ≠ indexedZero i) :
    HasDerivAt (zeroResolventJet f n i) (zeroResolventJet f (n + 1) i w) w := by
  have hd := (hasDerivAt_const w (indexedZero i)).sub (hasDerivAt_id w)
  have hn : indexedZero i - w ≠ 0 := sub_ne_zero.mpr hw.symm
  have h := (hasDerivAt_const w (n.factorial : ℂ)).div (hd.pow (n + 1)) (pow_ne_zero _ hn)
  convert! h using 1
  dsimp only [zeroResolventJet, Pi.pow_apply, Pi.sub_apply, id_eq]
  simp only [Nat.factorial_succ, Nat.cast_mul, Nat.cast_add, Nat.cast_one, Nat.add_sub_cancel]
  field_simp
  ring

theorem zeroResolventJet_locally_uniform {f : ℂ → ℂ} (hf : Differentiable ℂ f)
    (hs : ZeroPowerSummable f 1) (hf0 : f 0 ≠ 0) (n : ℕ) :
    HasSumLocallyUniformlyOn (zeroResolventJet f n)
      (iteratedDeriv n (fun w => ∑' i, zeroPartialFraction f i w)) {w | f w ≠ 0} := by
  have hU : IsOpen {w : ℂ | f w ≠ 0} := isOpen_ne_fun hf.continuous continuous_const
  have hn : ∀ i : ZeroMultiplicityIndex f, ∀ w ∈ {w | f w ≠ 0}, w ≠ indexedZero i := by
    intro i w hw he
    apply hw
    rw [he]
    exact i.1.property
  induction n with
  | zero =>
      have he : zeroResolventJet f 0 = zeroPartialFraction f := by
        funext i w
        simp [zeroResolventJet, zeroPartialFraction]
      rw [he, iteratedDeriv_zero]
      exact (zeroPartialFraction_locally_uniform hs hf0).mono (subset_univ _)
  | succ n ih =>
      have hd := locally_uniform_sum_deriv ih hU (fun i w hw =>
        (zeroResolventJet_hasDerivAt n i (hn i w hw)).differentiableAt.differentiableWithinAt)
      rw [← iteratedDeriv_succ] at hd
      apply hd.congr
      intro S w hw
      apply Finset.sum_congr rfl
      intro i _
      exact (zeroResolventJet_hasDerivAt n i (hn i w hw)).deriv

/-- The zero power sum uses the complete actual zero multiset. -/
def zeroPowerSum (f : ℂ → ℂ) (m : ℕ) : ℂ :=
  ∑' i : ZeroMultiplicityIndex f, 1 / indexedZero i ^ m

theorem zeroPowerSum_hasSum_from_resolvent {f : ℂ → ℂ} (hf : Differentiable ℂ f)
    (hs : ZeroPowerSummable f 1) (hf0 : f 0 ≠ 0) (n : ℕ) :
    HasSum (fun i : ZeroMultiplicityIndex f => (n.factorial : ℂ) / indexedZero i ^ (n + 1))
      (iteratedDeriv n (fun w => ∑' i, zeroPartialFraction f i w) 0) := by
  simpa only [zeroResolventJet, sub_zero] using
    (zeroResolventJet_locally_uniform hf hs hf0 n).hasSum hf0

theorem zeroPowerSum_resolvent_derivative {f : ℂ → ℂ} (hf : Differentiable ℂ f)
    (hs : ZeroPowerSummable f 1) (hf0 : f 0 ≠ 0) (n : ℕ) :
    iteratedDeriv n (fun w => ∑' i, zeroPartialFraction f i w) 0 =
      (n.factorial : ℂ) * zeroPowerSum f (n + 1) := by
  rw [← (zeroPowerSum_hasSum_from_resolvent hf hs hf0 n).tsum_eq, zeroPowerSum, ← tsum_mul_left]
  apply tsum_congr
  intro i
  rw [mul_one_div]

end
end Komorebi.PaperIV
