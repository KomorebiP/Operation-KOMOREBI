module
public import Euler.EulerSource
@[expose] public section
noncomputable section
namespace Komorebi.Euler
open PowerSeries

/-- One Newton tap, multiplied by the removed factor n+1, is a binomial coefficient. -/
lemma sourceTap_integer_binomial (n q : ℕ) :
    ((n:D)+1)*sourceTap q*(descPochhammer D q).eval (n:D) =
      (8:D)^q*((n+1).choose (q+1):D) := by
  rw [descPochhammer_eval_eq_descFactorial]
  apply Subtype.ext
  simp only [PadicInt.coe_mul, PadicInt.coe_add, PadicInt.coe_one,
    PadicInt.coe_natCast, PadicInt.coe_pow, sourceTap_coe]
  have hc : ((n:ℚ_[2])+1)*(n.descFactorial q:ℚ_[2]) =
      ((q+1).factorial:ℚ_[2])*((n+1).choose (q+1):ℚ_[2]) := by
    have h:=Nat.succ_descFactorial_succ n q
    rw [Nat.descFactorial_eq_factorial_mul_choose] at h
    exact_mod_cast h.symm
  have hfac : ((q+1).factorial:ℚ_[2])≠0 := by exact_mod_cast Nat.factorial_ne_zero (q+1)
  calc
    _ = ((8:ℚ_[2])^q / (q+1).factorial)*(((n:ℚ_[2])+1)*(n.descFactorial q:ℚ_[2])) := by ring
    _ = ((8:ℚ_[2])^q / (q+1).factorial)*
      (((q+1).factorial:ℚ_[2])*((n+1).choose (q+1):ℚ_[2])) := by rw [hc]
    _ = _ := by rw [div_mul_eq_mul_div, mul_div_assoc, mul_div_cancel_left₀ _ hfac]; rfl

/-- The exact binomial theorem closes the numerator on every nonnegative integer row. -/
theorem sourceNumerator_integer_identity (n : ℕ) :
    8*((n:D)+1)*reval sourceNumerator (n:D)=(9:D)^(n+1)-1 := by
  rw [sourceNumerator_reval_nat]
  have ht : ((n:D)+1)*
      (∑ q ∈ Finset.range (n+1),sourceTap q*(descPochhammer D q).eval (n:D)) =
      ∑ q ∈ Finset.range (n+1),(8:D)^q*((n+1).choose (q+1):D) := by
    rw [Finset.mul_sum]
    apply Finset.sum_congr rfl
    intro q _
    simpa only [← mul_assoc] using sourceTap_integer_binomial n q
  rw [mul_assoc,ht,Finset.mul_sum]
  have hp := add_pow (8:D) 1 (n+1)
  simp only [one_pow,mul_one] at hp
  rw [Finset.sum_range_succ'] at hp
  simp only [pow_zero,Nat.choose_zero_right,Nat.cast_one,mul_one] at hp
  have hsum : ∑ q ∈ Finset.range (n+1),8*((8:D)^q*((n+1).choose (q+1):D)) =
      ∑ q ∈ Finset.range (n+1),(8:D)^(q+1)*((n+1).choose (q+1):D) := by
    apply Finset.sum_congr rfl
    intro q _
    rw [pow_succ]
    ring
  rw [hsum]
  have hn : (8:D)+1=9 := by norm_num
  rw [hn] at hp
  exact (eq_sub_iff_add_eq).mpr hp.symm

/-- Denominator-cleared agreement with the original Euler source on every integer row. -/
theorem eulerSource_integer_identity (n : ℕ) :
    8*((n:D)+1)*(2*(n:D)+1)*reval eulerSource (n:D) =
      (9:D)^(n+1)-1 := by
  have h:=eulerSource_reval_identity (n:D)
  have hn:=sourceNumerator_integer_identity n
  calc
    _ = 8*((n:D)+1)*((1+2*(n:D))*reval eulerSource (n:D)) := by ring
    _ = _ := by rw [h]; exact hn

/-- The constructed convergent series is exactly the rational source used by Euler rows. -/
theorem eulerSource_integer_formula (n : ℕ) :
    qeval eulerSource (n:ℚ_[2]) =
      ((9:ℚ_[2])^(n+1)-1)/(8*((n:ℚ_[2])+1)*(2*(n:ℚ_[2])+1)) := by
  have hn : (8:ℚ_[2])*((n:ℚ_[2])+1)*(2*(n:ℚ_[2])+1)≠0 := by
    have h1 : (n:ℚ_[2])+1≠0 := by exact_mod_cast (show (n:ℤ)+1≠0 by omega)
    have h2 : 2*(n:ℚ_[2])+1≠0 := by exact_mod_cast (show 2*(n:ℤ)+1≠0 by omega)
    exact mul_ne_zero (mul_ne_zero (by norm_num) h1) h2
  apply (eq_div_iff hn).mpr
  have h:=congrArg (fun z:D => (z:ℚ_[2])) (eulerSource_integer_identity n)
  simp only [PadicInt.coe_mul,PadicInt.coe_add,PadicInt.coe_sub,PadicInt.coe_pow,
    PadicInt.coe_one,PadicInt.coe_natCast] at h
  have he : (reval eulerSource (n:D):ℚ_[2])=qeval eulerSource (n:ℚ_[2]) :=
    coe_reval eulerSource_restricted (n:D)
  rw [he] at h
  change (8:ℚ_[2])*((n:ℚ_[2])+1)*(2*(n:ℚ_[2])+1)*qeval eulerSource (n:ℚ_[2]) = (9:ℚ_[2])^(n+1)-1 at h
  simpa only [mul_comm] using h

/-- Source values are genuine dyadic units at all, not only integer, arguments. -/
theorem eulerSource_norm_one (x : D) : ‖reval eulerSource x‖=1 :=
  red_ne_zero_norm_one _ (by rw [eulerSource_reval_red]; norm_num)


/-- Agreement with the original 3^(2n+2) Euler-source formula, not just a renaming. -/
theorem eulerSource_original_formula (n : ℕ) :
    qeval eulerSource (n:ℚ_[2]) =
      ((3:ℚ_[2])^(2*n+2)-1)/(4*(2*(n:ℚ_[2])+1)*(2*(n:ℚ_[2])+2)) := by
  rw [eulerSource_integer_formula]
  have hp : (3:ℚ_[2])^(2*n+2)=(9:ℚ_[2])^(n+1) := by
    rw [show 2*n+2=2*(n+1) by omega,pow_mul]
    norm_num
  rw [hp]
  congr 1
  ring

end Komorebi.Euler
