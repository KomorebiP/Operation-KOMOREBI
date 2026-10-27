/-
Copyright (c) 2026 Komorebi P. All rights reserved.
Authors: Komorebi P.
-/
import KomorebiPaperIV.ZeroZetaContinuation
import KomorebiPaperIV.BranchedDirichlet

namespace Komorebi.PaperIV
noncomputable section
open Set Filter
open scoped Topology

/-- A chosen logarithm at each distinct zero, with the actual multiplicity. -/
def branchedZeroZetaTerm (f : ℂ → ℂ) (L : {z : ℂ // f z = 0} → ℂ)
    (z : {z : ℂ // f z = 0}) (s : ℂ) : ℂ :=
  (analyticOrderNatAt f z : ℂ) * Complex.exp (-s * L z)

def branchedZeroZeta (f : ℂ → ℂ) (L : {z : ℂ // f z = 0} → ℂ) (s : ℂ) : ℂ :=
  ∑' z, branchedZeroZetaTerm f L z s

theorem branchedZeroZetaTerm_entire (f : ℂ → ℂ) (L : {z : ℂ // f z = 0} → ℂ)
    (z : {z : ℂ // f z = 0}) : Differentiable ℂ (branchedZeroZetaTerm f L z) := by
  unfold branchedZeroZetaTerm
  fun_prop

/-- This support condition allows every logarithm choice on the finite exceptional
set, and requires the real logarithm on the proved positive tail. The results
below hold for arbitrary exceptional values, hence in particular for logarithms. -/
def RealLogOnReducedTail {N : ℕ} (hN : 2 ≤ N)
    (L : {z : ℂ // entireReducedDenominator N z = 0} → ℂ) : Prop :=
  ∀ m, L ((canonicalZeroEnumeration hN).reducedZero (by omega) m) =
    (Real.log ‖((canonicalZeroEnumeration hN).reducedRoot m)‖ : ℂ)

def reducedBranchCorrection {N : ℕ} (hN : 2 ≤ N)
    (L : {z : ℂ // entireReducedDenominator N z = 0} → ℂ) (s : ℂ) : ℂ :=
  ∑' z : ↥((range ((canonicalZeroEnumeration hN).reducedZero (by omega)))ᶜ),
    (branchedZeroZetaTerm (entireReducedDenominator N) L z.val s -
      absoluteZeroZetaTerm (entireReducedDenominator N) z.val s)

theorem reducedBranchCorrection_entire {N : ℕ} (hN : 2 ≤ N)
    (L : {z : ℂ // entireReducedDenominator N z = 0} → ℂ) :
    Differentiable ℂ (reducedBranchCorrection hN L) := by
  unfold reducedBranchCorrection
  exact finite_subtype_tsum_entire ((canonicalZeroEnumeration hN).reducedZero_finite_complement (by omega))
    (fun z s => branchedZeroZetaTerm (entireReducedDenominator N) L z s -
      absoluteZeroZetaTerm (entireReducedDenominator N) z s)
    (fun z => (branchedZeroZetaTerm_entire _ _ z).sub (absoluteZeroZetaTerm_entire _ z))

theorem branchedZeroZetaTerm_eq_absolute_on_tail {N : ℕ} (hN : 2 ≤ N)
    {L : {z : ℂ // entireReducedDenominator N z = 0} → ℂ}
    (hL : RealLogOnReducedTail hN L) (m : ℕ) (s : ℂ) :
    branchedZeroZetaTerm (entireReducedDenominator N) L
      ((canonicalZeroEnumeration hN).reducedZero (by omega) m) s =
    absoluteZeroZetaTerm (entireReducedDenominator N)
      ((canonicalZeroEnumeration hN).reducedZero (by omega) m) s := by
  simp only [branchedZeroZetaTerm, absoluteZeroZetaTerm, weightedDirichletTerm, hL m]
  rfl

theorem branchedReducedZeta_summable {N : ℕ} (hN : 2 ≤ N)
    {L : {z : ℂ // entireReducedDenominator N z = 0} → ℂ}
    (hL : RealLogOnReducedTail hN L) {s : ℂ} (hs : 1 / (N : ℝ) < s.re) :
    Summable (fun z => branchedZeroZetaTerm (entireReducedDenominator N) L z s) := by
  let e := canonicalZeroEnumeration hN
  have hc := e.reducedZero_finite_complement (by omega)
  have ha := ((entireReducedDenominator_zeta_absolute_convergence hN s).mpr hs).of_norm
  have hr : Summable (fun z : range (e.reducedZero (by omega)) =>
      branchedZeroZetaTerm (entireReducedDenominator N) L z.val s) := by
    apply (ha.subtype _).congr
    intro z
    change absoluteZeroZetaTerm (entireReducedDenominator N) z.val s =
      branchedZeroZetaTerm (entireReducedDenominator N) L z.val s
    obtain ⟨m, hm⟩ := z.property
    rw [← hm]
    exact (branchedZeroZetaTerm_eq_absolute_on_tail hN hL m s).symm
  have he := hc.summable_compl_iff (f := fun z => branchedZeroZetaTerm (entireReducedDenominator N) L z s)
  rw [compl_compl] at he
  exact he.mp hr

theorem branchedReducedZeta_eq_absolute_add_entire {N : ℕ} (hN : 2 ≤ N)
    {L : {z : ℂ // entireReducedDenominator N z = 0} → ℂ}
    (hL : RealLogOnReducedTail hN L) {s : ℂ} (hs : 1 / (N : ℝ) < s.re) :
    branchedZeroZeta (entireReducedDenominator N) L s =
      absoluteZeroZeta (entireReducedDenominator N) s + reducedBranchCorrection hN L s := by
  let e := canonicalZeroEnumeration hN
  have ha := ((entireReducedDenominator_zeta_absolute_convergence hN s).mpr hs).of_norm
  have hb := branchedReducedZeta_summable hN hL hs
  have hea := tsum_injection_add_complement (e.reducedZero (by omega)) (e.reducedZero_injective (by omega)) ha
  have heb := tsum_injection_add_complement (e.reducedZero (by omega)) (e.reducedZero_injective (by omega)) hb
  have hc : reducedBranchCorrection hN L s =
      (∑' z : ↥((range (e.reducedZero (by omega)))ᶜ), branchedZeroZetaTerm (entireReducedDenominator N) L z.val s) -
      ∑' z : ↥((range (e.reducedZero (by omega)))ᶜ), absoluteZeroZetaTerm (entireReducedDenominator N) z.val s :=
    (hb.subtype _).tsum_sub (ha.subtype _)
  have htail : (fun m => branchedZeroZetaTerm (entireReducedDenominator N) L (e.reducedZero (by omega) m) s) =
      (fun m => absoluteZeroZetaTerm (entireReducedDenominator N) (e.reducedZero (by omega) m) s) := by
    funext m
    exact branchedZeroZetaTerm_eq_absolute_on_tail hN hL m s
  rw [htail] at heb
  change _ = branchedZeroZeta (entireReducedDenominator N) L s at heb
  change _ = absoluteZeroZeta (entireReducedDenominator N) s at hea
  rw [hc]
  linear_combination hea - heb

def branchedReducedZetaContinuation {N : ℕ} (hN : 2 ≤ N)
    (L : {z : ℂ // entireReducedDenominator N z = 0} → ℂ) (s : ℂ) : ℂ :=
  reducedZetaContinuation hN s + reducedBranchCorrection hN L s

theorem branchedReducedZetaContinuation_eq {N : ℕ} (hN : 2 ≤ N)
    {L : {z : ℂ // entireReducedDenominator N z = 0} → ℂ}
    (hL : RealLogOnReducedTail hN L) {s : ℂ} (hs : 1 / (N : ℝ) < s.re) :
    branchedZeroZeta (entireReducedDenominator N) L s = branchedReducedZetaContinuation hN L s := by
  rw [branchedReducedZeta_eq_absolute_add_entire hN hL hs, entireReducedDenominator_zeta_eq_hurwitz hN hs]
  rfl

theorem branchedReducedZetaContinuation_meromorphic {N : ℕ} (hN : 2 ≤ N)
    (L : {z : ℂ // entireReducedDenominator N z = 0} → ℂ) (s : ℂ) :
    MeromorphicAt (branchedReducedZetaContinuation hN L) s :=
  (reducedZetaContinuation_meromorphic hN s).add
    ((reducedBranchCorrection_entire hN L).analyticAt s).meromorphicAt

theorem branchedReducedZetaContinuation_holomorphic_off_pole {N : ℕ} (hN : 2 ≤ N)
    (L : {z : ℂ // entireReducedDenominator N z = 0} → ℂ) {s : ℂ}
    (hs : s ≠ 1 / (N : ℂ)) : DifferentiableAt ℂ (branchedReducedZetaContinuation hN L) s :=
  (reducedZetaContinuation_holomorphic_off_pole hN hs).add (reducedBranchCorrection_entire hN L s)

theorem branchedReducedZetaContinuation_residue {N : ℕ} (hN : 2 ≤ N)
    (L : {z : ℂ // entireReducedDenominator N z = 0} → ℂ) :
    Tendsto (fun s : ℂ => (s - 1 / (N : ℂ)) * branchedReducedZetaContinuation hN L s)
      (𝓝[≠] (1 / (N : ℂ))) (𝓝 ((Real.sin (Real.pi / N) / (N * Real.pi) : ℝ) : ℂ)) :=
  entire_add_preserves_residue (reducedBranchCorrection_entire hN L) (reducedZetaContinuation_residue hN)

theorem branchedReducedZetaContinuation_simple_pole {N : ℕ} (hN : 2 ≤ N)
    (L : {z : ℂ // entireReducedDenominator N z = 0} → ℂ) :
    meromorphicOrderAt (branchedReducedZetaContinuation hN L) (1 / (N : ℂ)) = (-1 : ℤ) := by
  apply meromorphicOrderAt_eq_neg_one_of_residue (branchedReducedZetaContinuation_meromorphic hN L _)
    (fun s hs => branchedReducedZetaContinuation_holomorphic_off_pole hN L hs) _
    (branchedReducedZetaContinuation_residue hN L)
  apply Complex.ofReal_ne_zero.mpr
  exact ne_of_gt (div_pos (signed_sine_pos hN) (mul_pos (by exact_mod_cast (show 0 < N by omega)) Real.pi_pos))

/-- Any two allowed choices have an entire difference of continuations. -/
theorem branchedReducedZetaContinuation_difference_entire {N : ℕ} (hN : 2 ≤ N)
    (L M : {z : ℂ // entireReducedDenominator N z = 0} → ℂ) :
    Differentiable ℂ (fun s => branchedReducedZetaContinuation hN L s -
      branchedReducedZetaContinuation hN M s) := by
  have he : (fun s => branchedReducedZetaContinuation hN L s - branchedReducedZetaContinuation hN M s) =
      (fun s => reducedBranchCorrection hN L s - reducedBranchCorrection hN M s) := by
    funext s
    unfold branchedReducedZetaContinuation
    ring
  rw [he]
  exact (reducedBranchCorrection_entire hN L).sub (reducedBranchCorrection_entire hN M)

end
end Komorebi.PaperIV
