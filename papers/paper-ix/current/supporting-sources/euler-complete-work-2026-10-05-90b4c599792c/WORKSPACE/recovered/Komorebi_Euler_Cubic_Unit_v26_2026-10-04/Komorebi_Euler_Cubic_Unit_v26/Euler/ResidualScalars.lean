module
public import Euler.EulerKernel
@[expose] public section
noncomputable section
namespace Komorebi.Euler

/-- The genuine Taylor coefficient of (z / sinh z)^2, not a normalized placeholder. -/
def eulerBetaRat (m : ℕ) : ℚ :=
  eulerKappaRat m / ((4:ℚ)^m * (2*m).factorial)

@[simp] lemma eulerBetaRat_zero : eulerBetaRat 0 = 1 := by
  simp [eulerBetaRat]

lemma eulerBetaRat_ne_zero (m : ℕ) : eulerBetaRat m ≠ 0 := by
  exact div_ne_zero (eulerKappaRat_ne_zero m)
    (mul_ne_zero (pow_ne_zero _ (by norm_num))
      (by exact_mod_cast Nat.factorial_ne_zero (2*m)))

lemma eulerBetaRat_val (m : ℕ) (hm : 0<m) :
    padicValRat 2 (eulerBetaRat m) =
      2*(m:ℤ)-1-padicValNat 2 (2*m).factorial := by
  rw [eulerBetaRat, padicValRat.div (eulerKappaRat_ne_zero m)
    (mul_ne_zero (pow_ne_zero _ (by norm_num))
      (by exact_mod_cast Nat.factorial_ne_zero (2*m))),
    padicValRat.mul (pow_ne_zero _ (by norm_num))
      (by exact_mod_cast Nat.factorial_ne_zero (2*m)),
    eulerKappaRat_val m hm, padicValRat.pow, padicValRat.of_nat]
  have h4 : padicValRat 2 (4:ℚ)=2 := by
    rw [show (4:ℚ)=(2:ℚ)^2 by norm_num, padicValRat.pow]
    have hp : padicValRat 2 (2:ℚ)=1 := padicValRat.self (by norm_num)
    rw [hp]
    norm_num
  rw [h4]
  ring

lemma eulerBetaRat_val_nonneg (m : ℕ) : 0 ≤ padicValRat 2 (eulerBetaRat m) := by
  rcases Nat.eq_zero_or_pos m with rfl | hm
  · simp
  · rw [eulerBetaRat_val m hm]
    have h := padicValNat_factorial_lt_of_ne_zero 2 (show 2*m≠0 by omega)
    omega

/-- Beta is integral before extracting the r-dependent normalization. -/
def eulerBeta (m : ℕ) : D :=
  ⟨(eulerBetaRat m:ℚ_[2]), (Padic.norm_le_one_iff_val_nonneg _).mpr
    (by simpa only [Padic.valuation_ratCast] using eulerBetaRat_val_nonneg m)⟩

@[simp] lemma eulerBeta_coe (m : ℕ) :
    (eulerBeta m:ℚ_[2])=(eulerBetaRat m:ℚ_[2]) := rfl

@[simp] lemma eulerBeta_zero : eulerBeta 0=1 := by
  apply Subtype.ext
  simp

lemma eulerBeta_ne_zero (m : ℕ) : eulerBeta m≠0 := by
  intro h
  have hc := congrArg (fun x:D => (x:ℚ_[2])) h
  simp only [eulerBeta_coe, PadicInt.coe_zero] at hc
  exact eulerBetaRat_ne_zero m (by exact_mod_cast hc)

lemma eulerKappaRat_beta (m : ℕ) :
    eulerKappaRat m = (4:ℚ)^m * (2*m).factorial * eulerBetaRat m := by
  rw [eulerBetaRat]
  field_simp

lemma eulerKappa_beta (m : ℕ) :
    eulerKappa m = (4:D)^m * ((2*m).factorial:D) * eulerBeta m := by
  apply Subtype.ext
  simp only [eulerKappa_coe,PadicInt.coe_mul,PadicInt.coe_pow,
    PadicInt.coe_natCast,eulerBeta_coe]
  change (eulerKappaRat m:ℚ_[2]) = (4:ℚ_[2])^m * ((2*m).factorial:ℚ_[2]) * (eulerBetaRat m:ℚ_[2])
  have h := congrArg (fun x:ℚ => (x:ℚ_[2])) (eulerKappaRat_beta m)
  simpa only [Rat.cast_mul,Rat.cast_pow,Rat.cast_ofNat,Rat.cast_natCast] using h

/-- Integral numerator tap. Its 8^q decay is uniform in the residual depth r. -/
def residualNumeratorTap (r q : ℕ) : D := (8:D)^q * eulerBeta (r+q)

lemma residualNumeratorTap_norm (r q : ℕ) :
    ‖residualNumeratorTap r q‖ ≤ (1/8:ℝ)^q := by
  have h8 : ‖(8:D)‖=(1/8:ℝ) := by
    have h := PadicInt.norm_p_pow (p:=2) 3
    norm_num at h ⊢
    exact h
  rw [residualNumeratorTap,norm_mul,norm_pow,h8]
  exact mul_le_of_le_one_right (by positivity) (PadicInt.norm_le_one _)

end Komorebi.Euler
