module
public import Euler.PacketDerivatives
@[expose] public section
noncomputable section
namespace Komorebi.Euler
open PowerSeries Polynomial

lemma eulerPacket_odd_factor_red (i : ℕ) (x : D) :
    red (2*x-((2*i+1:ℕ):D))=1 := by
  simp only [map_sub,map_mul,red_two,zero_mul,Nat.cast_add,Nat.cast_mul]
  simp

lemma eulerPacket_odd_factor_ne_zero (i : ℕ) (x : D) :
    2*x-((2*i+1:ℕ):D)≠0 := by
  intro h
  have hh := eulerPacket_odd_factor_red i x
  rw [h,map_zero] at hh
  exact zero_ne_one hh

/-- No skeleton zero occurs before the integer row reaches its packet degree. -/
lemma eulerPacket_eval_nat_ne_zero (q n : ℕ) (hqn : q≤n) :
    (eulerPacket q).eval (n:D)≠0 := by
  rw [eulerPacket_eval]
  apply Finset.prod_ne_zero_iff.mpr
  intro i hi
  apply mul_ne_zero
  · apply sub_ne_zero.mpr
    exact_mod_cast (show n≠i by have := Finset.mem_range.mp hi; omega)
  · exact eulerPacket_odd_factor_ne_zero i (n:D)

lemma eulerPacket_derivative_succ (q : ℕ) (x : D) :
    (eulerPacket (q+1)).derivative.eval x=
      (eulerPacket q).derivative.eval x*(x-(q:D))*(2*x-((2*q+1:ℕ):D))+
      (eulerPacket q).eval x*(4*x-((4*q+1:ℕ):D)) := by
  rw [eulerPacket_succ]
  simp only [Polynomial.derivative_mul,Polynomial.derivative_sub,
    Polynomial.derivative_X,Polynomial.derivative_C,Polynomial.eval_add,
    Polynomial.eval_mul,Polynomial.eval_sub,Polynomial.eval_X,
    Polynomial.eval_C,Polynomial.eval_one,Polynomial.eval_zero]
  push_cast
  ring

lemma eulerPacket_first_omitted_derivative (n : ℕ) :
    (eulerPacket (n+1)).derivative.eval (n:D)=-(eulerPacket n).eval (n:D) := by
  rw [eulerPacket_derivative_succ,sub_self,mul_zero,zero_mul,zero_add]
  push_cast
  ring

/-- Every zero beyond an integer row is SIMPLE in the packet polynomial. -/
theorem eulerPacket_derivative_nat_ne_zero (q n : ℕ) (hnq : n<q) :
    (eulerPacket q).derivative.eval (n:D)≠0 := by
  induction q with
  | zero => omega
  | succ q ih =>
    by_cases hn : n<q
    · rw [eulerPacket_derivative_succ,eulerPacket_eval_nat_zero q n hn,
        zero_mul,add_zero]
      apply mul_ne_zero
      · apply mul_ne_zero (ih hn)
        apply sub_ne_zero.mpr
        exact_mod_cast (Nat.ne_of_lt hn)
      · exact eulerPacket_odd_factor_ne_zero q (n:D)
    · have he : n=q := by omega
      subst n
      rw [eulerPacket_first_omitted_derivative]
      exact neg_ne_zero.mpr (eulerPacket_eval_nat_ne_zero q q le_rfl)

lemma residualNumeratorTap_ne_zero (r q : ℕ) : residualNumeratorTap r q≠0 := by
  unfold residualNumeratorTap
  exact mul_ne_zero (pow_ne_zero _ (by norm_num)) (eulerBeta_ne_zero _)

/-- These packets vanish at the integer row, exactly as in finite Euler reconstruction. -/
theorem eulerPacketFunction_zero_after_row (r q n : ℕ) (hnq : n<q) :
    eulerPacketFunction r q (n:ℚ_[2])=0 := by
  have h := eulerPacketFunction_value r q (n:D)
  rw [eulerPacket_eval_nat_zero q n hnq,PadicInt.coe_zero,mul_zero,zero_mul] at h
  simpa only [PadicInt.coe_natCast] using h

/-- Their slopes do NOT vanish: the skeleton derivative survives, while the source
value remains a dyadic unit even at negative translated arguments. -/
theorem eulerPacketFunction_deriv_ne_zero_after_row (r q n : ℕ) (hnq : n<q) :
    deriv (eulerPacketFunction r q) (n:ℚ_[2])≠0 := by
  have h := (eulerPacketFunction_hasDerivAt r q (n:D)).deriv
  simp only [PadicInt.coe_natCast] at h
  rw [h]
  apply div_ne_zero
  · apply PadicInt.coe_ne_zero.mpr
    unfold residualPacketSlope
    rw [eulerPacket_eval_nat_zero q n hnq,zero_mul,add_zero]
    exact mul_ne_zero (residualNumeratorTap_ne_zero r q)
      (mul_ne_zero (eulerPacket_derivative_nat_ne_zero q n hnq)
        (eulerSource_reval_ne_zero _))
  · exact PadicInt.coe_ne_zero.mpr (eulerBeta_ne_zero r)

/-- Value termination at an integer is not a license to terminate its analytic slope sum. -/
theorem eulerPacket_derivative_tail_not_eventually_zero (r n : ℕ) :
    ¬ ∃ Q : ℕ, ∀ q≥Q, deriv (eulerPacketFunction r q) (n:ℚ_[2])=0 := by
  rintro ⟨Q,hQ⟩
  have hn : n<max Q (n+1) := by omega
  exact eulerPacketFunction_deriv_ne_zero_after_row r (max Q (n+1)) n hn
    (hQ _ (le_max_left _ _))

end Komorebi.Euler
