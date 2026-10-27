module
public import PrimeBlockPolynomial
public import Mathlib.RingTheory.PowerSeries.Exp
public import Mathlib.RingTheory.PowerSeries.Log
public import Mathlib.Tactic
@[expose] public section
noncomputable section
set_option autoImplicit false
namespace KomorebiPaperIX.BinomialLogSeries
open PowerSeries PrimeBlockPolynomial
variable {A : Type*} [CommRing A] [Algebra ℚ A]

/-- The actual exponential with a ring-valued exponent multiplier. -/
def expAt (a : A) : PowerSeries A := rescale a (exp A)

/-- The actual formal logarithmic substitution. -/
def logPullback (a : A) : PowerSeries A := (expAt a).subst (log A)

theorem expAt_derivative (a : A) : derivative A (expAt a)=C a*expAt a := by
  ext n
  simp only [expAt, coeff_derivative, coeff_rescale, coeff_exp, coeff_C_mul]
  have hf : algebraMap ℚ A (1/(n+1).factorial) * (n+1:A) =
      algebraMap ℚ A (1/n.factorial) := by
    have hn : (n+1:A)=algebraMap ℚ A (n+1) := by simp
    rw [hn, ←map_mul]
    congr 1
    rw [Nat.factorial_succ, Nat.cast_mul, Nat.cast_add, Nat.cast_one]
    field_simp
  calc
    _ = a*a^n*(algebraMap ℚ A (1/(n+1).factorial)*(n+1:A)) := by rw [pow_succ]; ring
    _ = _ := by rw [hf]; ring

theorem logPullback_zero (a : A) : constantCoeff (logPullback a)=1 := by
  rw [logPullback, constantCoeff_eq, constantCoeff_subst_of_constantCoeff_zero constantCoeff_log,
    ←constantCoeff_eq]
  simp [expAt]

theorem logPullback_equation (a : A) :
    derivative A (logPullback a) + derivative A (logPullback a)*X = C a*logPullback a := by
  have hs : HasSubst (log A) := HasSubst.of_constantCoeff_zero' constantCoeff_log
  have hd : derivative A (logPullback a) =
      (C a*logPullback a)*derivative A (log A) := by
    rw [logPullback, derivative_subst hs, expAt_derivative, subst_mul hs, subst_C]
    rfl
  rw [hd]
  calc
    _ = C a*logPullback a*(derivative A (log A)*(1+X)) := by ring
    _ = _ := by rw [derivative_log_mul_one_add_X]; ring

/-- The falling-factorial coefficient recurrence follows from the differential equation. -/
theorem logPullback_recurrence (a : A) (n : ℕ) :
    (n+1:A)*coeff (n+1) (logPullback a) = (a-(n:A))*coeff n (logPullback a) := by
  have h := congrArg (coeff n) (logPullback_equation a)
  cases n with
  | zero =>
    have hx : coeff 0 (derivative A (logPullback a)*X)=0 := by simp
    simp only [map_add, coeff_derivative, coeff_C_mul, Nat.cast_zero, zero_add, mul_one, hx,
      add_zero] at h
    simpa using h
  | succ n =>
    have hx : coeff (n+1) (derivative A (logPullback a)*X) =
        coeff n (derivative A (logPullback a)) := by
      simp
    simp only [map_add, hx, coeff_derivative, coeff_C_mul] at h
    push_cast at h ⊢
    linear_combination h

omit [Algebra ℚ A] in
theorem fallingAt_succ (a : A) (n : ℕ) :
    fallingAt a (n+1)=fallingAt a n*(a-(n:A)) := by
  exact Finset.prod_range_succ _ _

/-- Exact coefficient extraction, with no analytic convergence hypothesis. -/
theorem factorial_coeff_logPullback (a : A) (n : ℕ) :
    (n.factorial:A)*coeff n (logPullback a)=fallingAt a n := by
  induction n with
  | zero => simp [fallingAt, coeff_zero_eq_constantCoeff, logPullback_zero]
  | succ n ih =>
    rw [Nat.factorial_succ, Nat.cast_mul, fallingAt_succ]
    calc
      _ = (n.factorial:A)*((n+1:A)*coeff (n+1) (logPullback a)) := by push_cast; ring
      _ = (n.factorial:A)*((a-(n:A))*coeff n (logPullback a)) := by rw [logPullback_recurrence]
      _ = ((n.factorial:A)*coeff n (logPullback a))*(a-(n:A)) := by ring
      _ = _ := by rw [ih]

theorem coeff_logPullback (a : A) (n : ℕ) :
    coeff n (logPullback a)=algebraMap ℚ A (1/n.factorial)*fallingAt a n := by
  have hu : algebraMap ℚ A (1/n.factorial)*(n.factorial:A)=1 := by
    rw [←map_natCast (algebraMap ℚ A), ←map_mul]
    have hn : (n.factorial:ℚ)≠0 := Nat.cast_ne_zero.mpr (Nat.factorial_ne_zero n)
    rw [one_div, inv_mul_cancel₀ hn, map_one]
  rw [←factorial_coeff_logPullback a n, ←mul_assoc, hu, one_mul]

end KomorebiPaperIX.BinomialLogSeries
