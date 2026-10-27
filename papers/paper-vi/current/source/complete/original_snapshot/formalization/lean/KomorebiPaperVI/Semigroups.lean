import KomorebiPaperVI.Algebra
import Mathlib.Analysis.SpecialFunctions.Exponential
import Mathlib.Analysis.Calculus.Deriv.Mul
import Mathlib.MeasureTheory.Integral.IntervalIntegral.FundThmCalculus
import Mathlib.Tactic

/-! Author: Komorebi P. Banach-algebra exponentials and rectangular bounded-operator Duhamel. -/
namespace KomorebiPaperVI.Semigroups
open NormedSpace
open scoped Topology

section BanachAlgebra
variable {R : Type*} [NormedRing R] [NormedAlgebra ℝ R] [CompleteSpace R]

noncomputable def transfer (A : R) (t : ℝ) : R := exp (t • A)

omit [CompleteSpace R] in
theorem transfer_zero (A : R) : transfer A 0 = 1 := by simp [transfer]

theorem transfer_add (A : R) (s t : ℝ) : transfer A (s+t) = transfer A s*transfer A t := by
  let : NormedAlgebra ℚ R := NormedAlgebra.restrictScalars ℚ ℝ R
  dsimp [transfer]
  rw [add_smul]
  exact exp_add_of_commute (((Commute.refl A).smul_left s).smul_right t)

theorem transfer_derivative_right (A : R) (t : ℝ) :
    HasDerivAt (transfer A) (transfer A t*A) t := hasDerivAt_exp_smul_const A t

theorem transfer_derivative_left (A : R) (t : ℝ) :
    HasDerivAt (transfer A) (A*transfer A t) t := hasDerivAt_exp_smul_const' A t

@[fun_prop]
theorem transfer_continuous (A : R) : Continuous (transfer A) := by
  exact continuous_iff_continuousAt.mpr fun t => (transfer_derivative_right A t).continuousAt

theorem transfer_intertwining (C A B : R) (h : C*A=B*C) (t : ℝ) :
    C*transfer A t=transfer B t*C := by
  let : NormedAlgebra ℚ R := NormedAlgebra.restrictScalars ℚ ℝ R
  have hs : SemiconjBy C (t • A) (t • B) :=
    (show SemiconjBy C A B from h).smul_right t
  exact hs.exp_right


theorem exponential_packet_convolution {I : Type*} [Fintype I]
    (P : I → R) (hP : ∑ i, P i=1) (hid : ∀ i, P i*P i=P i)
    (A : R) (s t : ℝ) (b a : I) :
    Algebra.block P (transfer A (s+t)) b a =
      ∑ c, Algebra.block P (transfer A s) b c*Algebra.block P (transfer A t) c a :=
  Algebra.packet_semigroup_convolution P hP hid (transfer A) (transfer_add A) s t b a

end BanachAlgebra

section Rectangular
variable {E F : Type*} [NormedAddCommGroup E] [NormedSpace ℝ E] [CompleteSpace E]
    [NormedAddCommGroup F] [NormedSpace ℝ F] [CompleteSpace F]

theorem duhamel_integrand_derivative (A : E →L[ℝ] E) (B : F →L[ℝ] F)
    (C : E →L[ℝ] F) (t r : ℝ) :
    HasDerivAt (fun u => (transfer B (t-u)).comp (C.comp (transfer A u)))
      ((transfer B (t-r)).comp ((C.comp A-B.comp C).comp (transfer A r))) r := by
  have hb : HasDerivAt (fun u => transfer B (t-u)) (-(transfer B (t-r)*B)) r := by
    simpa [Function.comp_def] using (transfer_derivative_right B (t-r)).scomp r
      ((hasDerivAt_const r t).sub (hasDerivAt_id r))
  have hc := (hasDerivAt_const r C).clm_comp (transfer_derivative_left A r)
  convert hb.clm_comp hc using 1
  ext x
  simp [mul_apply_eq_comp, ContinuousLinearMap.comp_apply]
  abel

theorem duhamel_rectangular (A : E →L[ℝ] E) (B : F →L[ℝ] F)
    (C : E →L[ℝ] F) (t : ℝ) :
    C.comp (transfer A t)-(transfer B t).comp C =
      ∫ r in 0..t, (transfer B (t-r)).comp ((C.comp A-B.comp C).comp (transfer A r)) := by
  have hc : Continuous (fun r => (transfer B (t-r)).comp
      ((C.comp A-B.comp C).comp (transfer A r))) := by
    fun_prop
  have h := intervalIntegral.integral_eq_sub_of_hasDerivAt
    (fun r _ => duhamel_integrand_derivative A B C t r) (hc.intervalIntegrable 0 t)
  simpa [transfer_zero, ContinuousLinearMap.one_def] using h.symm

theorem exact_rectangular_intertwining (A : E →L[ℝ] E) (B : F →L[ℝ] F)
    (C : E →L[ℝ] F) (h : C.comp A=B.comp C) (t : ℝ) :
    C.comp (transfer A t)=(transfer B t).comp C := by
  have hd := duhamel_rectangular A B C t
  simp only [h, sub_self, ContinuousLinearMap.zero_comp, ContinuousLinearMap.comp_zero,
    intervalIntegral.integral_zero] at hd
  exact sub_eq_zero.mp hd

theorem contraction_duhamel_bound (A : E →L[ℝ] E) (B : F →L[ℝ] F)
    (C : E →L[ℝ] F) (t : ℝ) (ht : 0 ≤ t)
    (hA : ∀ u, 0 ≤ u → ‖transfer A u‖ ≤ 1)
    (hB : ∀ u, 0 ≤ u → ‖transfer B u‖ ≤ 1) :
    ‖C.comp (transfer A t)-(transfer B t).comp C‖ ≤ t*‖C.comp A-B.comp C‖ := by
  rw [duhamel_rectangular]
  have h := intervalIntegral.norm_integral_le_of_norm_le_const (a := 0) (b := t)
    (C := ‖C.comp A-B.comp C‖)
    (f := fun r => (transfer B (t-r)).comp ((C.comp A-B.comp C).comp (transfer A r)))
    (fun r hr => ?_)
  · simpa [abs_of_nonneg ht, mul_comm] using h
  · have hr' : r ∈ Set.Ioc 0 t := by simpa [Set.uIoc_of_le ht] using hr
    calc
      _ ≤ ‖transfer B (t-r)‖ * ‖(C.comp A-B.comp C).comp (transfer A r)‖ :=
        ContinuousLinearMap.opNorm_comp_le _ _
      _ ≤ 1*(‖C.comp A-B.comp C‖*1) :=
        mul_le_mul (hB _ (sub_nonneg.mpr hr'.2))
          ((ContinuousLinearMap.opNorm_comp_le _ _).trans
            (mul_le_mul_of_nonneg_left (hA _ hr'.1.le) (norm_nonneg _)))
          (norm_nonneg _) (by norm_num)
      _ = _ := by ring

end Rectangular
end KomorebiPaperVI.Semigroups
