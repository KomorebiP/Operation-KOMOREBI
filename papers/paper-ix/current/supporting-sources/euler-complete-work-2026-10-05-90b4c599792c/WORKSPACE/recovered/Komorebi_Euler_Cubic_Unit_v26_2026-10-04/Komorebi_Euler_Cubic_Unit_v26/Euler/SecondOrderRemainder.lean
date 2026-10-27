module
public import Euler.RestrictedCalculus
@[expose] public section
noncomputable section
set_option maxHeartbeats 500000
namespace Komorebi.Euler
open PowerSeries

lemma pow_add_two_third_remainder (n : ℕ) (x y : D) :
    ∃u:D, y^(n+2)-x^(n+2)-(n+2:D)*x^(n+1)*(y-x)-
      ((n+2).choose 2:D)*x^n*(y-x)^2=(y-x)^3*u := by
  induction n with
  | zero => exact ⟨0,by norm_num;ring⟩
  | succ n ih =>
    obtain ⟨u,hu⟩ := ih
    refine ⟨y*u+((n+2).choose 2:D)*x^n,?_⟩
    have hc : ((n+1+2).choose 2:D)=((n+2).choose 2:D)+(n+2:D) := by
      rw [show n+1+2=(n+2)+1 by omega,Nat.choose_succ_succ,Nat.choose_one_right]
      push_cast
      ring
    rw [hc]
    have he : y^(n+1+2)-x^(n+1+2)-(n+1+2:D)*x^(n+1+1)*(y-x)-
      (((n+2).choose 2:D)+(n+2:D))*x^(n+1)*(y-x)^2 =
      y*(y^(n+2)-x^(n+2)-(n+2:D)*x^(n+1)*(y-x)-
      ((n+2).choose 2:D)*x^n*(y-x)^2)+((n+2).choose 2:D)*x^n*(y-x)^3 := by
      simp only [show n+1+2=n+2+1 by omega,show n+2=n+1+1 by omega,
        pow_succ]
      ring
    simp only [Nat.cast_add,Nat.cast_one] at he ⊢
    rw [he,hu]
    ring

lemma norm_pow_third_le (n:ℕ) (x y:D) :
    ‖y^n-x^n-(n:D)*x^(n-1)*(y-x)-(n.choose 2:D)*x^(n-2)*(y-x)^2‖ ≤ ‖y-x‖^3 := by
  rcases n with _ | _ | n
  · simp
  · simp
  · obtain ⟨u,hu⟩ := pow_add_two_third_remainder n x y
    simp only [show n+1+1=n+2 by omega, Nat.add_sub_cancel,
      show n+2-1=n+1 by omega,Nat.cast_add,Nat.cast_ofNat]
    rw [hu,norm_mul,norm_pow]
    exact mul_le_of_le_one_right (by positivity) (PadicInt.norm_le_one _)

lemma second_jet_tsum {f:PowerSeries D} (hf:Restricted f) (x:D) :
    (∑'n,coeff n f*((n.choose 2:D)*x^(n-2)))=rjet 2 f x := by
  have hs := summable_weighted hf (fun n=>(n.choose 2:D)*x^(n-2))
  rw [←hs.sum_add_tsum_nat_add 2]
  simp only [Finset.sum_range_succ,Finset.sum_range_zero,Nat.choose_eq_zero_of_lt (by decide : 0<2),
    Nat.choose_eq_zero_of_lt (by decide : 1<2), Nat.cast_zero, zero_mul,mul_zero,zero_add,
    Nat.add_sub_cancel,rjet,reval,coeff_hasseSeries]
  apply tsum_congr
  intro n
  ring

/-- The second-order Taylor error of any integral restricted series is bounded by distance cubed. -/
theorem reval_second_order_error {f:PowerSeries D} (hf:Restricted f) (x y:D) :
    ‖reval f y-reval f x-(y-x)*rjet 1 f x-(y-x)^2*rjet 2 f x‖ ≤ ‖y-x‖^3 := by
  have hsum : HasSum (fun n=>coeff n f*(y^n-x^n-(n:D)*x^(n-1)*(y-x)-
      (n.choose 2:D)*x^(n-2)*(y-x)^2))
      (reval f y-reval f x-(y-x)*rjet 1 f x-(y-x)^2*rjet 2 f x) := by
    have h0 := (hasSum_reval hf y).sub (hasSum_reval hf x)
    have h1 := (summable_first_jet hf x).hasSum.mul_left (y-x)
    rw [first_jet_tsum hf x] at h1
    have h2 := (summable_weighted hf (fun n=>(n.choose 2:D)*x^(n-2))).hasSum.mul_left ((y-x)^2)
    rw [second_jet_tsum hf x] at h2
    convert (h0.sub h1).sub h2 using 1 <;> first | rfl | (ext n;ring)
  rw [←hsum.tsum_eq]
  apply IsUltrametricDist.norm_tsum_le_of_forall_le
  intro n
  rw [norm_mul]
  exact (mul_le_of_le_one_left (norm_nonneg _) (PadicInt.norm_le_one _)).trans
    (norm_pow_third_le n x y)

end Komorebi.Euler
