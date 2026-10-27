module
public import Euler.SecondOrderRemainder
@[expose] public section
noncomputable section
set_option maxHeartbeats 800000
namespace Komorebi.Euler
open PowerSeries

lemma pow_add_three_fourth_remainder (n:ℕ) (x y:D) :
    ∃u:D, y^(n+3)-x^(n+3)-(n+3:D)*x^(n+2)*(y-x)-
      ((n+3).choose 2:D)*x^(n+1)*(y-x)^2-
      ((n+3).choose 3:D)*x^n*(y-x)^3=(y-x)^4*u := by
  induction n with
  | zero => exact ⟨0,by norm_num;ring⟩
  | succ n ih =>
    obtain ⟨u,hu⟩ := ih
    refine ⟨y*u+((n+3).choose 3:D)*x^n,?_⟩
    have hc2 : ((n+1+3).choose 2:D)=((n+3).choose 2:D)+(n+3:D) := by
      rw [show n+1+3=(n+3)+1 by omega,Nat.choose_succ_succ,Nat.choose_one_right]
      push_cast;ring
    have hc3 : ((n+1+3).choose 3:D)=((n+3).choose 3:D)+((n+3).choose 2:D) := by
      rw [show n+1+3=(n+3)+1 by omega,Nat.choose_succ_succ]
      push_cast;ring
    rw [hc2,hc3]
    have he : y^(n+1+3)-x^(n+1+3)-(n+1+3:D)*x^(n+1+2)*(y-x)-
        (((n+3).choose 2:D)+(n+3:D))*x^(n+1+1)*(y-x)^2-
        (((n+3).choose 3:D)+((n+3).choose 2:D))*x^(n+1)*(y-x)^3 =
        y*(y^(n+3)-x^(n+3)-(n+3:D)*x^(n+2)*(y-x)-
          ((n+3).choose 2:D)*x^(n+1)*(y-x)^2-
          ((n+3).choose 3:D)*x^n*(y-x)^3)+((n+3).choose 3:D)*x^n*(y-x)^4 := by
      simp only [show n+1+3=n+3+1 by omega,show n+1+2=n+2+1 by omega,
        show n+2=n+1+1 by omega,pow_succ]
      ring
    simp only [Nat.cast_add,Nat.cast_one] at he ⊢
    rw [he,hu];ring

lemma norm_pow_fourth_le (n:ℕ) (x y:D) :
    ‖y^n-x^n-(n:D)*x^(n-1)*(y-x)-(n.choose 2:D)*x^(n-2)*(y-x)^2-
      (n.choose 3:D)*x^(n-3)*(y-x)^3‖≤‖y-x‖^4 := by
  rcases n with _ | _ | _ | n
  · simp
  · norm_num [Nat.choose]
  · norm_num [Nat.choose]; ring_nf; norm_num
  · obtain ⟨u,hu⟩ := pow_add_three_fourth_remainder n x y
    simp only [show n+1+1+1=n+3 by omega, Nat.add_sub_cancel,
      show n+3-1=n+2 by omega,show n+3-2=n+1 by omega,Nat.cast_add,Nat.cast_ofNat]
    rw [hu,norm_mul,norm_pow]
    exact mul_le_of_le_one_right (by positivity) (PadicInt.norm_le_one _)

lemma third_jet_tsum {f:PowerSeries D} (hf:Restricted f) (x:D) :
    (∑'n,coeff n f*((n.choose 3:D)*x^(n-3)))=rjet 3 f x := by
  have hs:=summable_weighted hf (fun n=>(n.choose 3:D)*x^(n-3))
  rw [←hs.sum_add_tsum_nat_add 3]
  simp only [Finset.sum_range_succ,Finset.sum_range_zero,
    Nat.choose_eq_zero_of_lt (by decide : 0<3),
    Nat.choose_eq_zero_of_lt (by decide : 1<3),
    Nat.choose_eq_zero_of_lt (by decide : 2<3),
    Nat.cast_zero,zero_mul,mul_zero,zero_add,Nat.add_sub_cancel,rjet,reval,coeff_hasseSeries]
  apply tsum_congr;intro n;ring

/-- Integral cubic Taylor approximation, with a fourth-order bound for the entire infinite tail. -/
theorem reval_third_order_error {f:PowerSeries D} (hf:Restricted f) (x y:D) :
    ‖reval f y-reval f x-(y-x)*rjet 1 f x-(y-x)^2*rjet 2 f x-
      (y-x)^3*rjet 3 f x‖≤‖y-x‖^4 := by
  have hsum : HasSum (fun n=>coeff n f*(y^n-x^n-(n:D)*x^(n-1)*(y-x)-
      (n.choose 2:D)*x^(n-2)*(y-x)^2-(n.choose 3:D)*x^(n-3)*(y-x)^3))
      (reval f y-reval f x-(y-x)*rjet 1 f x-(y-x)^2*rjet 2 f x-
        (y-x)^3*rjet 3 f x) := by
    have h0 := (hasSum_reval hf y).sub (hasSum_reval hf x)
    have h1 := (summable_first_jet hf x).hasSum.mul_left (y-x)
    rw [first_jet_tsum hf x] at h1
    have h2 := (summable_weighted hf (fun n=>(n.choose 2:D)*x^(n-2))).hasSum.mul_left ((y-x)^2)
    rw [second_jet_tsum hf x] at h2
    have h3 := (summable_weighted hf (fun n=>(n.choose 3:D)*x^(n-3))).hasSum.mul_left ((y-x)^3)
    rw [third_jet_tsum hf x] at h3
    convert ((h0.sub h1).sub h2).sub h3 using 1 <;> first | rfl | (ext n;ring)
  rw [←hsum.tsum_eq]
  apply IsUltrametricDist.norm_tsum_le_of_forall_le
  intro n;rw [norm_mul]
  exact (mul_le_of_le_one_left (norm_nonneg _) (PadicInt.norm_le_one _)).trans
    (norm_pow_fourth_le n x y)

/-- Over Z_2, a norm divisibility bound constructs an integral quotient. -/
lemma exists_mul_of_norm_le (a b:D) (hab:‖a‖≤‖b‖) : ∃c:D,a=b*c := by
  by_cases hb:b=0
  · subst b
    have ha:a=0:=norm_eq_zero.mp (le_antisymm (by simpa using hab) (norm_nonneg _))
    exact ⟨0,by simp [ha]⟩
  have hbk:(b:ℚ_[2])≠0 := by simpa using hb
  let c:D:=⟨(a:ℚ_[2])/(b:ℚ_[2]),by
    rw [norm_div]
    exact (div_le_one (norm_pos_iff.mpr hbk)).mpr hab⟩
  refine ⟨c,?_⟩
  apply Subtype.ext
  change (a:ℚ_[2])=(b:ℚ_[2])*((a:ℚ_[2])/(b:ℚ_[2]))
  field_simp

end Komorebi.Euler
