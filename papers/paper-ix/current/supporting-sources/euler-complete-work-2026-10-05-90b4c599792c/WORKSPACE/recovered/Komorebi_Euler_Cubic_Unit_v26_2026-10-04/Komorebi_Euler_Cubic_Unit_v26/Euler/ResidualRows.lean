module
public import Euler.ResidualEvaluation
@[expose] public section
noncomputable section
set_option maxHeartbeats 1000000
namespace Komorebi.Euler

lemma reconstructionTerm_desc (N m : ℕ) :
    reconstructionTerm N m =
      (4:D)^m * eulerBeta m * ((2*N).descFactorial (2*m):D) *
        reval eulerSource ((N-m:ℕ):D) := by
  rw [reconstructionTerm,eulerKappa_beta,Nat.descFactorial_eq_factorial_mul_choose]
  push_cast
  ring

lemma eulerPacket_nat_desc (n q : ℕ) :
    ((2*n).descFactorial (2*q):D)=(2:D)^q*(eulerPacket q).eval (n:D) := by
  have h:=eulerPacket_desc_factorial q (n:D)
  rw [show (2:D)*(n:D)=((2*n:ℕ):D) by push_cast; rfl,
    descPochhammer_eval_eq_descFactorial] at h
  exact h

/-- The factorial factor that remains before division by beta_r. -/
def residualRowFactor (r n : ℕ) : D :=
  (4:D)^r * ((2*(r+n)).descFactorial (2*r):D)

lemma residualRowFactor_ne_zero (r n : ℕ) : residualRowFactor r n≠0 := by
  apply mul_ne_zero (pow_ne_zero _ (by norm_num))
  have h : (2*(r+n)).descFactorial (2*r)≠0 :=
    (Nat.descFactorial_pos.mpr (show 2*r≤2*(r+n) by omega)).ne'
  exact_mod_cast h

lemma residualRowFactor_beta (r n : ℕ) :
    residualRowFactor r n*eulerBeta r =
      eulerKappa r*((2*(r+n)).choose (2*r):D) := by
  rw [residualRowFactor,eulerKappa_beta,Nat.descFactorial_eq_factorial_mul_choose]
  push_cast
  ring

/-- Exact cancellation of both factorial lanes in one original Euler summand. -/
lemma reconstructionTerm_packet (r n q : ℕ) (hq : q≤n) :
    reconstructionTerm (r+n) (r+q) =
      residualRowFactor r n *
        (residualNumeratorTap r q*(eulerPacket q).eval (n:D)*
          reval eulerSource ((n:D)-(q:D))) := by
  have hnat := Nat.descFactorial_mul_descFactorial
    (n:=2*(r+n)) (k:=2*r) (m:=2*(r+q)) (by omega)
  rw [show 2*(r+n)-2*r=2*n by omega,
    show 2*(r+q)-2*r=2*q by omega] at hnat
  have hd : ((2*(r+n)).descFactorial (2*(r+q)):D)=
      ((2*n).descFactorial (2*q):D)*((2*(r+n)).descFactorial (2*r):D) := by
    exact_mod_cast hnat.symm
  rw [reconstructionTerm_desc,hd,eulerPacket_nat_desc,
    show r+n-(r+q)=n-q by omega,Nat.cast_sub hq,
    residualRowFactor,residualNumeratorTap,pow_add]
  have hp : (4:D)^q*(2:D)^q=(8:D)^q := by rw [← mul_pow]; norm_num
  calc
    _ = (4:D)^r*((2*(r+n)).descFactorial (2*r):D)*
      (((4:D)^q*(2:D)^q)*eulerBeta (r+q)*(eulerPacket q).eval (n:D)*
        reval eulerSource ((n:D)-(q:D))) := by ring
    _ = _ := by rw [hp]

lemma reconstructionTail_reindex (r n : ℕ) (hr : 0<r) :
    reconstructionTail (r-1) (r+n)=
      ∑ q ∈ Finset.range (n+1), reconstructionTerm (r+n) (r+q) := by
  unfold reconstructionTail
  rw [Finset.sum_filter]
  have hcond (m:ℕ) : r-1<m ↔ r≤m := by omega
  simp_rw [hcond]
  rw [show r+n+1=r+(n+1) by omega,Finset.sum_range_add]
  have hzero : ∑ m ∈ Finset.range r,
      (if r≤m then reconstructionTerm (r+n) m else 0) = 0 := by
    apply Finset.sum_eq_zero
    intro m hm
    simp only [Finset.mem_range] at hm
    simp [show ¬ r≤m by omega]
  rw [hzero,zero_add]
  apply Finset.sum_congr rfl
  intro q _
  simp

/-- Whole-tail factorization in Z_2 before any possibly nonintegral scalar division. -/
theorem reconstructionTail_residualNumerator (r n : ℕ) (hr : 0<r) :
    reconstructionTail (r-1) (r+n)=
      residualRowFactor r n*reval (eulerResidualNumerator r) (n:D) := by
  rw [reconstructionTail_reindex r n hr,eulerResidualNumerator_reval_nat,Finset.mul_sum]
  apply Finset.sum_congr rfl
  intro q hq
  exact reconstructionTerm_packet r n q (by simpa only [Finset.mem_range,Nat.lt_succ_iff] using hq)

/-- The exact error in the independently defined Euler sequence has the constructed H_r factor. -/
theorem signedEuler_error_residual (r n : ℕ) (hr : 0<r) :
    ((signedEulerEven (r+n)-reconstructionTrunc (r-1) (r+n):D):ℚ_[2]) =
      (eulerKappa r:ℚ_[2])*((2*(r+n)).choose (2*r):ℚ_[2])*
        eulerResidual r (n:ℚ_[2]) := by
  rw [signedEuler_error_identity,reconstructionTail_residualNumerator r n hr,
    PadicInt.coe_mul]
  have hp := congrArg (fun z:D => (z:ℚ_[2])) (residualRowFactor_beta r n)
  simp only [PadicInt.coe_mul,PadicInt.coe_natCast] at hp
  rw [← hp,mul_assoc]
  have he := eulerResidual_beta_mul r (n:D)
  simp only [PadicInt.coe_natCast] at he
  rw [he]

/-- The original (r,N) form, including the exact nonempty-tail hypothesis. -/
theorem signedEuler_error_residual_of_le (r N : ℕ) (hr : 0<r) (hN : r≤N) :
    ((signedEulerEven N-reconstructionTrunc (r-1) N:D):ℚ_[2]) =
      (eulerKappa r:ℚ_[2])*((2*N).choose (2*r):ℚ_[2])*
        eulerResidual r ((N-r:ℕ):ℚ_[2]) := by
  have h := signedEuler_error_residual r (N-r) hr
  simpa only [Nat.add_sub_of_le hN] using h

/-- Root equivalence for a nonempty original Euler row. -/
theorem signedEuler_error_zero_iff_residual (r N : ℕ) (hr : 0<r) (hN : r≤N) :
    signedEulerEven N=reconstructionTrunc (r-1) N ↔
      eulerResidual r ((N-r:ℕ):ℚ_[2])=0 := by
  have hk : (eulerKappa r:ℚ_[2])≠0 := (PadicInt.coe_eq_zero).not.mpr (eulerKappa_ne_zero r)
  have hc : ((2*N).choose (2*r):ℚ_[2])≠0 := by
    exact_mod_cast (Nat.choose_pos (show 2*r≤2*N by omega)).ne'
  rw [← sub_eq_zero,← PadicInt.coe_eq_zero,signedEuler_error_residual_of_le r N hr hN]
  exact mul_eq_zero.trans (or_iff_right (mul_ne_zero hk hc))

end Komorebi.Euler
