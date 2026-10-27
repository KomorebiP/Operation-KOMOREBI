import KomorebiPaperVI.PoissonKernel
import KomorebiPaperVI.ReciprocalGaussian

/-! Author: Komorebi P. The improper subordination integral for every nonnegative spectral mode. -/
namespace KomorebiPaperVI.PoissonSubordination
open Set MeasureTheory
open KomorebiPaperVI.PoissonKernel KomorebiPaperVI.ReciprocalGaussian

theorem scaled_reciprocal_gaussian (t lam : ℝ) (ht : 0 < t) (hl : 0 ≤ lam) :
    (∫ u in Ioi 0, Real.exp (-(t^2/4)*u^2-lam/u^2))=
      Real.exp (-t*Real.sqrt lam)*Real.sqrt Real.pi/t := by
  let a := t/2*Real.sqrt lam
  have he : EqOn (fun u : ℝ => Real.exp (-(t^2/4)*u^2-lam/u^2))
      (fun u => Real.exp (-(t/2*u)^2-a^2/(t/2*u)^2)) (Ioi 0) := by
    intro u hu
    dsimp only
    congr 1
    dsimp [a]
    have hu0 : u ≠ 0 := ne_of_gt hu
    field_simp [hu0,ht.ne']
    nlinarith [Real.sq_sqrt hl]
  rw [setIntegral_congr_fun measurableSet_Ioi he]
  rw [integral_comp_mul_left_Ioi (fun u : ℝ => Real.exp (-u^2-a^2/u^2)) 0 (by positivity : 0 < t/2)]
  simp only [mul_zero,smul_eq_mul]
  rw [reciprocal_square_gaussian a (by dsimp [a]; positivity)]
  have he : -2*a= -t*Real.sqrt lam := by dsimp [a]; ring
  rw [he]
  field_simp

theorem heat_substitution (t lam s : ℝ) (hs : 0 < s) :
    heatIntegrand t lam s=t/Real.sqrt Real.pi *
      ((|(-1/2:ℝ)| *s^((-1/2:ℝ)-1)) •
        Real.exp (-(t^2/4)*(s^(-1/2:ℝ))^2-lam/(s^(-1/2:ℝ))^2)) := by
  unfold heatIntegrand
  rw [kernel_substitution t s hs.le,inverse_half_square s hs.le]
  simp only [smul_eq_mul]
  rw [mul_assoc,mul_assoc,← Real.exp_add]
  congr 3
  field_simp
  ring

theorem scalar_subordination (t lam : ℝ) (ht : 0 < t) (hl : 0 ≤ lam) :
    (∫ s in Ioi 0,heatIntegrand t lam s)=Real.exp (-t*Real.sqrt lam) := by
  rw [setIntegral_congr_fun measurableSet_Ioi (fun s hs => heat_substitution t lam s hs)]
  rw [integral_const_mul,integral_comp_rpow_Ioi
    (fun u : ℝ => Real.exp (-(t^2/4)*u^2-lam/u^2)) (p := -1/2) (by norm_num)]
  rw [scaled_reciprocal_gaussian t lam ht hl]
  have hp : Real.sqrt Real.pi ≠ 0 := (Real.sqrt_pos.mpr Real.pi_pos).ne'
  field_simp

variable {I E : Type*} [Fintype I] [NormedAddCommGroup E] [NormedSpace ℝ E] [CompleteSpace E]
theorem finite_spectral_subordination (P : I → E) (lam : I → ℝ) (hl : ∀ i,0 ≤ lam i)
    (t : ℝ) (ht : 0 < t) :
    (∫ s in Ioi 0,∑ i,heatIntegrand t (lam i) s • P i)=
      ∑ i,Real.exp (-t*Real.sqrt (lam i)) • P i := by
  rw [integral_finsetSum _ (fun i _ => (heat_integrand_integrable t (lam i) ht (hl i)).smul_const (P i))]
  congr 1
  funext i
  rw [integral_smul_const,scalar_subordination t (lam i) ht (hl i)]

open KomorebiPaperVI.SpectralPackets
variable {R : Type*} [DecidableEq I] [NormedRing R] [NormedAlgebra ℝ R] [CompleteSpace R]

omit [CompleteSpace R] in
theorem operator_integrand (P : I → R) (hP : ∑ i,P i=1)
    (h : ∀ i j,P i*P j=if i=j then P i else 0) (lam : I → ℝ) (t s : ℝ) :
    kernel t s • NormedSpace.exp ((-s) • resolve P lam)=
      ∑ i,heatIntegrand t (lam i) s • P i := by
  have he : (-s) • resolve P lam=resolve P (fun i => -s*lam i) := by
    simp [resolve,Finset.smul_sum,smul_smul]
  rw [he,exp_resolution P hP h]
  simp [resolve,Finset.smul_sum,smul_smul,heatIntegrand]

theorem operator_subordination (P : I → R) (hP : ∑ i,P i=1)
    (h : ∀ i j,P i*P j=if i=j then P i else 0) (lam : I → ℝ)
    (hl : ∀ i,0 ≤ lam i) (t : ℝ) (ht : 0 < t) :
    IntegrableOn (fun s => kernel t s • NormedSpace.exp ((-s) • resolve P lam)) (Ioi 0) ∧
    NormedSpace.exp ((-t) • fractional P lam (1/2))=
      ∫ s in Ioi 0,kernel t s • NormedSpace.exp ((-s) • resolve P lam) := by
  simp only [operator_integrand P hP h lam]
  refine ⟨finite_spectral_integrable P lam hl t ht,?_⟩
  rw [finite_spectral_subordination P lam hl t ht,spectral_transfer_exponential P hP h]
  simp only [spectralTransfer,resolve,Real.sqrt_eq_rpow]

end KomorebiPaperVI.PoissonSubordination
