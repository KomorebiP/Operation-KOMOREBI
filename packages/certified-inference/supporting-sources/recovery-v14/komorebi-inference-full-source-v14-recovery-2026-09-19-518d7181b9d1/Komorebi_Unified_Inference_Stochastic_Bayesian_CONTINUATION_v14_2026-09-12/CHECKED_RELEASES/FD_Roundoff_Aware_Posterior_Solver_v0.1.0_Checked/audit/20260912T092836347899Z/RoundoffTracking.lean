import Komorebi.RoundoffEnergy
import Komorebi.RichardsonIteration

set_option autoImplicit false
namespace Komorebi.RoundoffSolver
open Matrix Komorebi.ExactPosterior Komorebi.GainSolver
variable {ι κ : Type*} [Fintype ι] [Fintype κ] [DecidableEq κ]

/-- Successive execution of the declared update, including every rounding operation it contains. -/
def iterate (step : Matrix ι κ ℚ → Matrix ι κ ℚ) (B : Matrix ι κ ℚ) : ℕ → Matrix ι κ ℚ
  | 0 => B
  | n+1 => step (iterate step B n)

@[simp] theorem iterate_zero (step : Matrix ι κ ℚ → Matrix ι κ ℚ) (B : Matrix ι κ ℚ) :
    iterate step B 0 = B := rfl
@[simp] theorem iterate_succ (step : Matrix ι κ ℚ → Matrix ι κ ℚ) (B : Matrix ι κ ℚ) (n : ℕ) :
    iterate step B (n+1) = step (iterate step B n) := rfl

omit [Fintype ι] in
theorem gainStep_sub (A : Matrix ι κ ℚ) (S : Matrix κ κ ℚ) (τ : ℚ)
    (U V : Matrix ι κ ℚ) :
    gainStep A S τ U-gainStep A S τ V = (U-V)*(1-τ • S) := by
  simp only [gainStep, Matrix.mul_sub, Matrix.mul_one, Matrix.mul_smul,
    Matrix.sub_mul, smul_sub]
  abel

omit [Fintype ι] in
/-- Local update error enters the residual as a separate right-multiplied forcing term. -/
theorem residual_forced_step (A : Matrix ι κ ℚ) (S : Matrix κ κ ℚ) (τ : ℚ)
    (B E : Matrix ι κ ℚ) :
    A-(gainStep A S τ B+E)*S = (A-B*S)*(1-τ • S)-E*S := by
  rw [Matrix.add_mul, sub_add_eq_sub_sub, residual_gainStep]

/-- Uniform tracking of the ideal trajectory, under an actual local error bound. -/
theorem iterate_tracking_energy (A : Matrix ι κ ℚ) (S : Matrix κ κ ℚ) (τ q e : ℚ)
    (step : Matrix ι κ ℚ → Matrix ι κ ℚ) (B : Matrix ι κ ℚ)
    (hq : 0 ≤ q) (h1 : q < 1) (he : 0 ≤ e)
    (hT : ∀ F : Matrix ι κ ℚ, rationalEnergy (F*(1-τ • S)) ≤ q*rationalEnergy F)
    (hE : ∀ U, rationalEnergy (step U-gainStep A S τ U) ≤ e) (n : ℕ) :
    rationalEnergy (iterate step B n-gainIter A S τ B n) ≤ 6*e/(1-q)^2 := by
  induction n with
  | zero => simp only [iterate_zero,gainIter_zero,sub_self,energy_zero]; positivity
  | succ n ih =>
    let U := iterate step B n
    let V := gainIter A S τ B n
    have hid : step U-gainStep A S τ V =
        (U-V)*(1-τ • S)+(step U-gainStep A S τ U) := by
      rw [← gainStep_sub]
      abel
    change rationalEnergy (step U-gainStep A S τ V) ≤ _
    rw [hid]
    apply (energy_add_contract _ _ q (rationalEnergy (U-V)) e hq h1
      (rationalEnergy_nonneg _) he (hT _) (hE U)).trans
    calc
      ((1+q)/2)*rationalEnergy (U-V)+(3/(1-q))*e ≤
          ((1+q)/2)*(6*e/(1-q)^2)+(3/(1-q))*e := by
        exact add_le_add (mul_le_mul_of_nonneg_left ih (by positivity)) le_rfl
      _ = _ := invariant_energy_floor q e h1

/-- Gain tracking transfers to actual residual energy without an exact inverse. -/
theorem residual_energy_compare (A : Matrix ι κ ℚ) (S : Matrix κ κ ℚ)
    (U V : Matrix ι κ ℚ) :
    rationalEnergy (A-U*S) ≤
      2*rationalEnergy (A-V*S)+2*rationalEnergy (U-V)*rationalEnergy S := by
  have hid : A-U*S = (A-V*S)+ -((U-V)*S) := by
    rw [Matrix.sub_mul]
    abel
  rw [hid]
  apply (energy_add_le _ _).trans
  rw [energy_neg]
  have hm := mul_le_mul_of_nonneg_left (energy_mul_le (U-V) S) (by norm_num : (0:ℚ)≤2)
  nlinarith only [hm]

end Komorebi.RoundoffSolver
