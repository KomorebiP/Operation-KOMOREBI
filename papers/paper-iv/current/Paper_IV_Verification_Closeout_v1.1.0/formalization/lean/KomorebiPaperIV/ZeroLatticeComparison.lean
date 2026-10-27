/-
Copyright (c) 2026 Komorebi P. All rights reserved.
Authors: Komorebi P.
-/
import KomorebiPaperIV.ExponentialZetaComparison
import KomorebiPaperIV.HurwitzLattice

namespace Komorebi.PaperIV
noncomputable section
open Set Filter
open scoped Topology

theorem positiveZetaTerm_mul {x y : ℝ} (hx : 0 < x) (hy : 0 < y) (s : ℂ) :
    positiveZetaTerm (x * y) s = positiveZetaTerm x s * positiveZetaTerm y s := by
  simp only [positiveZetaTerm, Real.log_mul hx.ne' hy.ne', Complex.ofReal_add, mul_add,
    Complex.exp_add]

theorem positiveZetaTerm_eq_cpow {x : ℝ} (hx : 0 < x) (s : ℂ) :
    positiveZetaTerm x s = 1 / (x : ℂ) ^ s := by
  rw [one_div, Complex.cpow_def_of_ne_zero (Complex.ofReal_ne_zero.mpr hx.ne'),
    ← Complex.exp_neg, ← Complex.ofReal_log hx.le]
  unfold positiveZetaTerm
  congr 1
  ring

theorem positiveZetaTerm_norm {x : ℝ} (hx : 0 < x) (s : ℂ) :
    ‖positiveZetaTerm x s‖ = 1 / x ^ s.re := by
  simpa only [weightedDirichletTerm, Nat.cast_one, one_mul, positiveZetaTerm] using
    weightedDirichletTerm_norm (fun _ : Unit => 1) (fun _ => x) (fun _ => hx) () s

theorem positiveZetaTerm_lattice_hasSum {A : ℝ} (hA : 0 < A) (s : ℂ) (hs : 1 < s.re) :
    HasSum (fun m : ℕ => positiveZetaTerm (A * ((m : ℝ) + 1 / 2)) s)
      (hurwitzLatticeModel A 1 s) := by
  have h := (HurwitzZeta.hasSum_hurwitzZeta_of_one_lt_re
    (show (1 / 2 : ℝ) ∈ Icc 0 1 by constructor <;> norm_num) hs).mul_left (positiveZetaTerm A s)
  convert! h using 1
  · funext m
    rw [positiveZetaTerm_mul hA (by positivity), positiveZetaTerm_eq_cpow (x := (m : ℝ) + 1 / 2) (by positivity)]
    push_cast
    rfl
  · simp only [hurwitzLatticeModel, Nat.cast_one, one_mul, positiveZetaTerm]

theorem signedZeroCenter_positive {N : ℕ} (hN : 2 ≤ N) (m : ℕ) :
    0 < signedZeroCenter N m := by
  unfold signedZeroCenter
  exact mul_pos (div_pos Real.pi_pos (signed_sine_pos hN)) (by positivity)

theorem signedZeroCenter_reciprocal_square_summable {N : ℕ} (hN : 2 ≤ N) :
    Summable (fun m => 1 / signedZeroCenter N m ^ (2 : ℝ)) := by
  have h := (positiveZetaTerm_lattice_hasSum
    (div_pos Real.pi_pos (signed_sine_pos hN)) (2 : ℂ) (by norm_num)).summable.norm
  change Summable (fun m => ‖positiveZetaTerm (signedZeroCenter N m) (2 : ℂ)‖) at h
  simpa only [positiveZetaTerm_norm (signedZeroCenter_positive hN _), show (2 : ℂ).re = (2 : ℝ) by rfl] using! h

theorem SignedZeroEnumeration.root_tendsto_atTop {N : ℕ} (hN : 2 ≤ N)
    (e : SignedZeroEnumeration N) : Tendsto e.root atTop atTop := by
  exact (e.root_equivalent_lattice hN).symm.tendsto_atTop
    ((tendsto_natCast_atTop_atTop (R := ℝ)).const_mul_atTop
      (div_pos Real.pi_pos (signed_sine_pos hN)))

def SignedZeroEnumeration.latticeCorrection {N : ℕ} (e : SignedZeroEnumeration N) (s : ℂ) : ℂ :=
  ∑' m, exponentialZetaDifference e.root (fun j => signedZeroCenter N (j + e.offset)) m s

theorem SignedZeroEnumeration.latticeCorrection_locally_uniform {N : ℕ} (hN : 2 ≤ N)
    (e : SignedZeroEnumeration N) :
    HasSumLocallyUniformlyOn
      (exponentialZetaDifference e.root (fun j => signedZeroCenter N (j + e.offset)))
      e.latticeCorrection univ := by
  obtain ⟨C, hC, γ, hγ, hdisp⟩ := e.displacement
  apply exponentialZetaDifference_locally_uniform
    (fun m => signedZeroCenter_positive hN _) (e.root_tendsto_atTop hN)
    ((signedZeroCenter_tendsto_atTop hN).comp (tendsto_add_atTop_nat e.offset))
    ((signedZeroCenter_reciprocal_square_summable hN).comp_injective (fun _ _ h => Nat.add_right_cancel h))
    hC hγ
  exact Eventually.of_forall hdisp

theorem SignedZeroEnumeration.latticeCorrection_entire {N : ℕ} (hN : 2 ≤ N)
    (e : SignedZeroEnumeration N) : Differentiable ℂ e.latticeCorrection := by
  apply differentiableOn_univ.mp
  exact (e.latticeCorrection_locally_uniform hN).summableLocallyUniformlyOn.differentiableOn
    isOpen_univ (fun m s _ => exponentialZetaDifference_entire _ _ m s)

theorem SignedZeroEnumeration.positiveZetaTerm_summable {N : ℕ} (hN : 2 ≤ N)
    (e : SignedZeroEnumeration N) {s : ℂ} (hs : 1 < s.re) :
    Summable (fun m => positiveZetaTerm (e.root m) s) := by
  apply Summable.of_norm
  simp only [positiveZetaTerm_norm (e.positive _)]
  exact (e.root_reciprocal_rpow_summable_iff hN _).mpr hs

def SignedZeroEnumeration.latticePrefix {N : ℕ} (e : SignedZeroEnumeration N) (s : ℂ) : ℂ :=
  ∑ m ∈ Finset.range e.offset, positiveZetaTerm (signedZeroCenter N m) s

theorem SignedZeroEnumeration.latticePrefix_entire {N : ℕ} (e : SignedZeroEnumeration N) :
    Differentiable ℂ e.latticePrefix := by
  unfold SignedZeroEnumeration.latticePrefix
  exact Differentiable.fun_sum (fun m _ => positiveZetaTerm_entire _)

/-- Equality with the unshifted Hurwitz model; the finite prefix is retained. -/
theorem SignedZeroEnumeration.root_zeta_eq_model {N : ℕ} (hN : 2 ≤ N)
    (e : SignedZeroEnumeration N) {s : ℂ} (hs : 1 < s.re) :
    (∑' m, positiveZetaTerm (e.root m) s) =
      hurwitzLatticeModel (Real.pi / Real.sin (Real.pi / N)) 1 s +
        e.latticeCorrection s - e.latticePrefix s := by
  have hmodel := positiveZetaTerm_lattice_hasSum
    (div_pos Real.pi_pos (signed_sine_pos hN)) s hs
  have hsum := hmodel.summable
  have htail := hsum.comp_injective (fun _ _ h => Nat.add_right_cancel h :
    Function.Injective (fun m : ℕ => m + e.offset))
  have hc : e.latticeCorrection s = (∑' m, positiveZetaTerm (e.root m) s) -
      ∑' m, positiveZetaTerm (signedZeroCenter N (m + e.offset)) s :=
    (e.positiveZetaTerm_summable hN hs).tsum_sub htail
  have hp := hsum.sum_add_tsum_nat_add e.offset
  rw [hmodel.tsum_eq] at hp
  change e.latticePrefix s + (∑' m, positiveZetaTerm (signedZeroCenter N (m + e.offset)) s) = _ at hp
  rw [hc]
  linear_combination hp

end
end Komorebi.PaperIV
