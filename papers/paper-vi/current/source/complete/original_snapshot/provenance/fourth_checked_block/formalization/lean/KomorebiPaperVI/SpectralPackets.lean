import KomorebiPaperVI.Semigroups
import Mathlib.Analysis.SpecialFunctions.Pow.Real

/-! Author: Komorebi P. Finite spectral resolution, including the actual exponential bridge. -/
namespace KomorebiPaperVI.SpectralPackets
open scoped BigOperators
variable {I R : Type*} [Fintype I] [DecidableEq I] [NormedRing R] [NormedAlgebra ℝ R] [CompleteSpace R]

noncomputable def resolve (P : I → R) (c : I → ℝ) : R := ∑ i, c i • P i

omit [CompleteSpace R] in
theorem resolve_mul (P : I → R) (h : ∀ i j, P i*P j=if i=j then P i else 0)
    (c d : I → ℝ) : resolve P c*resolve P d=resolve P (fun i => c i*d i) := by
  classical
  simp only [resolve,Finset.sum_mul,Finset.mul_sum,smul_mul_smul_comm,h]
  simp [smul_ite]

omit [CompleteSpace R] in
theorem resolve_left_packet (P : I → R) (h : ∀ i j, P i*P j=if i=j then P i else 0)
    (c : I → ℝ) (j : I) : P j*resolve P c=c j • P j := by
  classical
  simp [resolve,Finset.mul_sum,Algebra.mul_smul_comm,h,smul_ite]

omit [CompleteSpace R] in
theorem resolve_right_packet (P : I → R) (h : ∀ i j, P i*P j=if i=j then P i else 0)
    (c : I → ℝ) (j : I) : resolve P c*P j=c j • P j := by
  classical
  simp [resolve,Finset.sum_mul,Algebra.smul_mul_assoc,h,smul_ite]

noncomputable def resolutionHom (P : I → R) (hP : ∑ i, P i=1)
    (h : ∀ i j, P i*P j=if i=j then P i else 0) : (I → ℝ) →+* R where
  toFun := resolve P
  map_zero' := by simp [resolve]
  map_one' := by simpa [resolve] using hP
  map_add' c d := by simp [resolve,add_smul,Finset.sum_add_distrib]
  map_mul' c d := (resolve_mul P h c d).symm

omit [CompleteSpace R] in
theorem exp_resolution (P : I → R) (hP : ∑ i, P i=1)
    (h : ∀ i j, P i*P j=if i=j then P i else 0) (c : I → ℝ) :
    NormedSpace.exp (resolve P c)=resolve P (fun i => Real.exp (c i)) := by
  let : NormedAlgebra ℚ R := NormedAlgebra.restrictScalars ℚ ℝ R
  have hc : Continuous (resolutionHom P hP h) := by
    change Continuous (resolve P)
    unfold resolve
    fun_prop
  have he := NormedSpace.map_exp (resolutionHom P hP h) hc c
  change resolve P (NormedSpace.exp c)=NormedSpace.exp (resolve P c) at he
  simpa only [Pi.exp_def,← Real.exp_eq_exp_ℝ] using he.symm

noncomputable def fractional (P : I → R) (lam : I → ℝ) (a : ℝ) : R :=
  resolve P (fun i => (lam i)^a)

noncomputable def spectralTransfer (P : I → R) (lam : I → ℝ) (a t : ℝ) : R :=
  resolve P (fun i => Real.exp (-t*(lam i)^a))

omit [CompleteSpace R] in
theorem fractional_add (P : I → R) (h : ∀ i j, P i*P j=if i=j then P i else 0)
    (lam : I → ℝ) (hl : ∀ i, 0 ≤ lam i) (a b : ℝ) (ha : 0 < a) (hb : 0 < b) :
    fractional P lam a*fractional P lam b=fractional P lam (a+b) := by
  unfold fractional
  rw [resolve_mul P h]
  congr 1
  funext i
  exact (Real.rpow_add' (hl i) (add_pos ha hb).ne').symm

omit [CompleteSpace R] in
theorem spectral_transfer_exponential (P : I → R) (hP : ∑ i, P i=1)
    (h : ∀ i j, P i*P j=if i=j then P i else 0) (lam : I → ℝ) (a t : ℝ) :
    NormedSpace.exp ((-t) • fractional P lam a)=spectralTransfer P lam a t := by
  have hs : (-t) • fractional P lam a=resolve P (fun i => -t*(lam i)^a) := by
    simp [fractional,resolve,Finset.smul_sum,smul_smul]
  rw [hs,exp_resolution P hP h]
  rfl

omit [CompleteSpace R] in
theorem spectral_transfer_add (P : I → R) (h : ∀ i j, P i*P j=if i=j then P i else 0)
    (lam : I → ℝ) (a s t : ℝ) :
    spectralTransfer P lam a s*spectralTransfer P lam a t=spectralTransfer P lam a (s+t) := by
  unfold spectralTransfer
  rw [resolve_mul P h]
  congr 1
  funext i
  rw [← Real.exp_add]
  congr 1
  ring

omit [CompleteSpace R] in
theorem fractional_reduces (P : I → R) (h : ∀ i j, P i*P j=if i=j then P i else 0)
    (lam : I → ℝ) (a : ℝ) (j : I) :
    P j*fractional P lam a=(lam j)^a • P j ∧
      fractional P lam a*P j=(lam j)^a • P j :=
  ⟨resolve_left_packet P h _ j,resolve_right_packet P h _ j⟩

omit [CompleteSpace R] in
theorem spectral_transfer_reduces (P : I → R) (h : ∀ i j, P i*P j=if i=j then P i else 0)
    (lam : I → ℝ) (a t : ℝ) (j : I) :
    P j*spectralTransfer P lam a t=Real.exp (-t*(lam j)^a) • P j ∧
      spectralTransfer P lam a t*P j=Real.exp (-t*(lam j)^a) • P j :=
  ⟨resolve_left_packet P h _ j,resolve_right_packet P h _ j⟩

end KomorebiPaperVI.SpectralPackets
