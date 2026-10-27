module
public import Euler.EulerFormalKernel
@[expose] public section
noncomputable section
namespace Komorebi.Euler
open PowerSeries

/-- Formal hyperbolic cosine, defined independently of the reconstruction. -/
def formalCosh (a : ℚ) : PowerSeries ℚ := C (1/2) * (formalExp a + formalExp (-a))

lemma formalCosh_twice (a : ℚ) : 2*formalCosh a=formalExp a+formalExp (-a) := by
  have hc : (2:PowerSeries ℚ)*C (1/2:ℚ)=1 := by
    have h2 : (C (2:ℚ):PowerSeries ℚ)=2 := by norm_cast
    rw [← h2, ← map_mul]
    norm_num
  unfold formalCosh
  rw [← mul_assoc,hc,one_mul]

lemma formalCosh_coeff (a : ℚ) (n : ℕ) :
    coeff n (formalCosh a) = (a^n+(-a)^n)/(2*n.factorial) := by
  simp only [formalCosh,coeff_C_mul,map_add,formalExp_coeff]
  ring

lemma formalCosh_coeff_even (a : ℚ) (n : ℕ) :
    coeff (2*n) (formalCosh a) = a^(2*n)/(2*n).factorial := by
  rw [formalCosh_coeff, (show Even (2*n) from even_two_mul n).neg_pow]
  ring

lemma formalCosh_coeff_odd (a : ℚ) (n : ℕ) :
    coeff (2*n+1) (formalCosh a)=0 := by
  rw [formalCosh_coeff, (show Odd (2*n+1) from ⟨n,rfl⟩).neg_pow]
  ring

@[simp] lemma formalCosh_constant (a : ℚ) : constantCoeff (formalCosh a)=1 := by
  rw [← coeff_zero_eq_constantCoeff_apply]
  simpa using formalCosh_coeff_even a 0

/-- The source EGF is defined by shifting the difference of the cosh series. -/
def formalSource : PowerSeries ℚ :=
  mk (fun n => coeff (n+2) (formalCosh 3-formalCosh 1)/4)

lemma formalSource_coeff (n : ℕ) :
    coeff n formalSource = (coeff (n+2) (formalCosh 3)-coeff (n+2) (formalCosh 1))/4 := by
  simp [formalSource]

lemma formalSource_cleared : 4*X^2*formalSource=formalCosh 3-formalCosh 1 := by
  have hc4 : (C (4:ℚ):PowerSeries ℚ)=4 := by norm_cast
  ext n
  rcases n with _ | _ | n
  · simp [← hc4]
  · rw [mul_assoc,← hc4,coeff_C_mul]
    rw [show (X:PowerSeries ℚ)^2*formalSource = X*(X*formalSource) by ring]
    rw [coeff_succ_X_mul]
    simp [formalCosh_coeff]
  · change coeff (n+2) (4*X^2*formalSource)=_
    rw [mul_assoc,← hc4,coeff_C_mul,coeff_X_pow_mul,formalSource_coeff]
    simp only [map_sub]
    ring

/-- The algebraic hyperbolic cancellation, with all divisions cleared. -/
lemma formalSource_cosh_cleared :
    16*X^2*formalSource*formalCosh 1 = formalExp (-4)*(formalExp 4-1)^2 := by
  have h1 := formalCosh_twice 1
  have h3 := formalCosh_twice 3
  have hneg := formalExp_neg_mul 4
  have hex : 4*(formalCosh 3-formalCosh 1)*formalCosh 1 =
      formalExp 4+formalExp (-4)-2 := by
    calc
      _ = (2*formalCosh 3-2*formalCosh 1)*(2*formalCosh 1) := by ring
      _ = (formalExp 3+formalExp (-3)-(formalExp 1+formalExp (-1)))*
          (formalExp 1+formalExp (-1)) := by rw [h1,h3]
      _ = formalExp 3*formalExp 1+formalExp 3*formalExp (-1)+
          formalExp (-3)*formalExp 1+formalExp (-3)*formalExp (-1)-
          formalExp 1*formalExp 1-formalExp (-1)*formalExp 1-
          formalExp 1*formalExp (-1)-formalExp (-1)*formalExp (-1) := by ring
      _ = _ := by simp only [formalExp_mul]; norm_num; ring
  calc
    _ = 4*(4*X^2*formalSource)*formalCosh 1 := by ring
    _ = formalExp 4+formalExp (-4)-2 := by rw [formalSource_cleared,hex]
    _ = formalExp (-4)*formalExp 4*formalExp 4-
          2*(formalExp (-4)*formalExp 4)+formalExp (-4) := by rw [hneg]; ring
    _ = _ := by ring

/-- The independent reciprocal-cosh EGF for the signed Euler sequence. -/
def signedEulerEGF : PowerSeries ℚ := (formalCosh 1)⁻¹

/-- This is the universal generating-function identity, not a definition of Euler numbers. -/
theorem formal_euler_reconstruction : formalKernel*formalSource=signedEulerEGF := by
  apply (eq_inv_iff_mul_eq_one (by simp : constantCoeff (formalCosh 1)≠0)).mpr
  have hs := formalSource_cosh_cleared
  have hk := formalKernel_cleared_identity
  have he := formalExp_neg_mul 4
  have h16 : (16:PowerSeries ℚ)≠0 := by
    intro h
    have hc16 : (C (16:ℚ):PowerSeries ℚ)=16 := by norm_cast
    rw [← hc16] at h
    have hh := congrArg (coeff (R:=ℚ) 0) h
    norm_num at hh
  apply mul_left_cancel₀ (show (16:PowerSeries ℚ)*X^2≠0 from
    mul_ne_zero h16 (pow_ne_zero _ X_ne_zero))
  calc
    (16*X^2)*(formalKernel*formalSource*formalCosh 1) =
        formalKernel*(16*X^2*formalSource*formalCosh 1) := by ring
    _ = formalExp (-4)*(formalKernel*(formalExp 4-1)^2) := by rw [hs]; ring
    _ = 16*X^2*(formalExp (-4)*formalExp 4) := by rw [hk]; ring
    _ = (16*X^2)*1 := by rw [he]

end Komorebi.Euler
