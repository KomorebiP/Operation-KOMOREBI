module
public import Euler.RestrictedCalculus
@[expose] public section
noncomputable section
set_option maxHeartbeats 500000
namespace Komorebi.Euler
open PowerSeries

/-- Division-free trapezoid remainder of a monomial has three distance factors. -/
lemma pow_succ_trapezoid_remainder (n : ℕ) (x y : D) :
    ∃ u : D, 2*(y^(n+1)-x^(n+1))-
      (y-x)*((n+1:D)*x^n+(n+1:D)*y^n)=(y-x)^3*u := by
  induction n with
  | zero => exact ⟨0,by simp;ring⟩
  | succ n ih =>
    obtain ⟨u,hu⟩ := ih
    obtain ⟨v,hv⟩ := pow_succ_second_remainder n x y
    refine ⟨y*u-v,?_⟩
    have he : 2*(y^(n+1+1)-x^(n+1+1))-
        (y-x)*((↑(n+1)+1:D)*x^(n+1)+(↑(n+1)+1:D)*y^(n+1)) =
        y*(2*(y^(n+1)-x^(n+1))-(y-x)*((n+1:D)*x^n+(n+1:D)*y^n))-
        (y-x)*(y^(n+1)-x^(n+1)-(n+1:D)*x^n*(y-x)) := by
      simp only [pow_succ,Nat.cast_add,Nat.cast_one]
      ring
    simp only [Nat.cast_add,Nat.cast_one] at he ⊢
    rw [he,hu,hv]
    ring

lemma norm_pow_trapezoid_le (n : ℕ) (x y : D) :
    ‖2*(y^n-x^n)-(y-x)*((n:D)*x^(n-1)+(n:D)*y^(n-1))‖ ≤ ‖y-x‖^3 := by
  cases n with
  | zero => simp
  | succ n =>
    obtain ⟨u,hu⟩ := pow_succ_trapezoid_remainder n x y
    simp only [Nat.add_sub_cancel,Nat.cast_add,Nat.cast_one]
    rw [hu,norm_mul,norm_pow]
    exact mul_le_of_le_one_right (by positivity) (PadicInt.norm_le_one _)

/-- Trapezoid defect of an actual infinite restricted series. -/
theorem reval_trapezoid_error {f : PowerSeries D} (hf : Restricted f) (x y : D) :
    ‖2*(reval f y-reval f x)-(y-x)*(rjet 1 f x+rjet 1 f y)‖ ≤ ‖y-x‖^3 := by
  have hsum : HasSum (fun n => coeff n f *
      (2*(y^n-x^n)-(y-x)*((n:D)*x^(n-1)+(n:D)*y^(n-1))))
      (2*(reval f y-reval f x)-(y-x)*(rjet 1 f x+rjet 1 f y)) := by
    have h1 := ((hasSum_reval hf y).sub (hasSum_reval hf x)).mul_left (2:D)
    have hx := (summable_first_jet hf x).hasSum
    have hy := (summable_first_jet hf y).hasSum
    rw [first_jet_tsum hf x] at hx
    rw [first_jet_tsum hf y] at hy
    have h2 := (hx.add hy).mul_left (y-x)
    convert h1.sub h2 using 1 <;> first | rfl | (ext n;ring)
  rw [←hsum.tsum_eq]
  apply IsUltrametricDist.norm_tsum_le_of_forall_le
  intro n
  rw [norm_mul]
  exact (mul_le_of_le_one_left (norm_nonneg _) (PadicInt.norm_le_one _)).trans
    (norm_pow_trapezoid_le n x y)

end Komorebi.Euler
