module
public import Euler.CollisionAnalytic
@[expose] public section
noncomputable section
namespace Komorebi.Euler
open PowerSeries

/-- A synthetic, genuinely infinite test of the evaluation/lifting bridge.
This is not an Euler residual or an Euler certificate. -/
def infiniteSplitExample : Series := mk fun n =>
  if n=0 then 0 else if n=1 ∨ n=2 then 1 else (4:D)^(n-2)

lemma infiniteSplitExample_tail (n : ℕ) :
    coeff (n+3) infiniteSplitExample=(4:D)^n*4 := by
  simp only [infiniteSplitExample, coeff_mk]
  simp only [show n+3 ≠ 0 by omega, show ¬ (n+3=1 ∨ n+3=2) by omega, ↓reduceIte]
  rw [show n+3-2=n+1 by omega, pow_succ]

lemma infiniteSplitExample_infinite_support (n : ℕ) :
    coeff (n+3) infiniteSplitExample ≠ 0 := by
  rw [infiniteSplitExample_tail]
  have hf : (4:D)≠0 := by norm_num
  exact mul_ne_zero (pow_ne_zero n hf) hf

lemma infiniteSplitExample_restricted : Restricted infiniteSplitExample :=
  restricted_of_four_tail infiniteSplitExample 3 (fun _ => 4) infiniteSplitExample_tail

lemma infiniteSplitExample_residue (n : ℕ) :
    res (coeff n infiniteSplitExample)=
      (Polynomial.X^2+Polynomial.X : Polynomial F₂).coeff n := by
  rcases n with _ | n
  · simp [infiniteSplitExample, Polynomial.coeff_X]
  rcases n with _ | n
  · simp [infiniteSplitExample, Polynomial.coeff_X]
  rcases n with _ | n
  · simp [infiniteSplitExample, Polynomial.coeff_X]
  · rw [show n+1+1+1=n+3 by omega, infiniteSplitExample_tail]
    have h4 : res (4:D)=0 := by rw [res_eq_red]; simp
    simp [h4, Polynomial.coeff_X, show n+3 ≠ 2 by omega]

/-- The genuinely infinite synthetic example has exactly two simple dyadic roots. -/
theorem infiniteSplitExample_two_roots :
    ∃ a b : D, res a=0 ∧ res b=1 ∧ a ≠ b ∧
      (∀ x : D, reval infiniteSplitExample x=0 ↔ x=a ∨ x=b) ∧
      (∀ x : D, reval infiniteSplitExample x=0 →
        deriv (qeval infiniteSplitExample) (x:ℚ_[2]) ≠ 0) :=
  restricted_two_simple_roots infiniteSplitExample_restricted infiniteSplitExample_residue

end Komorebi.Euler
