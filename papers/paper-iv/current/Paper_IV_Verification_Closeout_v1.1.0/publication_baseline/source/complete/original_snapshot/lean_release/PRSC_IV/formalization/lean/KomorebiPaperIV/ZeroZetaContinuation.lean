/-
Copyright (c) 2026 Komorebi P. All rights reserved.
Authors: Komorebi P.
-/
import KomorebiPaperIV.ZeroZetaDecomposition

namespace Komorebi.PaperIV
noncomputable section
open Set Filter
open scoped Topology

def reducedZetaCorrection {N : ℕ} (hN : 2 ≤ N) (s : ℂ) : ℂ :=
  let e := canonicalZeroEnumeration hN
  e.reducedExceptionZeta (by omega) s + e.latticeCorrection ((N : ℂ) * s) -
    e.latticePrefix ((N : ℂ) * s)

def absoluteZetaCorrection {N : ℕ} (hN : 2 ≤ N) (s : ℂ) : ℂ :=
  let e := canonicalZeroEnumeration hN
  e.absoluteExceptionZeta (by omega) s + (N : ℂ) * e.latticeCorrection s -
    (N : ℂ) * e.latticePrefix s

theorem reducedZetaCorrection_entire {N : ℕ} (hN : 2 ≤ N) :
    Differentiable ℂ (reducedZetaCorrection hN) := by
  unfold reducedZetaCorrection
  exact ((canonicalZeroEnumeration hN).reducedExceptionZeta_entire (by omega)).add
    (((canonicalZeroEnumeration hN).latticeCorrection_entire hN).comp (by fun_prop)) |>.sub
      (((canonicalZeroEnumeration hN).latticePrefix_entire).comp (by fun_prop))

theorem absoluteZetaCorrection_entire {N : ℕ} (hN : 2 ≤ N) :
    Differentiable ℂ (absoluteZetaCorrection hN) := by
  unfold absoluteZetaCorrection
  exact ((canonicalZeroEnumeration hN).absoluteExceptionZeta_entire (by omega)).add
    (((canonicalZeroEnumeration hN).latticeCorrection_entire hN).const_mul _) |>.sub
      (((canonicalZeroEnumeration hN).latticePrefix_entire).const_mul _)

/-- The manuscript's reduced formula, with its entire correction constructed
from the proved zero enumeration and actual exceptional zeros. -/
theorem entireReducedDenominator_zeta_eq_hurwitz {N : ℕ} (hN : 2 ≤ N)
    {s : ℂ} (hs : 1 / (N : ℝ) < s.re) :
    absoluteZeroZeta (entireReducedDenominator N) s =
      hurwitzLatticeModel (Real.pi / Real.sin (Real.pi / N)) N s + reducedZetaCorrection hN s := by
  let e := canonicalZeroEnumeration hN
  have hsN : 1 < ((N : ℂ) * s).re := by
    simp only [Complex.mul_re, Complex.natCast_re, Complex.natCast_im, zero_mul, sub_zero]
    exact (div_lt_iff₀ (by exact_mod_cast (show 0 < N by omega) : (0 : ℝ) < N)).mp hs |>.trans_eq (mul_comm _ _)
  rw [e.reducedZeta_decomposition hN hs, e.root_zeta_eq_model hN hsN]
  simp only [hurwitzLatticeModel, Nat.cast_one, one_mul, reducedZetaCorrection]
  dsimp [e]
  ring

theorem canonicalSignedDenominator_zeta_eq_hurwitz {N : ℕ} (hN : 2 ≤ N)
    {s : ℂ} (hs : 1 < s.re) :
    absoluteZeroZeta (canonicalSignedDenominator N) s =
      (N : ℂ) * hurwitzLatticeModel (Real.pi / Real.sin (Real.pi / N)) 1 s +
        absoluteZetaCorrection hN s := by
  let e := canonicalZeroEnumeration hN
  rw [e.absoluteZeta_decomposition hN hs, e.root_zeta_eq_model hN hs]
  dsimp [absoluteZetaCorrection, e]
  ring

def reducedZetaContinuation {N : ℕ} (hN : 2 ≤ N) (s : ℂ) : ℂ :=
  hurwitzLatticeModel (Real.pi / Real.sin (Real.pi / N)) N s + reducedZetaCorrection hN s

def absoluteZetaContinuation {N : ℕ} (hN : 2 ≤ N) (s : ℂ) : ℂ :=
  (N : ℂ) * hurwitzLatticeModel (Real.pi / Real.sin (Real.pi / N)) 1 s + absoluteZetaCorrection hN s

theorem reducedZetaContinuation_meromorphic {N : ℕ} (hN : 2 ≤ N) (s : ℂ) :
    MeromorphicAt (reducedZetaContinuation hN) s :=
  (hurwitzLatticeModel_meromorphicAt _ _ s).add
    ((reducedZetaCorrection_entire hN).analyticAt s).meromorphicAt

theorem absoluteZetaContinuation_meromorphic {N : ℕ} (hN : 2 ≤ N) (s : ℂ) :
    MeromorphicAt (absoluteZetaContinuation hN) s :=
  ((MeromorphicAt.const (N : ℂ) s).mul (hurwitzLatticeModel_meromorphicAt _ _ s)).add
    ((absoluteZetaCorrection_entire hN).analyticAt s).meromorphicAt

theorem reducedZetaContinuation_holomorphic_off_pole {N : ℕ} (hN : 2 ≤ N)
    {s : ℂ} (hs : s ≠ 1 / (N : ℂ)) : DifferentiableAt ℂ (reducedZetaContinuation hN) s :=
  (hurwitzLatticeModel_differentiableAt (by omega) hs).add (reducedZetaCorrection_entire hN s)

theorem absoluteZetaContinuation_holomorphic_off_pole {N : ℕ} (hN : 2 ≤ N)
    {s : ℂ} (hs : s ≠ 1) : DifferentiableAt ℂ (absoluteZetaContinuation hN) s := by
  have h : s ≠ 1 / ((1 : ℕ) : ℂ) := by simpa using hs
  exact ((hurwitzLatticeModel_differentiableAt (by norm_num : 0 < (1 : ℕ)) h).const_mul _).add
    (absoluteZetaCorrection_entire hN s)

theorem entire_add_preserves_residue {f Q : ℂ → ℂ} {p r : ℂ}
    (hQ : Differentiable ℂ Q)
    (h : Tendsto (fun s => (s - p) * f s) (𝓝[≠] p) (𝓝 r)) :
    Tendsto (fun s => (s - p) * (f s + Q s)) (𝓝[≠] p) (𝓝 r) := by
  have ht : Tendsto (fun s => (s - p) * Q s) (𝓝[≠] p) (𝓝 0) := by
    simpa only [sub_self, zero_mul] using
      ((show Continuous (fun s => (s - p) * Q s) from (continuous_id.sub continuous_const).mul hQ.continuous).tendsto p).mono_left nhdsWithin_le_nhds
  simpa only [mul_add, add_zero] using h.add ht

theorem reducedZetaContinuation_residue {N : ℕ} (hN : 2 ≤ N) :
    Tendsto (fun s : ℂ => (s - 1 / (N : ℂ)) * reducedZetaContinuation hN s)
      (𝓝[≠] (1 / (N : ℂ))) (𝓝 ((Real.sin (Real.pi / N) / (N * Real.pi) : ℝ) : ℂ)) := by
  have h := entire_add_preserves_residue (reducedZetaCorrection_entire hN)
    (hurwitzLatticeModel_residue (div_pos Real.pi_pos (signed_sine_pos hN)) (show 0 < N by omega))
  convert h using 1
  congr 1
  push_cast
  field_simp

theorem absoluteZetaContinuation_residue {N : ℕ} (hN : 2 ≤ N) :
    Tendsto (fun s : ℂ => (s - 1) * absoluteZetaContinuation hN s)
      (𝓝[≠] 1) (𝓝 ((N * Real.sin (Real.pi / N) / Real.pi : ℝ) : ℂ)) := by
  have h := (hurwitzLatticeModel_residue (div_pos Real.pi_pos (signed_sine_pos hN))
    (show 0 < (1 : ℕ) by norm_num)).const_mul (N : ℂ)
  simp only [Nat.cast_one, one_div_one, one_mul] at h
  have h' : Tendsto (fun s : ℂ => (s - 1) *
      ((N : ℂ) * hurwitzLatticeModel (Real.pi / Real.sin (Real.pi / N)) 1 s))
      (𝓝[≠] 1) (𝓝 ((N * Real.sin (Real.pi / N) / Real.pi : ℝ) : ℂ)) := by
    convert h using 1
    · funext s; ring
    · congr 1; push_cast; field_simp
  exact entire_add_preserves_residue (absoluteZetaCorrection_entire hN) h'

theorem reducedZetaContinuation_simple_pole {N : ℕ} (hN : 2 ≤ N) :
    meromorphicOrderAt (reducedZetaContinuation hN) (1 / (N : ℂ)) = (-1 : ℤ) := by
  apply meromorphicOrderAt_eq_neg_one_of_residue (reducedZetaContinuation_meromorphic hN _)
    (fun s hs => reducedZetaContinuation_holomorphic_off_pole hN hs) _ (reducedZetaContinuation_residue hN)
  apply Complex.ofReal_ne_zero.mpr
  exact ne_of_gt (div_pos (signed_sine_pos hN) (mul_pos (by exact_mod_cast (show 0 < N by omega)) Real.pi_pos))

theorem absoluteZetaContinuation_simple_pole {N : ℕ} (hN : 2 ≤ N) :
    meromorphicOrderAt (absoluteZetaContinuation hN) 1 = (-1 : ℤ) := by
  apply meromorphicOrderAt_eq_neg_one_of_residue (absoluteZetaContinuation_meromorphic hN _)
    (fun s hs => absoluteZetaContinuation_holomorphic_off_pole hN hs) _ (absoluteZetaContinuation_residue hN)
  apply Complex.ofReal_ne_zero.mpr
  exact ne_of_gt (div_pos (mul_pos (by exact_mod_cast (show 0 < N by omega)) (signed_sine_pos hN)) Real.pi_pos)

end
end Komorebi.PaperIV
