module
public import Euler.ResidualRecurrence
@[expose] public section
noncomputable section
namespace Komorebi.Euler

/-- Binary complexity is defined by the actual base-two digits. -/
def binaryDigitSum (n : ℕ) : ℕ := (Nat.digits 2 n).sum

@[simp] lemma binaryDigitSum_zero : binaryDigitSum 0=0 := by
  simp [binaryDigitSum]

lemma binaryDigitSum_two_mul (m : ℕ) : binaryDigitSum (2*m)=binaryDigitSum m := by
  rcases Nat.eq_zero_or_pos m with rfl | hm
  · simp
  · simp only [binaryDigitSum,Nat.digits_base_mul (by decide : 1<2) hm,
      List.sum_cons,zero_add]

lemma factorial_two_valuation_digits (n : ℕ) :
    (padicValNat 2 n.factorial:ℤ)=(n:ℤ)-(binaryDigitSum n:ℤ) := by
  have h := sub_one_mul_padicValNat_factorial (p:=2) n
  norm_num only [Nat.reduceSub,one_mul] at h
  rw [h,Nat.cast_sub (Nat.digit_sum_le 2 n)]
  rfl

/-- The exact binary-digit valuation of the actual beta coefficient. -/
theorem eulerBetaRat_val_digits (m : ℕ) (hm : 0<m) :
    padicValRat 2 (eulerBetaRat m)=(binaryDigitSum m:ℤ)-1 := by
  rw [eulerBetaRat_val m hm,factorial_two_valuation_digits,binaryDigitSum_two_mul]
  push_cast
  ring

lemma binaryDigitSum_pos (m : ℕ) (hm : 0<m) : 0<binaryDigitSum m := by
  have h := eulerBetaRat_val_nonneg m
  rw [eulerBetaRat_val_digits m hm] at h
  omega

theorem eulerBeta_valuation (m : ℕ) (hm : 0<m) :
    Padic.valuation (eulerBeta m:ℚ_[2])=(binaryDigitSum m:ℤ)-1 := by
  rw [eulerBeta_coe,Padic.valuation_ratCast,eulerBetaRat_val_digits m hm]

theorem eulerBeta_norm (m : ℕ) (hm : 0<m) :
    ‖eulerBeta m‖=(2:ℝ)^(-((binaryDigitSum m:ℤ)-1)) := by
  change ‖(eulerBeta m:ℚ_[2])‖=_
  rw [Padic.norm_eq_zpow_neg_valuation
    ((PadicInt.coe_eq_zero).not.mpr (eulerBeta_ne_zero m)),eulerBeta_valuation m hm]
  norm_num

/-- The exact scalar of the unnormalized H_r packet, over the rationals. -/
def residualScalarRat (r q : ℕ) : ℚ :=
  (8:ℚ)^q*eulerBetaRat (r+q)/eulerBetaRat r

lemma residualScalarRat_ne_zero (r q : ℕ) : residualScalarRat r q≠0 :=
  div_ne_zero (mul_ne_zero (pow_ne_zero _ (by norm_num))
    (eulerBetaRat_ne_zero _)) (eulerBetaRat_ne_zero _)

/-- The carry cost may be negative. It is not a natural-number truncation. -/
def residualCarryCost (r q : ℕ) : ℤ :=
  3*(q:ℤ)+(binaryDigitSum (r+q):ℤ)-(binaryDigitSum r:ℤ)

@[simp] lemma residualCarryCost_zero (r : ℕ) : residualCarryCost r 0=0 := by
  simp [residualCarryCost]

/-- Exact valuation of the actual packet scalar, not an assumed weight sequence. -/
theorem residualScalarRat_val (r q : ℕ) (hr : 0<r) :
    padicValRat 2 (residualScalarRat r q)=residualCarryCost r q := by
  rw [residualScalarRat,padicValRat.div
    (mul_ne_zero (pow_ne_zero _ (by norm_num)) (eulerBetaRat_ne_zero _))
    (eulerBetaRat_ne_zero _),
    padicValRat.mul (pow_ne_zero _ (by norm_num)) (eulerBetaRat_ne_zero _),
    padicValRat.pow,eulerBetaRat_val_digits (r+q) (by omega),eulerBetaRat_val_digits r hr]
  have h8 : padicValRat 2 (8:ℚ)=3 := by
    have hp : padicValRat 2 (2:ℚ)=1 := padicValRat.self (by norm_num)
    rw [show (8:ℚ)=(2:ℚ)^3 by norm_num,padicValRat.pow,hp]
    norm_num
  rw [h8,residualCarryCost]
  ring

lemma residualScalarRat_coe (r q : ℕ) :
    (residualScalarRat r q:ℚ_[2])=
      (8:ℚ_[2])^q*(eulerBeta (r+q):ℚ_[2])/(eulerBeta r:ℚ_[2]) := by
  simp only [residualScalarRat,Rat.cast_div,Rat.cast_mul,Rat.cast_pow,
    Rat.cast_ofNat,eulerBeta_coe]

theorem residualScalar_valuation (r q : ℕ) (hr : 0<r) :
    Padic.valuation ((8:ℚ_[2])^q*(eulerBeta (r+q):ℚ_[2])/(eulerBeta r:ℚ_[2]))=
      residualCarryCost r q := by
  rw [← residualScalarRat_coe,Padic.valuation_ratCast,residualScalarRat_val r q hr]

lemma residualCarryCost_lower (r q : ℕ) (hr : 0<r) :
    3*(q:ℤ)+1-(binaryDigitSum r:ℤ)≤residualCarryCost r q := by
  have h := binaryDigitSum_pos (r+q) (by omega)
  unfold residualCarryCost
  omega

/-- Every packet that can reach the minimum lies in this finite range. -/
theorem residualCarryCost_nonpositive_bound (r q : ℕ) (hr : 0<r)
    (hq : residualCarryCost r q≤0) :
    q≤(binaryDigitSum r-1)/3 := by
  have h := residualCarryCost_lower r q hr
  omega

/-- Beyond the finite search range the carry cost is strictly positive. -/
theorem residualCarryCost_positive_after (r q : ℕ) (hr : 0<r)
    (hq : (binaryDigitSum r-1)/3<q) : 0<residualCarryCost r q := by
  by_contra h
  have hle := residualCarryCost_nonpositive_bound r q hr (by omega)
  omega

end Komorebi.Euler
